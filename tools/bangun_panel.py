#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Edisi Panel Kartu Modern untuk Kitab Asraru Sulaimaniyyah.

Membaca BATCH_*.md di akar repo, lalu membangun:
  preview.html                   pratinjau web (satu kartu per halaman PDF)
  MASTER_PANEL_Batch_NN.pdf      PDF A4 margin 2 cm, PyMuPDF Story (MuPDF + HarfBuzz) + font Amiri
                                 (bernama KHATAM_TERJEMAHAN_Kitab_Asraru_Sulaimaniyyah.pdf bila 21 batch lengkap)
  TERJEMAHAN.md                  gabungan semua batch (lengkap dengan syarah/faedah)
  TERJEMAHAN_MATAN_MURNI.md      gabungan: Arab + Latin + Indonesia + gambar rajah saja

Pemakaian:
  python tools/bangun_panel.py              # bangun semuanya
  python tools/bangun_panel.py --cek        # hanya periksa mutu (tanpa membangun apa pun)
  python tools/bangun_panel.py --tanpa-pdf  # lewati PDF (tanpa PyMuPDF)

Kode keluar: 0 baik; 1 ada temuan pemeriksaan; 2 galat fatal.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"
RAJAH_DIR = ROOT / "rajah"

JUDUL_AR = "كتاب أسرار سليمانية"
JUDUL_ID = "Terjemahan Kitab Asraru Sulaimaniyyah"
JUDUL_KITAB_AR = "الأسرار السليمانية في العلوم الروحانية"
TOTAL_BATCH = 21
NAMA_KHATAM = "KHATAM_TERJEMAHAN_Kitab_Asraru_Sulaimaniyyah.pdf"

HIJAU, EMAS, KREM = "#0d4a36", "#c59b27", "#f4eee2"
EMAS_RGB = (0xC5 / 255, 0x9B / 255, 0x27 / 255)
MARGIN = 56.7  # 2 cm dalam poin

LABEL_BLOK = {
    "ar": "Teks Arab Asli",
    "la": "Transliterasi Latin Fonetik",
    "id": "Terjemahan Indonesia",
    "syarah": "Syarah & Penjelasan",
    "faedah": "Faedah / Keterangan Praktik",
}
KIND = {
    "Teks Arab Asli": "ar",
    "Transliterasi Latin Fonetik": "la",
    "Terjemahan Indonesia": "id",
    "Syarah": "syarah",
    "Faedah": "faedah",
}
LABEL_MD = {
    "ar": "Teks Arab Asli",
    "la": "Transliterasi Latin Fonetik",
    "id": "Terjemahan Indonesia",
    "syarah": "Syarah",
    "faedah": "Faedah",
}

RE_BERKAS = re.compile(r"^BATCH_(\d+)\.md$")
RE_HALAMAN = re.compile(r"^##\s+Halaman PDF\s+(\d+)\s*(?:\(=\s*([^)]*)\))?\s*$")
RE_HALAMAN_LAMPIRAN = re.compile(r"^##\s+PDF\s+(\d+)\s*(?:\(=\s*([^)]*)\))?\s*(?:[—–-]\s*(.*))?$")
RE_BAGIAN = re.compile(r"^###\s+Bagian\s+(\d+)\s*(?:[—–-]\s*(.*))?$")
RE_LABEL = re.compile(r"^\*\*\[([^\]]+)\]\*\*\s*$")
RE_GAMBAR = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)\)\s*$")
RE_TABEL = re.compile(r"^\s*\|.*\|\s*$")


# --------------------------------------------------------------------------- parser
def _paragraf(baris: list[str], kind: str) -> list[dict]:
    """Ubah baris-baris satu blok menjadi daftar paragraf {t: p|h|li, text}."""
    hasil: list[dict] = []
    cur: list[str] = []

    def tutup() -> None:
        if not cur:
            return
        teks = " ".join(cur).strip()
        cur.clear()
        if not teks:
            return
        if teks.startswith("**") and teks.endswith("**") and teks.count("**") == 2 and len(teks) > 4:
            hasil.append({"t": "h", "text": teks[2:-2].strip()})
            return
        if kind == "la" and teks.startswith("*") and teks.endswith("*") and not teks.startswith("**") and len(teks) > 2:
            teks = teks[1:-1].strip()
        hasil.append({"t": "p", "text": teks})

    for mentah in baris:
        s = mentah.strip()
        if s.startswith("<div") or s.startswith("</div"):
            continue
        if kind in ("syarah", "faedah"):
            s = re.sub(r"^>\s?", "", s).strip()
        if not s:
            tutup()
            continue
        if s.startswith("- "):
            tutup()
            hasil.append({"t": "li", "text": s[2:].strip()})
            continue
        cur.append(s)
    tutup()
    return hasil


def _parse_batch_lampiran(path: Path, batch: dict) -> dict:
    """BATCH_35 berisi prosa, rajah, doa, dan indeks; parse Markdown per halaman tanpa memaksakan skema nazham."""
    halaman = bagian = None
    jenis: str | None = None
    buf: list[str] = []
    nomor_bagian = 0
    tabel_aktif = False

    def selesai_blok() -> None:
        nonlocal jenis, buf
        if jenis is not None and bagian is not None:
            paras = _paragraf(buf, jenis)
            if paras:
                bagian["items"].append({"kind": jenis, "paras": paras})
        jenis, buf = None, []

    for mentah in path.read_text(encoding="utf-8").splitlines():
        baris = mentah.rstrip()
        mh = RE_HALAMAN_LAMPIRAN.match(baris)
        if mh:
            selesai_blok()
            halaman = {"pdf": int(mh.group(1)), "label": (mh.group(2) or "").strip(), "judul": (mh.group(3) or "").strip(), "bagian": []}
            batch["halaman"].append(halaman)
            bagian = None
            nomor_bagian = 0
            tabel_aktif = False
            continue
        if halaman is not None and baris.startswith("### "):
            selesai_blok()
            nomor_bagian += 1
            bagian = {"no": nomor_bagian, "judul": baris[4:].strip(), "items": []}
            halaman["bagian"].append(bagian)
            tabel_aktif = False
            continue
        if halaman is None:
            if baris.startswith("# "):
                batch["judul"] = baris[2:].strip()
            elif baris.startswith("> "):
                batch["intro"].append(baris[2:].strip())
            elif baris.startswith("- "):
                batch["catatan"].append(baris[2:].strip())
            continue
        teks = baris.strip()
        if bagian is None:
            if not teks or teks == "---":
                continue
            nomor_bagian += 1
            bagian = {"no": nomor_bagian, "judul": halaman.get("judul") or "Isi halaman", "items": []}
            halaman["bagian"].append(bagian)
        if teks == "<div dir=\"rtl\">":
            selesai_blok()
            jenis = "ar"
            tabel_aktif = False
            continue
        if teks == "</div>":
            selesai_blok()
            tabel_aktif = False
            continue
        if RE_TABEL.match(baris):
            selesai_blok()
            if tabel_aktif and bagian["items"] and bagian["items"][-1]["kind"] == "table":
                bagian["items"][-1]["rows"].append(teks)
            else:
                bagian["items"].append({"kind": "table", "rows": [teks]})
            tabel_aktif = True
            continue
        tabel_aktif = False
        if teks == "---":
            selesai_blok()
            continue
        if jenis is None:
            jenis = "id"
        buf.append(baris)
    selesai_blok()
    return batch


