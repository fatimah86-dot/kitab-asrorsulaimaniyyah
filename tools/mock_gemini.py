#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mock_gemini.py — server TIRUAN API Gemini (endpoint kompatibel-OpenAI + endpoint native) untuk
menguji kitab_pipeline.py / mulai_malam.sh tanpa internet dan tanpa biaya.

Dipakai oleh tools/test_pipeline.py. Bisa juga dijalankan manual:
    python tools/mock_gemini.py --port 8765 --auth aq_quirk
    KITAB_API_KEY=AQ.kunci-uji ./mulai_malam.sh kitab/asrorul-sulaimaniyah.pdf \
        http://127.0.0.1:8765/v1beta/openai/ gemini-2.5-pro 8 1 60

Kebijakan autentikasi (--auth):
  bearer        endpoint kompat menerima Authorization: Bearer; native menerima x-goog-api-key
  aq_quirk      kompat menolak Bearer (400 'Multiple authentication credentials received') tetapi
                menerima x-goog-api-key  (meniru laporan Juni 2026 tentang kunci 'AQ.')
  native_saja   kompat menolak semua cara (401); hanya native + x-goog-api-key yang diterima
  semua_ditolak semua permintaan 400 'API key not valid'
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import threading
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List, Optional, Set, Tuple

RE_LABEL = re.compile(r"\[Gambar berikut = Halaman PDF (\d+)\]")


class Skenario:
    def __init__(self, **kw) -> None:
        self.kunci: str = kw.get("kunci", "AQ.kunci-uji-123")
        self.auth: str = kw.get("auth", "bearer")
        self.model_ada: Set[str] = set(kw.get("model_ada", {"gemini-2.5-pro"}))
        self.tunda: float = kw.get("tunda", 0.02)
        self.tunda_pertama: Tuple[int, float] = kw.get("tunda_pertama", (0, 0.0))
        self.gagal_429_awal: int = kw.get("gagal_429_awal", 0)
        self.gagal_500_awal: int = kw.get("gagal_500_awal", 0)
        self.json_rusak_awal: int = kw.get("json_rusak_awal", 0)
        self.kuota_harian_setelah: Optional[int] = kw.get("kuota_harian_setelah")
        self.kuota_nol: bool = kw.get("kuota_nol", False)
        self.blokir_halaman: Set[int] = set(kw.get("blokir_halaman", ()))
        self.pendek_awal: int = kw.get("pendek_awal", 0)
        self.tanpa_pemisah: bool = kw.get("tanpa_pemisah", False)
        self.gema_kunci: bool = kw.get("gema_kunci", False)  # galat menyalin kunci (uji penyamaran)
        # ── rekaman ──
        self.lock = threading.Lock()
        self.permintaan = 0                       # semua POST yang sampai ke penanganan
        self.catatan: List[dict] = []             # satu entri per permintaan yang berisi gambar
        self.tes_koneksi = 0                      # permintaan tanpa gambar
        self.status: Counter = Counter()          # kode HTTP yang dikirim
        self.sistem_prompt: List[str] = []
        self.sedang = 0
        self.paralel_maks = 0
        self._hitung_halaman_ok = 0
        self._n_pendek = 0
        self._n_429 = 0
        self._n_500 = 0
        self._n_rusak = 0
        self._n_tunda = 0

    def halaman_diminta(self) -> List[int]:
        return [n for c in self.catatan for n in c["halaman"]]


def isi_halaman(n: int) -> str:
    return (f"## Halaman PDF {n} (= cetak {n - 1}) — JUDUL UJI {n}\n\n"
            f"**Teks Arab:**\n\n> نص تجريبي للصفحة {n}\n\n"
            f"**Latin Pesantren:**\n\n> nashsh tajriibii lish-shofhah {n}\n\n"
            f"**Terjemah Indonesia:**\n\nTeks uji untuk halaman {n}.\n")


def _ekstrak_kompat(body: dict) -> Tuple[str, List[Tuple[int, str, str, int, str]]]:
    """→ (sistem, [(halaman, sha256, mime, jumlah_byte, 3 byte pertama dalam hex)])"""
    sistem, gambar, menunggu = "", [], None
    for m in body.get("messages", []):
        if m.get("role") == "system":
            sistem = m.get("content", "") if isinstance(m.get("content"), str) else ""
        elif m.get("role") == "user" and isinstance(m.get("content"), list):
            for part in m["content"]:
                if part.get("type") == "text":
                    mm = RE_LABEL.search(part.get("text", ""))
                    if mm:
                        menunggu = int(mm.group(1))
                elif part.get("type") == "image_url":
                    url = part["image_url"]["url"]
                    mime = url.split(";", 1)[0][len("data:"):]
                    raw = base64.b64decode(url.split("base64,", 1)[1])
                    gambar.append((menunggu or -1, hashlib.sha256(raw).hexdigest(), mime, len(raw), raw[:3].hex()))
                    menunggu = None
    return sistem, gambar


