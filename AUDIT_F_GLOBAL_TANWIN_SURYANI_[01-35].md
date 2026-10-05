# AUDIT F — Scan global tanwin kasrah (*-in*) pada nama Suryani/Ibrani, BATCH_01–35

> **Status: AUDIT SAJA — belum ada satu pun teks yang diubah.**
> Lanjutan `AUDIT_E_TANWIN_SURYANI_HAL17-18.md` (62 kunci di `BATCH_02.md:102/108/112` sudah diberi tanwin kasrah);
> berkas ini memperluas pemindaian ke seluruh 35 batch.
>
> ### Hasil hitung: **305 kemunculan** nama Suryani/Ibrani pada 33 baris rantai prosa
> **60** sudah berharakat tanwin kasrah **ـٍ** (sesuai kaidah *‑in*) · **245** masih berharakat sukun **ْ** (kandidat dinormalisasi ke ـٍ).
> Ditambah **15** kemunculan berstatus *ragu* yang sengaja tidak dihitung (§6), dan **15** kemunculan nama di bagian nazham yang dikecualikan (§7).
>
> Angka **113** yang pernah disebut sebagai "rekap global" **tidak berhasil direproduksi** oleh definisi
> mana pun yang tersedia di repo ini — seluruh angka pembanding yang terukur ada di §8.
> Tanggal audit: 2026-10-06 · Pembangkit: `tools/audit_f_tanwin_suryani.py` · Lexicon: `KAMUS_SURYANI_HAROKAT_LATIN.json` (78 entri)

## 1. Definisi operasional

Tiga lapis penanda nama:

| Lapis | Kriteria | Sumber |
|---|---|---|
| **L1 — tercatat kamus** | skeleton token (harakat dibuang) cocok satu kata pada entri kamus; prefiks ب/و/ف/ل/ك/ال dilepas | `KAMUS_SURYANI_HAROKAT_LATIN.json` |
| **L2 — pola malaikat** | skeleton berakhiran ‎‑يال / ‑يائل / ‑يائيل / ‑ييل (mis. أُورِيَال، بِرَخْيَال، كَلْمِيَائِيل) | pola nama *‑iiyaal* |
| **L3 — di luar kamus** | token baris rantai yang skeletonnya tidak muncul ≥2× di baris non-rantai (kosakata Arab proxy) dan tidak masuk `STOP_ARAB` | korpus BATCH_01–35 |

**Baris rantai** = baris teks Arab yang memenuhi A atau B:

- **A** — memuat ≥2 token L1/L2;
- **B** — memuat ≥3 token berakhiran sukun/kasratan yang *hapax* (muncul 1× sekorpus), rasio hapax ≥0,45.

Hasil: **33 baris rantai** (§3) dari 9 batch. Yang dikecualikan dari pemindaian, beserta alasannya:

| Dikecualikan | Alasan |
|---|---|
| Blok syarah (baris `>`) | Teks penjelasan penyunting berbahasa Indonesia, bukan teks wirid |
| Baris tabel (baris `\|`) | Indeks/rubrik (mis. `BATCH_35.md:301`) menyebut nama sebagai kutipan, bukan wirid |
| Kutipan Qur'an ﴿…﴾ | Ayat; harakatnya qath'i, bukan pilihan editorial |
| Bagian nazham/bait | Akhiran kata terikat qafiyah & wazan — dihitung terpisah di §7 |

Kandidat audit hanya token berakhiran **sukun ْ** atau **tanwin kasrah ـٍ**: dua akhiran inilah yang terikat
kaidah *‑in*. Nama berakhiran fathah/dammah/alif (طَيْمُوثَا، بَطِيثَا، شَمْلَا) adalah keadaan *emphatic*
Aram ‑aa/‑uu dan di luar cakupan normalisasi ini.

## 2. Rekap per batch

| Batch | Sudah ـٍ | Masih ْ | Jumlah (A) | Baris rantai | Nama di nazham (B) | ٍ/ً/ٌ seluruh batch |
|---|---:|---:|---:|---|---:|---|
| `BATCH_01.md` | 0 | 13 | 13 | 181, 263 | — | 20 / 15 / 10 |
| `BATCH_02.md` | 59 | 64 | 123 | 102, 128, 168, 200, 290, 318 | — | 84 / 10 / 10 |
| `BATCH_03.md` | 0 | 12 | 12 | 60, 88, 246 | — | 37 / 16 / 16 |
| `BATCH_04.md` | 0 | 127 | 127 | 66, 144, 170, 188, 206, 228, 274 | — | 24 / 8 / 25 |
| `BATCH_05.md` | 0 | 0 | 0 | 128, 232, 262, 340 | — | 19 / 36 / 28 |
| `BATCH_06.md` | 0 | 0 | 0 | 26, 234 | 0 | 56 / 19 / 22 |
| `BATCH_07.md` | 0 | 23 | 23 | 200, 330 | — | 47 / 7 / 18 |
| `BATCH_08.md` | 0 | 2 | 2 | 26, 44, 62, 272 | 0 | 26 / 30 / 24 |
| `BATCH_09.md` | 1 | 4 | 5 | 417, 453, 475 | 3 | 12 / 11 / 6 |
| `BATCH_10.md` | 0 | 0 | 0 | — | 9 | 49 / 18 / 1 |
| `BATCH_11.md` | 0 | 0 | 0 | — | 0 | 26 / 10 / 8 |
| `BATCH_12.md` | 0 | 0 | 0 | — | 0 | 19 / 17 / 17 |
| `BATCH_13.md` | 0 | 0 | 0 | — | 0 | 57 / 18 / 8 |
| `BATCH_14.md` | 0 | 0 | 0 | — | 0 | 29 / 29 / 20 |
| `BATCH_15.md` | 0 | 0 | 0 | — | 0 | 20 / 3 / 0 |
| `BATCH_16.md` | 0 | 0 | 0 | — | 0 | 12 / 4 / 0 |
| `BATCH_17.md` | 0 | 0 | 0 | — | 0 | 13 / 8 / 0 |
| `BATCH_18.md` | 0 | 0 | 0 | — | 0 | 6 / 3 / 0 |
| `BATCH_19.md` | 0 | 0 | 0 | — | 0 | 10 / 11 / 0 |
| `BATCH_20.md` | 0 | 0 | 0 | — | 0 | 17 / 22 / 14 |
| `BATCH_21.md` | 0 | 0 | 0 | — | 0 | 3 / 5 / 1 |
| `BATCH_22.md` | 0 | 0 | 0 | — | 0 | 7 / 5 / 5 |
| `BATCH_23.md` | 0 | 0 | 0 | — | 0 | 16 / 6 / 6 |
| `BATCH_24.md` | 0 | 0 | 0 | — | 0 | 8 / 6 / 4 |
| `BATCH_25.md` | 0 | 0 | 0 | — | 0 | 10 / 12 / 2 |
| `BATCH_26.md` | 0 | 0 | 0 | — | 3 | 13 / 17 / 2 |
| `BATCH_27.md` | 0 | 0 | 0 | — | 0 | 18 / 10 / 4 |
| `BATCH_28.md` | 0 | 0 | 0 | — | 0 | 8 / 16 / 0 |
| `BATCH_29.md` | 0 | 0 | 0 | — | 0 | 11 / 2 / 0 |
| `BATCH_30.md` | 0 | 0 | 0 | — | 0 | 5 / 2 / 3 |
| `BATCH_31.md` | 0 | 0 | 0 | — | 0 | 14 / 1 / 1 |
| `BATCH_32.md` | 0 | 0 | 0 | — | 0 | 6 / 2 / 4 |
| `BATCH_33.md` | 0 | 0 | 0 | — | 0 | 6 / 3 / 0 |
| `BATCH_34.md` | 0 | 0 | 0 | — | 0 | 4 / 4 / 2 |
| `BATCH_35.md` | 0 | 0 | 0 | — | — | 26 / 30 / 15 |
| **TOTAL** | **60** | **245** | **305** | **33 baris** | **15** | **738 / 416 / 276** |