def parse_batch(path: Path) -> dict:
    path = Path(path)
    m = RE_BERKAS.match(path.name)
    if not m:
        raise ValueError(f"nama berkas bukan BATCH_NN.md: {path.name}")
    batch = {"berkas": path.name, "nomor": int(m.group(1)), "judul": "", "intro": [], "catatan": [], "halaman": []}
    if batch["nomor"] == 35:
        return _parse_batch_lampiran(path, batch)
    halaman = bagian = blok = None
    buf: list[str] = []
    tabel_aktif = False

    def selesai_blok() -> None:
        nonlocal blok, buf
        if blok is not None:
            blok["paras"] = _paragraf(buf, blok["kind"])
        blok, buf = None, []

    for mentah in path.read_text(encoding="utf-8").splitlines():
        baris = mentah.rstrip()
        mh = RE_HALAMAN.match(baris)
        if mh:
            selesai_blok()
            halaman = {"pdf": int(mh.group(1)), "label": (mh.group(2) or "").strip(), "bagian": []}
            batch["halaman"].append(halaman)
            bagian = None
            continue
        mb = RE_BAGIAN.match(baris)
        if mb and halaman is not None:
            selesai_blok()
            bagian = {"no": int(mb.group(1)), "judul": (mb.group(2) or "").strip(), "items": []}
            halaman["bagian"].append(bagian)
            continue
        ml = RE_LABEL.match(baris)
        if ml and bagian is not None:
            nama = ml.group(1).strip()
            kind = next((v for k, v in KIND.items() if nama.startswith(k)), None)
            if kind is None:
                raise ValueError(f"{path.name}: label blok tidak dikenal: [{nama}]")
            selesai_blok()
            blok = {"kind": kind, "paras": []}
            bagian["items"].append(blok)
            continue
        mg = RE_GAMBAR.match(baris)
        if mg and bagian is not None:
            selesai_blok()
            bagian["items"].append({"kind": "img", "alt": mg.group(1), "src": mg.group(2), "caption": ""})
            tabel_aktif = False
            continue
        if RE_TABEL.match(baris) and bagian is not None:
            selesai_blok()
            if tabel_aktif and bagian["items"] and bagian["items"][-1]["kind"] == "table":
                bagian["items"][-1]["rows"].append(baris.strip())
            else:
                bagian["items"].append({"kind": "table", "rows": [baris.strip()]})
            tabel_aktif = True
            continue
        tabel_aktif = False
        if baris.strip() == "---":
            selesai_blok()
            continue
        if halaman is None:  # pembuka berkas
            if baris.startswith("# "):
                batch["judul"] = baris[2:].strip()
            elif baris.startswith("> "):
                batch["intro"].append(baris[2:].strip())
            elif baris.startswith("- "):
                batch["catatan"].append(baris[2:].strip())
            continue
        if blok is not None:
            buf.append(baris)
            continue
        if bagian is not None and bagian["items"] and bagian["items"][-1]["kind"] == "img" and baris.strip():
            cap = baris.strip()
            if cap.startswith("*") and cap.endswith("*"):
                cap = cap.strip("*").strip()
            bagian["items"][-1]["caption"] = cap
    selesai_blok()
    return batch


def muat_batch(root: Path = ROOT) -> list[dict]:
    berkas = sorted((p for p in Path(root).iterdir() if RE_BERKAS.match(p.name)), key=lambda p: int(RE_BERKAS.match(p.name).group(1)))
    return [parse_batch(p) for p in berkas]


# --------------------------------------------------------------------------- utilitas teks
def esc(s: str) -> str:
    return html.escape(s, quote=False)


def inline(s: str) -> str:
    """Escape + penebalan/miring Markdown sederhana untuk teks Indonesia."""
    s = esc(s).replace("`", "")
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def tandai_editorial(s: str) -> str:
    return re.sub(r"(\[(?:المطبوع|كذا)[^\]]*\])", r'<span class="ed">\1</span>', s)


def nomor_arab(n: int) -> str:
    return str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def lencana_halaman(h: dict) -> str:
    label = h["label"].strip()
    return label[:1].upper() + label[1:] if label else ""


def nama_pdf(batches: list[dict]) -> str:
    nomor = sorted(b["nomor"] for b in batches)
    if nomor == list(range(1, TOTAL_BATCH + 1)):
        return NAMA_KHATAM
    if len(nomor) == 1:
        return f"MASTER_PANEL_Batch_{nomor[0]:02d}.pdf"
    return f"MASTER_PANEL_Batch_{nomor[0]:02d}-{nomor[-1]:02d}.pdf"


def rentang_pdf(batches: list[dict]) -> tuple[int, int]:
    nomor = [h["pdf"] for b in batches for h in b["halaman"]]
    return min(nomor), max(nomor)


