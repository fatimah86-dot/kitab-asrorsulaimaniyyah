#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDIT F — Scan global tanwin kasrah (*-in*) pada nama Suryani/Ibrani, BATCH_01..BATCH_35.

Keluaran : AUDIT_F_GLOBAL_TANWIN_SURYANI_[01-35].md  (di akar repo)
Pemakaian: python3 tools/audit_f_tanwin_suryani.py

Tiga lapis penanda nama (semuanya dinyatakan di berkas hasil, tidak ada kurasi tersembunyi):
  L1  tercatat kamus  : skeleton token cocok satu kata pada 78 entri
                        KAMUS_SURYANI_HAROKAT_LATIN.json (prefiks ب/و/ف/ل/ك/ال dilepas)
  L2  pola malaikat   : skeleton berakhiran يال / يائل / يائيل / ييل
  L3  di luar kamus   : token pada "baris rantai" yang skeletonnya tidak muncul >= 2x
                        di baris non-rantai (kosakata Arab proxy)

Baris rantai = baris teks Arab (bukan blok syarah '>', bukan baris tabel '|', kutipan
Qur'an ﴿...﴾ dibuang) yang memenuhi A atau B:
  A  memuat >= 2 token L1/L2
  B  memuat >= 3 token berakhiran sukun/kasratan yang hapax (muncul 1x sekorpus)
     dengan rasio hapax/berakhiran >= 0.45

Bagian nazham/bait (heading memuat nazham|larik|bait|syair — praktis BATCH_08..34)
dihitung terpisah sebagai Cakupan B dan TIDAK diusulkan berubah: pada bait, akhiran
kata terikat qafiyah/wazan, bukan pilihan editorial seperti pada prosa wirid.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAMUS = os.path.join(ROOT, "KAMUS_SURYANI_HAROKAT_LATIN.json")
KELUAR = os.path.join(ROOT, "AUDIT_F_GLOBAL_TANWIN_SURYANI_[01-35].md")

KASRATAN = "\u064d"
FATHATAN = "\u064b"
DAMMATAN = "\u064c"
SUKUN = "\u0652"
DIAC = set("\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0640\u0653\u0654\u0655\u0656")
TOK = re.compile(r"[\u0620-\u065f\u0670-\u0674\u0640]+")
QURAN = re.compile(r"﴿[^﴾]*﴾")
PREFIX = ["بال", "وال", "فال", "كال", "لل", "ال", "ب", "و", "ف", "ل", "ك", "با", "أ"]
NAZHAM = re.compile(r"nazham|larik|bait|syair", re.I)

# Kata Arab biasa yang skeleton-nya ikut tertulis di dalam entri rantai/leksikon kamus,
# atau muncul sebagai rangka kalimat pada baris rantai. Daftar ini hasil telaah manual
# atas daftar kandidat (§5 berkas hasil); sengaja terbuka di sini supaya bisa diaudit.
STOP_ARAB = {
    # dari entri kamus
    "على", "ما", "هو", "هذا", "وهذا", "بحق", "رب", "الملائكة", "هي", "قدوس", "جل",
    "آل", "والروح", "الجلب", "نجا", "أرى", "يرون", "نرم", "حفا", "سلمة", "تعداد",
    "جبروت", "السرياني",
    # rangka kalimat pada baris rantai prosa (kurasi manual)
    "لو", "أمرتكم", "أمرتمكم", "أمرتهم", "أنذرتهم", "أأنذرتهم", "بعالم", "فيكم", "إقليم", "آثارهم", "آذانهم", "أدبارهم", "أعناقكم",
    "أنفسهم", "بجمعكم", "بصغاركم", "بكم", "بربكم", "اصعق", "تعاهدتم", "تظلكم",
    "تقلكم", "حاضر", "حضوركم", "خصم", "ذرياتهم", "رواية", "ظهورهم", "عاهدتم",
    "فاغشيناهم", "فاحفظ", "فاستدع", "فتكلم", "قضيت", "قلوبهم", "كلكم", "كاف",
    "لتساقطت", "لحظة", "لهم", "لجاهل", "صرت", "عليكم", "وعليكم", "وعن", "وكباركم",
    "وأشهدهم", "وإذ", "وانفخ", "وتكلم", "وخصمكم", "يعرض", "أجبتم", "تلالأ", "واه",
    "أم", "هه", "مهل", "بشطور", "خلقهم", "اخضع", "عشير", "كيس", "بعود", "ميعه",
    "وميعه", "بقول", "بفعل", "بسوء", "غد", "متمرد", "بتون", "سلت", "صدت", "اسودت",
    "فردهم", "صراط", "مستقيم", "اباؤهم", "اكثرهم", "كم", "صابر", "متعال",
    "انذرتهم", "ازل", "يزل", "امرهم", "انفهم", "ايديهم", "امام", "انظر", "بكاف",
    "بمغفرة", "تنذرهم", "خلفهم", "دعوتهم", "ربهم", "سنة", "صاد", "ظاهر", "عاد",
    "عزة", "علم", "فهم", "كلهم", "لقد", "مبين", "محرز", "منهم", "هبطتم", "هم",
    "واثرهم", "واثارهم", "واجر", "وسلط", "يتخذ",
}
# Status namanya belum bisa diputuskan otomatis -> §6, tidak dihitung.
RAGU = {"شُطُورٍ", "بِشُطُورٍ", "عَجَجْ", "خَطَّافْ", "طَايِفْ", "أَجْجِبْ", "أَحْمَدْ"}
ALASAN_RAGU = {
    "شُطُورٍ": "Bisa pola *bi-* + nama (bishuturin) atau kata Arab *syuthuur*; konteks `BATCH_02.md:128` bercampur rangka Arab.",
    "بِشُطُورٍ": "Satu rangkaian dengan baris di atas.",
    "عَجَجْ": "Bisa nama rantai (bersanding عَشَعْ) atau kata Arab *'ajaj* (debu/riuh).",
    "خَطَّافْ": "Di rantai murni `BATCH_04.md:170` berpola nama, tetapi identik dengan kata Arab *khaththaaf*.",
    "طَايِفْ": "Sama: di rantai `BATCH_04.md:170`, tetapi identik dengan kata Arab *thaa-if*.",
    "أَجْجِبْ": "Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah).",
    "أَحْمَدْ": "Di rantai `BATCH_02.md:200` (إِلِي أَحْمَدْ رِيخْ): bisa nama Arab «Ahmad» yang tersisip, bisa unsur nama Suryani.",
}


HAMZAH = {"\u0623": "\u0627", "\u0625": "\u0627", "\u0622": "\u0627", "\u0671": "\u0627",
          "\u0629": "\u0647", "\u0649": "\u064a"}


def skel(kata: str) -> str:
    """Kerangka konsonan: harakat dibuang, hamzah/ta marbuthah/alif maqshurah dinormalisasi."""
    out = []
    for c in unicodedata.normalize("NFC", kata):
        if c in DIAC:
            continue
        out.append(HAMZAH.get(c, c))
    return "".join(out)


STOP_ARAB = {skel(x) for x in STOP_ARAB}


def muat_lexicon():
    with open(KAMUS, encoding="utf-8") as fh:
        kamus = json.load(fh)
    lex = {}
    for e in kamus["entri"]:
        for k in ("arab_gundul", "arab_harokat"):
            v = e.get(k)
            if not v:
                continue
            for w in v.split():
                s = skel(w).rstrip(":،.")
                if len(s) >= 2 and s not in STOP_ARAB:
                    lex.setdefault(s, set()).add(e["no"])
    return kamus, lex


def cocok_kamus(s: str, lex):
    for p in sorted(PREFIX, key=len, reverse=True) + [""]:
        if s.startswith(p) and s[len(p):] in lex:
            return s[len(p):]
    return None


def pola_malaikat(s: str) -> bool:
    return s.endswith(("يال", "يائل", "يائيل", "ييل"))


def peta_heading(lines):
    h, cur = {}, ""
    for i, l in enumerate(lines, 1):
        if l.startswith("#"):
            cur = l.strip()
        h[i] = cur
    return h


def pakai(line):
    """Baris yang ikut dipindai: bukan syarah, bukan baris tabel."""
    s = line.lstrip()
    return not (s.startswith(">") or s.startswith("|"))


def main():
    kamus, lex = muat_lexicon()
    berkas = sorted(glob.glob(os.path.join(ROOT, "BATCH_*.md")))
    data = {os.path.basename(f): open(f, encoding="utf-8").read().split("\n") for f in berkas}
    head = {f: peta_heading(lines) for f, lines in data.items()}

    def tok(line):
        return TOK.findall(QURAN.sub(" ", line))

    def akhiran(t):
        return t.endswith(KASRATAN) or t.endswith(SUKUN)

    # frekuensi skeleton sekorpus (untuk kosakata proxy + hapax)
    frek = collections.Counter()
    for lines in data.values():
        for l in lines:
            frek.update(skel(t) for t in tok(l))

    def n_l1l2(line):
        return sum(1 for t in tok(line)
                   if cocok_kamus(skel(t), lex) or pola_malaikat(skel(t)))

    # --- pisahkan baris prosa vs nazham -------------------------------------
    rantai, nazham_lines = set(), set()
    for f, lines in data.items():
        for i, line in enumerate(lines, 1):
            if not pakai(line) or not tok(line):
                continue
            if NAZHAM.search(head[f][i]):
                nazham_lines.add((f, i))
                continue
            akh = [t for t in tok(line) if akhiran(t)]
            hapax = [t for t in akh if frek[skel(t)] == 1]
            detA = n_l1l2(line) >= 2
            detB = len(hapax) >= 3 and len(akh) and len(hapax) / len(akh) >= 0.45
            if detA or detB:
                rantai.add((f, i))

    # --- kosakata Arab proxy: skeleton pada baris biasa (bukan rantai, bukan nazham)
    prosa = collections.Counter()
    for f, lines in data.items():
        for i, line in enumerate(lines, 1):
            if (f, i) in rantai or (f, i) in nazham_lines or not pakai(line):
                continue
            prosa.update(skel(t) for t in tok(line))

    # --- saksi: token ber-kasratan di seluruh repo --------------------------
    saksi = collections.defaultdict(list)
    for f, lines in data.items():
        for i, line in enumerate(lines, 1):
            for t in tok(line):
                if t.endswith(KASRATAN):
                    saksi[skel(t)].append((f, i, t))

    def ter_stop(s, dalam=0):
        """True bila skeleton — atau bentuknya setelah prefiks dilepas (maks. 2 lapis,
        mis. وَبِصَادٍ -> و+ب+صاد) — tercatat di STOP_ARAB."""
        if s in STOP_ARAB:
            return True
        if dalam >= 2:
            return False
        for p in sorted(PREFIX, key=len, reverse=True):
            if s.startswith(p) and ter_stop(s[len(p):], dalam + 1):
                return True
        return False

    def lapis(t):
        s = skel(t)
        if ter_stop(s):
            return None, None
        if t in RAGU:
            return "ragu", None
        k = cocok_kamus(s, lex)
        if k:
            return "L1", k
        if pola_malaikat(s):
            return "L2", None
        if prosa[s] >= 2:
            return None, None
        return "L3", None

    def kumpul(himpunan):
        out = []
        for f, i in sorted(himpunan):
            for t in tok(data[f][i - 1]):
                if not akhiran(t):
                    continue
                lp, sk = lapis(t)
                if not lp:
                    continue
                sk = sk or skel(t)
                sks = [x for x in saksi.get(sk, []) if (x[0], x[1]) != (f, i)]
                out.append(dict(berkas=f, baris=i, token=t, lapis=lp,
                                akhir="tanwin" if t.endswith(KASRATAN) else "sukun",
                                skeleton=sk, saksi=sks[:3],
                                usulan=t[:-1] + KASRATAN if t.endswith(SUKUN) else t))
        return out

    occ = kumpul(rantai)
    nama = [o for o in occ if o["lapis"] != "ragu"]
    ragu = [o for o in occ if o["lapis"] == "ragu"]
    sudah = [o for o in nama if o["akhir"] == "tanwin"]
    kandidat = [o for o in nama if o["akhir"] == "sukun"]

    # --- Cakupan B: nama L1/L2 di bagian nazham -----------------------------
    naz = kumpul(nazham_lines)
    naz_nama = [o for o in naz if o["lapis"] in ("L1", "L2")]

    # --- pembanding global --------------------------------------------------
    seluruh = collections.Counter()
    l1_kasrat_seluruh = 0
    for f, lines in data.items():
        for line in lines:
            for t in tok(line):
                if t.endswith(KASRATAN):
                    if cocok_kamus(skel(t), lex):
                        l1_kasrat_seluruh += 1
    for lines in data.values():
        for l in lines:
            seluruh["kasrat"] += l.count(KASRATAN)
            seluruh["fathat"] += l.count(FATHATAN)
            seluruh["dammat"] += l.count(DAMMATAN)

    per_batch = collections.OrderedDict()
    for f in sorted(data):
        per_batch[f] = dict(
            sudah=sum(1 for o in sudah if o["berkas"] == f),
            kandidat=sum(1 for o in kandidat if o["berkas"] == f),
            naz=sum(1 for o in naz_nama if o["berkas"] == f),
            naz_sukun=sum(1 for o in naz_nama if o["berkas"] == f and o["akhir"] == "sukun"),
            kasrat=sum(l.count(KASRATAN) for l in data[f]),
            fathat=sum(l.count(FATHATAN) for l in data[f]),
            dammat=sum(l.count(DAMMATAN) for l in data[f]),
            rantai=sorted(i for (ff, i) in rantai if ff == f),
            nazham=len([i for (ff, i) in nazham_lines if ff == f]),
        )

    tulis(kamus, per_batch, sudah, kandidat, ragu, naz_nama, rantai, nazham_lines,
          seluruh, l1_kasrat_seluruh)

    print(f"baris rantai (prosa)     : {len(rantai)}  di {len({f for f, _ in rantai})} batch")
    print(f"baris nazham dipindai    : {len(nazham_lines)}")
    print(f"nama sudah tanwin ٍ      : {len(sudah)}")
    print(f"nama masih sukun ْ        : {len(kandidat)}")
    print(f"TOTAL kemunculan (A)     : {len(nama)}   (+ragu {len(ragu)})")
    print(f"token unik               : {len({o['token'] for o in nama})}")
    print(f"Cakupan B (nazham, L1/L2): {len(naz_nama)}  (sukun {sum(1 for o in naz_nama if o['akhir'] == 'sukun')})")
    print(f"berkas                   : {KELUAR}")


def tulis(kamus, per_batch, sudah, kandidat, ragu, naz_nama, rantai, nazham_lines,
          seluruh, l1_kasrat_seluruh):
    tot = len(sudah) + len(kandidat)
    L, w = [], None
    w = L.append
    w("# AUDIT F — Scan global tanwin kasrah (*-in*) pada nama Suryani/Ibrani, BATCH_01–35")
    w("")
    w("> **Status: AUDIT SAJA — belum ada satu pun teks yang diubah.**")
    w("> Lanjutan `AUDIT_E_TANWIN_SURYANI_HAL17-18.md` (62 kunci di `BATCH_02.md:102/108/112` sudah diberi tanwin kasrah);")
    w("> berkas ini memperluas pemindaian ke seluruh 35 batch.")
    w(">")
    w(f"> ### Hasil hitung: **{tot} kemunculan** nama Suryani/Ibrani pada {len(rantai)} baris rantai prosa")
    w(f"> **{len(sudah)}** sudah berharakat tanwin kasrah **ـٍ** (sesuai kaidah *‑in*) · "
      f"**{len(kandidat)}** masih berharakat sukun **ْ** (kandidat dinormalisasi ke ـٍ).")
    w(f"> Ditambah **{len(ragu)}** kemunculan berstatus *ragu* yang sengaja tidak dihitung (§6), dan "
      f"**{len(naz_nama)}** kemunculan nama di bagian nazham yang dikecualikan (§7).")
    w(">")
    w("> Angka **113** yang pernah disebut sebagai \"rekap global\" **tidak berhasil direproduksi** oleh definisi")
    w("> mana pun yang tersedia di repo ini — seluruh angka pembanding yang terukur ada di §8.")
    w(f"> Tanggal audit: 2026-10-06 · Pembangkit: `tools/audit_f_tanwin_suryani.py` · "
      f"Lexicon: `KAMUS_SURYANI_HAROKAT_LATIN.json` ({len(kamus['entri'])} entri)")
    w("")
    w("## 1. Definisi operasional")
    w("")
    w("Tiga lapis penanda nama:")
    w("")
    w("| Lapis | Kriteria | Sumber |")
    w("|---|---|---|")
    w("| **L1 — tercatat kamus** | skeleton token (harakat dibuang) cocok satu kata pada entri kamus; prefiks ب/و/ف/ل/ك/ال dilepas | `KAMUS_SURYANI_HAROKAT_LATIN.json` |")
    w("| **L2 — pola malaikat** | skeleton berakhiran ‎‑يال / ‑يائل / ‑يائيل / ‑ييل (mis. أُورِيَال، بِرَخْيَال، كَلْمِيَائِيل) | pola nama *‑iiyaal* |")
    w("| **L3 — di luar kamus** | token baris rantai yang skeletonnya tidak muncul ≥2× di baris non-rantai (kosakata Arab proxy) dan tidak masuk `STOP_ARAB` | korpus BATCH_01–35 |")
    w("")
    w("**Baris rantai** = baris teks Arab yang memenuhi A atau B:")
    w("")
    w("- **A** — memuat ≥2 token L1/L2;")
    w("- **B** — memuat ≥3 token berakhiran sukun/kasratan yang *hapax* (muncul 1× sekorpus), rasio hapax ≥0,45.")
    w("")
    n_batch_rantai = len({f for f, _ in rantai})
    w(f"Hasil: **{len(rantai)} baris rantai** (§3) dari {n_batch_rantai} batch. "
      "Yang dikecualikan dari pemindaian, beserta alasannya:")
    w("")
    w("| Dikecualikan | Alasan |")
    w("|---|---|")
    w("| Blok syarah (baris `>`) | Teks penjelasan penyunting berbahasa Indonesia, bukan teks wirid |")
    w("| Baris tabel (baris `\\|`) | Indeks/rubrik (mis. `BATCH_35.md:301`) menyebut nama sebagai kutipan, bukan wirid |")
    w("| Kutipan Qur'an ﴿…﴾ | Ayat; harakatnya qath'i, bukan pilihan editorial |")
    w("| Bagian nazham/bait | Akhiran kata terikat qafiyah & wazan — dihitung terpisah di §7 |")
    w("")
    w("Kandidat audit hanya token berakhiran **sukun ْ** atau **tanwin kasrah ـٍ**: dua akhiran inilah yang terikat")
    w("kaidah *‑in*. Nama berakhiran fathah/dammah/alif (طَيْمُوثَا، بَطِيثَا، شَمْلَا) adalah keadaan *emphatic*")
    w("Aram ‑aa/‑uu dan di luar cakupan normalisasi ini.")
    w("")
    w("## 2. Rekap per batch")
    w("")
    w("| Batch | Sudah ـٍ | Masih ْ | Jumlah (A) | Baris rantai | Nama di nazham (B) | ٍ/ً/ٌ seluruh batch |")
    w("|---|---:|---:|---:|---|---:|---|")
    for f, d in per_batch.items():
        rb = ", ".join(str(i) for i in d["rantai"]) or "—"
        nz = f"{d['naz']}" if d["naz"] else ("—" if not d["nazham"] else "0")
        w(f"| `{f}` | {d['sudah']} | {d['kandidat']} | {d['sudah'] + d['kandidat']} | {rb} | {nz} | "
          f"{d['kasrat']} / {d['fathat']} / {d['dammat']} |")
    w(f"| **TOTAL** | **{len(sudah)}** | **{len(kandidat)}** | **{tot}** | **{len(rantai)} baris** | "
      f"**{len(naz_nama)}** | **{seluruh['kasrat']} / {seluruh['fathat']} / {seluruh['dammat']}** |")
    w("")
    w("## 3. Nama yang MASIH berharakat sukun ْ — kandidat tanwin kasrah (*-in*)")
    w("")
    w(f"**{len(kandidat)} kemunculan.** *Saksi* = token berskeleton sama yang **sudah** berharakat ـٍ di tempat lain")
    w("dalam repo (saksi internal, pola yang sama dengan AUDIT E §2). *Tanpa saksi* = normalisasi perlu keputusan")
    w("penyunting, bukan sekadar penyeragaman.")
    w("")
    w("| # | Lokasi | Token sekarang | Lapis | Usulan Arab | Saksi internal ـٍ |")
    w("|---:|---|---|:--:|---|---|")
    for n, o in enumerate(sorted(kandidat, key=lambda x: (x["berkas"], x["baris"])), 1):
        sks = "; ".join(f"`{a}:{b}` {c}" for a, b, c in o["saksi"]) or "*tanpa saksi*"
        w(f"| {n} | `{o['berkas']}:{o['baris']}` | {o['token']} | {o['lapis']} | **{o['usulan']}** | {sks} |")
    w("")
    w("## 4. Lokasi baris rantai")
    w("")
    w("| Batch | Baris |")
    w("|---|---|")
    for f, d in per_batch.items():
        if d["rantai"]:
            w(f"| `{f}` | " + ", ".join(f"`{i}`" for i in d["rantai"]) + " |")
    w("")
    w("## 5. Nama yang SUDAH berharakat tanwin kasrah ـٍ (pembanding, tidak diubah)")
    w("")
    w(f"**{len(sudah)} kemunculan.**")
    w("")
    w("| # | Lokasi | Token | Lapis |")
    w("|---:|---|---|:--:|")
    for n, o in enumerate(sorted(sudah, key=lambda x: (x["berkas"], x["baris"])), 1):
        w(f"| {n} | `{o['berkas']}:{o['baris']}` | {o['token']} | {o['lapis']} |")
    w("")
    w("## 6. Status *ragu* — tidak dihitung, perlu keputusan penyunting")
    w("")
    w("| Lokasi | Token | Alasan ragu |")
    w("|---|---|---|")
    for o in sorted(ragu, key=lambda x: (x["berkas"], x["baris"])):
        w(f"| `{o['berkas']}:{o['baris']}` | {o['token']} | {ALASAN_RAGU.get(o['token'], '—')} |")
    w("")
    w("## 7. Bagian nazham/bait — dihitung, tidak diusulkan berubah")
    w("")
    w(f"Bagian nazham mencakup **{len(nazham_lines)} baris** (heading memuat *nazham/larik/bait*; praktis "
      "`BATCH_08`–`BATCH_34`). Di dalamnya terdapat "
      f"**{len(naz_nama)} kemunculan** nama L1/L2 berakhiran sukun atau tanwin kasrah "
      f"({sum(1 for o in naz_nama if o['akhir'] == 'sukun')} sukun, "
      f"{sum(1 for o in naz_nama if o['akhir'] == 'tanwin')} tanwin).")
    w("")
    w("Alasan tidak diusulkan berubah: pada bait, harakat akhir kata ditentukan **qafiyah** (sajak akhir) dan")
    w("wazan larik, sehingga mengganti ْ menjadi ٍ akan merusak sajak — berbeda dari prosa wirid, tempat akhiran")
    w("nama memang pilihan editorial. Daftar lengkap:")
    w("")
    w("| Lokasi | Token | Akhir | Lapis |")
    w("|---|---|:--:|:--:|")
    for o in sorted(naz_nama, key=lambda x: (x["berkas"], x["baris"])):
        w(f"| `{o['berkas']}:{o['baris']}` | {o['token']} | {'ـٍ' if o['akhir'] == 'tanwin' else 'ْ'} | {o['lapis']} |")
    w("")
    w("## 8. Angka pembanding — mengapa 113 tidak dipakai")
    w("")
    w("| Definisi yang diukur | Hasil |")
    w("|---|---:|")
    w(f"| Semua tanda tanwin (ٍ + ً + ٌ) di BATCH_01–35 | {seluruh['kasrat'] + seluruh['fathat'] + seluruh['dammat']} |")
    w(f"| Semua tanwin kasrah ٍ di BATCH_01–35 | {seluruh['kasrat']} |")
    w(f"| Semua tanwin fathah ً / dammah ٌ di BATCH_01–35 | {seluruh['fathat']} / {seluruh['dammat']} |")
    w(f"| Token ٍ yang skeletonnya cocok L1/kamus di seluruh repo | {l1_kasrat_seluruh} |")
    w(f"| Nama (L1+L2+L3) berakhiran ـٍ atau ْ pada baris rantai prosa | **{tot}** |")
    w(f"| — sudah ـٍ | {len(sudah)} |")
    w(f"| — masih ْ | {len(kandidat)} |")
    w(f"| Token nama unik (bukan kemunculan) | {len({o['token'] for o in sudah + kandidat})} |")
    w(f"| Nama L1/L2 di bagian nazham | {len(naz_nama)} |")
    w("")
    w("Tidak satu pun definisi di atas menghasilkan 113, sehingga angka itu tidak dipakai sebagai dasar.")
    w("")
    w("## 9. Menjalankan ulang")
    w("")
    w("```bash")
    w("python3 tools/audit_f_tanwin_suryani.py")
    w("```")
    w("")
    w("Skrip menulis ulang berkas ini dari `BATCH_*.md` + `KAMUS_SURYANI_HAROKAT_LATIN.json`.")
    w("`STOP_ARAB` (stoplist kata Arab) dan `RAGU` dinyatakan terbuka di bagian atas skrip agar kurasi dapat diaudit.")
    w("")
    with open(KELUAR, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