## 3. Nama yang MASIH berharakat sukun ْ — kandidat tanwin kasrah (*-in*)

**245 kemunculan.** *Saksi* = token berskeleton sama yang **sudah** berharakat ـٍ di tempat lain
dalam repo (saksi internal, pola yang sama dengan AUDIT E §2). *Tanpa saksi* = normalisasi perlu keputusan
penyunting, bukan sekadar penyeragaman.

| # | Lokasi | Token sekarang | Lapis | Usulan Arab | Saksi internal ـٍ |
|---:|---|---|:--:|---|---|
| 1 | `BATCH_01.md:181` | طَشْ | L3 | **طَشٍ** | *tanpa saksi* |
| 2 | `BATCH_01.md:181` | طَشْ | L3 | **طَشٍ** | *tanpa saksi* |
| 3 | `BATCH_01.md:181` | طَشْطْ | L3 | **طَشْطٍ** | *tanpa saksi* |
| 4 | `BATCH_01.md:181` | طَشَهْ | L3 | **طَشَهٍ** | *tanpa saksi* |
| 5 | `BATCH_01.md:181` | يُوهَنِيطْ | L3 | **يُوهَنِيطٍ** | *tanpa saksi* |
| 6 | `BATCH_01.md:181` | هُومِيَاطْ | L3 | **هُومِيَاطٍ** | *tanpa saksi* |
| 7 | `BATCH_01.md:181` | هُوثَاوُطْ | L3 | **هُوثَاوُطٍ** | *tanpa saksi* |
| 8 | `BATCH_01.md:263` | شُوِينْ | L3 | **شُوِينٍ** | *tanpa saksi* |
| 9 | `BATCH_01.md:263` | كُنُوفِشْ | L3 | **كُنُوفِشٍ** | *tanpa saksi* |
| 10 | `BATCH_01.md:263` | لُونِيمْ | L3 | **لُونِيمٍ** | *tanpa saksi* |
| 11 | `BATCH_01.md:263` | كِيلِيمْ | L3 | **كِيلِيمٍ** | *tanpa saksi* |
| 12 | `BATCH_01.md:263` | يَعْطِيشْ | L3 | **يَعْطِيشٍ** | *tanpa saksi* |
| 13 | `BATCH_01.md:263` | بَالَهْ | L3 | **بَالَهٍ** | *tanpa saksi* |
| 14 | `BATCH_02.md:128` | غَشْيَالْ | L2 | **غَشْيَالٍ** | *tanpa saksi* |
| 15 | `BATCH_02.md:128` | هَدْرِيَالْ | L2 | **هَدْرِيَالٍ** | *tanpa saksi* |
| 16 | `BATCH_02.md:128` | لَهْفَيَالْ | L2 | **لَهْفَيَالٍ** | `BATCH_02.md:102` لَهْفَيَالٍ |
| 17 | `BATCH_02.md:128` | بَرْقِيَالْ | L2 | **بَرْقِيَالٍ** | `BATCH_02.md:102` بَرْقِيَالٍ |
| 18 | `BATCH_02.md:128` | نُورِيَالْ | L2 | **نُورِيَالٍ** | `BATCH_02.md:102` نُورِيَالٍ |
| 19 | `BATCH_02.md:128` | عَشْيَالْ | L2 | **عَشْيَالٍ** | `BATCH_02.md:102` عَشْيَالٍ |
| 20 | `BATCH_02.md:128` | غَشْيَالْ | L2 | **غَشْيَالٍ** | *tanpa saksi* |
| 21 | `BATCH_02.md:128` | فَلَايَالْ | L2 | **فَلَايَالٍ** | *tanpa saksi* |
| 22 | `BATCH_02.md:128` | تِرْيَالْ | L2 | **تِرْيَالٍ** | *tanpa saksi* |
| 23 | `BATCH_02.md:128` | سَرْحِيَالْ | L2 | **سَرْحِيَالٍ** | *tanpa saksi* |
| 24 | `BATCH_02.md:128` | شُوصَهْ | L3 | **شُوصَهٍ** | *tanpa saksi* |
| 25 | `BATCH_02.md:128` | شَرَمَهْ | L3 | **شَرَمَهٍ** | *tanpa saksi* |
| 26 | `BATCH_02.md:168` | عَلْمَهَشَاشَقْ | L3 | **عَلْمَهَشَاشَقٍ** | *tanpa saksi* |
| 27 | `BATCH_02.md:168` | آثْيَالَغْ | L3 | **آثْيَالَغٍ** | *tanpa saksi* |
| 28 | `BATCH_02.md:168` | عَشَعْ | L3 | **عَشَعٍ** | *tanpa saksi* |
| 29 | `BATCH_02.md:168` | أَشْطِيغْ | L3 | **أَشْطِيغٍ** | *tanpa saksi* |
| 30 | `BATCH_02.md:168` | عَسَعْ | L3 | **عَسَعٍ** | *tanpa saksi* |
| 31 | `BATCH_02.md:168` | أَشْطِيغْ | L3 | **أَشْطِيغٍ** | *tanpa saksi* |
| 32 | `BATCH_02.md:168` | مِيخْ | L3 | **مِيخٍ** | *tanpa saksi* |
| 33 | `BATCH_02.md:168` | عَلِيبَاخْ | L3 | **عَلِيبَاخٍ** | *tanpa saksi* |
| 34 | `BATCH_02.md:168` | مَلِيخْ | L3 | **مَلِيخٍ** | *tanpa saksi* |
| 35 | `BATCH_02.md:168` | شَلْمِيثْ | L3 | **شَلْمِيثٍ** | *tanpa saksi* |
| 36 | `BATCH_02.md:168` | قُمُوَارَشْ | L3 | **قُمُوَارَشٍ** | *tanpa saksi* |
| 37 | `BATCH_02.md:168` | هَلَهْنُوشْ | L3 | **هَلَهْنُوشٍ** | *tanpa saksi* |
| 38 | `BATCH_02.md:168` | شَمْلَهُوشْ | L3 | **شَمْلَهُوشٍ** | *tanpa saksi* |
| 39 | `BATCH_02.md:168` | صَعْطَفْ | L3 | **صَعْطَفٍ** | *tanpa saksi* |
| 40 | `BATCH_02.md:168` | طَطِيفْ | L3 | **طَطِيفٍ** | *tanpa saksi* |
| 41 | `BATCH_02.md:168` | عَيْقَقَنْ | L3 | **عَيْقَقَنٍ** | *tanpa saksi* |
| 42 | `BATCH_02.md:168` | مِشْصَرْ | L3 | **مِشْصَرٍ** | *tanpa saksi* |
| 43 | `BATCH_02.md:168` | نُوفِيلْ | L3 | **نُوفِيلٍ** | *tanpa saksi* |
| 44 | `BATCH_02.md:168` | بَرِيهُوثْ | L3 | **بَرِيهُوثٍ** | *tanpa saksi* |
| 45 | `BATCH_02.md:168` | دَيْفُوبْ | L3 | **دَيْفُوبٍ** | *tanpa saksi* |
| 46 | `BATCH_02.md:168` | طَنْطَفِيغْ | L3 | **طَنْطَفِيغٍ** | *tanpa saksi* |
| 47 | `BATCH_02.md:168` | اقْهُوشْ | L3 | **اقْهُوشٍ** | *tanpa saksi* |
| 48 | `BATCH_02.md:168` | شَمَايِخْ | L3 | **شَمَايِخٍ** | *tanpa saksi* |
| 49 | `BATCH_02.md:168` | عَطْلَايَاخْ | L3 | **عَطْلَايَاخٍ** | *tanpa saksi* |
| 50 | `BATCH_02.md:168` | شَمْلَخْ | L3 | **شَمْلَخٍ** | *tanpa saksi* |
| 51 | `BATCH_02.md:168` | فَطِيخْ | L3 | **فَطِيخٍ** | *tanpa saksi* |
| 52 | `BATCH_02.md:168` | شَاهَهْنِيكْ | L3 | **شَاهَهْنِيكٍ** | *tanpa saksi* |
| 53 | `BATCH_02.md:168` | بِقُيُورَشْ | L3 | **بِقُيُورَشٍ** | *tanpa saksi* |
| 54 | `BATCH_02.md:168` | طَحِيطْمَفِيلْيَالْ | L2 | **طَحِيطْمَفِيلْيَالٍ** | *tanpa saksi* |
| 55 | `BATCH_02.md:168` | طَحِيطْمَفِيلْيَالْ | L2 | **طَحِيطْمَفِيلْيَالٍ** | *tanpa saksi* |
| 56 | `BATCH_02.md:168` | مَيْطَطْرُونْ | L1 | **مَيْطَطْرُونٍ** | `BATCH_02.md:102` مَيْطَطْرُونٍ |
| 57 | `BATCH_02.md:200` | زَحَاجْ | L3 | **زَحَاجٍ** | *tanpa saksi* |
| 58 | `BATCH_02.md:200` | رِيخْ | L3 | **رِيخٍ** | *tanpa saksi* |
| 59 | `BATCH_02.md:200` | الطُّودْ | L3 | **الطُّودٍ** | *tanpa saksi* |
| 60 | `BATCH_02.md:200` | طُودْ | L3 | **طُودٍ** | *tanpa saksi* |
| 61 | `BATCH_02.md:200` | أَطَلْ | L3 | **أَطَلٍ** | *tanpa saksi* |
| 62 | `BATCH_02.md:200` | يَالَغْ | L3 | **يَالَغٍ** | *tanpa saksi* |
| 63 | `BATCH_02.md:200` | شَمْ | L3 | **شَمٍ** | *tanpa saksi* |
| 64 | `BATCH_02.md:200` | بِيغْ | L3 | **بِيغٍ** | *tanpa saksi* |
| 65 | `BATCH_02.md:200` | رَقَشْ | L3 | **رَقَشٍ** | *tanpa saksi* |
| 66 | `BATCH_02.md:200` | يَادَهْ | L3 | **يَادَهٍ** | *tanpa saksi* |
| 67 | `BATCH_02.md:200` | شَامِينْ | L3 | **شَامِينٍ** | *tanpa saksi* |
| 68 | `BATCH_02.md:200` | اكْبِنْ | L3 | **اكْبِنٍ** | *tanpa saksi* |
| 69 | `BATCH_02.md:318` | الفَرْقَشْ | L3 | **الفَرْقَشٍ** | *tanpa saksi* |
| 70 | `BATCH_02.md:318` | هَامُورْ | L3 | **هَامُورٍ** | *tanpa saksi* |
| 71 | `BATCH_02.md:318` | أَسَرْ | L3 | **أَسَرٍ** | *tanpa saksi* |
| 72 | `BATCH_02.md:318` | شَخْمَلُوشْ | L3 | **شَخْمَلُوشٍ** | *tanpa saksi* |
| 73 | `BATCH_02.md:318` | طِيشْ | L3 | **طِيشٍ** | *tanpa saksi* |
| 74 | `BATCH_02.md:318` | طِيشِيشْ | L3 | **طِيشِيشٍ** | *tanpa saksi* |
| 75 | `BATCH_02.md:318` | هَعِيشْ | L3 | **هَعِيشٍ** | *tanpa saksi* |
| 76 | `BATCH_02.md:318` | أَرْمِيشْ | L3 | **أَرْمِيشٍ** | *tanpa saksi* |
| 77 | `BATCH_02.md:318` | شَخْمَلُوشْ | L3 | **شَخْمَلُوشٍ** | *tanpa saksi* |
| 78 | `BATCH_03.md:60` | هَفْيَهْ | L3 | **هَفْيَهٍ** | *tanpa saksi* |
| 79 | `BATCH_03.md:60` | ظَهْرَشْ | L3 | **ظَهْرَشٍ** | *tanpa saksi* |
| 80 | `BATCH_03.md:88` | بِهَنْطَشْ | L3 | **بِهَنْطَشٍ** | *tanpa saksi* |
| 81 | `BATCH_03.md:88` | بِكَهْيَصْ | L3 | **بِكَهْيَصٍ** | *tanpa saksi* |
| 82 | `BATCH_03.md:88` | عَشَقْ | L3 | **عَشَقٍ** | *tanpa saksi* |
| 83 | `BATCH_03.md:246` | شَاهْ | L3 | **شَاهٍ** | *tanpa saksi* |
| 84 | `BATCH_03.md:246` | شَاهْ | L3 | **شَاهٍ** | *tanpa saksi* |
| 85 | `BATCH_03.md:246` | اشْ | L3 | **اشٍ** | *tanpa saksi* |
| 86 | `BATCH_03.md:246` | لِيَالْ | L2 | **لِيَالٍ** | *tanpa saksi* |
| 87 | `BATCH_03.md:246` | لِيَالْ | L2 | **لِيَالٍ** | *tanpa saksi* |
| 88 | `BATCH_03.md:246` | حَالِفْ | L3 | **حَالِفٍ** | *tanpa saksi* |
| 89 | `BATCH_03.md:246` | حَالِفْ | L3 | **حَالِفٍ** | *tanpa saksi* |
| 90 | `BATCH_04.md:66` | شَهْشَطُوشْ | L3 | **شَهْشَطُوشٍ** | *tanpa saksi* |
| 91 | `BATCH_04.md:66` | شَطِيطْ | L3 | **شَطِيطٍ** | *tanpa saksi* |
| 92 | `BATCH_04.md:66` | طَفْكُوشْ | L3 | **طَفْكُوشٍ** | *tanpa saksi* |
| 93 | `BATCH_04.md:66` | حَجَجْ | L3 | **حَجَجٍ** | *tanpa saksi* |
| 94 | `BATCH_04.md:66` | كَشْكَشْ | L3 | **كَشْكَشٍ** | *tanpa saksi* |
| 95 | `BATCH_04.md:66` | لِيَعْتُوشْ | L3 | **لِيَعْتُوشٍ** | *tanpa saksi* |
| 96 | `BATCH_04.md:66` | شَهَشْ | L3 | **شَهَشٍ** | *tanpa saksi* |
| 97 | `BATCH_04.md:66` | لِطُوشْ | L3 | **لِطُوشٍ** | *tanpa saksi* |
| 98 | `BATCH_04.md:144` | شَلْشِيشْ | L1 | **شَلْشِيشٍ** | *tanpa saksi* |
| 99 | `BATCH_04.md:144` | شَلْشِيشْ | L1 | **شَلْشِيشٍ** | *tanpa saksi* |
| 100 | `BATCH_04.md:144` | مَلْشِيشْ | L3 | **مَلْشِيشٍ** | *tanpa saksi* |
| 101 | `BATCH_04.md:144` | مَلْشِيشْ | L3 | **مَلْشِيشٍ** | *tanpa saksi* |
| 102 | `BATCH_04.md:144` | أَهِيلِيلْ | L3 | **أَهِيلِيلٍ** | *tanpa saksi* |
| 103 | `BATCH_04.md:144` | أَهِيلِيلْ | L3 | **أَهِيلِيلٍ** | *tanpa saksi* |
| 104 | `BATCH_04.md:144` | هَيْبُولْ | L3 | **هَيْبُولٍ** | *tanpa saksi* |
| 105 | `BATCH_04.md:144` | هَيْبُولْ | L3 | **هَيْبُولٍ** | *tanpa saksi* |
| 106 | `BATCH_04.md:144` | مَلْتِينْ | L3 | **مَلْتِينٍ** | *tanpa saksi* |
| 107 | `BATCH_04.md:144` | مَلْتِينْ | L3 | **مَلْتِينٍ** | *tanpa saksi* |
| 108 | `BATCH_04.md:144` | كَلْكِيَامْ | L3 | **كَلْكِيَامٍ** | *tanpa saksi* |
| 109 | `BATCH_04.md:144` | كَلْكِيَامْ | L3 | **كَلْكِيَامٍ** | *tanpa saksi* |
| 110 | `BATCH_04.md:144` | أَهِيلْ | L3 | **أَهِيلٍ** | *tanpa saksi* |
| 111 | `BATCH_04.md:144` | أَهِيلْ | L3 | **أَهِيلٍ** | *tanpa saksi* |
| 112 | `BATCH_04.md:144` | كَلْكَثُومْ | L3 | **كَلْكَثُومٍ** | *tanpa saksi* |
| 113 | `BATCH_04.md:144` | كَلْكَثُومْ | L3 | **كَلْكَثُومٍ** | *tanpa saksi* |
| 114 | `BATCH_04.md:144` | أَكْيَاهُومْ | L3 | **أَكْيَاهُومٍ** | *tanpa saksi* |
| 115 | `BATCH_04.md:144` | أَكْيَاهُومْ | L3 | **أَكْيَاهُومٍ** | *tanpa saksi* |
| 116 | `BATCH_04.md:144` | كَلْكِيَائِيلْ | L2 | **كَلْكِيَائِيلٍ** | *tanpa saksi* |
| 117 | `BATCH_04.md:144` | كَلْكِيَائِيلْ | L2 | **كَلْكِيَائِيلٍ** | *tanpa saksi* |
| 118 | `BATCH_04.md:144` | بِدَمْلَاخْ | L1 | **بِدَمْلَاخٍ** | *tanpa saksi* |
| 119 | `BATCH_04.md:144` | بَرَاخْ | L1 | **بَرَاخٍ** | `BATCH_02.md:102` بَرَاخٍ; `BATCH_09.md:33` بَرَّاخٍ |
| 120 | `BATCH_04.md:144` | بَرَاخْ | L1 | **بَرَاخٍ** | `BATCH_02.md:102` بَرَاخٍ; `BATCH_09.md:33` بَرَّاخٍ |
| 121 | `BATCH_04.md:144` | هَيْطَيَائِيلْ | L2 | **هَيْطَيَائِيلٍ** | *tanpa saksi* |
| 122 | `BATCH_04.md:144` | هَيْطَيَائِيلْ | L2 | **هَيْطَيَائِيلٍ** | *tanpa saksi* |
| 123 | `BATCH_04.md:144` | أَرْبَابْ | L3 | **أَرْبَابٍ** | *tanpa saksi* |
| 124 | `BATCH_04.md:144` | بِيَارَبْ | L3 | **بِيَارَبٍ** | *tanpa saksi* |
| 125 | `BATCH_04.md:144` | بَهَيْتَنَاخْ | L3 | **بَهَيْتَنَاخٍ** | *tanpa saksi* |
| 126 | `BATCH_04.md:144` | هَيْتَنَاخْ | L3 | **هَيْتَنَاخٍ** | *tanpa saksi* |
| 127 | `BATCH_04.md:144` | مُلْتِيَاهُوخْ | L3 | **مُلْتِيَاهُوخٍ** | *tanpa saksi* |
| 128 | `BATCH_04.md:144` | مُلْتِيَاهُوخْ | L3 | **مُلْتِيَاهُوخٍ** | *tanpa saksi* |
| 129 | `BATCH_04.md:144` | بَاقِطَهْ | L3 | **بَاقِطَهٍ** | *tanpa saksi* |
| 130 | `BATCH_04.md:144` | عَيْطَلَهْ | L3 | **عَيْطَلَهٍ** | *tanpa saksi* |
| 131 | `BATCH_04.md:144` | أَجْرِيَائِيلْ | L2 | **أَجْرِيَائِيلٍ** | *tanpa saksi* |
| 132 | `BATCH_04.md:144` | طَيْلَهُوبْ | L3 | **طَيْلَهُوبٍ** | *tanpa saksi* |
| 133 | `BATCH_04.md:144` | طَيْلَهُوبْ | L3 | **طَيْلَهُوبٍ** | *tanpa saksi* |
| 134 | `BATCH_04.md:144` | طَيْطُوبْ | L3 | **طَيْطُوبٍ** | *tanpa saksi* |
| 135 | `BATCH_04.md:144` | طَيْلَعُوبْ | L3 | **طَيْلَعُوبٍ** | *tanpa saksi* |
| 136 | `BATCH_04.md:144` | هَيْبَاوُطْ | L1 | **هَيْبَاوُطٍ** | *tanpa saksi* |
| 137 | `BATCH_04.md:170` | هَيْبَاوُطْ | L1 | **هَيْبَاوُطٍ** | *tanpa saksi* |
| 138 | `BATCH_04.md:170` | كِيلْيَانَئِيلْ | L1 | **كِيلْيَانَئِيلٍ** | *tanpa saksi* |
| 139 | `BATCH_04.md:170` | كِيلْيَانَئِيلْ | L1 | **كِيلْيَانَئِيلٍ** | *tanpa saksi* |
| 140 | `BATCH_04.md:170` | كَلْمِيَائِيلْ | L1 | **كَلْمِيَائِيلٍ** | *tanpa saksi* |
| 141 | `BATCH_04.md:170` | بِدَمْلَاخْ | L1 | **بِدَمْلَاخٍ** | *tanpa saksi* |
| 142 | `BATCH_04.md:170` | دَمْلَاخْ | L1 | **دَمْلَاخٍ** | *tanpa saksi* |
| 143 | `BATCH_04.md:170` | بَرَاخْ | L1 | **بَرَاخٍ** | `BATCH_02.md:102` بَرَاخٍ; `BATCH_09.md:33` بَرَّاخٍ |
| 144 | `BATCH_04.md:170` | بَرَاخْ | L1 | **بَرَاخٍ** | `BATCH_02.md:102` بَرَاخٍ; `BATCH_09.md:33` بَرَّاخٍ |
| 145 | `BATCH_04.md:170` | بِسْتَطَافْ | L3 | **بِسْتَطَافٍ** | *tanpa saksi* |
| 146 | `BATCH_04.md:170` | سَطَافْ | L3 | **سَطَافٍ** | *tanpa saksi* |
| 147 | `BATCH_04.md:170` | بِصَفِيفْ | L3 | **بِصَفِيفٍ** | *tanpa saksi* |
| 148 | `BATCH_04.md:170` | صَفِيفْ | L3 | **صَفِيفٍ** | *tanpa saksi* |
| 149 | `BATCH_04.md:170` | بِمَطُوفْ | L3 | **بِمَطُوفٍ** | *tanpa saksi* |
| 150 | `BATCH_04.md:170` | مَطُوفْ | L3 | **مَطُوفٍ** | *tanpa saksi* |
| 151 | `BATCH_04.md:170` | شَعْدِيَاشْ | L3 | **شَعْدِيَاشٍ** | *tanpa saksi* |
| 152 | `BATCH_04.md:170` | شَقْدِيَاشْ | L3 | **شَقْدِيَاشٍ** | *tanpa saksi* |
| 153 | `BATCH_04.md:170` | وَرْدِيَاشْ | L3 | **وَرْدِيَاشٍ** | *tanpa saksi* |
| 154 | `BATCH_04.md:170` | شَرْعُونْ | L3 | **شَرْعُونٍ** | *tanpa saksi* |
| 155 | `BATCH_04.md:170` | شَرْعُونْ | L3 | **شَرْعُونٍ** | *tanpa saksi* |
| 156 | `BATCH_04.md:170` | جُوحَشَامْ | L3 | **جُوحَشَامٍ** | *tanpa saksi* |
| 157 | `BATCH_04.md:170` | جُوحَشَامْ | L3 | **جُوحَشَامٍ** | *tanpa saksi* |
| 158 | `BATCH_04.md:170` | بِسُلْطَالِينْ | L3 | **بِسُلْطَالِينٍ** | *tanpa saksi* |
| 159 | `BATCH_04.md:170` | سُلْطَالِينْ | L3 | **سُلْطَالِينٍ** | *tanpa saksi* |
| 160 | `BATCH_04.md:170` | مَهْلُوَانْ | L3 | **مَهْلُوَانٍ** | *tanpa saksi* |
| 161 | `BATCH_04.md:170` | مَهْلُوَانْ | L3 | **مَهْلُوَانٍ** | *tanpa saksi* |
| 162 | `BATCH_04.md:170` | بَابُرُوشْ | L3 | **بَابُرُوشٍ** | *tanpa saksi* |
| 163 | `BATCH_04.md:170` | جَرُوشْ | L3 | **جَرُوشٍ** | *tanpa saksi* |
| 164 | `BATCH_04.md:170` | بِكْلُوشْ | L3 | **بِكْلُوشٍ** | *tanpa saksi* |
| 165 | `BATCH_04.md:170` | كُلُوشْ | L3 | **كُلُوشٍ** | *tanpa saksi* |
| 166 | `BATCH_04.md:170` | بِطَقْشَرْ | L3 | **بِطَقْشَرٍ** | *tanpa saksi* |
| 167 | `BATCH_04.md:170` | طَقْشَرْ | L3 | **طَقْشَرٍ** | *tanpa saksi* |
| 168 | `BATCH_04.md:170` | بِشْلَامِينْ | L3 | **بِشْلَامِينٍ** | *tanpa saksi* |
| 169 | `BATCH_04.md:170` | شْلَامِينْ | L3 | **شْلَامِينٍ** | *tanpa saksi* |
| 170 | `BATCH_04.md:170` | رَطْقَشْ | L3 | **رَطْقَشٍ** | *tanpa saksi* |
| 171 | `BATCH_04.md:170` | رَطْقَشْ | L3 | **رَطْقَشٍ** | *tanpa saksi* |
| 172 | `BATCH_04.md:170` | بِشْلِيمْ | L3 | **بِشْلِيمٍ** | *tanpa saksi* |
| 173 | `BATCH_04.md:170` | شْلِيمْ | L3 | **شْلِيمٍ** | `BATCH_02.md:102` شَلِّيمٍ |
| 174 | `BATCH_04.md:170` | يِيتِلَهْ | L3 | **يِيتِلَهٍ** | *tanpa saksi* |
| 175 | `BATCH_04.md:170` | هَيْتِلَهْ | L3 | **هَيْتِلَهٍ** | *tanpa saksi* |
| 176 | `BATCH_04.md:170` | بِهَنْ | L3 | **بِهَنٍ** | *tanpa saksi* |
| 177 | `BATCH_04.md:170` | هَنْ | L3 | **هَنٍ** | *tanpa saksi* |
| 178 | `BATCH_04.md:170` | بِخَفْ | L3 | **بِخَفٍ** | *tanpa saksi* |
| 179 | `BATCH_04.md:170` | خَفْ | L3 | **خَفٍ** | *tanpa saksi* |
| 180 | `BATCH_04.md:170` | بِشْدِهْ | L3 | **بِشْدِهٍ** | `BATCH_18.md:130` بِشِدَّةٍ |
| 181 | `BATCH_04.md:170` | شْدِهْ | L3 | **شْدِهٍ** | *tanpa saksi* |
| 182 | `BATCH_04.md:170` | بِضَيْفْ | L3 | **بِضَيْفٍ** | *tanpa saksi* |
| 183 | `BATCH_04.md:170` | ضَيْفْ | L3 | **ضَيْفٍ** | *tanpa saksi* |
| 184 | `BATCH_04.md:170` | بِدَلْخَمْ | L3 | **بِدَلْخَمٍ** | *tanpa saksi* |
| 185 | `BATCH_04.md:170` | دَلْخَمْ | L3 | **دَلْخَمٍ** | *tanpa saksi* |
| 186 | `BATCH_04.md:170` | كَشْكَمْ | L3 | **كَشْكَمٍ** | *tanpa saksi* |
| 187 | `BATCH_04.md:170` | كَشْكَمْ | L3 | **كَشْكَمٍ** | *tanpa saksi* |
| 188 | `BATCH_04.md:170` | بِكِشْتَهْ | L3 | **بِكِشْتَهٍ** | *tanpa saksi* |
| 189 | `BATCH_04.md:170` | كِشْتَهْ | L3 | **كِشْتَهٍ** | *tanpa saksi* |
| 190 | `BATCH_04.md:170` | بِعَقْتِهِمْ | L3 | **بِعَقْتِهِمٍ** | *tanpa saksi* |
| 191 | `BATCH_04.md:170` | عَقْتِهِمْ | L3 | **عَقْتِهِمٍ** | *tanpa saksi* |
| 192 | `BATCH_04.md:170` | يُوقْتَمْ | L3 | **يُوقْتَمٍ** | *tanpa saksi* |
| 193 | `BATCH_04.md:170` | يُوقْتَمْ | L3 | **يُوقْتَمٍ** | *tanpa saksi* |
| 194 | `BATCH_04.md:170` | تَقُوفَهْ | L3 | **تَقُوفَهٍ** | *tanpa saksi* |
| 195 | `BATCH_04.md:170` | تَقُوفَهْ | L3 | **تَقُوفَهٍ** | *tanpa saksi* |
| 196 | `BATCH_04.md:170` | دَرْتِيَاوُبْ | L3 | **دَرْتِيَاوُبٍ** | *tanpa saksi* |
| 197 | `BATCH_04.md:170` | دَرْتِيَاوُبْ | L3 | **دَرْتِيَاوُبٍ** | *tanpa saksi* |
| 198 | `BATCH_04.md:188` | الأَرْكِيَاظْ | L1 | **الأَرْكِيَاظٍ** | *tanpa saksi* |
| 199 | `BATCH_04.md:188` | الأَرْكِيَاظْ | L1 | **الأَرْكِيَاظٍ** | *tanpa saksi* |
| 200 | `BATCH_04.md:188` | هَيْبُورْ | L1 | **هَيْبُورٍ** | *tanpa saksi* |
| 201 | `BATCH_04.md:188` | هَيْبُورْ | L1 | **هَيْبُورٍ** | *tanpa saksi* |
| 202 | `BATCH_04.md:188` | كَسْرِيَاوُبْ | L1 | **كَسْرِيَاوُبٍ** | *tanpa saksi* |
| 203 | `BATCH_04.md:188` | كَسْرِيَاوُبْ | L1 | **كَسْرِيَاوُبٍ** | *tanpa saksi* |
| 204 | `BATCH_04.md:188` | عَلْشَقُومْ | L3 | **عَلْشَقُومٍ** | *tanpa saksi* |
| 205 | `BATCH_04.md:188` | عَلْشَقُومْ | L3 | **عَلْشَقُومٍ** | *tanpa saksi* |
| 206 | `BATCH_04.md:188` | عَلْشَافَشْ | L3 | **عَلْشَافَشٍ** | *tanpa saksi* |
| 207 | `BATCH_04.md:188` | عَلْشَافَشْ | L3 | **عَلْشَافَشٍ** | *tanpa saksi* |
| 208 | `BATCH_04.md:188` | مِهْرَاقَشْ | L3 | **مِهْرَاقَشٍ** | *tanpa saksi* |
| 209 | `BATCH_04.md:188` | مِهْرَاقَشْ | L3 | **مِهْرَاقَشٍ** | *tanpa saksi* |
| 210 | `BATCH_04.md:206` | أَقْشَامَقَشْ | L1 | **أَقْشَامَقَشٍ** | *tanpa saksi* |
| 211 | `BATCH_04.md:206` | عَقَشْ | L1 | **عَقَشٍ** | *tanpa saksi* |
| 212 | `BATCH_04.md:206` | طَهْشِيزْ | L1 | **طَهْشِيزٍ** | *tanpa saksi* |
| 213 | `BATCH_04.md:206` | كَشْلَخْ | L3 | **كَشْلَخٍ** | *tanpa saksi* |
| 214 | `BATCH_04.md:206` | قَشْلَمَقَمْشْ | L3 | **قَشْلَمَقَمْشٍ** | *tanpa saksi* |
| 215 | `BATCH_04.md:206` | قَشْلَمَقَمْشْ | L3 | **قَشْلَمَقَمْشٍ** | *tanpa saksi* |
| 216 | `BATCH_04.md:206` | إِيشَايَقَشْ | L3 | **إِيشَايَقَشٍ** | *tanpa saksi* |
| 217 | `BATCH_07.md:330` | شَمْخَابَارُوخْ | L3 | **شَمْخَابَارُوخٍ** | *tanpa saksi* |
| 218 | `BATCH_07.md:330` | شَمْخَابَارُوخْ | L3 | **شَمْخَابَارُوخٍ** | *tanpa saksi* |
| 219 | `BATCH_07.md:330` | كَهْكَهِيجْ | L3 | **كَهْكَهِيجٍ** | *tanpa saksi* |
| 220 | `BATCH_07.md:330` | بِخَطَشْ | L3 | **بِخَطَشٍ** | *tanpa saksi* |
| 221 | `BATCH_07.md:330` | بَلْطَشْغَشْوِيلْ | L3 | **بَلْطَشْغَشْوِيلٍ** | *tanpa saksi* |
| 222 | `BATCH_07.md:330` | أَمُوِيلْ | L3 | **أَمُوِيلٍ** | *tanpa saksi* |
| 223 | `BATCH_07.md:330` | هَجْلِيجْ | L3 | **هَجْلِيجٍ** | *tanpa saksi* |
| 224 | `BATCH_07.md:330` | مَهْجَاجْ | L3 | **مَهْجَاجٍ** | *tanpa saksi* |
| 225 | `BATCH_07.md:330` | بِكَتْمَهْ | L3 | **بِكَتْمَهٍ** | *tanpa saksi* |
| 226 | `BATCH_07.md:330` | بَعْلَشَاقَشْ | L3 | **بَعْلَشَاقَشٍ** | *tanpa saksi* |
| 227 | `BATCH_07.md:330` | بَعْلَشَاقَشْ | L3 | **بَعْلَشَاقَشٍ** | *tanpa saksi* |
| 228 | `BATCH_07.md:330` | مِهْرَاقَشْ | L3 | **مِهْرَاقَشٍ** | *tanpa saksi* |
| 229 | `BATCH_07.md:330` | مِهْرَاقَشْ | L3 | **مِهْرَاقَشٍ** | *tanpa saksi* |
| 230 | `BATCH_07.md:330` | أَقْشَامَقَشْ | L1 | **أَقْشَامَقَشٍ** | *tanpa saksi* |
| 231 | `BATCH_07.md:330` | أَقْشَامَقَشْ | L1 | **أَقْشَامَقَشٍ** | *tanpa saksi* |
| 232 | `BATCH_07.md:330` | شَقْمُونِهَشْ | L3 | **شَقْمُونِهَشٍ** | *tanpa saksi* |
| 233 | `BATCH_07.md:330` | شَقْمُونِهَشْ | L3 | **شَقْمُونِهَشٍ** | *tanpa saksi* |
| 234 | `BATCH_07.md:330` | كَشْلَخْ | L3 | **كَشْلَخٍ** | *tanpa saksi* |
| 235 | `BATCH_07.md:330` | عَكْشْ | L3 | **عَكْشٍ** | *tanpa saksi* |
| 236 | `BATCH_07.md:330` | طَهَشْ | L3 | **طَهَشٍ** | *tanpa saksi* |
| 237 | `BATCH_07.md:330` | أَبْجَدْ | L1 | **أَبْجَدٍ** | *tanpa saksi* |
| 238 | `BATCH_07.md:330` | بَكَدْ | L1 | **بَكَدٍ** | *tanpa saksi* |
| 239 | `BATCH_07.md:330` | زَهَجْ | L1 | **زَهَجٍ** | *tanpa saksi* |
| 240 | `BATCH_08.md:26` | شَمْهَاهِيرْ | L3 | **شَمْهَاهِيرٍ** | *tanpa saksi* |
| 241 | `BATCH_08.md:26` | شَمْهَاهِيرْ | L3 | **شَمْهَاهِيرٍ** | *tanpa saksi* |
| 242 | `BATCH_09.md:453` | هَلْ | L1 | **هَلٍ** | *tanpa saksi* |
| 243 | `BATCH_09.md:453` | صَلْصَلَتْ | L1 | **صَلْصَلَتٍ** | *tanpa saksi* |
| 244 | `BATCH_09.md:475` | كَمَاهْ | L1 | **كَمَاهٍ** | *tanpa saksi* |
| 245 | `BATCH_09.md:475` | أَوَاهْ | L1 | **أَوَاهٍ** | *tanpa saksi* |

