#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Uji Edisi Panel: parser BATCH_*.md, pemeriksaan mutu, PDF (PyMuPDF), dan server pratinjau.

Jalankan:  python -m unittest tools/test_panel.py   (butuh PyMuPDF, numpy, fontTools)
"""
from __future__ import annotations

import http.client
import re
import shutil
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bangun_panel as bp  # noqa: E402
import server_preview as sv  # noqa: E402

ROOT = bp.ROOT

CONTOH = """# BATCH 07 — contoh

> intro satu
- catatan satu
- catatan dua

---

## Halaman PDF 9 (= cetak 8)

### Bagian 1 — Uji

**[Teks Arab Asli]**

<div dir="rtl">

**بِسْمِ اللَّهِ**

كِتَابٌ جَمِيلٌ

</div>

**[Transliterasi Latin Fonetik]**

**Bismillaah**

*Kitaabun jamiil*

**[Terjemahan Indonesia]**

**Dengan nama Allah**

Sebuah *kitab* yang **indah**.

**[Faedah]**

> Ringkasan:
>
> - butir satu
> - butir dua

![Rajah Hal. 8 (cetak 8) — uji](rajah/rajah_p05_khatam_01.png)

*Keterangan rajah: contoh.*
"""


def salin_akar(tujuan: Path) -> None:
    """Salin hanya yang diperlukan pembangun ke folder sementara."""
    shutil.copy(ROOT / "BATCH_01.md", tujuan / "BATCH_01.md")
    shutil.copytree(ROOT / "rajah", tujuan / "rajah")


class ParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "BATCH_07.md").write_text(CONTOH, encoding="utf-8")
        self.b = bp.parse_batch(self.tmp / "BATCH_07.md")

    def test_struktur(self) -> None:
        self.assertEqual(self.b["nomor"], 7)
        self.assertEqual(self.b["intro"], ["intro satu"])
        self.assertEqual(self.b["catatan"], ["catatan satu", "catatan dua"])
        (h,) = self.b["halaman"]
        self.assertEqual((h["pdf"], h["label"]), (9, "cetak 8"))
        (bg,) = h["bagian"]
        self.assertEqual([it["kind"] for it in bg["items"]], ["ar", "la", "id", "faedah", "img"])

    def test_paragraf_judul_dan_pembungkus(self) -> None:
        ar, la, idn, faedah, img = self.b["halaman"][0]["bagian"][0]["items"]
        self.assertEqual(ar["paras"], [{"t": "h", "text": "بِسْمِ اللَّهِ"}, {"t": "p", "text": "كِتَابٌ جَمِيلٌ"}])
        self.assertEqual(la["paras"], [{"t": "h", "text": "Bismillaah"}, {"t": "p", "text": "Kitaabun jamiil"}])  # *…* dilepas
        self.assertEqual(idn["paras"][1]["text"], "Sebuah *kitab* yang **indah**.")
        self.assertEqual([p["t"] for p in faedah["paras"]], ["p", "li", "li"])
        self.assertEqual(img["caption"], "Keterangan rajah: contoh.")

    def test_inline(self) -> None:
        self.assertEqual(bp.inline("Sebuah *kitab* yang **indah** & <b>"), "Sebuah <em>kitab</em> yang <strong>indah</strong> &amp; &lt;b&gt;")
        self.assertIn('class="ed"', bp.tandai_editorial("x [المطبوع: عمد] y"))

    def test_label_tak_dikenal(self) -> None:
        (self.tmp / "BATCH_08.md").write_text(CONTOH.replace("[Faedah]", "[Aneh]"), encoding="utf-8")
        with self.assertRaises(ValueError):
            bp.parse_batch(self.tmp / "BATCH_08.md")

    def test_nama_pdf(self) -> None:
        mk = lambda n: [{"nomor": i} for i in n]  # noqa: E731
        self.assertEqual(bp.nama_pdf(mk([1])), "MASTER_PANEL_Batch_01.pdf")
        self.assertEqual(bp.nama_pdf(mk([1, 2, 3])), "MASTER_PANEL_Batch_01-03.pdf")
        self.assertEqual(bp.nama_pdf(mk(range(1, 22))), bp.NAMA_KHATAM)
        self.assertEqual(bp.nomor_arab(1905), "١٩٠٥")


class BatchAsliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.batches = bp.muat_batch(ROOT)

    def test_batch_1_lengkap(self) -> None:
        b = self.batches[0]
        self.assertEqual([h["pdf"] for h in b["halaman"]], [1, 2, 3, 4, 5])
        for h in b["halaman"]:
            for bg in h["bagian"]:
                jenis = {it["kind"] for it in bg["items"]}
                self.assertTrue({"ar", "la", "id"} <= jenis, f"hal {h['pdf']} bagian {bg['no']}: {jenis}")

    def test_lulus_pemeriksaan_mutu(self) -> None:
        temuan, ringkasan = bp.periksa(self.batches, ROOT)
        self.assertEqual(temuan, [])
        self.assertTrue(ringkasan[0].startswith("BATCH_01.md"))

    def test_rajah_ada_dan_putih_bersih(self) -> None:
        from PIL import Image

        im = Image.open(ROOT / "rajah" / "rajah_p05_khatam_01.png").convert("L")
        px = im.getdata()
        putih = sum(1 for v in px if v == 255) / len(px)
        self.assertGreater(putih, 0.85)
        self.assertEqual(im.getpixel((2, 2)), 255)  # sudut = latar putih

    def test_gabungan_markdown_bolak_balik(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "BATCH_01.md").write_text(bp.ke_markdown(self.batches, murni=False), encoding="utf-8")
        ulang = bp.parse_batch(tmp / "BATCH_01.md")  # judul gabungan tidak memengaruhi isi
        asli = self.batches[0]

        def bentuk(b):
            return [(h["pdf"], [(bg["no"], [(it["kind"], len(it.get("paras", []))) for it in bg["items"]]) for bg in h["bagian"]]) for h in b["halaman"]]

        self.assertEqual(bentuk(ulang), bentuk(asli))
        murni = bp.ke_markdown(self.batches, murni=True)
        self.assertNotIn("**[Syarah]**", murni)
        self.assertNotIn("**[Faedah]**", murni)
        self.assertIn("![Rajah Hal. 5", murni)
        self.assertIn("**[Teks Arab Asli]**", murni)


class PemeriksaanTest(unittest.TestCase):
    def cek(self, ubah) -> list[str]:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        salin_akar(tmp)
        (tmp / "BATCH_01.md").write_text(ubah((ROOT / "BATCH_01.md").read_text(encoding="utf-8")), encoding="utf-8")
        temuan, _ = bp.periksa(bp.muat_batch(tmp), tmp)
        return temuan

    def test_karakter_tak_ada_di_font(self) -> None:
        t = self.cek(lambda s: s.replace("Bismillaahir-Rahmaanir-Rahiim", "Bismillaahir-Rahmaanir-Rahiim \u2020"))
        self.assertTrue(any("U+2020" in x for x in t), t)

    def test_pola_latin_salah(self) -> None:
        t = self.cek(lambda s: s.replace("wal-mutamarridiin", "al-Syamsi at-tii wlaa"))
        for sub in ("al-Syamsi", "at-tii", "wlaa"):
            self.assertTrue(any(sub in x for x in t), (sub, t))

    def test_jumlah_paragraf_tak_sama(self) -> None:
        t = self.cek(lambda s: s.replace("**Dengan nama Allah Yang Maha Pengasih lagi Maha Penyayang.**", "", 1))
        self.assertTrue(any("tidak sama" in x for x in t), t)

    def test_gambar_hilang(self) -> None:
        t = self.cek(lambda s: s.replace("rajah/rajah_p05_khatam_01.png", "rajah/tidak_ada.png"))
        self.assertTrue(any("gambar tidak ada" in x for x in t), t)

    def test_harakat_hilang(self) -> None:
        t = self.cek(lambda s: re.sub("[\u064B-\u0652]", "", s))
        self.assertTrue(any("cakupan harakat" in x for x in t), t)


class PdfTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import pymupdf

        cls.pymupdf = pymupdf
        cls.tmp = Path(tempfile.mkdtemp())
        cls.berkas = cls.tmp / "uji.pdf"
        cls.n = bp.bangun_pdf(bp.muat_batch(ROOT), cls.berkas)
        cls.doc = pymupdf.open(str(cls.berkas))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.doc.close()
        shutil.rmtree(cls.tmp, True)

    def test_a4_dan_halaman(self) -> None:
        self.assertEqual(len(self.doc), self.n)
        self.assertGreaterEqual(self.n, 5)
        r = self.doc[0].rect
        self.assertLess(abs(r.width - 595.28), 0.5)
        self.assertLess(abs(r.height - 841.89), 0.5)

    def test_font_amiri_tertanam_sekali(self) -> None:
        nama: dict[str, set[int]] = {}
        for i in range(len(self.doc)):
            for f in self.doc.get_page_fonts(i):
                nama.setdefault(f[3], set()).add(f[0])
        self.assertTrue({"Amiri Regular", "Amiri Bold", "Amiri Italic"} <= set(nama), nama)
        self.assertTrue(all(len(v) == 1 for v in nama.values()), nama)  # tidak berganda -> berkas kecil
        self.assertLess(self.berkas.stat().st_size, 3 * 1024 * 1024)

    def test_teks_arab_bisa_disalin_dan_dicari(self) -> None:
        """Regresi: ToUnicode bawaan MuPDF mengacak huruf Arab kontekstual; kita menulis ulang dari font."""
        import unicodedata

        semua = unicodedata.normalize("NFKC", " ".join(self.doc[i].get_text() for i in range(len(self.doc))))
        huruf = re.sub("[\u064B-\u0652\u0670]", "", semua)
        for kata in ("السليمانية", "الروحانية", "ميكائيل", "جبرائيل", "بسم الله الرحمن الرحيم", "سبحانك يا حي"):
            self.assertIn(kata, huruf)
        arab = [c for c in semua if "\u0600" <= c <= "\u06ff"]
        asing = [c for c in semua if "\u0700" <= c <= "\u1fff" or "\u2c00" <= c <= "\ufaff"]
        self.assertGreater(len(arab), 2000)
        self.assertEqual(asing, [], "karakter aksara lain (ToUnicode rusak): " + "".join(asing[:20]))

    def test_peta_gid_unicode(self) -> None:
        peta = bp._peta_gid_unicode((ROOT / "fonts" / "Amiri-Regular.ttf").read_bytes())
        self.assertGreater(len(peta), 1500)
        teks = "".join(peta.values())
        for ch in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي\u064E\u0651":
            self.assertIn(ch, teks)
        self.assertTrue(any(len(v) == 2 and v[0] == "ل" and v[1] == "ا" for v in peta.values()), "ligatur lam-alif harus terurai")

    def test_header_footer_dengan_angka_arab(self) -> None:
        akhir = self.doc[len(self.doc) - 1].get_text()
        self.assertIn(f"Halaman {len(self.doc)} dari {len(self.doc)}", akhir)
        angka = bp.nomor_arab(len(self.doc))
        self.assertTrue(angka in akhir or angka[::-1] in akhir, akhir[-80:])

    def test_baris_arab_rata_kanan(self) -> None:
        """Regresi: text-align:right di MuPDF membalik ke kiri pada blok RTL.

        Ekstraksi memecah satu baris visual menjadi beberapa fragmen; gabungkan dulu per baris visual."""
        kanan = self.doc[0].rect.width - bp.MARGIN
        ditemukan = 0
        for pno in range(len(self.doc)):
            baris: list[list] = []  # [tengah_y, x1_terjauh, ada_huruf_arab]
            for blk in self.doc[pno].get_text("dict")["blocks"]:
                for ln in blk.get("lines", []):
                    if not 16.0 <= max(sp["size"] for sp in ln["spans"]) <= 18.0:
                        continue
                    arab = bool(re.search("[\u0621-\u064A]", "".join(sp["text"] for sp in ln["spans"])))
                    tengah = (ln["bbox"][1] + ln["bbox"][3]) / 2
                    for r in baris:
                        if abs(r[0] - tengah) < 8:
                            r[1], r[2] = max(r[1], ln["bbox"][2]), r[2] or arab
                            break
                    else:
                        baris.append([tengah, ln["bbox"][2], arab])
            for tengah, x1, arab in baris:
                if not arab:
                    continue
                ditemukan += 1
                self.assertGreater(x1, kanan - 22, f"hal {pno + 1}: baris Arab (y={tengah:.0f}) tidak rata kanan, x1={x1:.0f}")
        self.assertGreater(ditemukan, 20)

    def test_tanpa_serpihan_bar_hijau(self) -> None:
        """Regresi: blok yang berakhir di dasar halaman meninggalkan bar hijau di puncak halaman berikutnya."""
        import numpy as np

        for pno in range(len(self.doc)):
            pix = self.doc[pno].get_pixmap(dpi=100, alpha=False)
            a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).astype(int)
            hijau = (abs(a[:, :, 0] - 13) < 25) & (abs(a[:, :, 1] - 74) < 25) & (abs(a[:, :, 2] - 54) < 25)
            baris = np.where(hijau[:, int(pix.width * 0.12):int(pix.width * 0.88)].mean(axis=1) > 0.5)[0]
            if pno == 0:
                baris = baris[baris > 200]  # banner halaman 1 memang hijau
            self.assertEqual(len(baris), 0, f"halaman {pno + 1}: bar hijau horizontal di baris {baris[:3]}")

    def test_gambar_rajah_ada_di_pdf(self) -> None:
        jumlah = sum(len(self.doc[i].get_images()) for i in range(len(self.doc)))
        self.assertGreaterEqual(jumlah, 1)


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp())
        salin_akar(cls.tmp)
        shutil.copytree(ROOT / "fonts", cls.tmp / "fonts")
        (cls.tmp / ".git").mkdir()
        (cls.tmp / ".git" / "config").write_text("[remote]\nurl = https://rahasia@example.invalid\n")
        (cls.tmp / "README.md").write_text("jangan disajikan")
        assert bp.main(["--akar", str(cls.tmp)]) == 0
        cls.srv = sv.buat_server("127.0.0.1", 0, root=cls.tmp)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.srv.shutdown()
        cls.srv.server_close()
        shutil.rmtree(cls.tmp, True)

    def ambil(self, path: str, metode: str = "GET"):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=15)
        c.request(metode, path)
        r = c.getresponse()
        isi = r.read()
        c.close()
        return r.status, dict((k.lower(), v) for k, v in r.getheaders()), isi

    def test_halaman_dan_tombol_emas(self) -> None:
        st, h, isi = self.ambil("/")
        self.assertEqual(st, 200)
        self.assertIn("text/html", h["content-type"])
        t = isi.decode("utf-8")
        self.assertIn("📥 Unduh PDF Master Panel", t)
        self.assertIn('href="unduh/pdf"', t)  # URL relatif, aman di balik proxy
        self.assertEqual(t.count('<article class="kartu">'), 5)
        for warna in ("#0d4a36", "#c59b27", "#f7faf7", "#f4f6f8", "#faf7ef", "#fff8f2"):
            self.assertIn(warna, t)
        self.assertNotIn("localhost", t)
        self.assertNotIn("127.0.0.1", t)

    def test_unduh_pdf_sebagai_lampiran(self) -> None:
        st, h, isi = self.ambil("/unduh/pdf")
        self.assertEqual(st, 200)
        self.assertEqual(h["content-type"], "application/pdf")
        self.assertIn("attachment", h["content-disposition"])
        self.assertIn("MASTER_PANEL_Batch_01.pdf", h["content-disposition"])
        self.assertTrue(isi.startswith(b"%PDF"))
        self.assertEqual(isi, (self.tmp / "MASTER_PANEL_Batch_01.pdf").read_bytes())
        st, h, isi = self.ambil("/unduh/pdf", "HEAD")
        self.assertEqual((st, isi), (200, b""))

    def test_aset_dan_zip(self) -> None:
        self.assertEqual(self.ambil("/rajah/rajah_p05_khatam_01.png")[0], 200)
        self.assertEqual(self.ambil("/fonts/Amiri-Regular.ttf")[1]["content-type"], "font/ttf")
        st, h, isi = self.ambil("/unduh/zip")
        self.assertEqual(st, 200)
        import io

        nama = set(zipfile.ZipFile(io.BytesIO(isi)).namelist())
        self.assertTrue({"BATCH_01.md", "preview.html", "MASTER_PANEL_Batch_01.pdf", "rajah/rajah_p05_khatam_01.png", "fonts/Amiri-Regular.ttf"} <= nama, nama)
        self.assertFalse(any(n.startswith(".git") for n in nama))

    def test_tidak_membuka_berkas_lain(self) -> None:
        for p in ("/.git/config", "/README.md", "/BATCH_01.md", "/rajah/../README.md", "/rajah/%2e%2e/README.md",
                  "/fonts/..%2fREADME.md", "/rajah/.git", "/rajah/", "/fonts/OFL.txt", "/etc/passwd", "/tools/bangun_panel.py"):
            st, _, isi = self.ambil(p)
            self.assertEqual(st, 404, p)
            self.assertNotIn(b"rahasia", isi)
            self.assertNotIn("jangan disajikan".encode(), isi)

    def test_healthz(self) -> None:
        self.assertEqual(self.ambil("/healthz")[2], b"ok\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