# --------------------------------------------------------------------------- HTML (web & pdf)
def _table_html(blok: dict) -> str:
    rows = [[c.strip() for c in row.strip().strip("|").split("|")] for row in blok.get("rows", [])]
    if not rows:
        return ""
    header, *sisa = rows
    body = [r for r in sisa if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
    th = "".join(f"<th>{inline(c)}</th>" for c in header)
    tr = []
    for row in body:
        cells = []
        for i, cell in enumerate(row):
            arah = ' dir="rtl" lang="ar"' if i == 1 else ""
            cells.append(f"<td{arah}>{inline(cell)}</td>")
        tr.append("<tr>" + "".join(cells) + "</tr>")
    return '<div class="blok blok-tabel"><table><thead><tr>' + th + '</tr></thead><tbody>' + "".join(tr) + '</tbody></table></div>'


def _blok_html(blok: dict) -> str:
    kind = blok["kind"]
    if kind == "table":
        return _table_html(blok)
    isi: list[str] = []
    daftar: list[str] = []

    def tutup_daftar() -> None:
        nonlocal daftar
        if daftar:
            isi.append("<ul>" + "".join(daftar) + "</ul>")
            daftar = []

    for p in blok["paras"]:
        if p["t"] == "li":
            daftar.append(f"<li>{inline(p['text'])}</li>")
            continue
        tutup_daftar()
        kepala = p["t"] == "h"
        if kind == "ar":
            isi.append(f'<p class="{"ar-h" if kepala else "ar-p"}">{tandai_editorial(esc(p["text"]))}</p>')
        elif kind == "la":
            isi.append(f'<p class="{"la-h" if kepala else "la-p"}">{esc(p["text"])}</p>')
        else:
            isi.append(f'<p class="{"id-h" if kepala else "id-p"}">{inline(p["text"])}</p>')
    tutup_daftar()
    arah = ' dir="rtl" lang="ar"' if kind == "ar" else ""
    return f'<div class="lbl">{esc(LABEL_BLOK[kind])}</div><div class="blok blok-{kind}"{arah}>{"".join(isi)}</div>'


def _gambar_html(item: dict, mode: str) -> str:
    src = item["src"] if mode == "web" else Path(item["src"]).name
    lebar = 460 if mode == "web" else 300
    cap = f'<p class="gambar-ket"><em>{inline(item["caption"])}</em></p>' if item["caption"] else ""
    alt = html.escape(item["alt"], quote=True)
    return (
        f'<div class="gambar"><img src="{html.escape(src, quote=True)}" alt="{alt}" width="{lebar}"/>'
        f'<p class="gambar-judul">{esc(item["alt"])}</p>{cap}</div>'
    )


def _kartu_html(batch: dict, h: dict, mode: str = "web") -> str:
    lencana = [f"Halaman PDF {h['pdf']}"]
    if h["label"]:
        lencana.append(lencana_halaman(h))
    lencana.append(f"Batch {batch['nomor']:02d}")
    kepala = "".join(f'<span class="lencana">{esc(x)}</span>' for x in lencana)
    bagian_html: list[str] = []
    for b in h["bagian"]:
        judul = f"Bagian {b['no']}" + (f" — {b['judul']}" if b["judul"] else "")
        potongan = [f'<h3 class="bagian-judul">{esc(judul)}</h3>']
        for it in b["items"]:
            potongan.append(_gambar_html(it, mode) if it["kind"] == "img" else _blok_html(it))
        bagian_html.append(f'<section class="bagian">{"".join(potongan)}</section>')
    return f'<article class="kartu"><div class="kartu-kepala">{kepala}</div>{"".join(bagian_html)}</article>'


def _unit_kartu_pdf(batch: dict, h: dict) -> list[str]:
    """Pecah satu kartu halaman menjadi unit tata letak: judul bagian + label + blok tidak boleh terpisah."""
    lencana = [f"Halaman PDF {h['pdf']}"]
    if h["label"]:
        lencana.append(lencana_halaman(h))
    lencana.append(f"Batch {batch['nomor']:02d}")
    awalan = f'<p class="kartu-kepala">{esc(" · ".join(lencana))}</p>'
    unit: list[str] = []
    for b in h["bagian"]:
        judul = f"Bagian {b['no']}" + (f" — {b['judul']}" if b["judul"] else "")
        kepala_bagian = f'<h3 class="bagian-judul">{esc(judul)}</h3>'
        punya_gambar = any(it["kind"] == "img" for it in b["items"])
        potongan: list[str] = []
        for it in b["items"]:
            potongan.append(_gambar_html(it, "pdf") if it["kind"] == "img" else _blok_html(it))
        if punya_gambar:  # bagian dengan gambar: satu unit utuh (teks pengantar + gambar tidak terpisah)
            unit.append(awalan + kepala_bagian + "".join(potongan))
            awalan = ""
            continue
        for i, isi in enumerate(potongan):
            unit.append(awalan + (kepala_bagian if i == 0 else "") + isi)
            awalan = ""
    return unit


def _catatan_html(batches: list[dict], mode: str) -> str:
    butir = batches[0]["catatan"] if batches else []
    if not butir:
        return ""
    li = "".join(f"<li>{inline(x)}</li>" for x in butir)
    if mode == "web":
        return f'<details class="catatan" open><summary>Catatan penyunting</summary><ul>{li}</ul></details>'
    return f'<div class="catatan"><p><strong>Catatan penyunting</strong></p><ul>{li}</ul></div>'


FACE_WEB = "".join(
    f"@font-face{{font-family:'Amiri';src:url('fonts/Amiri-{nama}.ttf') format('truetype');font-weight:{w};font-style:{s};font-display:swap}}"
    for nama, w, s in (("Regular", 400, "normal"), ("Bold", 700, "normal"), ("Italic", 400, "italic"), ("BoldItalic", 700, "italic"))
)
FACE_PDF = "".join(
    f"@font-face {{ font-family: Amiri; font-weight: {w}; font-style: {s}; src: url('Amiri-{nama}.ttf'); }}\n"
    for nama, w, s in (("Regular", "normal", "normal"), ("Bold", "bold", "normal"), ("Italic", "normal", "italic"), ("BoldItalic", "bold", "italic"))
)

CSS_WEB = """
:root{--hijau:#0d4a36;--emas:#c59b27;--krem:#f4eee2}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#e9efea;color:#1f2933;font-family:'Amiri',Georgia,'Times New Roman',serif;font-size:19px;line-height:1.65}
.hero{background:var(--hijau);color:#fff;text-align:center;padding:26px 16px 22px;border-bottom:6px solid var(--emas)}
.hero-ar{font-family:'Amiri',serif;font-size:clamp(38px,8vw,64px);line-height:1.5;color:#f3d57c;direction:rtl}
.hero-sub{font:500 14px/1.4 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;opacity:.92;margin:2px 0 16px}
.btn-unduh{display:inline-block;background:linear-gradient(#e2b73f,var(--emas));color:var(--hijau);font:800 17px/1.25 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;padding:14px 22px;border-radius:12px;text-decoration:none;box-shadow:0 3px 0 #8f6d12,0 8px 18px rgba(0,0,0,.28)}
.btn-unduh:active{transform:translateY(2px);box-shadow:0 1px 0 #8f6d12}
.hero-info{font:13px/1.55 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;margin-top:12px;color:#d7e6dd}
.hero-info a{color:#f3d57c}
main{max-width:880px;margin:0 auto;padding:6px 12px 40px}
.catatan{background:#faf7ef;border:1px dashed var(--emas);border-radius:10px;padding:10px 16px;margin:18px 0;font:14px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}
.catatan summary{cursor:pointer;font-weight:700;color:var(--hijau)}
.catatan ul{margin:.5em 0 .2em 1.1em;padding:0}
.kartu{background:#fff;border-radius:16px;box-shadow:0 2px 12px rgba(13,74,54,.14);margin:22px 0;overflow:hidden}
.kartu-kepala{background:var(--krem);border-bottom:2px solid var(--emas);padding:10px 14px;display:flex;flex-wrap:wrap;gap:8px;font:700 13px/1 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:var(--hijau)}
.lencana{background:#fff;border:1px solid var(--emas);border-radius:999px;padding:5px 11px}
.bagian{padding:4px 16px 14px}
.bagian-judul{font:700 15px/1.4 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:var(--hijau);margin:18px 0 2px;border-bottom:1px solid #e5e0d0;padding-bottom:5px}
.lbl{font:600 11px/1 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#6b7280;margin:12px 2px 4px}
.blok{border-radius:8px;padding:8px 16px}
.blok p{margin:.25em 0}
.blok-ar{background:#f7faf7;border-right:4px solid var(--hijau);direction:rtl;text-align:right;font-family:'Amiri',serif;font-size:clamp(23px,4.8vw,31px);line-height:2.2}
.ar-h{font-weight:700}
.blok-la{background:#f4f6f8;border-left:4px solid #94a3b8;font-style:italic;font-size:18px}
.la-h,.id-h{font-weight:700}
.blok-id{text-align:justify;hyphens:auto}
.blok-syarah{background:#faf7ef;border:1px dashed var(--emas);font-size:17px;text-align:justify}
.blok-faedah{background:#fff8f2;border:1px solid #fb923c;font-size:17px}
.blok ul{margin:.3em 0 .3em 1.1em;padding:0}
.blok-tabel{overflow-x:auto;padding:8px 0}
.blok-tabel table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.45}
.blok-tabel th,.blok-tabel td{border:1px solid #cbd5d1;padding:5px 7px;vertical-align:top}
.blok-tabel th{background:#f4eee2;color:#0d4a36;text-align:center}
.blok-tabel td:nth-child(2){text-align:right}
.gambar{margin:16px 0;text-align:center;border:2px dashed var(--emas);background:#fff;border-radius:10px;padding:14px}
.gambar img{max-width:min(100%,460px);height:auto}
.gambar-judul{font:700 14px/1.4 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:var(--hijau);margin:8px 0 2px}
.gambar-ket{font:14px/1.55 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:#4b5563;text-align:left;margin:4px 0 0}
.ed{color:#9a3412;font-size:.62em;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;white-space:nowrap}
footer{text-align:center;font:12px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:#5b6b63;padding:6px 16px 26px}
"""

CSS_PDF = """
body { margin: 0; padding: 0; font-family: Amiri; font-size: 10.5pt; color: #1f2933; }
p { margin: 0 0 3pt 0; }
.banner { background-color: #0d4a36; border-bottom: 4pt solid #c59b27; padding: 8pt 12pt; margin-bottom: 8pt; }
.banner-ar { font-size: 30pt; color: #f3d57c; direction: rtl; text-align: center; line-height: 1.5; margin: 0; }
.banner-sub { color: #f4eee2; font-size: 10pt; text-align: center; margin: 0; }
.catatan { background-color: #faf7ef; border: 1pt dashed #c59b27; padding: 5pt 10pt; margin: 6pt 0 10pt 0; font-size: 8.5pt; }
.catatan ul { margin: 2pt 0 0 0; }
.kartu-kepala { background-color: #f4eee2; border-bottom: 1.5pt solid #c59b27; padding: 4pt 8pt; margin: 0 0 4pt 0; font-weight: bold; color: #0d4a36; font-size: 10pt; }
.bagian-judul { color: #0d4a36; font-size: 11.5pt; font-weight: bold; margin: 8pt 0 1pt 0; }
.lbl { font-size: 7.5pt; color: #6b7280; margin: 4pt 0 1pt 2pt; }
.blok p { margin: 0; }
.blok ul { margin: 0 0 0 12pt; padding: 0; }
.blok-ar { direction: rtl; background-color: #f7faf7; border-right: 4pt solid #0d4a36; padding: 0 10pt; font-size: 17pt; line-height: 2.2; }
.ar-h { font-weight: bold; }
.blok-la { background-color: #f4f6f8; border-left: 4pt solid #94a3b8; font-style: italic; padding: 0 10pt; line-height: 1.7; }
.la-h, .id-h { font-weight: bold; }
.blok-id { text-align: justify; padding: 0 10pt; line-height: 1.6; }
.blok-syarah { background-color: #faf7ef; border: 1pt dashed #c59b27; padding: 0 10pt; font-size: 9.5pt; line-height: 1.6; text-align: justify; }
.blok-faedah { background-color: #fff8f2; border: 1pt solid #fb923c; padding: 0 10pt; font-size: 9.5pt; line-height: 1.6; }
.blok-tabel { padding: 2pt 0; }
.blok-tabel table { border-collapse: collapse; width: 100%; font-size: 7.5pt; line-height: 1.3; }
.blok-tabel th, .blok-tabel td { border: 0.5pt solid #b8c1bc; padding: 2pt 3pt; vertical-align: top; }
.blok-tabel th { background-color: #f4eee2; color: #0d4a36; text-align: center; }
.blok-tabel td:nth-child(2) { text-align: right; }
.gambar { text-align: center; border: 2pt dashed #c59b27; background-color: #ffffff; padding: 8pt; margin: 8pt 36pt; page-break-inside: avoid; }
.gambar-judul { font-weight: bold; color: #0d4a36; font-size: 9pt; margin: 4pt 0 1pt 0; }
.gambar-ket { font-size: 8pt; color: #4b5563; text-align: left; }
.ed { color: #9a3412; font-size: 8pt; }
"""


def render_preview(batches: list[dict], nama_berkas_pdf: str | None) -> str:
    a, z = rentang_pdf(batches)
    nomor = [b["nomor"] for b in batches]
    batch_txt = f"Batch {nomor[0]:02d}" if len(nomor) == 1 else f"Batch {nomor[0]:02d}–{nomor[-1]:02d}"
    kartu = "".join(_kartu_html(b, h, "web") for b in batches for h in b["halaman"])
    tautan = ""
    if nama_berkas_pdf:
        tautan = (
            f'Tulisan Arab tersambung utuh (font Amiri · PyMuPDF/HarfBuzz) · {batch_txt} (hal. PDF {a}–{z}) · '
            f'<a href="unduh/zip">Unduh semua berkas batch (ZIP)</a> · '
            f'<a href="{html.escape(nama_berkas_pdf, quote=True)}">tautan langsung PDF</a>'
        )
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(JUDUL_AR)} — {esc(JUDUL_ID)}</title><style>{FACE_WEB}{CSS_WEB}</style></head><body>"
        f'<header class="hero"><div class="hero-ar">{esc(JUDUL_AR)}</div>'
        f'<div class="hero-sub">{esc(JUDUL_ID)} · Edisi Panel Kartu Modern</div>'
        '<a class="btn-unduh" href="unduh/pdf" download>📥 Unduh PDF Master Panel</a>'
        f'<div class="hero-info">{tautan}</div></header>'
        f"<main>{_catatan_html(batches, 'web')}{kartu}</main>"
        "<footer>Harakat, transliterasi, dan terjemahan dibuat dengan bantuan AI dan perlu dikoreksi nahwu/sharaf. "
        "Sumber: pindaian kitab (kitab/asrorul-sulaimaniyah.pdf).</footer></body></html>"
    )