## 4. Lokasi baris rantai

| Batch | Baris |
|---|---|
| `BATCH_01.md` | `181`, `263` |
| `BATCH_02.md` | `102`, `128`, `168`, `200`, `290`, `318` |
| `BATCH_03.md` | `60`, `88`, `246` |
| `BATCH_04.md` | `66`, `144`, `170`, `188`, `206`, `228`, `274` |
| `BATCH_05.md` | `128`, `232`, `262`, `340` |
| `BATCH_06.md` | `26`, `234` |
| `BATCH_07.md` | `200`, `330` |
| `BATCH_08.md` | `26`, `44`, `62`, `272` |
| `BATCH_09.md` | `417`, `453`, `475` |

## 5. Nama yang SUDAH berharakat tanwin kasrah ـٍ (pembanding, tidak diubah)

**60 kemunculan.**

| # | Lokasi | Token | Lapis |
|---:|---|---|:--:|
| 1 | `BATCH_02.md:102` | وَيَاهٍ | L3 |
| 2 | `BATCH_02.md:102` | شَلِّيمٍ | L3 |
| 3 | `BATCH_02.md:102` | نَمُوَاهٍ | L3 |
| 4 | `BATCH_02.md:102` | نَمُوَاهٍ | L3 |
| 5 | `BATCH_02.md:102` | آهٍ | L3 |
| 6 | `BATCH_02.md:102` | هِيَاهٍ | L3 |
| 7 | `BATCH_02.md:102` | آهٍ | L3 |
| 8 | `BATCH_02.md:102` | نُوخٍ | L3 |
| 9 | `BATCH_02.md:102` | هِيَهٍ | L3 |
| 10 | `BATCH_02.md:102` | نَمُوهٍ | L3 |
| 11 | `BATCH_02.md:102` | نَمُوهٍ | L3 |
| 12 | `BATCH_02.md:102` | نٍ | L3 |
| 13 | `BATCH_02.md:102` | صَفْفَصٍ | L3 |
| 14 | `BATCH_02.md:102` | صَصٍ | L3 |
| 15 | `BATCH_02.md:102` | شَمَخٍ | L3 |
| 16 | `BATCH_02.md:102` | هُورِينٍ | L3 |
| 17 | `BATCH_02.md:102` | أَشْمَخٍ | L1 |
| 18 | `BATCH_02.md:102` | شَمَاخٍ | L1 |
| 19 | `BATCH_02.md:102` | بَرَاخٍ | L1 |
| 20 | `BATCH_02.md:102` | طَنْطِيشٍ | L3 |
| 21 | `BATCH_02.md:102` | شَفَشٍ | L3 |
| 22 | `BATCH_02.md:102` | أَكْرَاكُوكٍ | L3 |
| 23 | `BATCH_02.md:102` | هَابُوتَرَاخٍ | L3 |
| 24 | `BATCH_02.md:102` | بَخٍ | L3 |
| 25 | `BATCH_02.md:102` | بِشَمَخٍ | L3 |
| 26 | `BATCH_02.md:102` | هُولَايِينٍ | L3 |
| 27 | `BATCH_02.md:102` | قَطٍ | L3 |
| 28 | `BATCH_02.md:102` | قَطٍ | L3 |
| 29 | `BATCH_02.md:102` | هُورَصٍ | L3 |
| 30 | `BATCH_02.md:102` | هُوغَانٍ | L3 |
| 31 | `BATCH_02.md:102` | مَايْتُوتٍ | L3 |
| 32 | `BATCH_02.md:102` | شَمُوتٍ | L3 |
| 33 | `BATCH_02.md:102` | شَتَمُوتٍ | L3 |
| 34 | `BATCH_02.md:102` | بِمَصُورَشٍ | L3 |
| 35 | `BATCH_02.md:102` | صَصٍ | L3 |
| 36 | `BATCH_02.md:102` | مِيصٍ | L3 |
| 37 | `BATCH_02.md:102` | تَهَيْمَصٍ | L3 |
| 38 | `BATCH_02.md:102` | صَصٍ | L3 |
| 39 | `BATCH_02.md:102` | صَمْصُومَهٍ | L3 |
| 40 | `BATCH_02.md:102` | هُوتَاهٍ | L3 |
| 41 | `BATCH_02.md:102` | فَثْطَلِيسٍ | L3 |
| 42 | `BATCH_02.md:102` | مَيْطَطْرُونٍ | L1 |
| 43 | `BATCH_02.md:102` | يَهٍ | L3 |
| 44 | `BATCH_02.md:102` | يَهٍ | L3 |
| 45 | `BATCH_02.md:102` | يَهٍ | L3 |
| 46 | `BATCH_02.md:102` | يَهٍ | L3 |
| 47 | `BATCH_02.md:102` | يَهٍ | L3 |
| 48 | `BATCH_02.md:102` | يَهٍ | L3 |
| 49 | `BATCH_02.md:102` | بِيهٍ | L3 |
| 50 | `BATCH_02.md:102` | أُورِيَالٍ | L2 |
| 51 | `BATCH_02.md:102` | بِرَخْيَالٍ | L2 |
| 52 | `BATCH_02.md:102` | هُورِيَالٍ | L2 |
| 53 | `BATCH_02.md:102` | شُورِيَالٍ | L2 |
| 54 | `BATCH_02.md:102` | رَغْشِيَالٍ | L2 |
| 55 | `BATCH_02.md:102` | هُورِيَالٍ | L2 |
| 56 | `BATCH_02.md:102` | لَهْفَيَالٍ | L2 |
| 57 | `BATCH_02.md:102` | بَرْقِيَالٍ | L2 |
| 58 | `BATCH_02.md:102` | نُورِيَالٍ | L2 |
| 59 | `BATCH_02.md:102` | عَشْيَالٍ | L2 |
| 60 | `BATCH_09.md:475` | تَانٍ | L1 |

