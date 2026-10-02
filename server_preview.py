#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Server pratinjau Edisi Panel (bawaan port 3000) dengan tombol unduh PDF langsung.

Rute (semua tautan di halaman memakai URL relatif, jadi aman di belakang proxy):
  /                  preview.html (kartu panel per halaman)
  /unduh/pdf         PDF master panel sebagai lampiran (Content-Disposition: attachment)
  /unduh/zip         paket lengkap (BATCH_*.md, TERJEMAHAN*.md, rajah/, fonts/, PDF, preview.html, tools/)
  /rajah/<berkas>    gambar rajah (png/jpg)
  /fonts/<berkas>    font Amiri (ttf)
  /<nama>.pdf        tautan langsung ke PDF master
  /healthz           "ok"
Hanya rute di atas yang dilayani; folder .git, kunci, dan berkas lain tidak pernah terbuka.

Pemakaian:
  python tools/bangun_panel.py        # bangun preview.html + PDF lebih dulu
  python tools/server_preview.py      # lalu buka http://localhost:3000
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
NAMA_KHATAM = "KHATAM_TERJEMAHAN_Kitab_Asraru_Sulaimaniyyah.pdf"
RE_PDF = re.compile(r"^(?:KHATAM_TERJEMAHAN_Kitab_Asraru_Sulaimaniyyah|MASTER_PANEL_Batch_[0-9]+(?:-[0-9]+)?)\.pdf$")
JENIS = {
    ".html": "text/html; charset=utf-8",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ttf": "font/ttf",
}
EKSTENSI = {"rajah": {".png", ".jpg", ".jpeg"}, "fonts": {".ttf"}}
# isi paket ZIP (relatif terhadap akar repo) supaya bisa langsung diunggah ke GitHub
POLA_ZIP = [
    "BATCH_*.md", "TERJEMAHAN.md", "TERJEMAHAN_MATAN_MURNI.md", "preview.html",
    "KHATAM_TERJEMAHAN_Kitab_Asraru_Sulaimaniyyah.pdf", "MASTER_PANEL_Batch_*.pdf",
    "rajah/*.png", "rajah/*.jpg", "fonts/*.ttf", "fonts/OFL.txt", "fonts/BACA-SAYA.txt",
    "tools/bangun_panel.py", "tools/server_preview.py", "tools/test_panel.py", "README.md", "requirements-panel.txt",
]


def pdf_terbaru(root: Path = ROOT) -> Path | None:
    kandidat = [p for p in root.glob("*.pdf") if RE_PDF.match(p.name)]
    khatam = [p for p in kandidat if p.name == NAMA_KHATAM]
    if khatam:
        return khatam[0]
    return max(kandidat, key=lambda p: p.stat().st_mtime, default=None)


def berkas_aman(root: Path, sub: str, nama: str) -> Path | None:
    """Kembalikan path berkas di root/sub bila aman (tanpa traversal, ekstensi diizinkan), selain itu None."""
    if not nama or "/" in nama or "\\" in nama or "\x00" in nama or nama.startswith("."):
        return None
    if Path(nama).suffix.lower() not in EKSTENSI.get(sub, set()):
        return None
    try:
        p = (root / sub / nama).resolve(strict=True)
    except OSError:
        return None
    if (root / sub).resolve() not in p.parents or not p.is_file():
        return None
    return p


def buat_zip(root: Path = ROOT) -> bytes:
    buf = io.BytesIO()
    sudah: set[str] = set()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for pola in POLA_ZIP:
            for p in sorted(root.glob(pola)):
                rel = p.relative_to(root).as_posix()
                if p.is_file() and rel not in sudah:
                    z.write(p, rel)
                    sudah.add(rel)
    return buf.getvalue()


class ServerTenang(ThreadingHTTPServer):
    """ThreadingHTTPServer yang tidak mencetak traceback untuk klien yang memutus sambungan."""

    daemon_threads = True

    def handle_error(self, request, client_address) -> None:
        if isinstance(sys.exc_info()[1], (ConnectionResetError, BrokenPipeError, TimeoutError)):
            return
        super().handle_error(request, client_address)