def _ekstrak_native(body: dict) -> Tuple[str, List[Tuple[int, str, str, int, str]]]:
    sistem = ""
    si = body.get("systemInstruction") or {}
    if si.get("parts"):
        sistem = si["parts"][0].get("text", "")
    gambar, menunggu = [], None
    for c in body.get("contents", []):
        for part in c.get("parts", []):
            if "text" in part:
                mm = RE_LABEL.search(part["text"])
                if mm:
                    menunggu = int(mm.group(1))
            elif "inlineData" in part:
                raw = base64.b64decode(part["inlineData"]["data"])
                gambar.append((menunggu or -1, hashlib.sha256(raw).hexdigest(),
                               part["inlineData"]["mimeType"], len(raw), raw[:3].hex()))
                menunggu = None
    return sistem, gambar


def buat_handler(sk: Skenario):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a, **k) -> None:  # senyap
            pass

        # ── pembantu respons ──
        def _kirim(self, kode: int, badan, header: Optional[Dict[str, str]] = None) -> None:
            data = badan if isinstance(badan, bytes) else json.dumps(badan, ensure_ascii=False).encode("utf-8")
            with sk.lock:
                sk.status[kode] += 1
            try:
                self.send_response(kode)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                for k, v in (header or {}).items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):  # klien sudah menyerah (timeout)
                self.close_connection = True

        def _galat(self, kode: int, status: str, pesan: str, header=None) -> None:
            self._kirim(kode, {"error": {"code": kode, "message": pesan, "status": status}}, header)

        def _auth_ok(self, jalur: str) -> Optional[Tuple[int, str, str]]:
            """None = lolos; selain itu (kode, status, pesan)."""
            bearer = self.headers.get("Authorization", "")
            xg = self.headers.get("x-goog-api-key", "")
            k = sk.kunci
            tolak_kunci = (400, "INVALID_ARGUMENT", "API key not valid. Please pass a valid API key."
                           + (f" (kunci diterima: {bearer or xg})" if sk.gema_kunci else ""))
            if sk.auth == "semua_ditolak":
                return tolak_kunci
            if sk.auth == "bearer":
                ok = (bearer == f"Bearer {k}") if jalur == "kompat" else (xg == k)
                return None if ok else (401, "UNAUTHENTICATED", "Request had invalid authentication credentials.")
            if sk.auth == "aq_quirk":
                if jalur == "kompat" and bearer:
                    return (400, "INVALID_ARGUMENT", "Multiple authentication credentials received. "
                                                     "Please pass only one.")
                return None if xg == k else (401, "UNAUTHENTICATED", "invalid_api_key")
            if sk.auth == "native_saja":
                if jalur == "kompat":
                    return (401, "UNAUTHENTICATED", "invalid_api_key")
                return None if xg == k else (401, "UNAUTHENTICATED", "invalid_api_key")
            return tolak_kunci

        def do_GET(self) -> None:
            if self.path.rstrip("/").endswith("/models"):
                self._kirim(200, {"object": "list", "data": [{"id": f"models/{m}"} for m in sk.model_ada]})
            else:
                self._galat(404, "NOT_FOUND", "no such path")

        def do_POST(self) -> None:
            n_byte = int(self.headers.get("Content-Length", "0") or 0)
            mentah = self.rfile.read(n_byte) if n_byte else b""   # selalu habiskan badan (keep-alive)
            if self.path.rstrip("/").endswith("/chat/completions"):
                jalur = "kompat"
            elif ":generateContent" in self.path:
                jalur = "native"
            else:
                return self._galat(404, "NOT_FOUND", f"path tidak dikenal: {self.path}")
            with sk.lock:
                sk.permintaan += 1
                sk.sedang += 1
                sk.paralel_maks = max(sk.paralel_maks, sk.sedang)
            try:
                self._tangani(jalur, mentah)
            finally:
                with sk.lock:
                    sk.sedang -= 1

        def _tangani(self, jalur: str, mentah: bytes) -> None:
            galat = self._auth_ok(jalur)
            if galat:
                return self._galat(*galat)
            try:
                body = json.loads(mentah.decode("utf-8"))
            except ValueError:
                return self._galat(400, "INVALID_ARGUMENT", "badan bukan JSON")
            if jalur == "kompat":
                model = body.get("model", "")
            else:
                model = re.search(r"/models/([^:/]+):", self.path).group(1)
            if model.replace("models/", "") not in sk.model_ada:
                return self._galat(404, "NOT_FOUND", f"models/{model} is not found for API version v1beta")
            sistem, gambar = (_ekstrak_kompat if jalur == "kompat" else _ekstrak_native)(body)
            halaman = [g[0] for g in gambar]

            with sk.lock:
                if sk.sistem_prompt == [] and sistem:
                    sk.sistem_prompt.append(sistem)
                if gambar:
                    sk.catatan.append({"jalur": jalur, "halaman": halaman, "sha": [g[1] for g in gambar],
                                       "mime": [g[2] for g in gambar], "byte": [g[3] for g in gambar],
                                       "magic": [g[4] for g in gambar],
                                       "bearer": bool(self.headers.get("Authorization")),
                                       "xgoog": bool(self.headers.get("x-goog-api-key")),
                                       "waktu": time.time(), "temperature": body.get("temperature")
                                       if jalur == "kompat" else (body.get("generationConfig") or {}).get("temperature")})
                else:
                    sk.tes_koneksi += 1
                kena_tunda = sk._n_tunda < sk.tunda_pertama[0]
                if kena_tunda:
                    sk._n_tunda += 1
                kena_429 = sk._n_429 < sk.gagal_429_awal
                if kena_429:
                    sk._n_429 += 1
                kena_500 = (not kena_429) and sk._n_500 < sk.gagal_500_awal
                if kena_500:
                    sk._n_500 += 1
                kena_rusak = (not kena_429 and not kena_500) and sk._n_rusak < sk.json_rusak_awal
                if kena_rusak:
                    sk._n_rusak += 1
                harian = (sk.kuota_harian_setelah is not None and gambar
                          and sk._hitung_halaman_ok >= sk.kuota_harian_setelah)

            if kena_tunda:
                time.sleep(sk.tunda_pertama[1])
            else:
                time.sleep(sk.tunda)
            if sk.kuota_nol:
                return self._galat(429, "RESOURCE_EXHAUSTED",
                                   "Quota exceeded for metric: generate_content_free_tier_requests, limit: 0")
            if harian:
                return self._galat(429, "RESOURCE_EXHAUSTED",
                                   "You exceeded your current quota. quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier")
            if kena_429:
                return self._galat(429, "RESOURCE_EXHAUSTED",
                                   "Resource has been exhausted (e.g. check quota). quotaId: GenerateRequestsPerMinutePerProjectPerModel-FreeTier",
                                   {"Retry-After": "0"})
            if kena_500:
                return self._galat(500, "INTERNAL", "An internal error has occurred.")
            if kena_rusak:
                return self._kirim(200, b"<html>bad gateway</html>")

            if not gambar:  # tes koneksi
                return self._jawab(jalur, "OK", 12, 2)
            if any(n in sk.blokir_halaman for n in halaman):
                return self._diblokir(jalur)
            with sk.lock:
                pendek = sk._n_pendek < sk.pendek_awal
                if pendek:
                    sk._n_pendek += 1
                else:
                    sk._hitung_halaman_ok += len(halaman)
            if pendek:
                return self._jawab(jalur, "Maaf.", 1000, 2)
            if len(halaman) == 1:
                teks = isi_halaman(halaman[0])
            elif sk.tanpa_pemisah:
                teks = "\n".join(isi_halaman(n) for n in halaman)
            else:
                teks = "\n".join(f"<<<HALAMAN {n}>>>\n{isi_halaman(n)}" for n in halaman)
            self._jawab(jalur, teks, 1200 * len(halaman), 600 * len(halaman))

        def _jawab(self, jalur: str, teks: str, tok_masuk: int, tok_keluar: int) -> None:
            if jalur == "kompat":
                self._kirim(200, {"id": "mock", "object": "chat.completion", "model": "gemini-2.5-pro",
                                  "choices": [{"index": 0, "finish_reason": "stop",
                                               "message": {"role": "assistant", "content": teks}}],
                                  "usage": {"prompt_tokens": tok_masuk, "completion_tokens": tok_keluar,
                                            "total_tokens": tok_masuk + tok_keluar}})
            else:
                self._kirim(200, {"candidates": [{"index": 0, "finishReason": "STOP",
                                                  "content": {"role": "model", "parts": [
                                                      {"text": "(berpikir…)", "thought": True}, {"text": teks}]}}],
                                  "usageMetadata": {"promptTokenCount": tok_masuk,
                                                    "candidatesTokenCount": tok_keluar,
                                                    "thoughtsTokenCount": 100,
                                                    "totalTokenCount": tok_masuk + tok_keluar + 100}})

        def _diblokir(self, jalur: str) -> None:
            if jalur == "kompat":
                self._kirim(200, {"id": "mock", "choices": [{"index": 0, "finish_reason": "content_filter",
                                                             "message": {"role": "assistant", "content": None}}],
                                  "usage": {"prompt_tokens": 1200, "completion_tokens": 0}})
            else:
                self._kirim(200, {"promptFeedback": {"blockReason": "PROHIBITED_CONTENT"}})

    return Handler


class _Server(ThreadingHTTPServer):
    def handle_error(self, request, client_address) -> None:  # senyap: klien putus itu wajar di uji timeout
        pass


def buat_server(sk: Skenario, host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    srv = _Server((host, port), buat_handler(sk))
    srv.daemon_threads = True
    return srv


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--auth", default="bearer", choices=["bearer", "aq_quirk", "native_saja", "semua_ditolak"])
    ap.add_argument("--kunci", default="AQ.kunci-uji-123")
    ap.add_argument("--tunda", type=float, default=0.5, help="detik tunda per permintaan")
    a = ap.parse_args()
    sk = Skenario(kunci=a.kunci, auth=a.auth, tunda=a.tunda)
    srv = buat_server(sk, "127.0.0.1", a.port)
    print(f"Mock Gemini di http://127.0.0.1:{a.port}/v1beta/openai/  (auth={a.auth}, kunci={a.kunci})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