## 6. Status *ragu* — tidak dihitung, perlu keputusan penyunting

| Lokasi | Token | Alasan ragu |
|---|---|---|
| `BATCH_02.md:128` | شُطُورٍ | Bisa pola *bi-* + nama (bishuturin) atau kata Arab *syuthuur*; konteks `BATCH_02.md:128` bercampur rangka Arab. |
| `BATCH_02.md:168` | عَجَجْ | Bisa nama rantai (bersanding عَشَعْ) atau kata Arab *'ajaj* (debu/riuh). |
| `BATCH_02.md:168` | عَجَجْ | Bisa nama rantai (bersanding عَشَعْ) atau kata Arab *'ajaj* (debu/riuh). |
| `BATCH_02.md:200` | أَحْمَدْ | Di rantai `BATCH_02.md:200` (إِلِي أَحْمَدْ رِيخْ): bisa nama Arab «Ahmad» yang tersisip, bisa unsur nama Suryani. |
| `BATCH_04.md:170` | خَطَّافْ | Di rantai murni `BATCH_04.md:170` berpola nama, tetapi identik dengan kata Arab *khaththaaf*. |
| `BATCH_04.md:170` | خَطَّافْ | Di rantai murni `BATCH_04.md:170` berpola nama, tetapi identik dengan kata Arab *khaththaaf*. |
| `BATCH_04.md:170` | طَايِفْ | Sama: di rantai `BATCH_04.md:170`, tetapi identik dengan kata Arab *thaa-if*. |
| `BATCH_04.md:170` | طَايِفْ | Sama: di rantai `BATCH_04.md:170`, tetapi identik dengan kata Arab *thaa-if*. |
| `BATCH_08.md:44` | أَجْجِبْ | Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah). |
| `BATCH_08.md:62` | أَجْجِبْ | Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah). |
| `BATCH_08.md:62` | أَجْجِبْ | Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah). |
| `BATCH_08.md:62` | أَجْجِبْ | Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah). |
| `BATCH_08.md:62` | أَجْجِبْ | Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah). |
| `BATCH_08.md:62` | أَجْجِبْ | Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah). |
| `BATCH_08.md:62` | أَجْجِبْ | Di `BATCH_08.md:44` berada dalam deretan nama, tetapi bentuknya identical dengan fi'il amr *ajjib* (jawablah). |

