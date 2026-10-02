#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uji offline untuk kitab_pipeline.py dan mulai_malam.sh memakai server tiruan (mock_gemini.py).
Tidak memakai internet dan tidak memakai kunci API sungguhan.

Jalankan dari akar repo:
    python -m unittest tools/test_pipeline.py -v
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

AKAR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import kitab_pipeline as kp  # noqa: E402
import mock_gemini as mg  # noqa: E402

try:
    import pymupdf  # noqa: E402
except ImportError:  # pragma: no cover
    import fitz as pymupdf  # type: ignore  # noqa: E402

PDF_ASLI = AKAR / "kitab" / "asrorul-sulaimaniyah.pdf"
KUNCI = "AQ.kunci-uji-123"


@contextlib.contextmanager
def server(**kw):
    sk = mg.Skenario(**kw)
    srv = mg.buat_server(sk)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield sk, f"http://127.0.0.1:{srv.server_address[1]}/v1beta/openai/"
    finally:
        srv.shutdown()
        srv.server_close()


def lingkungan(kunci=KUNCI, extra=None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("KITAB_")}
    env.update({"KITAB_API_KEY": kunci, "KITAB_JEDA_DASAR": "0.02", "KITAB_JEDA_MAKS": "0.2"})
    env.update(extra or {})
    return env


def jalankan(url, keluaran, *tambahan, pdf=None, model="gemini-2.5-pro", kunci=KUNCI, env=None,
             perintah="proses"):
    """Panggil kp.main() di proses ini → (kode_keluar, teks_log)."""
    pdf = pdf or PDF_ASLI
    argumen = ["proses", str(pdf), url, model, "--keluaran", str(keluaran)] if perintah == "proses" \
        else [perintah, url, model]
    argumen += ["--timeout", "20"] + [str(a) for a in tambahan]
    buf = io.StringIO()
    with mock.patch.dict(os.environ, lingkungan(kunci, env), clear=True), contextlib.redirect_stdout(buf):
        kode = kp.main(argumen)
    return kode, buf.getvalue()


def state_semua(d) -> dict:
    return {int(p.stem.split("_")[1]): json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((Path(d) / "_state").glob("halaman_*.json"))}


def nomor_ok(d) -> list:
    return sorted(n for n, st in state_semua(d).items() if st["status"] == "ok")


def buat_pdf_uji(path: Path, n: int = 8, teks=()) -> Path:
    """PDF pindaian tiruan: tiap halaman = satu gambar JPEG penuh; halaman di `teks` = teks vektor."""
    doc = pymupdf.open()
    for i in range(n):
        page = doc.new_page(width=400, height=560)
        if i in teks:
            page.insert_text((50, 100), f"Halaman teks {i + 1}", fontsize=20)
        else:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 200, 280))
            pix.set_rect(pix.irect, (20 + 25 * i, 90, 160))
            page.insert_image(page.rect, stream=pix.tobytes("jpeg"))
    doc.save(str(path))
    doc.close()
    return path


def semua_berkas_teks(d) -> str:
    bagian = []
    for p in Path(d).rglob("*"):
        if p.is_file() and p.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            bagian.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(bagian)