def unit_pdf(batches: list[dict]) -> list[tuple[str, bool]]:
    """Daftar (html, halaman_baru). Setiap kartu halaman PDF dimulai di halaman baru."""
    a, z = rentang_pdf(batches)
    banner = (
        f'<div class="banner"><p class="banner-ar" dir="rtl">{esc(JUDUL_AR)}</p>'
        f'<p class="banner-sub">{esc(JUDUL_ID)} · Edisi Panel Kartu Modern · hal. PDF {a}–{z}</p></div>'
    )
    unit: list[tuple[str, bool]] = [(banner, False)]
    catatan = _catatan_html(batches, "pdf")
    if catatan:
        unit.append((catatan, False))
    pertama = True
    for b in batches:
        for h in b["halaman"]:
            for i, u in enumerate(_unit_kartu_pdf(b, h)):
                unit.append((u, i == 0 and not pertama))
            pertama = False
    return unit


# --------------------------------------------------------------------------- PDF
def _header_footer(doc, batches: list[dict], pymupdf, arc, awal_lampiran: int | None = None) -> None:
    css = FACE_PDF + "body { font-family: Amiri; color: #0d4a36; font-size: 9pt; } p { margin: 0; }"
    total = len(doc)
    nomor = [b["nomor"] for b in batches]
    rentang = f"Batch {nomor[0]:02d}" if len(nomor) == 1 else f"Batch {nomor[0]:02d}–{nomor[-1]:02d}"
    for i, page in enumerate(doc):
        r = page.rect
        kiri, kanan = MARGIN, r.width - MARGIN
        label_kiri = f"Pindaian sumber PDF {i - awal_lampiran + 1:03d}" if awal_lampiran is not None and i >= awal_lampiran else f"{rentang} · Kartu Panel"
        page.draw_line((kiri, 50), (kanan, 50), color=EMAS_RGB, width=0.9)
        page.draw_line((kiri, r.height - 50), (kanan, r.height - 50), color=EMAS_RGB, width=0.9)
        page.insert_htmlbox(
            pymupdf.Rect(kanan - 240, 20, kanan, 49),
            f'<p dir="rtl" style="text-align:right;font-size:14pt">{esc(JUDUL_AR)}</p>', css=css, archive=arc)
        page.insert_htmlbox(
            pymupdf.Rect(kiri, 30, kiri + 240, 49),
            f'<p style="font-size:8.5pt">{esc(label_kiri)}</p>', css=css, archive=arc)
        page.insert_htmlbox(
            pymupdf.Rect(r.width / 2 - 70, r.height - 47, r.width / 2 + 70, r.height - 14),
            f'<p style="text-align:center;font-size:14pt">﴿ {nomor_arab(i + 1)} ﴾</p>', css=css, archive=arc)
        page.insert_htmlbox(
            pymupdf.Rect(kiri, r.height - 40, kiri + 200, r.height - 16),
            f'<p style="font-size:8pt;color:#6b7280">Halaman {i + 1} dari {total}</p>', css=css, archive=arc)


