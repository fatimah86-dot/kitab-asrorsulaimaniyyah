# PANDUAN KAMUS SURYANI META - RUJUKAN WAJIB BATCH 41++

> **CATATAN LINGKUNGAN (ditambahkan Arena, 2026-10-06) — baca dulu.**
> Perintah `cp /mnt/data/KAMUS_SURYANI_META.json terjemahan/` **tidak bisa dijalankan** di sandbox ini:
> `/mnt/data` kosong — berkas kamus 799 baris tidak ada di lingkungan Arena, dan tidak ada juga di seluruh
> ref remote (main, PR 1–20, cabang arena). Yang sekarang ada di repo adalah
> `terjemahan/KAMUS_SURYANI_META.json` berisi **78 entri terverifikasi** (bukan 799), disusun ulang dari
> `KAMUS_SURYANI_HAROKAT_LATIN.json` ke format kolom di atas — tanpa entri karangan.
> **Konsekuensi untuk aturan no. 1:** empat contoh Ism Suryani (هَيّا/HAYYA, الْوْحًا/ALUHAAN,
> حَاجَ طَخُوْجَ/HAAJA THOKHUUJA, هَيَالٍ/HAYALIN) **tidak ada** di berkas 78 entri itu. Kalau ketemu di
> batch: jangan tebak, dan jangan pakai berkas repo sebagai dasar menebak — tandai perlu kamus 799 baris.
> Lampirkan (attach) berkas 799 baris di chat untuk menggantinya. Rincian lengkap di bagian
> "Catatan lingkungan — rincian" di bawah.

Sumber: KAMUS_SURYANI_META.json 799 baris
Format: Arab (Asli) | Arab Berharokat (Sesuai Latin) | Latin (Bacaan) | Makna | Keterangan

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
| Hasil | **GAGAL** — `/mnt/data` kosong; berkas 799 baris tidak ada di sandbox, juga tidak di seluruh ref remote |
| Isi repo sekarang | `terjemahan/KAMUS_SURYANI_META.json` = **78 entri terverifikasi** (16 inti akar Ibrani + 57 leksikon Suryani + 5 rantai tanpa makna) |
| Sumber isi | `KAMUS_SURYANI_HAROKAT_LATIN.json` (main `771bc3d`), sudah termasuk `koreksi_2026_10_05` (kolom Latin tabel 2.1 no. 19–31) |
| Kaidah | Sama dengan `KAMUS_SURYANI_ASROR_35_BATCH.md`: hanya entri berrujukan baris repo; tanpa karangan; bentuk cetak dipertahankan |

### 2. Konsekuensi untuk aturan no. 1

Empat contoh Ism Suryani pada aturan no. 1 — **هَيّا (HAYYA)**, **الْوْحًا (ALUHAAN)**,
**حَاجَ طَخُوْجَ (HAAJA THOKHUUJA)**, **هَيَالٍ (HAYALIN)** — **tidak terdapat** di berkas 78 entri.
Kolom Latin (Bacaan) di berkas repo hanya memuat transliterasi washal yang sudah terverifikasi di
BATCH_01–35 (mis. *Yaa Hiyan Syaraa Hiyan Adunayya Ashba-uuti Ali Syadayya … wa Yahin*).
Kalau keempat nama itu muncul di batch: **jangan tebak**, dan jangan pakai berkas repo ini sebagai
alasan menebak — tandai sebagai "perlu kamus 799 baris".

### 3. Cara mengganti dengan kamus 799 baris

Lampirkan (attach) berkas `KAMUS_SURYANI_META.json` 799 baris di chat Arena; berkas akan disalin ke
`terjemahan/KAMUS_SURYANI_META.json` menggantikan subset 78 entri, lalu catatan ini diperbarui.
Sampai itu terjadi, angka "799" pada baris *Sumber* di atas **tidak berlaku** untuk berkas di repo.

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
