#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kitab_pipeline.py — OCR + Latin Pesantren + terjemah Indonesia untuk kitab PDF pindaian,
halaman demi halaman, lewat API Gemini (endpoint kompatibel-OpenAI). Bisa dilanjutkan (resume).

Sub-perintah
  proses PDF BASE_URL MODEL   kerjakan halaman yang belum selesai, lalu gabungkan hasilnya
  tes    BASE_URL MODEL       hanya uji koneksi/kunci/model (biaya nyaris nol)
  gabung                      hanya gabungkan hasil yang sudah ada (tanpa memanggil API)

Kunci API dibaca HANYA dari variabel lingkungan KITAB_API_KEY. Kunci tidak pernah diterima
lewat argumen, tidak pernah ditulis ke berkas, dan disamarkan di semua log.

Kode keluar: 0 semua halaman selesai | 1 sebagian gagal/belum | 2 galat fatal (kunci, model,
jaringan, berkas) | 3 kuota harian/kuota nol habis.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import queue
import random
import re
import signal
import sys
import threading
import time
import traceback
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlsplit

import requests

try:  # PyMuPDF >= 1.24.3
    import pymupdf
except ImportError:  # versi lama
    import fitz as pymupdf  # type: ignore

VERSI = "1.0"
KODE_OK, KODE_SEBAGIAN, KODE_FATAL, KODE_KUOTA = 0, 1, 2, 3
DIR_SKRIP = Path(__file__).resolve().parent
PEMISAH_HALAMAN = "<<<HALAMAN {n}>>>"

ATURAN_EDISI = {
    "kajian": (
        "ATURAN EDISI (sama dengan edisi-edisi lain di repo ini): terjemah disajikan sebagai KAJIAN "
        "FILOLOGI — menguraikan apa yang tertulis, apa maksudnya, dan untuk apa menurut pengarangnya. "
        "Teks Arab dan Latin tetap disalin utuh dan setia. Namun untuk amalan yang dimaksudkan "
        "mencelakai, memaksa, atau memperdaya orang lain (misalnya sihir pemisah/pembinasa atau "
        "guna-guna paksaan), bagian Terjemah Indonesia cukup menguraikan isi dan tujuannya menurut "
        "naskah (beri label *bahan kajian*) tanpa merinci langkah praktik yang memudaratkan. Amalan "
        "yang baik (doa, ayat, perlindungan, pengobatan) diterjemahkan lengkap."
    ),
    "penuh": (
        "ATURAN EDISI: terjemahkan SELURUH isi halaman secara setia dan lengkap — termasuk bacaan, "
        "bahan, jumlah, dan tata cara persis seperti tertulis. Jangan meringkas, jangan menyensor, "
        "jangan menambah komentar."
    ),
}
ATURAN_DOKUMEN = {
    "kajian": ("Terjemah disajikan sebagai **kajian filologi**: menguraikan apa yang tertulis, apa "
               "maksudnya, dan untuk apa menurut pengarangnya — tanpa merinci langkah praktik yang "
               "memudaratkan."),
    "penuh": "Terjemah disajikan **lengkap dan setia** sebagaimana tertulis pada halaman.",
}
NAMA_MODE = {
    "bearer": "header Authorization: Bearer",
    "xgoog": "header x-goog-api-key",
    "native": "endpoint native Gemini (generateContent)",
}
BLOK_NATIVE = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "RECITATION", "IMAGE_SAFETY"}


# ───────────────────────────── utilitas umum ─────────────────────────────

def env_str(nama: str, default: str = "") -> str:
    v = os.environ.get(nama)
    return v if v not in (None, "") else default


def env_int(nama: str, default: int) -> int:
    try:
        return int(env_str(nama, str(default)).strip())
    except ValueError:
        print(f"Peringatan: {nama} bukan angka, memakai {default}", file=sys.stderr)
        return default


def env_bool(nama: str) -> bool:
    return env_str(nama).strip().lower() in ("1", "true", "ya", "yes", "y", "on")


