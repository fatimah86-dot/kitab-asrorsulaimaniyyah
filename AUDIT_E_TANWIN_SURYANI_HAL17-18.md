# AUDIT E — Tanwin -in pada kunci doa Suryani/Ibrani (Kartu Panel hal. 17–18)

> Status: **DITERAPKAN (keputusan pengguna: opsi b + c)** — 62 kunci Suryani pada BATCH_02.md:102/108/112 diberi tanwin kasrah ـٍ / akhiran *-in*,
> termasuk يَهْ ×6 → Yahin, هُورِينْ/هُولَايِينْ/مَايْتُوتْ, 4 seruan pendek (آهْ آهْ بِهْ نْ), dan koreksi salah baca أَشْسَخْ → **أَشْمَخٍ / Asymakhin** (alif cetak dipertahankan).
> Butir «Ali Syadayya» diperiksa: sudah benar di 2 tempat, tidak diubah. Turunan dibangun ulang dengan `tools/bangun_panel.py --tanpa-pdf`.
> Tanggal audit: 2026-10-05 · Tanggal penerapan: 2026-10-06

## 1. Lokasi

| Rujukan | Nilai |
|---|---|
| Kartu Panel (`MASTER_PANEL_Batch_01-35.pdf`) | Halaman **17–18** dari 409 |
| Batch | **BATCH_02.md** — Halaman PDF 7 (= cetak 6) |
| Bagian | **Bagian 2 — Seruan dengan nama-nama tersimpan dan nama-nama malaikat** |
| Baris | Arab `BATCH_02.md:102` · Latin `BATCH_02.md:108` · Terjemah `BATCH_02.md:112` |
| Salinan turunan | `TERJEMAHAN.md`, `TERJEMAHAN_MATAN_MURNI.md`, `preview.html`, PDF panel (dibangun ulang dari BATCH) |

Catatan dasar: cetakan asli (`kitab/asrorul-sulaimaniyah.pdf` hal. 7) **gundul/tanpa harakat** — sukun maupun tanwin pada
nama Suryani semuanya tambahan penyunting AI. Jadi sukun yang ada sekarang bukan "bacaan cetak", melainkan pilihan editorial
yang boleh dinormalisasi ke tanwin kasrah bila kaidah wirid memang begitu.

## 2. Saksi internal tanwin kasrah ـٍ (sudah ada di repo)

| Saksi Arab | Latin di repo | Lokasi | Keterangan |
|---|---|---|---|
| **العَالِي عَلَى كُلِّ بَرَّاخٍ** | *'alaa kulli barraakhin* | BATCH_09.md:33 / :73 (PDF 41) | **Frasa identik** dengan BATCH_02 «العَالِي عَلَى كُلٍّ بَرَاخْ / kull Barakh» → saksi langsung untuk *Baraakhin* |
| **بِحَقِّ شَمَاخٍ وَأَشْمَخَ** | — (nazham) | BATCH_26.md:103 (PDF 84) | Kata **sama persis** dengan شَمَاخْ BATCH_02 → *Syamaakhin*; juga saksi bahwa kata ketiga seharusnya **أَشْمَخ** |
| كَذَا بَاشْمَخَ وضِيَاءُ شُمَاخَ | *Baasyamakha … Syumaakha* | BATCH_09.md:31 / :71 | Saksi ejaan اشمخ (bukan اشسخ) |
| بِشَنْخٍ شُمُوخٍ شَايِخٍ | — | BATCH_29.md:163; BATCH_23.md:21,149 | Pola prefiks *bi-* + nama berakhir ـٍ → saksi *Bisyamakhin* |
| بَنُوخٍ | — | BATCH_29.md:165 | Saksi akhiran ـوخٍ → *Nuukhin*, *Baarukhin* |
| بِهَشْكَاخٍ هِشْكَاخِ | — | BATCH_10.md:429 | Pola pasangan nama + tanwin kasrah |
| لِيَارُوشٍ | — | BATCH_21.md:84, :206 | Nama Suryani berakhir ـٍ |
| يَا هِيًا شَرًا هِيًا | *Yaa Hiyan Syaraa Hiyan* | BATCH_02.md:102 (baris yang sama) | Tanwin **sudah dipakai** pada nama Suryani di awal kunci ini — hanya nama-nama berikutnya yang masih sukun |
| `"Yahin": 4` / `latin_cepat: "Yahin Yahin"` | — | KAMUS_SURYANI_HAROKAT_LATIN.json:40,142 | Kamus sudah menetapkan **Yahin** sebagai bentuk baku, tetapi Arabnya di BATCH_02:102 masih **وَيَاهْ** (sukun) — tidak sinkron |