## 7. Bagian nazham/bait — dihitung, tidak diusulkan berubah

Bagian nazham mencakup **1166 baris** (heading memuat *nazham/larik/bait*; praktis `BATCH_08`–`BATCH_34`). Di dalamnya terdapat **15 kemunculan** nama L1/L2 berakhiran sukun atau tanwin kasrah (5 sukun, 10 tanwin).

Alasan tidak diusulkan berubah: pada bait, harakat akhir kata ditentukan **qafiyah** (sajak akhir) dan
wazan larik, sehingga mengganti ْ menjadi ٍ akan merusak sajak — berbeda dari prosa wirid, tempat akhiran
nama memang pilihan editorial. Daftar lengkap:

| Lokasi | Token | Akhir | Lapis |
|---|---|:--:|:--:|
| `BATCH_09.md:33` | بَرَّاخٍ | ـٍ | L1 |
| `BATCH_09.md:503` | بَاجٍ | ـٍ | L1 |
| `BATCH_09.md:509` | بِهَلْ | ْ | L1 |
| `BATCH_10.md:49` | بِطَيْطَفَتْ | ْ | L1 |
| `BATCH_10.md:57` | سَمَتْ | ْ | L1 |
| `BATCH_10.md:59` | بِصَمْصَامٍ | ـٍ | L1 |
| `BATCH_10.md:59` | مِهْرَاشٍ | ـٍ | L1 |
| `BATCH_10.md:61` | بِمَهْرَاشٍ | ـٍ | L1 |
| `BATCH_10.md:287` | حَوْسَمٍ | ـٍ | L1 |
| `BATCH_10.md:315` | أَبْرَامٍ | ـٍ | L1 |
| `BATCH_10.md:417` | نَشْمَخَتْ | ْ | L1 |
| `BATCH_10.md:429` | بِهَشْكَاخٍ | ـٍ | L1 |
| `BATCH_26.md:103` | شَمَاخٍ | ـٍ | L1 |
| `BATCH_26.md:103` | سَمَتْ | ْ | L1 |
| `BATCH_26.md:105` | بِصِمْصَامٍ | ـٍ | L1 |