def sekarang_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tulis_atomik(path: Path, isi) -> None:
    """Tulis lewat berkas sementara + os.replace: tak pernah ada berkas setengah jadi."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp{os.getpid()}_{threading.get_ident()}")
    if isinstance(isi, (bytes, bytearray)):
        with open(tmp, "wb") as f:
            f.write(isi)
            f.flush()
            os.fsync(f.fileno())
    else:
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(isi)
            f.flush()
            os.fsync(f.fileno())
    os.replace(tmp, path)


def baca_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def format_durasi(detik: float) -> str:
    detik = int(max(0, detik))
    j, sisa = divmod(detik, 3600)
    m, s = divmod(sisa, 60)
    if j:
        return f"{j} j {m:02d} mnt"
    return f"{m} mnt {s:02d} dtk" if m else f"{s} dtk"


def ringkas_rentang(nomor: List[int]) -> str:
    """[7, 8, 9, 12] → '7–9, 12'"""
    kelompok: List[List[int]] = []
    for n in sorted(set(nomor)):
        if kelompok and n == kelompok[-1][-1] + 1:
            kelompok[-1].append(n)
        else:
            kelompok.append([n])
    return ", ".join(str(k[0]) if len(k) == 1 else f"{k[0]}–{k[-1]}" for k in kelompok)


class Catatan:
    """Log ke layar + berkas. Semua keluaran disamarkan dari kunci API."""

    def __init__(self) -> None:
        self._kunci = ""
        self._lock = threading.Lock()
        self._berkas = None

    def atur_kunci(self, kunci: str) -> None:
        self._kunci = kunci or ""

    def buka_berkas(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._berkas = open(path, "a", encoding="utf-8")

    def tutup(self) -> None:
        with self._lock:
            if self._berkas:
                self._berkas.close()
                self._berkas = None

    def bersihkan(self, teks) -> str:
        teks = str(teks)
        if self._kunci:
            teks = teks.replace(self._kunci, "***")
        return teks

    def __call__(self, pesan: str = "") -> None:
        baris = f"{time.strftime('%H:%M:%S')} {self.bersihkan(pesan)}"
        with self._lock:
            print(baris, flush=True)
            if self._berkas:
                self._berkas.write(baris + "\n")
                self._berkas.flush()


class GalatFatal(Exception):
    def __init__(self, pesan: str, kode: int = KODE_FATAL) -> None:
        super().__init__(pesan)
        self.kode = kode


class GalatAPI(Exception):
    """kategori: auth | model | kuota_harian | kuota_nol | laju | server | jaringan | timeout |
    respons | permintaan"""

    def __init__(self, pesan: str, *, status: Optional[int] = None, kategori: str = "permintaan",
                 bisa_diulang: bool = False, jeda_saran: Optional[float] = None) -> None:
        super().__init__(pesan)
        self.pesan = pesan
        self.status = status
        self.kategori = kategori
        self.bisa_diulang = bisa_diulang
        self.jeda_saran = jeda_saran

    def ringkas(self) -> str:
        return f"HTTP {self.status}: {self.pesan}" if self.status else self.pesan


@dataclass
class Konfigurasi:
    pdf: Path
    base_url: str
    model: str
    keluaran: Path
    pekerja: int = 8
    halaman_per_permintaan: int = 1
    timeout: float = 600.0
    mulai: int = 1
    akhir: Optional[int] = None
    maks_percobaan: int = 8
    auth: str = "auto"
    aturan: str = "kajian"
    judul: str = ""
    ulang_semua: bool = False
    lewati_tes: bool = False
    jeda_dasar: float = 5.0
    jeda_maks: float = 300.0
    batas_stagnasi: float = 1200.0
    batas_waktu: float = 0.0  # detik; 0 = tanpa batas. Berhenti rapi sebelum job Actions dipotong.
    suhu: float = 0.2
    reasoning_effort: Optional[str] = None
    maks_token: Optional[int] = None
    dpi_render: int = 200


@dataclass
class Jawaban:
    teks: str
    selesai: Optional[str]
    token_masuk: int
    token_keluar: int
    diblokir: bool
    mode: str


@dataclass
class GambarHalaman:
    nomor: int
    path: Path
    mime: str
    sha256: str
    ukuran: int
    asli: bool


# ───────────────────────────── PDF → gambar halaman ─────────────────────────────

RE_DO = re.compile(rb"/([^\s/<>\[\]()%]+)\s+Do\b")
_ANGKA = rb"([-+]?(?:\d+\.?\d*|\.\d+))"
RE_CM = re.compile(rb"\s+".join([_ANGKA] * 6) + rb"\s+cm\b")
BATAS_GAMBAR = 7_000_000  # byte; di atas ini halaman dirender ulang agar muat di permintaan


def gambar_tertanam(doc, page) -> Optional[Tuple[bytes, str]]:
    """Bila halaman hanyalah satu gambar penuh (pindaian), ambil gambar aslinya tanpa render.

    Dibaca dari aliran isi halaman (`q a 0 0 d e f cm /Nama Do Q`), bukan get_image_info():
    PDF hasil 'Image to PDF' mendaftarkan SEMUA gambar di setiap halaman, sehingga
    get_image_info() butuh ~1,5 dtk per halaman.
    """
    try:
        aliran = page.read_contents()
        if len(aliran) > 512 or page.rotation != 0:
            return None
        do, cm = RE_DO.findall(aliran), RE_CM.findall(aliran)
        if len(do) != 1 or len(cm) != 1:
            return None
        a, b, c, d = (float(x) for x in cm[0][:4])
        if abs(b) > 1e-3 or abs(c) > 1e-3 or a <= 0 or d <= 0:
            return None  # diputar / dicerminkan → render saja
        if (a * d) / max(page.rect.width * page.rect.height, 1e-9) < 0.85:
            return None  # bukan gambar-penuh
        nama = do[0].decode("latin-1")
        xref = [im[0] for im in page.get_images(full=True) if im[7] == nama]
        if len(xref) != 1:
            return None
        info = doc.extract_image(xref[0])
        if info.get("ext") not in ("jpeg", "png") or info.get("colorspace") not in (1, 3):
            return None
        if info.get("smask", 0):
            return None
        data = info["image"]
        if len(data) > BATAS_GAMBAR:
            return None
        return data, ("jpg" if info["ext"] == "jpeg" else "png")
    except Exception:
        return None


def ambil_gambar_halaman(doc, page, dpi: int) -> Tuple[bytes, str, bool]:
    """→ (byte gambar, ekstensi, asli?). Cadangan: render halaman ke JPEG."""
    g = gambar_tertanam(doc, page)
    if g:
        return g[0], g[1], True
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    try:
        data = pix.tobytes("jpeg", jpg_quality=90)
    except TypeError:
        data = pix.tobytes("jpeg")
    return data, "jpg", False


# ───────────────────────────── prompt & pengurai jawaban ─────────────────────────────

def muat_sistem_prompt(aturan: str) -> str:
    teks = (DIR_SKRIP / "prompt_halaman.txt").read_text(encoding="utf-8")
    return teks.replace("{ATURAN_EDISI}", ATURAN_EDISI[aturan]).strip()


RE_PEMISAH = re.compile(r"^[ \t]*<<<\s*HALAMAN\s+(\d+)\s*>>>[ \t]*$", re.M)
RE_JUDUL = re.compile(r"^\s{0,3}#{1,6}\s*Halaman\s+PDF\s+\d+", re.I)
RE_PAGAR = re.compile(r"^```[A-Za-z]*\s*$")


def urai_kelompok(teks: str, kelompok: List[int]) -> Dict[int, str]:
    """Pisahkan jawaban per halaman. Kelompok tunggal: seluruh teks (tanpa penanda)."""
    if len(kelompok) == 1:
        return {kelompok[0]: RE_PEMISAH.sub("", teks).strip()}
    hasil: Dict[int, str] = {}
    penanda = list(RE_PEMISAH.finditer(teks))
    for i, m in enumerate(penanda):
        akhir = penanda[i + 1].start() if i + 1 < len(penanda) else len(teks)
        n, isi = int(m.group(1)), teks[m.end():akhir].strip()
        if n in kelompok and isi and n not in hasil:
            hasil[n] = isi
    return hasil


def rapikan_halaman(teks: str, n: int) -> str:
    """Buang pagar kode pembungkus; pastikan judul '## Halaman PDF n' ada dan bernomor benar."""
    baris = teks.replace("\r\n", "\n").replace("\r", "\n").strip("\n").split("\n")
    while baris and not baris[0].strip():
        baris.pop(0)
    if baris and RE_PAGAR.match(baris[0].strip()):
        baris.pop(0)
        while baris and not baris[-1].strip():
            baris.pop()
        if baris and baris[-1].strip() == "```":
            baris.pop()
    for i, b in enumerate(baris):
        if not b.strip():
            continue
        if RE_JUDUL.match(b):
            baris[i] = re.sub(r"^\s{0,3}#{1,6}\s*Halaman\s+PDF\s+\d+", f"## Halaman PDF {n}", b,
                              count=1, flags=re.I)
        else:
            baris[i:i] = [f"## Halaman PDF {n}", ""]
        break
    return "\n".join(baris).strip() + "\n"


def format_baku(teks: str) -> bool:
    return "**Teks Arab" in teks and "**Terjemah Indonesia" in teks


# ───────────────────────────── klasifikasi galat HTTP ─────────────────────────────

RE_HARIAN = re.compile(r"per\s?day|daily|harian", re.I)
RE_KUOTA_NOL = re.compile(r"limit:\s*0\b")
RE_JEDA = re.compile(r'"?retryDelay"?\s*[:=]\s*"?(\d+(?:\.\d+)?)s', re.I)
RE_AUTH400 = re.compile(r"api[ _-]?key|authenticat|credential|unauthenticated", re.I)


def pesan_dari_badan(teks: str) -> str:
    try:
        data = json.loads(teks)
    except ValueError:
        return " ".join(teks.split())[:300]
    if isinstance(data, list) and data:
        data = data[0]
    if isinstance(data, dict):
        err = data.get("error", data)
        if isinstance(err, dict):
            msg = str(err.get("message") or "")
            st = str(err.get("status") or "")
            gabung = f"{st}: {msg}" if st and st not in msg else msg
            return " ".join((gabung or teks).split())[:300]
        if isinstance(err, str):
            return err[:300]
    return " ".join(teks.split())[:300]


def ringkas_jaringan(e: Exception) -> str:
    """Ubah galat requests/urllib3 yang panjang menjadi satu kalimat yang bisa ditindaklanjuti."""
    teks = " ".join(str(e).split())
    kecil = teks.lower()
    if isinstance(e, requests.exceptions.SSLError) or "ssl" in kecil or "tls" in kecil:
        return "handshake TLS diputus (kemungkinan host diblokir firewall/proxy)"
    if any(k in kecil for k in ("name or service not known", "temporary failure in name resolution",
                                "nodename nor servname", "getaddrinfo", "failed to resolve")):
        return "nama host tidak ditemukan (DNS)"
    if "connection refused" in kecil or "errno 111" in kecil:
        return "koneksi ditolak (port tertutup / layanan tidak berjalan)"
    if any(k in kecil for k in ("reset", "aborted", "remotedisconnected")):
        return "koneksi diputus oleh server/jaringan"
    if "timed out" in kecil:
        return "waktu sambung habis"
    return f"{type(e).__name__}: {teks[:120]}"


def klasifikasi(status: int, teks: str, header) -> GalatAPI:
    pesan = pesan_dari_badan(teks)
    jeda: Optional[float] = None
    ra = (header.get("Retry-After") or "").strip()
    if re.fullmatch(r"\d+(\.\d+)?", ra):
        jeda = float(ra)
    m = RE_JEDA.search(teks)
    if m:
        jeda = max(jeda or 0.0, float(m.group(1)))
    if status == 429:
        if RE_KUOTA_NOL.search(teks):
            return GalatAPI(pesan, status=status, kategori="kuota_nol")
        if RE_HARIAN.search(teks):
            return GalatAPI(pesan, status=status, kategori="kuota_harian", jeda_saran=jeda)
        return GalatAPI(pesan, status=status, kategori="laju", bisa_diulang=True, jeda_saran=jeda)
    if status in (401, 403):
        return GalatAPI(pesan, status=status, kategori="auth")
    if status == 404:
        return GalatAPI(pesan, status=status, kategori="model")
    if status == 400 and RE_AUTH400.search(teks):
        return GalatAPI(pesan, status=status, kategori="auth")
    if status >= 500 or status == 408:
        return GalatAPI(pesan, status=status, kategori="server", bisa_diulang=True, jeda_saran=jeda)
    return GalatAPI(pesan, status=status, kategori="permintaan")


# ───────────────────────────── klien API ─────────────────────────────

class Klien:
    """Satu fungsi: panggil(sistem, bagian) → Jawaban. Mendukung 3 cara autentikasi:
    bearer (standar OpenAI), xgoog (header x-goog-api-key), native (generateContent)."""

    def __init__(self, cfg: Konfigurasi, kunci: str, log: Catatan) -> None:
        self.cfg, self.kunci, self.log = cfg, kunci, log
        u = urlsplit(cfg.base_url)
        if u.scheme not in ("http", "https") or not u.netloc:
            raise GalatFatal(f"base_url tidak valid: {cfg.base_url!r} (harus diawali http:// atau https://)")
        self.host = u.hostname or ""
        self.url_kompat = cfg.base_url.rstrip("/") + "/chat/completions"
        google = self.host.endswith("googleapis.com")
        model_id = cfg.model[len("models/"):] if cfg.model.startswith("models/") else cfg.model
        self.url_native = (f"{u.scheme}://{u.netloc}/v1beta/models/{model_id}:generateContent"
                           if (google or env_bool("KITAB_NATIVE")) else None)
        self.mode: Optional[str] = None
        self._lokal = threading.local()

    def _sesi(self) -> requests.Session:
        s = getattr(self._lokal, "sesi", None)
        if s is None:
            s = requests.Session()
            self._lokal.sesi = s
        return s

    def _header(self, mode: str) -> Dict[str, str]:
        h = {"Content-Type": "application/json; charset=utf-8", "User-Agent": f"kitab-pipeline/{VERSI}"}
        if mode == "bearer":
            h["Authorization"] = f"Bearer {self.kunci}"
        else:
            h["x-goog-api-key"] = self.kunci
        return h

    def _badan(self, mode: str, sistem: str, bagian: list) -> dict:
        c = self.cfg
        if mode == "native":
            parts = [{"text": b[1]} if b[0] == "teks" else {"inlineData": {"mimeType": b[1], "data": b[2]}}
                     for b in bagian]
            body: dict = {"contents": [{"role": "user", "parts": parts}],
                          "generationConfig": {"temperature": c.suhu}}
            if sistem:
                body["systemInstruction"] = {"parts": [{"text": sistem}]}
            if c.maks_token:
                body["generationConfig"]["maxOutputTokens"] = c.maks_token
            return body
        isi = [{"type": "text", "text": b[1]} if b[0] == "teks"
               else {"type": "image_url", "image_url": {"url": f"data:{b[1]};base64,{b[2]}"}}
               for b in bagian]
        pesan = ([{"role": "system", "content": sistem}] if sistem else []) + [{"role": "user", "content": isi}]
        body = {"model": c.model, "messages": pesan, "temperature": c.suhu}
        if c.maks_token:
            body["max_tokens"] = c.maks_token
        if c.reasoning_effort:
            body["reasoning_effort"] = c.reasoning_effort
        return body

    def panggil(self, sistem: str, bagian: list, mode: Optional[str] = None) -> Jawaban:
        mode = mode or self.mode or "bearer"
        url = self.url_native if mode == "native" else self.url_kompat
        if not url:
            raise GalatAPI("mode native tidak tersedia untuk host ini", kategori="permintaan")
        data = json.dumps(self._badan(mode, sistem, bagian), ensure_ascii=False).encode("utf-8")
        try:
            r = self._sesi().post(url, headers=self._header(mode), data=data,
                                  timeout=(15, self.cfg.timeout))
        except requests.exceptions.Timeout:
            raise GalatAPI(f"tidak ada jawaban dalam {self.cfg.timeout:.0f} dtk",
                           kategori="timeout", bisa_diulang=True)
        except requests.exceptions.RequestException as e:
            raise GalatAPI(f"koneksi gagal: {ringkas_jaringan(e)}", kategori="jaringan", bisa_diulang=True)
        if r.status_code != 200:
            raise klasifikasi(r.status_code, r.text, r.headers)
        try:
            badan = r.json()
        except ValueError:
            raise GalatAPI("jawaban server bukan JSON", status=200, kategori="respons", bisa_diulang=True)
        return self._urai(mode, badan)

    @staticmethod
    def _urai(mode: str, d: dict) -> Jawaban:
        if mode == "native":
            kand = d.get("candidates") or []
            um = d.get("usageMetadata") or {}
            mi = int(um.get("promptTokenCount") or 0)
            mk = int(um.get("candidatesTokenCount") or 0) + int(um.get("thoughtsTokenCount") or 0)
            if not kand:
                alasan = (d.get("promptFeedback") or {}).get("blockReason")
                return Jawaban("", alasan or "tanpa_kandidat", mi, mk, bool(alasan), mode)
            c0 = kand[0]
            parts = (c0.get("content") or {}).get("parts") or []
            teks = "".join(p.get("text", "") for p in parts if isinstance(p, dict) and not p.get("thought"))
            selesai = c0.get("finishReason")
            return Jawaban(teks, selesai, mi, mk, (not teks.strip()) and selesai in BLOK_NATIVE, mode)
        pilihan = d.get("choices") or []
        if not pilihan and d.get("error"):
            raise GalatAPI(pesan_dari_badan(json.dumps(d)), status=200, kategori="server", bisa_diulang=True)
        us = d.get("usage") or {}
        mi, mk = int(us.get("prompt_tokens") or 0), int(us.get("completion_tokens") or 0)
        if not pilihan:
            return Jawaban("", "tanpa_pilihan", mi, mk, False, mode)
        c0 = pilihan[0]
        isi = (c0.get("message") or {}).get("content")
        if isinstance(isi, list):
            isi = "".join(p.get("text", "") for p in isi if isinstance(p, dict))
        teks = isi or ""
        selesai = c0.get("finish_reason")
        return Jawaban(teks, selesai, mi, mk, (not teks.strip()) and selesai == "content_filter", mode)

    # ── uji awal: gagal cepat bila kunci/model/jaringan salah, sebelum menyentuh 103 halaman ──
    def urutan_mode(self) -> List[str]:
        a = self.cfg.auth
        if a == "auto":
            return ["bearer", "xgoog"] + (["native"] if self.url_native else [])
        return [{"x-goog-api-key": "xgoog"}.get(a, a)]

    def tes_koneksi(self) -> None:
        riwayat: List[Tuple[str, GalatAPI]] = []
        for mode in self.urutan_mode():
            if mode == "native" and not self.url_native:
                continue
            for percobaan in range(1, 6):
                t0 = time.monotonic()
                try:
                    j = self.panggil("", [("teks", "Balas hanya dengan satu kata: OK")], mode=mode)
                except GalatAPI as e:
                    riwayat.append((mode, e))
                    # galat jaringan (tolak koneksi, DNS gagal) jarang sementara → cepat menyerah;
                    # 429/5xx/timeout sering sementara → lebih sabar
                    batas = 3 if e.kategori == "jaringan" else 5
                    if e.kategori in ("jaringan", "timeout", "server", "laju") and percobaan < batas:
                        jeda = min(self.cfg.jeda_maks, max(e.jeda_saran or 0.0,
                                                           self.cfg.jeda_dasar * 2 ** (percobaan - 1)))
                        self.log(f"  tes koneksi ({mode}): {e.ringkas()} — ulang {jeda:.0f} dtk lagi")
                        time.sleep(jeda)
                        continue
                    break
                self.mode = mode
                self.log(f"✓ Tes koneksi berhasil — {NAMA_MODE[mode]}, model {self.cfg.model}, "
                         f"{time.monotonic() - t0:.1f} dtk"
                         + (f" (jawaban: {j.teks.strip()[:20]!r})" if j.teks.strip() else ""))
                return
            if riwayat and riwayat[-1][1].kategori not in ("auth", "permintaan"):
                break  # model salah / jaringan / kuota: mencoba cara lain tidak ada gunanya
        if not riwayat:
            raise GalatFatal(f"Mode autentikasi '{self.cfg.auth}' tidak tersedia untuk host {self.host} "
                             "(mode native hanya untuk generativelanguage.googleapis.com).")
        raise self._galat_tes(riwayat)

    def _galat_tes(self, riwayat: List[Tuple[str, GalatAPI]]) -> GalatFatal:
        baris = ["Tes koneksi GAGAL — pekerjaan dibatalkan sebelum memakai kuota."]
        hitung: Counter = Counter((mode, e.ringkas()) for mode, e in riwayat)
        for (mode, ringkas), n in hitung.items():  # Counter menjaga urutan kemunculan pertama
            baris.append(f"  • {NAMA_MODE[mode]}: {ringkas}" + (f"  (×{n})" if n > 1 else ""))
        kat = {e.kategori for _, e in riwayat}
        kode = KODE_FATAL
        if kat <= {"jaringan", "timeout"}:
            baris.append(f"Tidak bisa terhubung ke {self.host}. Periksa internet/firewall/proxy "
                         "(sebagian jaringan memblokir domain Google).")
        elif "kuota_nol" in kat:
            kode = KODE_KUOTA
            baris.append("Kuota model ini 0 untuk kunci Anda (paket gratis tidak mencakupnya?). "
                         "Aktifkan penagihan di AI Studio atau pakai model lain.")
        elif "kuota_harian" in kat:
            kode = KODE_KUOTA
            baris.append("Kuota harian habis. Coba lagi setelah kuota direset (pukul 00.00 waktu Pasifik).")
        elif "model" in kat:
            baris.append(f"Model {self.cfg.model!r} tidak ditemukan / tidak tersedia untuk kunci ini.")
        elif "auth" in kat:
            baris.append("Kunci ditolak. Pastikan KITAB_API_KEY benar & aktif (AI Studio → API keys) dan "
                         "diizinkan memakai Gemini API. Kunci baru berawalan 'AQ.' kadang ditolak pada "
                         "endpoint kompatibel-OpenAI; skrip ini sudah mencoba cara lain secara otomatis.")
        return GalatFatal("\n".join(baris), kode)


class Gerbang:
    """Jeda bersama: begitu satu pekerja kena 429/5xx, semua pekerja menunggu."""

    def __init__(self) -> None:
        self._sampai = 0.0
        self._lock = threading.Lock()

    def tutup(self, detik: float) -> None:
        with self._lock:
            self._sampai = max(self._sampai, time.monotonic() + detik)

    def tunggu(self, stop: threading.Event) -> None:
        while not stop.is_set():
            sisa = self._sampai - time.monotonic()
            if sisa <= 0:
                return
            stop.wait(min(sisa, 1.0))


# ───────────────────────────── penggabung hasil (tanpa API) ─────────────────────────────

def _nama(n: int, lebar: int) -> str:
    return f"halaman_{n:0{lebar}d}"


def _gambar_rel(keluaran: Path, n: int, lebar: int) -> Optional[str]:
    for ext in ("jpg", "png"):
        if (keluaran / "gambar" / f"{_nama(n, lebar)}.{ext}").is_file():
            return f"gambar/{_nama(n, lebar)}.{ext}"
    return None


def gabungkan(keluaran: Path, log: Catatan) -> dict:
    """Rakit TERJEMAHAN.md + STATUS.md dari berkas per-halaman. Aman dijalankan kapan saja."""
    info = baca_json(keluaran / "_state" / "_proses.json") or {}
    dir_state = keluaran / "_state"
    nomor_ada = [int(m.group(1)) for p in dir_state.glob("halaman_*.json")
                 if (m := re.match(r"halaman_(\d+)\.json$", p.name))]
    total = int(info.get("total") or (max(nomor_ada) if nomor_ada else 0))
    if total <= 0:
        raise GalatFatal(f"Belum ada hasil di {keluaran}/ untuk digabungkan.")
    lebar = max(3, len(str(total)))
    judul = info.get("judul") or "Terjemahan Kitab"
    aturan = info.get("aturan") if info.get("aturan") in ATURAN_DOKUMEN else "kajian"

    blok: List[str] = []
    ok = Counter()
    bermasalah: List[Tuple[int, str, str]] = []
    tidak_baku: List[int] = []
    token_masuk = token_keluar = 0
    model_dipakai: Counter = Counter()
    for n in range(1, total + 1):
        st = baca_json(dir_state / f"{_nama(n, lebar)}.json") or {}
        md = keluaran / "halaman" / f"{_nama(n, lebar)}.md"
        gambar = _gambar_rel(keluaran, n, lebar)
        if st.get("status") == "ok" and md.is_file() and md.stat().st_size > 0:
            teks = md.read_text(encoding="utf-8").rstrip()
            ok["ok"] += 1
            token_masuk += int(st.get("token_masuk") or 0)
            token_keluar += int(st.get("token_keluar") or 0)
            model_dipakai[st.get("model") or "?"] += 1
            if not st.get("baku", True):
                tidak_baku.append(n)
        else:
            status = st.get("status") or "belum"
            alasan = st.get("alasan") or ("belum diproses" if status == "belum" else "")
            ok[status] += 1
            bermasalah.append((n, status, alasan))
            label = {"belum": "BELUM DIPROSES", "gagal": "GAGAL DIPROSES",
                     "diblokir": "DIBLOKIR FILTER MODEL"}.get(status, status.upper())
            teks = f"## Halaman PDF {n} — *({label}{': ' + alasan if alasan and status != 'belum' else ''})*"
        if gambar:
            teks += f"\n\n![Halaman PDF {n} — gambar asli]({gambar})"
        blok.append(teks)

    n_ok = ok["ok"]
    model_str = ", ".join(f"`{m}`" for m, _ in model_dipakai.most_common()) or f"`{info.get('model', '?')}`"
    kepala = [
        f"# {judul}",
        "## Teks Arab · Latin Pesantren · Terjemah Indonesia",
        "",
        "> **TATA CARA EDISI INI**",
        "> 1. Setiap halaman diberi nomor ganda: **Halaman PDF N (= cetak M)** — nomor cetak adalah nomor "
        "yang tercantum pada kitab aslinya.",
        f"> 2. Teks Arab disalin dari pindaian (OCR oleh model {model_str}), dilatinkan dengan **Latin "
        "Pesantren** (kh, sy, ts, gh, dz, q, ' ; vokal panjang digandakan: aa, ii, uu), lalu diterjemahkan "
        "ke bahasa Indonesia.",
        f"> 3. {ATURAN_DOKUMEN[aturan]}",
        "> 4. Rajah/wafaq/tilsam atau tulisan yang tidak terbaca ditandai *(rajah — tidak terbaca)* atau "
        "[tidak terbaca] dan tidak ditebak; gambar halaman asli disertakan di bawah setiap halaman.",
        "> 5. **Hasil mesin**: OCR dan terjemah dapat keliru. Mohon ditelaah ulang oleh ahlinya sebelum "
        "dijadikan rujukan.",
        ">",
        f"> Dihasilkan otomatis oleh `mulai_malam.sh` · {sekarang_utc()} · {n_ok}/{total} halaman selesai",
        "",
    ]
    tulis_atomik(keluaran / "TERJEMAHAN.md", "\n".join(kepala) + "\n" + "\n\n".join(blok) + "\n")

    baris = [
        "# STATUS PROSES MALAM",
        "",
        "| Butir | Nilai |",
        "|---|---|",
        f"| Berkas | `{info.get('pdf', '?')}` ({total} halaman) |",
        f"| Model | {model_str} |",
        f"| Pengaturan | {info.get('pekerja', '?')} pekerja · {info.get('halaman_per_permintaan', '?')} "
        f"halaman/permintaan · timeout {info.get('timeout', '?')} dtk · aturan edisi: {aturan} |",
        f"| Selesai | **{n_ok}/{total}** |",
        f"| Gagal | {ok['gagal']} |",
        f"| Diblokir filter | {ok['diblokir']} |",
        f"| Belum diproses | {ok['belum']} |",
        f"| Token masuk / keluar | {token_masuk:,} / {token_keluar:,} |",
        f"| Berhenti karena | {info.get('berhenti') or ('-' if info.get('kode') in (None, 0) else 'lihat log')} |",
        f"| Terakhir diperbarui | {sekarang_utc()} |",
        "",
    ]
    gagal_rinci = [(n, st, al) for n, st, al in bermasalah if st != "belum"]
    belum_nomor = [n for n, st, _ in bermasalah if st == "belum"]
    if gagal_rinci:
        baris += ["## Halaman bermasalah", "", "| Halaman | Status | Keterangan |", "|---|---|---|"]
        for n, status, alasan in gagal_rinci:
            baris.append(f"| {n} | {status} | {alasan.replace('|', '/')} |")
        baris.append("")
    if belum_nomor:
        baris += ["## Belum diproses", "", f"Halaman {ringkas_rentang(belum_nomor)} ({len(belum_nomor)} halaman).", ""]
    if tidak_baku:
        baris += ["## Perlu dicek manual",
                  "",
                  "Keluaran tidak mengikuti format baku (bagian *Teks Arab* / *Terjemah Indonesia* tidak "
                  "ditemukan): halaman " + ", ".join(map(str, tidak_baku)), ""]
    baris += ["## Cara melanjutkan", "",
              "Jalankan ulang perintah yang sama. Halaman yang sudah selesai dilewati; hanya halaman "
              "gagal/belum yang dikerjakan lagi. Tambahkan `KITAB_ULANG_SEMUA=1` untuk mengulang dari awal.",
              ""]
    tulis_atomik(keluaran / "STATUS.md", "\n".join(baris))
    log(f"Hasil digabung → {keluaran}/TERJEMAHAN.md  ({n_ok}/{total} halaman selesai)")
    return {"total": total, "ok": n_ok, "gagal": ok["gagal"], "diblokir": ok["diblokir"],
            "belum": ok["belum"], "token_masuk": token_masuk, "token_keluar": token_keluar}


# ───────────────────────────── orkestrasi pekerjaan ─────────────────────────────

class Pekerjaan:
    def __init__(self, cfg: Konfigurasi, kunci: str, log: Catatan) -> None:
        self.cfg, self.log = cfg, log
        self.klien = Klien(cfg, kunci, log)
        self.sistem = muat_sistem_prompt(cfg.aturan)
        self.gerbang = Gerbang()
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.fatal: Optional[Tuple[int, str]] = None
        self.dihentikan = False
        self.batas_tercapai = False
        self.total = 0
        self.lebar = 3
        self.gambar: Dict[int, GambarHalaman] = {}
        self.n_ok = self.n_gagal = 0
        self.target = 0
        self.token_masuk = self.token_keluar = 0
        self.t_mulai = time.monotonic()
        self.sukses_terakhir = time.monotonic()

    # ── berkas ──
    def p_md(self, n: int) -> Path:
        return self.cfg.keluaran / "halaman" / f"{_nama(n, self.lebar)}.md"

    def p_state(self, n: int) -> Path:
        return self.cfg.keluaran / "_state" / f"{_nama(n, self.lebar)}.json"

    def sudah_ok(self, n: int) -> bool:
        st = baca_json(self.p_state(n))
        return bool(st and st.get("status") == "ok" and self.p_md(n).is_file() and self.p_md(n).stat().st_size > 0)

    def _tulis_info(self, **tambahan) -> None:
        c = self.cfg
        u = urlsplit(c.base_url)
        info = baca_json(c.keluaran / "_state" / "_proses.json") or {}
        info.update({
            "versi": VERSI, "pdf": str(c.pdf), "base_url": f"{u.scheme}://{u.netloc}{u.path}",
            "model": c.model, "total": self.total, "judul": c.judul, "aturan": c.aturan,
            "pekerja": c.pekerja, "halaman_per_permintaan": c.halaman_per_permintaan,
            "timeout": c.timeout, "diperbarui": sekarang_utc(),
        })
        info.update(tambahan)
        tulis_atomik(c.keluaran / "_state" / "_proses.json", json.dumps(info, ensure_ascii=False, indent=2) + "\n")

    # ── siapkan gambar ──
    def siapkan_gambar(self, doc, rentang: List[int]) -> None:
        asli = 0
        for n in rentang:
            data, ext, dari_pdf = ambil_gambar_halaman(doc, doc[n - 1], self.cfg.dpi_render)
            path = self.cfg.keluaran / "gambar" / f"{_nama(n, self.lebar)}.{ext}"
            sha = hashlib.sha256(data).hexdigest()
            if not (path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == sha):
                tulis_atomik(path, data)
            self.gambar[n] = GambarHalaman(n, path, "image/png" if ext == "png" else "image/jpeg",
                                           sha, len(data), dari_pdf)
            asli += dari_pdf
        mb = sum(g.ukuran for g in self.gambar.values()) / 1e6
        self.log(f"Gambar {len(rentang)} halaman siap ({asli} diambil asli dari PDF, "
                 f"{len(rentang) - asli} dirender) — {mb:.1f} MB → {self.cfg.keluaran}/gambar/")

    def susun_bagian(self, kelompok: List[int]) -> list:
        if len(kelompok) == 1:
            teks = (f"Kerjakan gambar di bawah ini, yaitu Halaman PDF {kelompok[0]} (dari {self.total} "
                    "halaman). Keluarkan hanya Markdown halaman itu sesuai format pada instruksi sistem.")
        else:
            daftar = ", ".join(str(n) for n in kelompok)
            teks = (f"Di bawah ini ada {len(kelompok)} gambar halaman berurutan: Halaman PDF {daftar} "
                    f"(dari {self.total} halaman). Kerjakan SETIAP halaman sesuai format pada instruksi "
                    "sistem. Mulai bagian tiap halaman dengan satu baris yang hanya berisi penanda persis "
                    "seperti ini: <<<HALAMAN n>>> (ganti n dengan nomor Halaman PDF), lalu isi Markdown "
                    "halaman itu. Jangan menulis apa pun sebelum penanda pertama.")
        bagian: list = [("teks", teks)]
        for n in kelompok:
            g = self.gambar[n]
            bagian.append(("teks", f"[Gambar berikut = Halaman PDF {n}]"))
            bagian.append(("gambar", g.mime, base64.b64encode(g.path.read_bytes()).decode("ascii")))
        return bagian

    # ── pencatatan hasil ──
    def _hitung_jeda(self, percobaan: int, saran: Optional[float]) -> float:
        dasar = self.cfg.jeda_dasar * 2 ** (percobaan - 1)
        jeda = min(self.cfg.jeda_maks, max(dasar, saran or 0.0))
        return jeda * random.uniform(0.85, 1.15)

    def _eta(self) -> str:
        selesai = self.n_ok + self.n_gagal
        if selesai == 0:
            return "?"
        sisa = max(0, self.target - selesai)
        return format_durasi((time.monotonic() - self.t_mulai) / selesai * sisa)

    def _simpan_ok(self, n: int, teks: str, j: Jawaban, durasi: float, percobaan: int, k: int) -> None:
        rapi = rapikan_halaman(teks, n)
        tulis_atomik(self.p_md(n), rapi)
        st = {"halaman": n, "status": "ok", "model": self.cfg.model, "percobaan": percobaan,
              "durasi_dtk": round(durasi, 1), "token_masuk": j.token_masuk // k,
              "token_keluar": j.token_keluar // k, "selesai_karena": j.selesai,
              "baku": format_baku(rapi), "halaman_per_permintaan": k, "mode_auth": j.mode,
              "gambar_sha256": self.gambar[n].sha256, "waktu": sekarang_utc()}
        tulis_atomik(self.p_state(n), json.dumps(st, ensure_ascii=False, indent=2) + "\n")  # 'ok' ditulis terakhir
        with self.lock:
            self.n_ok += 1
            self.token_masuk += st["token_masuk"]
            self.token_keluar += st["token_keluar"]
            hitung = self.n_ok + self.n_gagal
        self.log(f"[{hitung}/{self.target}] ✓ halaman {n}  {durasi:.0f} dtk  "
                 f"{j.token_keluar // k} token keluar  · sisa ±{self._eta()}"
                 + ("" if st["baku"] else "  (format tak baku — cek manual)"))

    def _catat_gagal(self, kelompok: List[int], status: str, alasan: str, percobaan: int) -> None:
        for n in kelompok:
            st = {"halaman": n, "status": status, "alasan": self.log.bersihkan(alasan)[:400],
                  "percobaan": percobaan, "model": self.cfg.model, "waktu": sekarang_utc()}
            tulis_atomik(self.p_state(n), json.dumps(st, ensure_ascii=False, indent=2) + "\n")
            with self.lock:
                self.n_gagal += 1
                hitung = self.n_ok + self.n_gagal
            self.log(f"[{hitung}/{self.target}] ✗ halaman {n}  {status}: {self.log.bersihkan(alasan)[:200]}")

    def _fatal(self, kode: int, pesan: str) -> None:
        with self.lock:
            if self.fatal is None:
                self.fatal = (kode, pesan)
                self.log("⛔ " + pesan)
        self.stop.set()

    # ── inti: kerjakan satu kelompok halaman ──
    def proses_kelompok(self, kelompok: List[int]) -> None:
        label = (f"halaman {kelompok[0]}" if len(kelompok) == 1
                 else f"halaman {kelompok[0]}–{kelompok[-1]}")
        percobaan = 0
        while not self.stop.is_set():
            self.gerbang.tunggu(self.stop)
            if self.stop.is_set():
                return
            percobaan += 1
            t0 = time.monotonic()
            try:
                j = self.klien.panggil(self.sistem, self.susun_bagian(kelompok))
            except GalatAPI as e:
                if self._tangani_galat(kelompok, label, e, percobaan):
                    continue
                return
            durasi = time.monotonic() - t0
            self.sukses_terakhir = time.monotonic()

            if j.diblokir or not j.teks.strip():
                alasan = (f"diblokir filter model ({j.selesai})" if j.diblokir
                          else f"jawaban kosong (finish_reason={j.selesai})")
                if len(kelompok) > 1:  # cari halaman biang keladinya: kerjakan satu per satu
                    self.log(f"  ⚠ {label}: {alasan} — dikerjakan satu per satu")
                    for n in kelompok:
                        if self.stop.is_set():
                            return
                        self.proses_kelompok([n])
                    return
                batas = min(2, self.cfg.maks_percobaan) if j.diblokir else self.cfg.maks_percobaan
                if percobaan >= batas:
                    self._catat_gagal(kelompok, "diblokir" if j.diblokir else "gagal", alasan, percobaan)
                    return
                self.log(f"  ↻ {label}: {alasan} — ulangi (percobaan {percobaan}/{batas})")
                self.stop.wait(self.cfg.jeda_dasar)
                continue

            bagian = urai_kelompok(j.teks, kelompok)
            diterima = [n for n in kelompok if len(bagian.get(n, "").strip()) >= 20]
            for n in diterima:
                self._simpan_ok(n, bagian[n], j, durasi, percobaan, len(kelompok))
            sisa = [n for n in kelompok if n not in diterima]
            if not sisa:
                return
            if len(kelompok) > 1:  # jawaban tak bisa dipisah rapi → ulangi satu-satu
                self.log(f"  ⚠ {label}: {len(sisa)} halaman tak terurai dari jawaban gabungan — "
                         "dikerjakan satu per satu")
                for n in sisa:
                    if self.stop.is_set():
                        return
                    self.proses_kelompok([n])
                return
            if percobaan >= self.cfg.maks_percobaan:
                self._catat_gagal(kelompok, "gagal", "jawaban terlalu pendek / tidak terbaca", percobaan)
                return
            self.log(f"  ↻ {label}: jawaban terlalu pendek — ulangi (percobaan {percobaan})")
            self.stop.wait(self.cfg.jeda_dasar)

    def _tangani_galat(self, kelompok: List[int], label: str, e: GalatAPI, percobaan: int) -> bool:
        """True = coba lagi; False = menyerah untuk kelompok ini (atau seluruh proses bila fatal)."""
        if e.kategori in ("auth", "model"):
            arti = "Kunci API ditolak/dicabut" if e.kategori == "auth" else "Model tidak ditemukan"
            self._fatal(KODE_FATAL, f"{arti} di tengah proses ({e.ringkas()}). Hasil yang sudah ada tersimpan; "
                                    "perbaiki lalu jalankan ulang untuk melanjutkan.")
            return False
        if e.kategori in ("kuota_harian", "kuota_nol"):
            self._fatal(KODE_KUOTA, f"Kuota habis ({e.ringkas()}). Hasil yang sudah ada tersimpan; "
                                    "jalankan ulang setelah kuota direset untuk melanjutkan.")
            return False
        if time.monotonic() - self.sukses_terakhir > self.cfg.batas_stagnasi:
            self._fatal(KODE_FATAL, f"Tidak ada permintaan yang berhasil selama "
                                    f"{format_durasi(self.cfg.batas_stagnasi)} (terakhir: {e.ringkas()}). Dihentikan.")
            return False
        if not e.bisa_diulang:
            self._catat_gagal(kelompok, "gagal", e.ringkas(), percobaan)
            return False
        if percobaan >= self.cfg.maks_percobaan:
            self._catat_gagal(kelompok, "gagal", f"menyerah setelah {percobaan} percobaan: {e.ringkas()}", percobaan)
            return False
        jeda = self._hitung_jeda(percobaan, e.jeda_saran)
        if e.kategori in ("laju", "server"):
            self.gerbang.tutup(jeda)
        self.log(f"  ⏳ {label}: {e.ringkas()} — ulang ±{jeda:.0f} dtk lagi "
                 f"(percobaan {percobaan}/{self.cfg.maks_percobaan})")
        self.stop.wait(jeda)
        return not self.stop.is_set()

    # ── alur utama ──
    def _sinyal(self, signum, _frame) -> None:
        if self.dihentikan:  # tekan lagi = keluar paksa
            os._exit(130)
        self.dihentikan = True
        self.log("Menerima sinyal berhenti — menyelesaikan penyimpanan… (tekan sekali lagi untuk paksa keluar)")
        self.stop.set()

    def jalankan(self) -> int:
        c = self.cfg
        if not c.pdf.is_file():
            raise GalatFatal(f"Berkas PDF tidak ditemukan: {c.pdf}")
        try:
            doc = pymupdf.open(str(c.pdf))
        except Exception as e:  # noqa: BLE001
            raise GalatFatal(f"PDF tidak bisa dibuka: {e}")
        if getattr(doc, "needs_pass", False):
            raise GalatFatal("PDF terkunci kata sandi.")
        self.total = doc.page_count
        self.lebar = max(3, len(str(self.total)))
        awal, akhir = max(1, c.mulai), min(self.total, c.akhir or self.total)
        if awal > akhir:
            raise GalatFatal(f"Rentang halaman kosong: mulai={c.mulai}, akhir={c.akhir}, total={self.total}")
        rentang = list(range(awal, akhir + 1))
        c.keluaran.mkdir(parents=True, exist_ok=True)
        self.log.buka_berkas(c.keluaran / "log" / f"malam_{time.strftime('%Y%m%d_%H%M%S')}.log")
        self.log(f"=== MULAI MALAM v{VERSI} === {c.pdf.name}: {self.total} halaman, dikerjakan {awal}–{akhir}")
        self.log(f"Model {c.model} · {c.pekerja} pekerja · {c.halaman_per_permintaan} halaman/permintaan · "
                 f"timeout {c.timeout:.0f} dtk · maks {c.maks_percobaan} percobaan · aturan edisi: {c.aturan}")
        self._tulis_info(mulai=sekarang_utc(), awal=awal, akhir=akhir, kode=None, berhenti=None)
        self.siapkan_gambar(doc, rentang)
        doc.close()

        tertunda = [n for n in rentang if c.ulang_semua or not self.sudah_ok(n)]
        self.target = len(tertunda)
        self.log(f"Sudah selesai sebelumnya: {len(rentang) - len(tertunda)} · akan dikerjakan: {len(tertunda)}")

        if tertunda:
            try:
                if c.lewati_tes:
                    self.klien.mode = self.klien.urutan_mode()[0]
                    self.log("Tes koneksi dilewati.")
                else:
                    self.klien.tes_koneksi()
            except GalatFatal as e:
                self._fatal(e.kode, str(e))
            if not self.fatal:
                self._kerjakan(tertunda)
        return self._selesaikan(rentang)

    def _kerjakan(self, tertunda: List[int]) -> None:
        c = self.cfg
        k = c.halaman_per_permintaan
        antrean: "queue.Queue[List[int]]" = queue.Queue()
        for i in range(0, len(tertunda), k):
            antrean.put(tertunda[i:i + k])
        self.t_mulai = self.sukses_terakhir = time.monotonic()
        stagger = min(1.0, c.jeda_dasar / 10.0)

        def kerja(idx: int) -> None:
            self.stop.wait(stagger * idx)  # hindari 8 permintaan serentak di detik pertama
            while not self.stop.is_set():
                try:
                    kel = antrean.get_nowait()
                except queue.Empty:
                    return
                try:
                    self.proses_kelompok(kel)
                except Exception as e:  # noqa: BLE001
                    self.log(f"  ✗ galat tak terduga pada halaman {kel}: {e!r}")
                    self.log(traceback.format_exc())
                    self._catat_gagal(kel, "gagal", f"galat internal: {e!r}", 0)

        pekerja = [threading.Thread(target=kerja, args=(i,), daemon=True, name=f"pekerja-{i}")
                   for i in range(min(c.pekerja, antrean.qsize()))]
        for t in pekerja:
            t.start()
        while any(t.is_alive() for t in pekerja) and not self.stop.is_set():
            self.stop.wait(0.3)
            if c.batas_waktu and time.monotonic() - self.t_mulai > c.batas_waktu:
                self.batas_tercapai = True
                self.log(f"⏱ Batas waktu {format_durasi(c.batas_waktu)} tercapai — berhenti rapi dan menyimpan hasil. "
                         "Jalankan ulang untuk melanjutkan.")
                self.stop.set()
        if self.stop.is_set():  # beri waktu singkat agar penulisan yang sedang berjalan tuntas
            batas = time.monotonic() + 5.0
            for t in pekerja:
                t.join(timeout=max(0.0, batas - time.monotonic()))

    def _selesaikan(self, rentang: List[int]) -> int:
        belum_ok = [n for n in rentang if not self.sudah_ok(n)]
        if self.fatal:
            kode, berhenti = self.fatal[0], self.log.bersihkan(self.fatal[1].splitlines()[0])[:200]
        elif self.dihentikan:
            kode, berhenti = KODE_SEBAGIAN, "dihentikan pengguna"
        elif self.batas_tercapai:
            kode, berhenti = KODE_SEBAGIAN, "batas waktu tercapai"
        else:
            kode, berhenti = (KODE_OK if not belum_ok else KODE_SEBAGIAN), None
        self._tulis_info(selesai=sekarang_utc(), kode=kode, berhenti=berhenti)
        ringkas = gabungkan(self.cfg.keluaran, self.log)
        self.log("────────────────────────────────────────")
        self.log(f"Sesi ini: {self.n_ok} halaman selesai · {self.n_gagal} gagal · "
                 f"belum selesai di rentang: {len(belum_ok)} · total berkas ok: {ringkas['ok']}/{ringkas['total']}")
        self.log(f"Token sesi ini: masuk {self.token_masuk:,} / keluar {self.token_keluar:,} · "
                 f"lama {format_durasi(time.monotonic() - self.t_mulai)}")
        if belum_ok:
            self.log("Halaman belum selesai: " + ", ".join(map(str, belum_ok[:30])) + (" …" if len(belum_ok) > 30 else ""))
            self.log("→ Jalankan ulang perintah yang sama untuk melanjutkan (yang sudah selesai dilewati).")
        return kode


# ───────────────────────────── CLI ─────────────────────────────

def judul_dari_pdf(pdf: Path) -> str:
    return " ".join(w.capitalize() for w in re.split(r"[-_\s]+", pdf.stem) if w) or "Terjemahan Kitab"


def bangun_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="kitab_pipeline.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="perintah", required=True)

    def umum(sp, pdf: bool) -> None:
        if pdf:
            sp.add_argument("pdf", help="berkas PDF pindaian")
        sp.add_argument("base_url", help="mis. https://generativelanguage.googleapis.com/v1beta/openai/")
        sp.add_argument("model", help="mis. gemini-2.5-pro")
        sp.add_argument("--timeout", type=float, default=600.0, help="batas tunggu satu permintaan, detik (600)")
        sp.add_argument("--auth", default=env_str("KITAB_AUTH", "auto"),
                        choices=["auto", "bearer", "x-goog-api-key", "native"],
                        help="cara kirim kunci (auto: coba satu per satu)")

    p = sub.add_parser("proses", help="kerjakan halaman yang belum selesai")
    umum(p, True)
    p.add_argument("--pekerja", type=int, default=8, help="permintaan paralel (8)")
    p.add_argument("--halaman-per-permintaan", type=int, default=1, dest="halaman_per_permintaan",
                   help="berapa halaman dikirim dalam satu permintaan (1)")
    p.add_argument("--keluaran", default=env_str("KITAB_KELUARAN", "hasil"))
    p.add_argument("--mulai", type=int, default=env_int("KITAB_MULAI", 1), help="halaman PDF pertama (1)")
    p.add_argument("--akhir", type=int, default=env_int("KITAB_AKHIR", 0) or None,
                   help="halaman PDF terakhir (default: sampai habis)")
    p.add_argument("--maks-percobaan", type=int, default=env_int("KITAB_MAKS_PERCOBAAN", 8),
                   dest="maks_percobaan")
    p.add_argument("--aturan", default=env_str("KITAB_ATURAN", "kajian"), choices=sorted(ATURAN_EDISI),
                   help="kajian = uraikan tanpa merinci langkah yang memudaratkan; penuh = terjemah lengkap")
    p.add_argument("--judul", default=env_str("KITAB_JUDUL", ""))
    p.add_argument("--ulang-semua", action="store_true", default=env_bool("KITAB_ULANG_SEMUA"))
    p.add_argument("--lewati-tes", action="store_true", default=env_bool("KITAB_LEWATI_TES"))

    t = sub.add_parser("tes", help="uji koneksi/kunci/model saja")
    umum(t, False)

    g = sub.add_parser("gabung", help="gabungkan hasil yang ada tanpa memanggil API")
    g.add_argument("--keluaran", default=env_str("KITAB_KELUARAN", "hasil"))
    return ap


def konfigurasi_dari(args, perintah: str) -> Konfigurasi:
    def f(nama: str, default: float) -> float:
        return float(env_str(nama, str(default)))

    return Konfigurasi(
        pdf=Path(getattr(args, "pdf", "") or "."), base_url=args.base_url, model=args.model,
        keluaran=Path(getattr(args, "keluaran", "hasil")),
        pekerja=getattr(args, "pekerja", 1), halaman_per_permintaan=getattr(args, "halaman_per_permintaan", 1),
        timeout=args.timeout, mulai=getattr(args, "mulai", 1), akhir=getattr(args, "akhir", None),
        maks_percobaan=getattr(args, "maks_percobaan", 3), auth=args.auth,
        aturan=getattr(args, "aturan", "kajian"),
        judul=(getattr(args, "judul", "") or (judul_dari_pdf(Path(args.pdf)) if getattr(args, "pdf", None) else "")),
        ulang_semua=getattr(args, "ulang_semua", False), lewati_tes=getattr(args, "lewati_tes", False),
        jeda_dasar=f("KITAB_JEDA_DASAR", 5.0), jeda_maks=f("KITAB_JEDA_MAKS", 300.0),
        batas_stagnasi=f("KITAB_BATAS_STAGNASI", 1200.0), batas_waktu=f("KITAB_BATAS_WAKTU", 0.0),
        suhu=f("KITAB_SUHU", 0.2),
        reasoning_effort=env_str("KITAB_REASONING_EFFORT") or None,
        maks_token=env_int("KITAB_MAKS_TOKEN", 0) or None,
        dpi_render=env_int("KITAB_DPI", 200),
    )


def periksa(cfg: Konfigurasi, perintah: str) -> None:
    if perintah == "proses":
        if not 1 <= cfg.pekerja <= 64:
            raise GalatFatal("--pekerja harus 1–64")
        if not 1 <= cfg.halaman_per_permintaan <= 20:
            raise GalatFatal("--halaman-per-permintaan harus 1–20")
        if cfg.maks_percobaan < 1:
            raise GalatFatal("--maks-percobaan harus ≥ 1")
    if cfg.timeout < 0.5:
        raise GalatFatal("--timeout terlalu kecil")


def ambil_kunci() -> str:
    kunci = os.environ.get("KITAB_API_KEY", "").strip().strip("'\"")
    if kunci.lower().startswith("bearer "):
        kunci = kunci[7:].strip()
    if not kunci:
        raise GalatFatal("Variabel KITAB_API_KEY belum diisi.\n"
                         "  Lokal   : export KITAB_API_KEY=\"kunci-anda\"\n"
                         "  Actions : Settings → Secrets and variables → Actions → New repository secret "
                         "(nama: KITAB_API_KEY)")
    if not kunci.isascii():
        raise GalatFatal("KITAB_API_KEY mengandung karakter non-ASCII — salin ulang kuncinya dengan benar.")
    if re.search(r"\s", kunci):
        raise GalatFatal("KITAB_API_KEY mengandung spasi/baris baru — salin ulang kuncinya tanpa spasi.")
    return kunci


def main(argv: Optional[List[str]] = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass
    args = bangun_parser().parse_args(argv)
    log = Catatan()
    try:
        if args.perintah == "gabung":
            gabungkan(Path(args.keluaran), log)
            return KODE_OK
        kunci = ambil_kunci()
        log.atur_kunci(kunci)
        cfg = konfigurasi_dari(args, args.perintah)
        periksa(cfg, args.perintah)
        if args.perintah == "tes":
            klien = Klien(cfg, kunci, log)
            klien.tes_koneksi()
            log("Kunci, model, dan endpoint siap dipakai. Aman menjalankan proses penuh.")
            return KODE_OK
        job = Pekerjaan(cfg, kunci, log)
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, job._sinyal)
            except ValueError:  # bukan thread utama (mis. saat diuji)
                pass
        return job.jalankan()
    except GalatFatal as e:
        for baris in log.bersihkan(e).splitlines():
            log("⛔ " + baris)
        return e.kode
    finally:
        log.tutup()


if __name__ == "__main__":
    sys.exit(main())