## 3. Tiga puluh token pertama yang perlu tanwin -in (urut sesuai teks)

Idx = nomor urut token Arab pada `BATCH_02.md:102` (0-based, 211 token). Kolom "Arab sekarang / Latin sekarang" = kondisi
repo saat ini (belum diubah). Kolom usulan hanya untuk ditinjau.

| No | Idx | Arab sekarang (sukun) | Latin sekarang | Usulan Latin (-in) | Usulan Arab (ـٍ) | Saksi / catatan |
|---|---|---|---|---|---|---|
| 1 | 14 | وَيَاهْ | wa Yahin wa Yahin | wa Yahin | وَيَاهٍ | Latin sudah -in, **Arab belum**; cetak hanya **1×** «وياه», Latin & terjemah menulis 2× → perlu diputuskan |
| 2 | 21 | شَلِّيمْ | Syallim | Syallimin | شَلِّيمٍ | — |
| 3 | 22 | نَمُوَاهْ | Namuwaah | Namuwaahin | نَمُوَاهٍ | — |
| 4 | 23 | نَمُوَاهْ | Namuwaah | Namuwaahin | نَمُوَاهٍ | — |
| 5 | 25 | هِيَاهْ | Hiyaah | Hiyaahin | هِيَاهٍ | — |
| 6 | 32 | نُوخْ | Nuukh | Nuukhin | نُوخٍ | بَنُوخٍ (BATCH_29:165) |
| 7 | 34 | هِيَهْ | Hiyah | Hiyahin | هِيَهٍ | — |
| 8 | 35 | نَمُوهْ | namuh | Namuuhin | نَمُوهٍ | Latin sekarang juga kehilangan panjang *uu* |
| 9 | 36 | نَمُوهْ | namuh | Namuuhin | نَمُوهٍ | idem |
| 10 | 52 | صَفْفَصْ | shaffash | Shaffashin | صَفْفَصٍ | — |
| 11 | 53 | صَصْ | shash | Shashin | صَصٍ | — |
| 12 | 66 | شَمَخْ | **Syamakh** | **Syamakhin** | شَمَخٍ | شَمَاخٍ (BATCH_26:103) — contoh laporan pengguna |
| 13 | 119 | هُورِينْ | Huuriin | Huuriinin (?) | هُورِينٍ | Berakhir nun asli; bentuk *-iinin* perlu konfirmasi pengguna |
| 14 | 120 | بَارُوخْ | **Baarukh** | **Baarukhin** | بَارُوخٍ | بَنُوخٍ (pola ـوخٍ) — contoh laporan pengguna |
| 15 | 121 | أَشْسَخْ | **Asyakh** | **Asymakhin** | **أَشْمَخٍ** | ⚠️ Cetak terbaca **اشمخ** (bukan اشسخ); saksi وَأَشْمَخَ (BATCH_26:103), بَاشْمَخَ (BATCH_09:31). Latin "Asyakh" juga kehilangan satu huruf |
| 16 | 122 | شَمَاخْ | **Syamaakh** | **Syamaakhin** | شَمَاخٍ | **شَمَاخٍ** (BATCH_26:103) — identik |
| 17 | 126 | بَرَاخْ | **Barakh** | **Baraakhin** | بَرَاخٍ | **بَرَّاخٍ / barraakhin** (BATCH_09:33,73) — frasa identik «العالي على كل براخ» |
| 18 | 127 | طَنْطِيشْ | Thanthiisy | Thanthiisyin | طَنْطِيشٍ | — |
| 19 | 128 | شَفَشْ | Syafasy | Syafasyin | شَفَشٍ | — |
| 20 | 129 | أَكْرَاكُوكْ | Akraakuuk | Akraakuukin | أَكْرَاكُوكٍ | — |
| 21 | 136 | هَابُوتَرَاخْ | Haabuutarakh | Haabuutaraakhin | هَابُوتَرَاخٍ | Latin sekarang kehilangan *aa* pada suku akhir |
| 22 | 137 | بَخْ | bakh | Bakhin | بَخٍ | — |
| 23 | 138 | بِعَالَمْ | bi-'aalam | Bi'aalamin | بِعَالَمٍ | Bisa juga kata Arab (بِعَالَمِ …) — perlu keputusan |
| 24 | 145 | بِشَمَخْ | bisyamakh | Bisyamakhin | بِشَمَخٍ | بِشَنْخٍ (BATCH_23:21; BATCH_29:163) pola *bi-* + ـٍ |
| 25 | 150 | هُولَايِينْ | Huulaayiin | Huulaayiinin (?) | هُولَايِينٍ | Nun asli — konfirmasi seperti no. 13 |
| 26 | 152 | قَطْ | qath | Qathin | قَطٍ | — |
| 27 | 153 | قَطْ | qath | Qathin | قَطٍ | — |
| 28 | 160 | هُورَصْ | Huurash | Huurashin | هُورَصٍ | — |
| 29 | 161 | هُوغَانْ | Huughaan | Huughaanin | هُوغَانٍ | — |
| 30 | 166 | مَايْتُوتْ | Maayuut | Maaytuutin | مَايْتُوتٍ | Latin sekarang kehilangan **ت** |