## 8. Angka pembanding — mengapa 113 tidak dipakai

| Definisi yang diukur | Hasil |
|---|---:|
| Semua tanda tanwin (ٍ + ً + ٌ) di BATCH_01–35 | 1430 |
| Semua tanwin kasrah ٍ di BATCH_01–35 | 738 |
| Semua tanwin fathah ً / dammah ٌ di BATCH_01–35 | 416 / 276 |
| Token ٍ yang skeletonnya cocok L1/kamus di seluruh repo | 15 |
| Nama (L1+L2+L3) berakhiran ـٍ atau ْ pada baris rantai prosa | **305** |
| — sudah ـٍ | 60 |
| — masih ْ | 245 |
| Token nama unik (bukan kemunculan) | 242 |
| Nama L1/L2 di bagian nazham | 15 |

Tidak satu pun definisi di atas menghasilkan 113, sehingga angka itu tidak dipakai sebagai dasar.

## 9. Menjalankan ulang

```bash
python3 tools/audit_f_tanwin_suryani.py
```

Skrip menulis ulang berkas ini dari `BATCH_*.md` + `KAMUS_SURYANI_HAROKAT_LATIN.json`.
`STOP_ARAB` (stoplist kata Arab) dan `RAGU` dinyatakan terbuka di bagian atas skrip agar kurasi dapat diaudit.

