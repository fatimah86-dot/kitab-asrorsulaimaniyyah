# PANDUAN KAMUS SURYANI META - RUJUKAN WAJIB BATCH 41++

> **CATATAN LINGKUNGAN (Arena, 2026-10-06) — baca dulu.**
> **Kamus 799 baris LENGKAP sudah masuk.** `terjemahan/KAMUS_SURYANI_META.json` kini berisi
> **799 entri** (bukan 78) — diambil dari gist pengguna `2b0cc3bc…` lewat API GitHub, ditulis dengan
> format 5 kolom persis seperti xlsx asli: Arab (Asli) | Arab Berharokat (Sesuai Latin) | Latin (Bacaan) |
> Makna / Terjemahan Indonesia | Keterangan / Referensi. Verifikasi: `wc -l` = **799**,
> `jq length` = **799**. Isi entri tidak diubah — hanya penulannya satu objek per baris agar
> satu baris = satu entri.
> **Konsekuensi untuk aturan no. 1:** keempat contoh Ism Suryani **sudah ada** di berkas — HAYYA (#62),
> الْوْحًا (Latin: `ALUHAN`, #326 — dieja ALUHAN di kamus, bukan ALUHAAN), حَاجَ طَخُوْجَ dan rantai
> Ism Azimah (#443–449), هَيَالٍ (#317). Riwayat singkat: perintah `cp /mnt/data/...` dan lampiran
> attachment gagal (3x) — berkas akhirnya masuk via gist. Rincian di "Catatan lingkungan — rincian" bawah.

Sumber: KAMUS_SURYANI_META.json 799 baris
Format: Arab (Asli) | Arab Berharokat (Sesuai Latin) | Latin (Bacaan) | Makna / Terjemahan Indonesia | Keterangan / Referensi

## Aturan pakai (sama kayak Asraru Sulaimaniyyah 17.2 MB 382 hal):

1. Kalau di Picture 102-104 ketemu Ism Suryani (contoh: هَيّا, الْوْحًا, حَاجَ طَخُوْجَ, هَيَالٍ), jangan tebak. Cari di KAMUS_SURYANI_META.json kolom Latin (Bacaan) - sudah ada transliterasi washal: HAYYA, ALUHAAN, HAAJA THOKHUUJA, HAYALIN.

2. Makna: pakai kolom Makna / Terjemahan Indonesia. Contoh:
   - HAYYA = Segeralah / ayo cepat (Ism fi'il amr Suryani)
   - ALUHAAN = Segera / cepat (Suryani) - ta'jil
   - Kalau tidak ada makna (masih misteri), tulis: Ism Suryani - [Latin] - makna dirahasiakan dalam cetakan (sama kayak PR #19: Tujuh nama berbahasa suryani)

3. 3 Hukum Washal tetap:
   - Hukum 1 Washal Harakat: Bismillaahir-Rahmaanir-Rahiim (sambung)
   - Hukum 2 Washal Tanwin & Idgham: fil-'uluumir-ruuhaaniyyah
   - Hukum 3 Washal Waqaf: tepi melengkung Picture 099-101 jangan dipotong jadi kolom

4. Rajah: kalau di Hal 200-204 ternyata ada wafaq (Batch 40 bilang belum cetak sampai Hal 199), cek Picture 102-104 perbesaran 2,4x. Kalau ada, simpan ke assets/ dengan nama BATCH-41-RAJAH-XX.png, kumulatif 167 -> 168+

5. Catatan tashih: lanjutkan no. 39+ (Batch 40 total 38). Pertentangan 7x (Hal 195 vs 196) sudah no.11 - jangan diseragamkan.

---

## Catatan lingkungan — rincian (Arena, 2026-10-06)

### 1. Status berkas kamus

| Butir | Nilai |
|---|---|
| Perintah asli | `cp /mnt/data/KAMUS_SURYANI_META.json terjemahan/KAMUS_SURYANI_META.json` |
| Hasil | **BERHASIL via gist** — `cp` dari `/mnt/data` gagal (direktori kosong), attachment gagal 3x, isi akhirnya diambil dari gist pengguna `2b0cc3bc216c8c6c74652c2fa6a22179` lewat API GitHub (gist secret; raw URL kena blokir SSL dari sandbox) |
| Isi repo sekarang | `terjemahan/KAMUS_SURYANI_META.json` = **799 entri**, format 5 kolom: Arab (Asli) \| Arab Berharokat (Sesuai Latin) \| Latin (Bacaan) \| Makna / Terjemahan Indonesia \| Keterangan / Referensi |
| Verifikasi | `wc -l` = 799 · `jq length` = 799 · `json.load` OK · kolom konsisten di semua entri |
| Sumber isi | Gist pengguna (KAMUS_SURYANI_META.json, 213.900 byte), isi entri tidak diubah — hanya diformat satu objek per baris |
| Commit | `63c988c` "KAMUS FULL 799 FIX VALID - bukan 78 - acuan Batch 41 Hal 200-204 Qasam Ammari Kabir - 3 hukum washal + nahwu shorof" |

Catatan QA: 0 sel kolom kosong; 13 Latin muncul dua kali (mis. `AL-HAQQI`, `KADZA WA KADZA`) — dipertahankan apa adanya karena itu data kamus pengguna, bukan duplikat penyuntingan.

### 2. Konsekuensi untuk aturan no. 1

Keempat contoh Ism Suryani pada aturan no. 1 **sudah terdapat** di berkas 799 entri:

| Contoh | Entri | Latin (Bacaan) | Makna |
|---|---|---|---|
| هَيّا | #62 | `HAYYA` | Segeralah / ayo cepat — Ism fi'il amr Suryani |
| الْوْحًا | #326 | `ALUHAN` | Segera / cepat (Suryani) — ta'jil. **Dieja `ALUHAN` (satu A) di kamus, bukan `ALUHAAN`** |
| حَاجَ طَخُوْجَ | #443–449 | `HAAJA / HAAJJ`, `THOKHUUJA`, `THOORIJA / TAARIJA`, `THORKHUUJA`, `THOLAJA`, `THOLUUHIN`, `AKHNUUJ` | Ism Azimah Suryani (rantai, satu entri per kata) |
| هَيَالٍ | #317 | `HAYALIN HAYALIN` | (diikuti `SAYALIN SAYALIN` #318, `MAYALIN MAYALIN` #319) |

Pelengkap lain yang juga sudah masuk: `WA BARHAMUUTSAA` (#102), `WA SYAIMUUTSAA` (#103) — Ism Ibrani/Suryani.

### 3. Cara mengganti dengan kamus 799 baris

**Sudah terlaksana** (2026-10-06): berkas 799 baris dari gist pengguna menggantikan subset 78 entri
(`63c988c`). Kalau kelak ada revisi kamus: kirim URL gist baru (sebagai teks polos, jangan dalam
perintah — perintah kena strip platform) atau paste isinya; berkas akan ditimpa dan catatan ini
diperbarui. Angka "799" pada baris *Sumber* di atas sekarang **berlakukan** untuk berkas di repo.

### 4. Lokasi repo

Perintah `cd asoro-wa-khofiyyat-fi-ilmu-ruhaniyyah` tidak bisa dijalankan: direktori itu tidak ada di
sandbox. Isi panduan ini merujuk proyek **ini** — repo `kitab-asrorsulaimaniyyah`
(الأسرار السليمانية في العلوم الروحانية; `KHATAM_TERJEMAHAN_Kitab_Asraru_Sulaimaniyyah.pdf` = 17,2 MB,
382 hal, cocok dengan "17.2 MB 382 hal" di judul aturan). Karena itu berkas ditaruh di `terjemahan/`
pada akar repo ini.

### 5. Git

`git push origin main` **tidak dijalankan**: sesi Arena ini terikat ke cabang
`arena/35d9a6d7-kitab-asrorsulaimaniyyah`. Commit dan push dilakukan ke cabang itu saja; PR bisa
dibuka dari cabang ini bila ingin digabungkan ke `main`.