## 4. Sisa token sukun pada bagian yang sama (di luar 30 pertama)

Nama/kunci (28): شَمُوتْ، شَتَمُوتْ، بِمَصُورَشْ، صَصْ، مِيصْ، تَهَيْمَصْ، صَصْ، صَمْصُومَهْ، هُوتَاهْ، فَثْطَلِيسْ، مَيْطَطْرُونْ،
**يَهْ ×6** (Latin: *Yah Yah Yah Yah Yah Yah* → usulan **Yahin ×6**, contoh laporan pengguna), بِيهْ (*Biyah* → *Biyahin*),
أُورِيَالْ، بِرَخْيَالْ، هُورِيَالْ، شُورِيَالْ، رَغْشِيَالْ، هُورِيَالْ، لَهْفَيَالْ، بَرْقِيَالْ، نُورِيَالْ، عَشْيَالْ.

Seruan pendek (4) — **perlu keputusan** apakah ikut kaidah -in: آهْ (idx 24), آهْ (29), بِهْ (30), نْ (37).

Kata Arab berakhir sukun yang **tidak** termasuk kaidah (5): تَلَأْلَأْ، مِنْ ×2، لَوْ، لَتَسَاقَطَتْ.

Rekap: 211 token · 67 berakhir sukun · 62 kunci Suryani (30 tabel + 28 sisa + 4 seruan pendek) · 5 kata Arab.

## 5. Temuan sampingan (jangan diubah sebelum dikonfirmasi)

1. **أَشْسَخْ → أَشْمَخْ**: zoom pindaian hal. 7 baris «الروح لتساقطت رؤوس الملائكة الكروبيين هورين باروخ **اشمخ** شماخ»
   jelas memakai م; dua saksi internal (BATCH_09:31, BATCH_26:103) juga أشمخ. Latin "Asyakh" ikut salah.
2. **وَيَاهْ** cetak 1×, tetapi Latin/terjemah menulis "wa Yahin wa Yahin" (2×) — salah satu perlu disamakan.
3. Latin yang kehilangan huruf/panjang: *Maayuut* (مَايْتُوتْ), *namuh* (نَمُوهْ), *Haabuutarakh* (هَابُوتَرَاخْ).
4. Kolom **Terjemahan** (`BATCH_02.md:112`) menyalin ulang nama-nama Latin (Hurin Barukh Asyakh Syamakh … Yah Yah …);
   bila -in diterapkan, baris ini dan kamus (`KAMUS_SURYANI_*`) harus ikut, lalu TERJEMAHAN*.md / preview.html / PDF panel
   dibangun ulang (`tools/bangun_panel.py`).