class Penangan(BaseHTTPRequestHandler):
    server_version = "PanelKitab/1.0"
    protocol_version = "HTTP/1.1"
    timeout = 30  # sambungan menganggur dilepas
    root = ROOT

    def log_message(self, fmt: str, *args) -> None:  # ringkas, ke stderr
        sys.stderr.write("[panel] %s %s\n" % (self.address_string(), fmt % args))

    def do_GET(self) -> None:
        self._layani(False)

    def do_HEAD(self) -> None:
        self._layani(True)

    def _kirim(self, kode: int, isi: bytes, jenis: str, head: bool, tambahan: dict | None = None) -> None:
        self.send_response(kode)
        self.send_header("Content-Type", jenis)
        self.send_header("Content-Length", str(len(isi)))
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (tambahan or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if not head:
            self.wfile.write(isi)

    def _layani(self, head: bool) -> None:
        path = unquote(urlparse(self.path).path)
        try:
            if path in ("/", "/index.html", "/preview.html"):
                f = self.root / "preview.html"
                if not f.is_file():
                    return self._kirim(503, "preview.html belum dibangun. Jalankan: python tools/bangun_panel.py\n".encode(), "text/plain; charset=utf-8", head)
                return self._kirim(200, f.read_bytes(), JENIS[".html"], head, {"Cache-Control": "no-store"})
            if path == "/healthz":
                return self._kirim(200, b"ok\n", "text/plain; charset=utf-8", head)
            if path == "/unduh/pdf":
                f = pdf_terbaru(self.root)
                if f is None:
                    return self._kirim(404, b"PDF belum dibangun. Jalankan: python tools/bangun_panel.py\n", "text/plain; charset=utf-8", head)
                return self._kirim(200, f.read_bytes(), JENIS[".pdf"], head,
                                   {"Content-Disposition": f'attachment; filename="{f.name}"', "Cache-Control": "no-store"})
            if path == "/unduh/zip":
                return self._kirim(200, buat_zip(self.root), "application/zip", head,
                                   {"Content-Disposition": 'attachment; filename="Asraru_Sulaimaniyyah_paket_batch.zip"', "Cache-Control": "no-store"})
            m = re.match(r"^/(rajah|fonts)/([^/]+)$", path)
            if m:
                f = berkas_aman(self.root, m.group(1), m.group(2))
                if f is not None:
                    return self._kirim(200, f.read_bytes(), JENIS[f.suffix.lower()], head, {"Cache-Control": "public, max-age=300"})
            m = re.match(r"^/([^/]+\.pdf)$", path)
            if m and RE_PDF.match(m.group(1)) and (self.root / m.group(1)).is_file():
                f = self.root / m.group(1)
                return self._kirim(200, f.read_bytes(), JENIS[".pdf"], head,
                                   {"Content-Disposition": f'inline; filename="{f.name}"'})
            return self._kirim(404, b"tidak ditemukan\n", "text/plain; charset=utf-8", head)
        except (BrokenPipeError, ConnectionResetError):
            pass


def buat_server(host: str = "0.0.0.0", port: int = 3000, root: Path = ROOT) -> ServerTenang:
    kelas = type("PenanganAkar", (Penangan,), {"root": Path(root)})
    return ServerTenang((host, port), kelas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Server pratinjau Edisi Panel")
    ap.add_argument("--host", default="0.0.0.0", help="alamat ikat (bawaan 0.0.0.0 agar terlihat di pratinjau)")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "3000")))
    args = ap.parse_args(argv)
    try:
        srv = buat_server(args.host, args.port)
    except OSError as exc:
        print(f"GALAT: tidak bisa membuka port {args.port}: {exc}", file=sys.stderr)
        return 2
    pdf = pdf_terbaru()
    print(f"Pratinjau Edisi Panel: http://{args.host}:{args.port}/  (PDF: {pdf.name if pdf else 'belum ada'})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