def _susun_halaman(unit: list[tuple[str, bool]], arc, pymupdf, penulis) -> None:
    """Tata letak sendiri: tiap unit diukur lalu ditaruh utuh di satu halaman bila muat.

    MuPDF tidak mendukung page-break-inside dan menyisakan serpihan kotak (bar hijau) di puncak
    halaman bila sebuah blok berakhir tepat di dasar halaman sebelumnya. Dengan menaruh unit utuh,
    serpihan itu tidak muncul dan judul/label tidak terpisah dari bloknya."""
    css = FACE_PDF + CSS_PDF
    mb = pymupdf.paper_rect("a4")
    kiri, kanan = MARGIN, mb.width - MARGIN
    atas, bawah = MARGIN, mb.height - MARGIN
    tinggi_isi = bawah - atas
    jeda = 3.0
    dev = None
    y = atas

    def story(h: str):
        return pymupdf.Story(html=f"<html><body>{h}</body></html>", user_css=css, em=11, archive=arc)

    def buka():
        nonlocal dev, y
        dev = penulis.begin_page(mb)
        y = atas

    def tutup():
        nonlocal dev
        if dev is not None:
            penulis.end_page()
            dev = None

    for isi, baru in unit:
        if dev is None:
            buka()
        elif baru:
            tutup()
            buka()
        _, terisi = story(isi).place(pymupdf.Rect(kiri, 0, kanan, 100000))
        tinggi = pymupdf.Rect(terisi).y1
        if y + tinggi > bawah + 0.01 and (tinggi <= tinggi_isi or y > atas + 0.6 * tinggi_isi):
            tutup()
            buka()
        s = story(isi)
        while True:
            lagi, terisi = s.place(pymupdf.Rect(kiri, y, kanan, bawah))
            s.draw(dev)
            y = pymupdf.Rect(terisi).y1 + jeda
            if not lagi:
                break
            tutup()
            buka()
    tutup()