class DasarUji(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pdf_kecil = buat_pdf_uji(Path(cls.tmp.name) / "kecil.pdf", 8)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.d = self._d.name
        self.addCleanup(self._d.cleanup)


# ═════════════════════════ fungsi murni ═════════════════════════

class UjiFungsiMurni(unittest.TestCase):
    def test_rapikan_buang_pagar_kode(self):
        hasil = kp.rapikan_halaman("```markdown\n## Halaman PDF 7 (= cetak 6) — X\n\nisi\n```", 7)
        self.assertEqual(hasil, "## Halaman PDF 7 (= cetak 6) — X\n\nisi\n")

    def test_rapikan_koreksi_nomor_dan_sisip_judul(self):
        self.assertTrue(kp.rapikan_halaman("## Halaman PDF 99 — X\n\nisi", 12).startswith("## Halaman PDF 12 — X"))
        self.assertTrue(kp.rapikan_halaman("### halaman pdf 3\nisi", 5).startswith("## Halaman PDF 5\n"))
        self.assertEqual(kp.rapikan_halaman("isi saja", 4), "## Halaman PDF 4\n\nisi saja\n")

    def test_urai_kelompok(self):
        teks = "<<<HALAMAN 4>>>\nA\n\n<<<HALAMAN 5>>>\nB\n<<<HALAMAN 99>>>\nasing\n<<<HALAMAN 6>>>\n"
        self.assertEqual(kp.urai_kelompok(teks, [4, 5, 6]), {4: "A", 5: "B"})  # 6 kosong, 99 diabaikan
        self.assertEqual(kp.urai_kelompok("<<<HALAMAN 9>>>\nisi", [9]), {9: "isi"})
        self.assertEqual(kp.urai_kelompok("tanpa penanda", [1, 2]), {})

    def test_klasifikasi_galat(self):
        k = kp.klasifikasi
        g = k(429, '{"error":{"message":"quota","status":"RESOURCE_EXHAUSTED"}}', {"Retry-After": "7"})
        self.assertEqual((g.kategori, g.bisa_diulang, g.jeda_saran), ("laju", True, 7.0))
        g = k(429, '{"error":{"details":[{"retryDelay":"34s"}],"message":"PerMinute"}}', {})
        self.assertEqual((g.kategori, g.jeda_saran), ("laju", 34.0))
        self.assertEqual(k(429, "quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier", {}).kategori, "kuota_harian")
        self.assertEqual(k(429, "Quota exceeded ... limit: 0", {}).kategori, "kuota_nol")
        self.assertEqual(k(400, '{"error":{"message":"API key not valid. Please pass a valid API key."}}', {}).kategori, "auth")
        self.assertEqual(k(400, "Multiple authentication credentials received", {}).kategori, "auth")
        self.assertEqual(k(401, "x", {}).kategori, "auth")
        self.assertEqual(k(403, "x", {}).kategori, "auth")
        self.assertEqual(k(404, "x", {}).kategori, "model")
        g = k(400, '{"error":{"message":"Request payload size exceeds the limit"}}', {})
        self.assertEqual((g.kategori, g.bisa_diulang), ("permintaan", False))
        g = k(503, "overloaded", {})
        self.assertEqual((g.kategori, g.bisa_diulang), ("server", True))

    def test_pesan_dari_badan_bentuk_daftar(self):
        self.assertEqual(kp.pesan_dari_badan('[{"error":{"message":"gagal","status":"INTERNAL"}}]'), "INTERNAL: gagal")
        self.assertEqual(kp.pesan_dari_badan("<html>  502\n bad </html>"), "<html> 502 bad </html>")

    def test_ringkas_jaringan(self):
        import requests
        r = kp.ringkas_jaringan
        self.assertIn("TLS", r(requests.exceptions.SSLError("SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF)')")))
        self.assertIn("DNS", r(requests.exceptions.ConnectionError("Failed to resolve 'x' ([Errno -2] Name or service not known)")))
        self.assertIn("ditolak", r(requests.exceptions.ConnectionError("[Errno 111] Connection refused")))
        self.assertIn("diputus", r(requests.exceptions.ConnectionError("Connection aborted.")))
        self.assertTrue(r(RuntimeError("aneh")).startswith("RuntimeError"))

    def test_ringkas_rentang(self):
        self.assertEqual(kp.ringkas_rentang([7, 8, 9, 12, 14, 15, 103]), "7–9, 12, 14–15, 103")
        self.assertEqual(kp.ringkas_rentang([]), "")

    def test_ambil_kunci(self):
        with mock.patch.dict(os.environ, {"KITAB_API_KEY": '  "Bearer AQ.abc"  '}):
            self.assertEqual(kp.ambil_kunci(), "AQ.abc")
        for buruk in ("", "ada spasi di tengah", "kunci-ñ"):
            with mock.patch.dict(os.environ, {"KITAB_API_KEY": buruk}):
                with self.assertRaises(kp.GalatFatal):
                    kp.ambil_kunci()


# ═════════════════════════ alur utama ═════════════════════════

class UjiPDFAsli(DasarUji):
    """Seluruh 103 halaman PDF Anda yang sebenarnya, melawan server tiruan."""

    def test_semua_halaman_selesai(self):
        with server(tunda=0.05) as (sk, url):
            kode, out = jalankan(url, self.d, "--pekerja", "8")
        self.assertEqual(kode, 0, out)
        self.assertEqual(nomor_ok(self.d), list(range(1, 104)))
        self.assertEqual(sorted(sk.halaman_diminta()), list(range(1, 104)))  # tiap halaman tepat sekali
        self.assertEqual(sk.tes_koneksi, 1)
        self.assertTrue(2 <= sk.paralel_maks <= 8, f"paralelisme={sk.paralel_maks}")
        self.assertTrue(all(c["jalur"] == "kompat" and c["bearer"] and not c["xgoog"] for c in sk.catatan))
        self.assertTrue(all(abs(c["temperature"] - 0.2) < 1e-9 for c in sk.catatan))
        # prompt sistem sampai ke server dan memuat format yang dijanjikan
        sistem = sk.sistem_prompt[0]
        for harus in ("Latin Pesantren", "Halaman PDF {N}", "ATURAN EDISI", "[tidak terbaca]"):
            self.assertIn(harus, sistem)
        # dokumen gabungan: 103 judul, berurutan
        md = (Path(self.d) / "TERJEMAHAN.md").read_text(encoding="utf-8")
        judul = [int(l.split()[3]) for l in md.splitlines() if l.startswith("## Halaman PDF ")]
        self.assertEqual(judul, list(range(1, 104)))
        self.assertEqual(md.count("![Halaman PDF"), 103)
        self.assertIn("103/103", (Path(self.d) / "STATUS.md").read_text(encoding="utf-8"))
        self.assertEqual(len(list((Path(self.d) / "gambar").glob("*.jpg"))), 103)

    def test_gambar_yang_dikirim_adalah_jpeg_asli_dari_pdf(self):
        sampel = [1, 2, 11, 26, 52, 77, 103]
        with server() as (sk, url):
            kode, _ = jalankan(url, self.d, "--pekerja", "8")
        self.assertEqual(kode, 0)
        terkirim = {n: sha for c in sk.catatan for n, sha in zip(c["halaman"], c["sha"])}
        doc = pymupdf.open(str(PDF_ASLI))
        for n in sampel:  # pembanding independen & otoritatif (lambat, jadi hanya sampel)
            xref = doc[n - 1].get_image_info(xrefs=True)[0]["xref"]
            asli = hashlib.sha256(doc.extract_image(xref)["image"]).hexdigest()
            self.assertEqual(terkirim[n], asli, f"halaman {n}: bukan JPEG asli dari PDF")
            self.assertEqual(hashlib.sha256((Path(self.d) / "gambar" / f"halaman_{n:03d}.jpg").read_bytes()).hexdigest(), asli)
        self.assertTrue(all(m == ["ffd8ff"] for m in (c["magic"] for c in sk.catatan)))

    def test_kunci_tidak_pernah_ditulis(self):
        with server() as (sk, url):
            kode, out = jalankan(url, self.d, "--akhir", "6")
        self.assertEqual(kode, 0)
        self.assertNotIn(KUNCI, out)
        self.assertNotIn(KUNCI, semua_berkas_teks(self.d))


class UjiAlur(DasarUji):
    def test_lanjutkan_dan_ulang_semua(self):
        with server() as (sk, url):
            self.assertEqual(jalankan(url, self.d, "--akhir", "4", pdf=self.pdf_kecil)[0], 0)
            self.assertEqual(sorted(sk.halaman_diminta()), [1, 2, 3, 4])
            sk.catatan.clear()
            kode, out = jalankan(url, self.d, pdf=self.pdf_kecil)
            self.assertEqual(kode, 0)
            self.assertEqual(sorted(sk.halaman_diminta()), [5, 6, 7, 8])  # hanya sisanya
            self.assertIn("Sudah selesai sebelumnya: 4", out)
            sk.catatan.clear()
            kode, out = jalankan(url, self.d, pdf=self.pdf_kecil)  # semuanya sudah selesai
            self.assertEqual((kode, sk.halaman_diminta()), (0, []))
            self.assertEqual(sk.tes_koneksi, 2)  # tidak ada tes koneksi tambahan bila tak ada kerja
            sk.catatan.clear()
            jalankan(url, self.d, "--ulang-semua", pdf=self.pdf_kecil)
            self.assertEqual(sorted(sk.halaman_diminta()), list(range(1, 9)))

    def test_berkas_setengah_jadi_tidak_dianggap_selesai(self):
        with server() as (sk, url):
            jalankan(url, self.d, pdf=self.pdf_kecil)
            (Path(self.d) / "halaman" / "halaman_003.md").write_text("", encoding="utf-8")  # rusak
            (Path(self.d) / "_state" / "halaman_005.json").write_text("{bukan json", encoding="utf-8")
            sk.catatan.clear()
            kode, _ = jalankan(url, self.d, pdf=self.pdf_kecil)
            self.assertEqual((kode, sorted(sk.halaman_diminta())), (0, [3, 5]))

    def test_batas_laju_429_lalu_pulih(self):
        with server(gagal_429_awal=6) as (sk, url):
            kode, out = jalankan(url, self.d, "--lewati-tes", "--pekerja", "4", pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        self.assertEqual(nomor_ok(self.d), list(range(1, 9)))
        self.assertEqual(sk.status[429], 6)
        self.assertIn("⏳", out)

    def test_tes_koneksi_sabar_menghadapi_429(self):
        with server(gagal_429_awal=4) as (sk, url):
            kode, out = jalankan(url, self.d, "--akhir", "2", pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        self.assertEqual(sk.status[429], 4)

    def test_galat_server_5xx_json_rusak_dan_jawaban_pendek_diulang(self):
        for nama, kw in (("500", {"gagal_500_awal": 3}), ("json", {"json_rusak_awal": 2}),
                         ("pendek", {"pendek_awal": 3})):
            with self.subTest(nama), server(**kw) as (sk, url), tempfile.TemporaryDirectory() as d:
                kode, out = jalankan(url, d, "--lewati-tes", "--pekerja", "3", pdf=self.pdf_kecil)
                self.assertEqual(kode, 0, out)
                self.assertEqual(nomor_ok(d), list(range(1, 9)))
                self.assertGreater(len(sk.halaman_diminta()), 8)  # ada yang diulang

    def test_timeout_lalu_ulang(self):
        with server(tunda_pertama=(2, 2.5)) as (sk, url):
            kode, out = jalankan(url, self.d, "--lewati-tes", "--akhir", "3", "--pekerja", "3",
                                 "--timeout", "1", pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        self.assertIn("tidak ada jawaban dalam", out)
        self.assertGreaterEqual(max(st["percobaan"] for st in state_semua(self.d).values()), 2)

    def test_kuota_harian_berhenti_rapi_lalu_dilanjutkan(self):
        with server(kuota_harian_setelah=3) as (sk, url):
            kode, out = jalankan(url, self.d, "--pekerja", "2", pdf=self.pdf_kecil)
        self.assertEqual(kode, 3, out)
        selesai = nomor_ok(self.d)
        self.assertTrue(3 <= len(selesai) < 8, selesai)
        self.assertIn("Kuota habis", out)
        md = (Path(self.d) / "TERJEMAHAN.md").read_text(encoding="utf-8")
        self.assertIn("BELUM DIPROSES", md)  # dokumen tetap utuh, sisa halaman bertanda
        self.assertIn("Kuota habis", (Path(self.d) / "STATUS.md").read_text(encoding="utf-8"))
        with server() as (sk2, url2):  # keesokan harinya
            kode, out = jalankan(url2, self.d, pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        self.assertEqual(sorted(sk2.halaman_diminta()), sorted(set(range(1, 9)) - set(selesai)))
        self.assertEqual(nomor_ok(self.d), list(range(1, 9)))

    def test_kuota_nol_gagal_di_tes_koneksi(self):
        with server(kuota_nol=True) as (sk, url):
            kode, out = jalankan(url, self.d, pdf=self.pdf_kecil)
        self.assertEqual(kode, 3)
        self.assertIn("Kuota model ini 0", out)
        self.assertEqual(sk.halaman_diminta(), [])

    def test_halaman_diblokir_filter_tidak_menghentikan_yang_lain(self):
        with server(blokir_halaman={3}) as (sk, url):
            kode, out = jalankan(url, self.d, "--akhir", "6", pdf=self.pdf_kecil)
        self.assertEqual(kode, 1, out)
        st = state_semua(self.d)
        self.assertEqual(st[3]["status"], "diblokir")
        self.assertEqual(nomor_ok(self.d), [1, 2, 4, 5, 6])
        self.assertEqual(sk.halaman_diminta().count(3), 2)  # satu kali coba ulang, lalu menyerah
        md = (Path(self.d) / "TERJEMAHAN.md").read_text(encoding="utf-8")
        self.assertIn("DIBLOKIR FILTER MODEL", md)
        self.assertIn("| 3 | diblokir |", (Path(self.d) / "STATUS.md").read_text(encoding="utf-8"))

    def test_pengawas_stagnasi_menghentikan_proses_yang_macet(self):
        with server(gagal_500_awal=10 ** 6) as (sk, url):
            kode, out = jalankan(url, self.d, "--lewati-tes", "--pekerja", "2", pdf=self.pdf_kecil,
                                 env={"KITAB_BATAS_STAGNASI": "0.3", "KITAB_JEDA_DASAR": "0.05"})
        self.assertEqual(kode, 2, out)
        self.assertIn("Tidak ada permintaan yang berhasil", out)

    def test_batas_waktu_berhenti_rapi_lalu_dilanjutkan(self):
        with server(tunda=0.4) as (sk, url):
            kode, out = jalankan(url, self.d, "--lewati-tes", "--pekerja", "1", pdf=self.pdf_kecil,
                                 env={"KITAB_BATAS_WAKTU": "0.9"})
        self.assertEqual(kode, 1, out)
        self.assertIn("Batas waktu", out)
        selesai = nomor_ok(self.d)
        self.assertTrue(1 <= len(selesai) < 8, selesai)
        self.assertIn("batas waktu tercapai", (Path(self.d) / "STATUS.md").read_text(encoding="utf-8"))
        with server() as (sk2, url2):
            kode, out = jalankan(url2, self.d, pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        self.assertEqual(nomor_ok(self.d), list(range(1, 9)))
        self.assertEqual(sorted(sk2.halaman_diminta()), sorted(set(range(1, 9)) - set(selesai)))

    def test_rentang_halaman_tidak_valid(self):
        with server() as (sk, url):
            kode, out = jalankan(url, self.d, "--mulai", "9", "--akhir", "12", pdf=self.pdf_kecil)
        self.assertEqual(kode, 2)
        self.assertIn("Rentang halaman kosong", out)


class UjiBanyakHalamanPerPermintaan(DasarUji):
    def test_kelompok_tiga_halaman(self):
        with server() as (sk, url):
            kode, out = jalankan(url, self.d, "--halaman-per-permintaan", "3", pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        ukuran = sorted(len(c["halaman"]) for c in sk.catatan)
        self.assertEqual(ukuran, [2, 3, 3])
        for n in range(1, 9):  # setiap halaman mendapat isinya sendiri, bukan milik tetangga
            md = (Path(self.d) / "halaman" / f"halaman_{n:03d}.md").read_text(encoding="utf-8")
            self.assertIn(f"Teks uji untuk halaman {n}.", md)
            self.assertNotIn("<<<", md)

    def test_tanpa_penanda_dikerjakan_satu_satu(self):
        with server(tanpa_pemisah=True) as (sk, url):
            kode, out = jalankan(url, self.d, "--halaman-per-permintaan", "4", pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        self.assertEqual(nomor_ok(self.d), list(range(1, 9)))
        self.assertIn("dikerjakan satu per satu", out)

    def test_satu_halaman_diblokir_di_dalam_kelompok(self):
        with server(blokir_halaman={2}) as (sk, url):
            kode, out = jalankan(url, self.d, "--halaman-per-permintaan", "3", "--akhir", "3", pdf=self.pdf_kecil)
        self.assertEqual(kode, 1, out)
        st = state_semua(self.d)
        self.assertEqual((st[1]["status"], st[2]["status"], st[3]["status"]), ("ok", "diblokir", "ok"))


class UjiAutentikasi(DasarUji):
    def test_kunci_ditolak_gagal_cepat_dan_tidak_bocor(self):
        with server(auth="semua_ditolak", gema_kunci=True) as (sk, url):
            kode, out = jalankan(url, self.d, pdf=self.pdf_kecil)
        self.assertEqual(kode, 2)
        self.assertIn("Tes koneksi GAGAL", out)
        self.assertEqual(sk.halaman_diminta(), [])
        self.assertFalse((Path(self.d) / "halaman").exists())
        self.assertNotIn(KUNCI, out)
        self.assertNotIn(KUNCI, semua_berkas_teks(self.d))

    def test_model_salah(self):
        with server() as (sk, url):
            kode, out = jalankan(url, self.d, model="gemini-xyz", pdf=self.pdf_kecil)
        self.assertEqual(kode, 2)
        self.assertIn("tidak ditemukan", out)
        self.assertEqual(sk.halaman_diminta(), [])

    def test_kunci_aq_ditolak_bearer_lalu_pakai_x_goog_api_key(self):
        with server(auth="aq_quirk") as (sk, url):
            kode, out = jalankan(url, self.d, pdf=self.pdf_kecil)
        self.assertEqual(kode, 0, out)
        self.assertIn("header x-goog-api-key", out)
        self.assertTrue(all(c["xgoog"] and not c["bearer"] for c in sk.catatan))
        self.assertEqual({st["mode_auth"] for st in state_semua(self.d).values() if st["status"] == "ok"}, {"xgoog"})

    def test_cadangan_endpoint_native(self):
        with server(auth="native_saja") as (sk, url):
            kode, out = jalankan(url, self.d, pdf=self.pdf_kecil, env={"KITAB_NATIVE": "1"})
        self.assertEqual(kode, 0, out)
        self.assertTrue(all(c["jalur"] == "native" for c in sk.catatan))
        md = (Path(self.d) / "halaman" / "halaman_002.md").read_text(encoding="utf-8")
        self.assertIn("Teks uji untuk halaman 2.", md)
        self.assertNotIn("berpikir", md)  # bagian 'thought' tidak ikut masuk

    def test_mode_yang_dikunci_tidak_mencoba_cara_lain(self):
        with server(auth="aq_quirk") as (sk, url):
            kode, out = jalankan(url, self.d, "--auth", "bearer", pdf=self.pdf_kecil)
        self.assertEqual(kode, 2)
        self.assertEqual(sk.permintaan, 1)  # satu percobaan saja: cara yang dikunci pengguna tidak diganti diam-diam
        self.assertEqual(sk.status[400], 1)
        self.assertEqual(sk.halaman_diminta(), [])

    def test_perintah_tes(self):
        with server() as (sk, url):
            kode, out = jalankan(url, self.d, perintah="tes")
        self.assertEqual(kode, 0, out)
        self.assertIn("siap dipakai", out)
        self.assertEqual((sk.tes_koneksi, sk.halaman_diminta()), (1, []))

    def test_google_tidak_terjangkau_gagal_dengan_pesan_jelas(self):
        # port yang pasti tertutup: meniru jaringan yang memblokir domain Google
        kode, out = jalankan("http://127.0.0.1:1/v1beta/openai/", self.d, pdf=self.pdf_kecil,
                             env={"KITAB_JEDA_DASAR": "0.01"})
        self.assertEqual(kode, 2)
        self.assertIn("Tidak bisa terhubung", out)
        self.assertIn("koneksi ditolak", out)          # satu kalimat jelas ...
        self.assertNotIn("HTTPConnectionPool", out)    # ... bukan tumpukan galat mentah
        self.assertIn("(×3)", out)                     # percobaan identik diringkas


class UjiGambarHalaman(DasarUji):
    def test_jalur_cepat_dan_render_cadangan(self):
        pdf = buat_pdf_uji(Path(self.d) / "campur.pdf", 4, teks={2})
        with server() as (sk, url):
            kode, out = jalankan(url, Path(self.d) / "h", pdf=pdf)
        self.assertEqual(kode, 0, out)
        self.assertIn("3 diambil asli dari PDF, 1 dirender", out)
        magic = {n: m for c in sk.catatan for n, m in zip(c["halaman"], c["magic"])}
        self.assertEqual(set(magic.values()), {"ffd8ff"})  # halaman teks dirender menjadi JPEG
        self.assertEqual({sk_["mime"][0] for sk_ in sk.catatan}, {"image/jpeg"})


# ═════════════════════════ pembungkus shell ═════════════════════════

class UjiSkripShell(DasarUji):
    def jalankan_skrip(self, *args, extra=None, kunci=KUNCI):
        env = {k: v for k, v in os.environ.items() if not k.startswith("KITAB_")}
        env["PATH"] = os.path.dirname(sys.executable) + os.pathsep + env.get("PATH", "")
        env.update({"KITAB_JEDA_DASAR": "0.02", "KITAB_JEDA_MAKS": "0.2"})
        if kunci:
            env["KITAB_API_KEY"] = kunci
        env.update(extra or {})
        return subprocess.run(["bash", str(AKAR / "mulai_malam.sh"), *map(str, args)], cwd=AKAR, env=env,
                              capture_output=True, text=True, timeout=120)

    def test_perintah_persis_seperti_yang_dikirim_pengguna(self):
        with server() as (sk, url):
            r = self.jalankan_skrip("kitab/asrorul-sulaimaniyah.pdf", url, "gemini-2.5-pro", 8, 1, 600,
                                    extra={"KITAB_AKHIR": "5", "KITAB_KELUARAN": self.d})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Pekerja    : 8 · halaman/permintaan: 1 · timeout: 600 dtk", r.stdout)
        self.assertIn(f"terpasang ({len(KUNCI)} karakter; tidak ditampilkan)", r.stdout)
        self.assertNotIn(KUNCI, r.stdout + r.stderr)
        self.assertEqual(nomor_ok(self.d), [1, 2, 3, 4, 5])

    def test_tes_saja(self):
        with server() as (sk, url):
            r = self.jalankan_skrip("kitab/asrorul-sulaimaniyah.pdf", url, "gemini-2.5-pro",
                                    extra={"KITAB_TES_SAJA": "1", "KITAB_KELUARAN": self.d})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((sk.tes_koneksi, sk.halaman_diminta()), (1, []))

    def test_validasi_argumen(self):
        casos = [((), 2, "Butuh 3–6 argumen"),
                 (("kitab/tidak-ada.pdf", "https://x", "m"), 2, "Berkas PDF tidak ditemukan"),
                 (("kitab/asrorul-sulaimaniyah.pdf", "ftp://x", "m"), 2, "base_url"),
                 (("kitab/asrorul-sulaimaniyah.pdf", "https://x", "m", 0), 2, "pekerja"),
                 (("kitab/asrorul-sulaimaniyah.pdf", "https://x", "m", 8, "dua"), 2, "halaman_per_permintaan"),
                 (("kitab/asrorul-sulaimaniyah.pdf", "https://x", "m", 8, 1, 1), 2, "timeout_dtk")]
        for args, rc, pesan in casos:
            with self.subTest(args=args):
                r = self.jalankan_skrip(*args)
                self.assertEqual(r.returncode, rc)
                self.assertIn(pesan, r.stdout + r.stderr)
                self.assertNotIn(KUNCI, r.stdout + r.stderr)

    def test_tanpa_kunci(self):
        r = self.jalankan_skrip("kitab/asrorul-sulaimaniyah.pdf", "https://x", "m", kunci=None)
        self.assertEqual(r.returncode, 2)
        self.assertIn("KITAB_API_KEY belum diisi", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