def _peta_gid_unicode(ttf: bytes) -> dict[int, str]:
    """Peta glyph-id -> teks Unicode, dihitung dari font itu sendiri (cmap + substitusi GSUB).

    MuPDF menulis ToUnicode berupa tebakan rentang sehingga bentuk huruf Arab kontekstual
    (awal/tengah/akhir/ligatur) terekstrak sebagai simbol acak. Peta ini memperbaikinya."""
    import io
    import unicodedata

    from fontTools.ttLib import TTFont

    f = TTFont(io.BytesIO(ttf), lazy=True)
    urut = f.getGlyphOrder()
    gid = {n: i for i, n in enumerate(urut)}
    uni: dict[int, str] = {}
    for cp, nama in sorted(f.getBestCmap().items()):
        g = gid.get(nama)
        if g is None or g in uni:
            continue
        ch = chr(cp)
        if 0xFB50 <= cp <= 0xFDFF or 0xFE70 <= cp <= 0xFEFF:  # bentuk presentasi -> huruf dasar
            ch = unicodedata.normalize("NFKC", ch)
        uni[g] = ch
    balik: dict[int, list[list[int]]] = {}  # keluaran -> daftar kemungkinan urutan masukan
    potongan: set[int] = set()  # glyph pecahan (GSUB tipe 2) yang tak membawa teks sendiri

    def catat(keluar: str, masuk: list[str]) -> None:
        balik.setdefault(gid[keluar], []).append([gid[x] for x in masuk])

    if "GSUB" in f and f["GSUB"].table.LookupList:
        for lookup in f["GSUB"].table.LookupList.Lookup:
            for st in lookup.SubTable:
                st = getattr(st, "ExtSubTable", st)
                if hasattr(st, "alternates"):
                    for a, alts in st.alternates.items():
                        for b in alts:
                            catat(b, [a])
                elif hasattr(st, "ligatures"):
                    for first, ligs in st.ligatures.items():
                        for lg in ligs:
                            catat(lg.LigGlyph, [first] + list(lg.Component))
                elif hasattr(st, "mapping"):
                    for a, b in st.mapping.items():
                        if isinstance(b, str):
                            catat(b, [a])
                        elif b:  # GSUB tipe 2: satu glyph dipecah jadi beberapa potongan
                            catat(b[0], [a])
                            for x in b[1:]:
                                potongan.add(gid[x])
                elif hasattr(st, "Substitute") and hasattr(st, "Coverage"):  # GSUB tipe 8 (reverse chaining)
                    for a, b in zip(st.Coverage.glyphs, st.Substitute):
                        catat(b, [a])
    cache: dict[int, str] = {}

    def selesai(g: int, pila: tuple = ()) -> str:
        if g in uni:
            return uni[g]
        if g in cache:
            return cache[g]
        if g in pila:
            return ""
        for alt in balik.get(g, []):
            t = "".join(selesai(x, pila + (g,)) for x in alt)
            if t:
                cache[g] = t
                return t
        return ""

    peta = {}
    for g in range(len(urut)):
        t = selesai(g)
        if t:
            peta[g] = t
    for g in potongan:  # pecahan glyph tanpa teks: ZWSP (entri nol-panjang ditolak MuPDF,
        peta.setdefault(g, "\u200b")  # CID tanpa pemetaan dibaca balik sebagai unicode acak)
    return peta


def _cmap_tounicode(peta: dict[int, str]) -> bytes:
    baris = ["/CIDInit /ProcSet findresource begin", "12 dict begin", "begincmap",
             "/CIDSystemInfo <</Registry(Adobe)/Ordering(UCS)/Supplement 0>> def",
             "/CMapName /Adobe-Identity-UCS def", "/CMapType 2 def",
             "1 begincodespacerange", "<0000> <FFFF>", "endcodespacerange"]
    butir = sorted(peta.items())
    for i in range(0, len(butir), 100):  # batas spesifikasi: 100 entri per blok
        potong = butir[i:i + 100]
        baris.append(f"{len(potong)} beginbfchar")
        baris += [f"<{g:04X}> <{t.encode('utf-16-be').hex().upper()}>" for g, t in potong]
        baris.append("endbfchar")
    baris += ["endcmap", "CMapName currentdict /CMap defineresource pop", "end", "end"]
    return ("\n".join(baris) + "\n").encode("ascii")


def _perbaiki_tounicode(doc) -> int:
    """Tulis ulang ToUnicode semua font Type0 tertanam supaya salin/cari teks Arab dari PDF benar."""
    diperbaiki = 0
    sudah: set[int] = set()
    for pno in range(len(doc)):
        for f in doc.get_page_fonts(pno):
            xref = f[0]
            if xref in sudah:
                continue
            sudah.add(xref)
            tu = doc.xref_get_key(xref, "ToUnicode")
            desc = doc.xref_get_key(xref, "DescendantFonts")
            if tu[0] != "xref" or desc[0] != "array":
                continue
            d_x = int(re.search(r"(\d+) 0 R", desc[1]).group(1))
            fd = doc.xref_get_key(d_x, "FontDescriptor")
            if fd[0] != "xref":
                continue
            ff = doc.xref_get_key(int(re.search(r"(\d+) 0 R", fd[1]).group(1)), "FontFile2")
            if ff[0] != "xref":
                continue
            ttf = doc.xref_stream(int(re.search(r"(\d+) 0 R", ff[1]).group(1)))
            peta = _peta_gid_unicode(ttf)
            if peta:
                doc.update_stream(int(re.search(r"(\d+) 0 R", tu[1]).group(1)), _cmap_tounicode(peta))
                diperbaiki += 1
    return diperbaiki


def _tambahkan_pindaian_sumber(doc, batches: list[dict], pymupdf) -> int | None:
    """Lampirkan 103 pindaian halaman penuh pada panel lengkap, satu scan per halaman A4."""
    nomor = sorted(b["nomor"] for b in batches)
    if nomor != list(range(1, 36)):
        return None
    berkas = [ROOT / "hasil" / "gambar" / f"halaman_{i:03d}.jpg" for i in range(1, 104)]
    hilang = [str(p) for p in berkas if not p.is_file()]
    if hilang:
        raise FileNotFoundError("pindaian sumber penuh tidak lengkap: " + ", ".join(hilang[:5]))

    a4 = pymupdf.paper_rect("a4")
    mulai = len(doc)
    for no, sumber in enumerate(berkas, 1):
        page = doc.new_page(width=a4.width, height=a4.height)
        page.insert_textbox(
            pymupdf.Rect(MARGIN, 55, a4.width - MARGIN, 73),
            f"Pindaian penuh sumber - halaman PDF {no:03d} / 103",
            fontname="helv", fontsize=8, align=pymupdf.TEXT_ALIGN_CENTER, color=(0.2, 0.25, 0.2))
        px = pymupdf.Pixmap(str(sumber))
        area = pymupdf.Rect(22, 78, a4.width - 22, a4.height - 58)
        skala = min(area.width / px.width, area.height / px.height)
        lebar, tinggi = px.width * skala, px.height * skala
        gambar = pymupdf.Rect(
            area.x0 + (area.width - lebar) / 2,
            area.y0 + (area.height - tinggi) / 2,
            area.x0 + (area.width + lebar) / 2,
            area.y0 + (area.height + tinggi) / 2)
        page.insert_image(gambar, filename=str(sumber), keep_proportion=True, overlay=True)
    return mulai


def bangun_pdf(batches: list[dict], keluaran: Path) -> int:
    """Bangun PDF master. Mengembalikan jumlah halaman."""
    import pymupdf  # impor malas: --cek dan server tidak memerlukannya

    arc = pymupdf.Archive()
    arc.add(str(FONT_DIR))
    arc.add(str(RAJAH_DIR))
    sementara = Path(str(keluaran) + ".tmp")
    penulis = pymupdf.DocumentWriter(str(sementara))
    _susun_halaman(unit_pdf(batches), arc, pymupdf, penulis)
    penulis.close()
    doc = pymupdf.open(str(sementara))
    awal_lampiran = _tambahkan_pindaian_sumber(doc, batches, pymupdf)
    _header_footer(doc, batches, pymupdf, arc, awal_lampiran)
    try:
        _perbaiki_tounicode(doc)
    except Exception as exc:  # noqa: BLE001 - tampilan PDF tidak terpengaruh; hanya salin/cari teks
        print(f"  PERINGATAN: ToUnicode tidak diperbaiki ({exc}); salin teks Arab dari PDF mungkin tidak akurat", file=sys.stderr)
    doc.set_metadata({
        "title": f"{JUDUL_ID} — Edisi Panel",
        "author": "Terjemahan dibantu AI (perlu koreksi) — kitab karya Dr. Abdullah al-Jundi",
        "subject": JUDUL_KITAB_AR,
        "keywords": "Asraru Sulaimaniyyah, terjemahan, Arab, Latin, Indonesia",
        "creator": "tools/bangun_panel.py (PyMuPDF Story + HarfBuzz, font Amiri)",
    })
    halaman = len(doc)
    doc.save(str(keluaran), garbage=4, deflate=True, deflate_fonts=True)
    doc.close()
    sementara.unlink()
    return halaman


# --------------------------------------------------------------------------- Markdown gabungan
def _md_para(kind: str, p: dict) -> str:
    if p["t"] == "li":
        return f"- {p['text']}"
    if p["t"] == "h":
        return f"**{p['text']}**"
    return f"*{p['text']}*" if kind == "la" else p["text"]


def ke_markdown(batches: list[dict], murni: bool) -> str:
    nomor = [b["nomor"] for b in batches]
    nama = "TERJEMAHAN_MATAN_MURNI" if murni else "TERJEMAHAN"
    k = [f"# {nama} — {JUDUL_KITAB_AR}", ""]
    rentang = f"Batch {nomor[0]:02d}" if len(nomor) == 1 else f"Batch {nomor[0]:02d}–{nomor[-1]:02d}"
    k.append(f"> Gabungan {rentang}, dibangun otomatis oleh `tools/bangun_panel.py`. "
             "Jangan disunting di sini; ubah `BATCH_NN.md` lalu bangun ulang.")
    k.append("")
    if not murni and batches[0]["catatan"]:
        k.append("**Catatan penyunting:**")
        k.append("")
        k.extend(f"- {c}" for c in batches[0]["catatan"])
        k.append("")
    for b in batches:
        a, z = min(h["pdf"] for h in b["halaman"]), max(h["pdf"] for h in b["halaman"])
        k += ["---", "", f"# BATCH {b['nomor']:02d} — Halaman PDF {a}–{z}", ""]
        for h in b["halaman"]:
            k.append(f"## Halaman PDF {h['pdf']}" + (f" (= {h['label']})" if h["label"] else ""))
            k.append("")
            for bg in h["bagian"]:
                k.append(f"### Bagian {bg['no']}" + (f" — {bg['judul']}" if bg["judul"] else ""))
                k.append("")
                for it in bg["items"]:
                    if it["kind"] == "img":
                        k += [f"![{it['alt']}]({it['src']})", ""]
                        if it["caption"]:
                            k += [f"*{it['caption']}*", ""]
                        continue
                    if it["kind"] == "table":
                        k += it.get("rows", []) + [""]
                        continue
                    if murni and it["kind"] in ("syarah", "faedah"):
                        continue
                    k += [f"**[{LABEL_MD[it['kind']]}]**", ""]
                    if it["kind"] == "ar":
                        k += ['<div dir="rtl">', ""]
                    ada_li = False
                    for p in it["paras"]:
                        if it["kind"] in ("syarah", "faedah"):
                            if p["t"] == "li":
                                k.append(f"> {_md_para(it['kind'], p)}")
                                ada_li = True
                            else:
                                if ada_li:
                                    k.append(">")
                                    ada_li = False
                                k += [f"> {_md_para(it['kind'], p)}", ">"]
                            continue
                        k += [_md_para(it["kind"], p), ""]
                    if it["kind"] in ("syarah", "faedah"):
                        while k and k[-1] == ">":
                            k.pop()
                        k.append("")
                    if it["kind"] == "ar":
                        k += ["</div>", ""]
    return "\n".join(k).rstrip() + "\n"


# --------------------------------------------------------------------------- pemeriksaan mutu
TANDA_HARAKAT = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0656\u0657\u0658\u0670")
VOKAL_PENDEK = set("\u064B\u064C\u064D\u064E\u064F\u0650")
HURUF_ARAB = lambda c: "\u0621" <= c <= "\u064A" or c == "\u0671"  # noqa: E731
SUMBU_LATIN = r"(?:t|ts|d|dz|r|z|s|sy|sh|dh|th|zh|n)"
POLA_LATIN_SALAH = [
    (re.compile(r"\bat-tii\b", re.I), "at-tii: tulis 'allatii'"),
    (re.compile(r"\badz-dzii\b", re.I), "adz-dzii: tulis 'alladzii'"),
    (re.compile(r"\bwlaa\b", re.I), "wlaa: tulis 'wa laa'"),
    (re.compile(r"\bal-" + SUMBU_LATIN + r"[aiu][\w'-]*", re.I), "al- + huruf syamsiyah belum dileburkan"),
    (re.compile(r"\b(?:min|fii|bi|li|'an|'alaa)\s+(?:al|ash|ath|an|ar|as|az|ad|at|asy)-", re.I), "partikel belum disambung (minal-, fil-, bil-, lil-, 'anil-, 'alal-)"),
]


def _kata_arab_berharakat(teks: str) -> tuple[int, int]:
    teks = re.sub(r"\[[^\]]*\]", " ", teks)
    teks = teks.replace("(؟)", " ")
    jumlah = ada = 0
    for kata in re.findall(r"[\u0621-\u0652\u0670\u0671]+", teks):
        huruf = [c for c in kata if HURUF_ARAB(c)]
        if len(huruf) < 2:
            continue
        jumlah += 1
        if any(c in TANDA_HARAKAT for c in kata):
            ada += 1
    return jumlah, ada


def periksa(batches: list[dict], root: Path = ROOT) -> tuple[list[str], list[str]]:
    """Kembalikan (temuan, ringkasan)."""
    temuan: list[str] = []
    ringkasan: list[str] = []
    try:
        from fontTools.ttLib import TTFont

        peta = TTFont(str(FONT_DIR / "Amiri-Regular.ttf")).getBestCmap()
    except Exception:  # noqa: BLE001 - fontTools opsional
        peta = None
    for b in batches:
        if b["nomor"] == 35:  # prosa, rajah, doa, dan indeks; bukan bait berpasangan untuk uji 95% harakat
            ringkasan.append(f"{b['berkas']}: {len(b['halaman'])} halaman lampiran non-nazham")
            continue
        jml = ada = 0
        for h in b["halaman"]:
            for bg in h["bagian"]:
                tag = f"{b['berkas']} hal.PDF {h['pdf']} bagian {bg['no']}"
                hitung = {"ar": 0, "la": 0, "id": 0}
                for it in bg["items"]:
                    if it["kind"] == "img":
                        if not (root / it["src"]).is_file():
                            temuan.append(f"{tag}: gambar tidak ada: {it['src']}")
                        continue
                    if it["kind"] == "table":
                        continue
                    if it["kind"] in hitung:
                        hitung[it["kind"]] = len([p for p in it["paras"] if p["t"] != "li"])
                    teks = " ".join(p["text"] for p in it["paras"])
                    if peta is not None:
                        hilang = sorted({c for c in teks if not unicodedata.name(c, "").startswith(("LATIN ", "MODIFIER LETTER ")) and ord(c) not in peta})
                        if hilang:
                            temuan.append(f"{tag} [{it['kind']}]: karakter tidak ada di font: " + " ".join(f"U+{ord(c):04X}" for c in hilang))
                    if it["kind"] == "ar":
                        j, a = _kata_arab_berharakat(teks)
                        jml, ada = jml + j, ada + a
                        for kata in re.findall(r"[\u0621-\u0652\u0670\u0671]+", re.sub(r"\[[^\]]*\]", " ", teks)):
                            tanda = [c for c in kata if c in VOKAL_PENDEK]
                            for x, y in zip(kata, kata[1:]):
                                if x in VOKAL_PENDEK and y in VOKAL_PENDEK:
                                    temuan.append(f"{tag}: dua harakat berurutan pada satu huruf: {kata}")
                                    break
                            if len(tanda) > 2 and "\u0651" not in kata and len(tanda) > len(kata) // 2 + 1:
                                temuan.append(f"{tag}: harakat berlebih: {kata}")
                    if it["kind"] == "la":
                        for pola, pesan in POLA_LATIN_SALAH:
                            for m in pola.finditer(teks):
                                temuan.append(f"{tag}: Latin '{m.group(0)}' — {pesan}")
                sedikit = {hitung["ar"], hitung["la"], hitung["id"]}
                if len(sedikit) != 1 or 0 in sedikit:
                    temuan.append(f"{tag}: jumlah paragraf Arab/Latin/Indonesia tidak sama {hitung}")
        persen = 100.0 * ada / jml if jml else 0.0
        ringkasan.append(f"{b['berkas']}: {len(b['halaman'])} halaman, kata Arab berharakat {ada}/{jml} ({persen:.1f}%)")
        if persen < 95.0:
            temuan.append(f"{b['berkas']}: cakupan harakat {persen:.1f}% < 95%")
    return temuan, ringkasan


# --------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bangun Edisi Panel (preview.html, PDF, TERJEMAHAN*.md) dari BATCH_*.md")
    ap.add_argument("--cek", action="store_true", help="hanya periksa mutu, tanpa membangun")
    ap.add_argument("--tanpa-pdf", action="store_true", help="lewati pembuatan PDF")
    ap.add_argument("--akar", default=str(ROOT), help="folder repo (bawaan: induk tools/)")
    args = ap.parse_args(argv)
    akar = Path(args.akar)
    try:
        batches = muat_batch(akar)
    except (ValueError, OSError) as exc:
        print(f"GALAT: {exc}", file=sys.stderr)
        return 2
    if not batches:
        print("GALAT: tidak ada BATCH_NN.md di " + str(akar), file=sys.stderr)
        return 2
    temuan, ringkasan = periksa(batches, akar)
    for r in ringkasan:
        print("  " + r)
    for t in temuan:
        print("  TEMUAN:", t)
    if args.cek:
        print("PEMERIKSAAN: " + ("ada temuan" if temuan else "bersih"))
        return 1 if temuan else 0
    nama = nama_pdf(batches)
    (akar / "TERJEMAHAN.md").write_text(ke_markdown(batches, False), encoding="utf-8")
    (akar / "TERJEMAHAN_MATAN_MURNI.md").write_text(ke_markdown(batches, True), encoding="utf-8")
    print("  ditulis: TERJEMAHAN.md, TERJEMAHAN_MATAN_MURNI.md")
    if not args.tanpa_pdf:
        for lama in akar.glob("MASTER_PANEL_Batch_*.pdf"):
            if lama.name != nama:
                lama.unlink()
        try:
            n = bangun_pdf(batches, akar / nama)
        except ImportError:
            print("GALAT: PyMuPDF belum terpasang (pip install -r requirements.txt)", file=sys.stderr)
            return 2
        print(f"  ditulis: {nama} ({n} halaman, {(akar / nama).stat().st_size // 1024} KB)")
    (akar / "preview.html").write_text(render_preview(batches, None if args.tanpa_pdf else nama), encoding="utf-8")
    print("  ditulis: preview.html")
    return 1 if temuan else 0


if __name__ == "__main__":
    sys.exit(main())
