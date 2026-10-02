# Kitab Asrar Sulaimaniyyah — OCR + Latin + Terjemah (otomatis, semalam)

Mengubah pindaian **الأسرار السليمانية في العلوم الروحانية** (`kitab/asrorul-sulaimaniyah.pdf`, 103 halaman)
menjadi **Teks Arab · Latin Pesantren · Terjemah Indonesia**, halaman demi halaman, memakai Gemini.
Dibuat agar aman dibiarkan semalaman: **bisa dilanjutkan**, mundur sendiri saat kena batas laju (429),
berhenti rapi bila kuota harian habis, dan tidak pernah menyimpan kunci API.

## Cara 1 — Jalankan di GitHub Actions (tidak perlu perangkat menyala)

1. **Gabungkan** (merge) pull request yang memuat berkas ini ke `main` — tombol *Run workflow* hanya muncul bila
   workflow ada di `main`.
2. **Buat rahasia**: *Settings → Secrets and variables → Actions → New repository secret* →
   nama **`KITAB_API_KEY`**, isi dengan kunci API Gemini Anda.
3. Buka tab **Actions → "Mulai Malam — OCR + Latin + Terjemah Kitab" → Run workflow**. Jalankan **berurutan**:
   1. `tes_saja` = ✔ → memastikan kunci, model, dan endpoint benar (hampir tanpa biaya, ±20 detik).
   2. `halaman_akhir` = `3` → uji coba 3 halaman; baca hasilnya di `hasil/TERJEMAHAN.md`.
   3. kosongkan `halaman_akhir` → seluruh kitab.
4. Hasil otomatis di-commit ke folder **`hasil/`** (bisa dibaca langsung di GitHub / aplikasi GitHub) dan
   diunggah juga sebagai *artifact* `hasil-malam`. Ringkasan muncul di halaman job.

Terputus, kena kuota, atau ada halaman gagal? **Jalankan ulang workflow yang sama** — halaman yang sudah selesai
dilewati, hanya sisanya yang dikerjakan.

## Cara 2 — Jalankan di komputer/server sendiri

```bash
export KITAB_API_KEY="kunci-anda"
./mulai_malam.sh kitab/asrorul-sulaimaniyah.pdf \
    "https://generativelanguage.googleapis.com/v1beta/openai/" "gemini-2.5-pro" 8 1 600
```

Argumen: `<pdf> <base_url> <model> [pekerja=8] [halaman_per_permintaan=1] [timeout_dtk=600]`.
Pertama kali dijalankan, skrip menyiapkan lingkungan Python-nya sendiri (`.venv-kitab/`, sekali saja).
Semalaman: `nohup ./mulai_malam.sh … > malam.log 2>&1 &`.

Opsi tambahan lewat variabel lingkungan:

| Variabel | Fungsi |
|---|---|
| `KITAB_TES_SAJA=1` | hanya uji kunci/model/endpoint lalu berhenti |
| `KITAB_MULAI`, `KITAB_AKHIR` | kerjakan sebagian halaman saja (mis. `KITAB_AKHIR=3`) |
| `KITAB_ATURAN=kajian\|penuh` | `kajian` (bawaan, sama seperti edisi Anda yang lain) atau terjemah `penuh` — lihat di bawah |
| `KITAB_ULANG_SEMUA=1` | abaikan hasil sebelumnya, kerjakan ulang semua |
| `KITAB_AUTH=auto\|bearer\|x-goog-api-key\|native` | cara mengirim kunci (bawaan `auto`) |
| `KITAB_KELUARAN`, `KITAB_JUDUL` | folder hasil, judul dokumen |
| `KITAB_BATAS_WAKTU=detik` | berhenti rapi setelah sekian detik (di Actions: 340 menit) |
| `KITAB_MAKS_PERCOBAAN`, `KITAB_REASONING_EFFORT`, `KITAB_MAKS_TOKEN`, `KITAB_SUHU` | penyetelan lanjutan |

## Hasil

| Berkas | Isi |
|---|---|
| `hasil/TERJEMAHAN.md` | seluruh kitab: `## Halaman PDF N (= cetak M)` → Teks Arab, Latin Pesantren, Terjemah Indonesia, + gambar halaman asli |
| `hasil/STATUS.md` | berapa halaman selesai/gagal/diblokir, token terpakai, alasan berhenti, cara melanjutkan |
| `hasil/halaman/` | satu berkas `.md` per halaman |
| `hasil/gambar/` | gambar halaman asli (JPEG asli dari PDF, tanpa dikompres ulang) |
| `hasil/_state/` | catatan per halaman untuk melanjutkan (jangan dihapus bila ingin resume) |

Halaman yang gagal atau diblokir filter model tetap muncul di `TERJEMAHAN.md` sebagai penanda, lengkap dengan
gambar aslinya, sehingga urutan kitab tidak bergeser.

## Aturan edisi: `kajian` atau `penuh`

Edisi-edisi Anda yang lain memakai aturan *kajian filologi*: teks Arab disalin utuh, tetapi amalan yang dimaksudkan
mencelakai/memaksa orang lain diuraikan isi dan tujuannya saja, tanpa merinci langkah praktik yang memudaratkan.
Itu **bawaan di sini** (`kajian`). Untuk terjemah lengkap dan setia apa adanya, pakai `KITAB_ATURAN=penuh`
(di Actions: input `aturan`). Seluruh instruksi ke model ada di `tools/prompt_halaman.txt` dan bisa Anda ubah.

## Batas, biaya, dan kuota

- Paket gratis Gemini punya batas permintaan per menit **dan per hari** yang ketat untuk model Pro. Skrip mundur
  otomatis saat kena batas per menit; bila **kuota harian** habis, ia berhenti rapi (kode keluar 3) dan menyimpan
  semuanya — jalankan ulang setelah kuota direset.
- Setiap halaman = satu permintaan bergambar (`1` halaman/permintaan). Lihat tab *Usage* di AI Studio untuk biaya.
- Job GitHub-hosted dibatasi 6 jam; skrip berhenti rapi di menit ke-340 agar hasil sempat disimpan.

## Kunci API: keamanan

- Kunci **hanya** dibaca dari `KITAB_API_KEY`; tidak pernah dari argumen, tidak ditulis ke berkas, dan disamarkan di log.
  Di Actions kunci disimpan sebagai *secret* terenkripsi.
- Jangan pernah men-commit kunci. Kunci yang pernah ditempel di obrolan/dokumen sebaiknya dicabut dan dibuat ulang
  di AI Studio setelah pekerjaan selesai.
- Kunci baru berawalan `AQ.` kadang ditolak oleh endpoint kompatibel-OpenAI bila dikirim sebagai `Bearer`. Skrip
  mengujinya dulu dan otomatis mencoba cara lain (`x-goog-api-key`, lalu endpoint native). Jalankan `tes_saja` untuk
  melihat cara mana yang dipakai.

## Bila ada masalah

| Pesan | Artinya |
|---|---|
| `Tes koneksi GAGAL … Tidak bisa terhubung` | jaringan memblokir domain Google (mis. sebagian sandbox/kantor); jalankan di GitHub Actions atau jaringan lain |
| `Kunci ditolak` (400/401/403) | kunci salah/dicabut, atau tidak boleh memakai Gemini API |
| `Model … tidak ditemukan` (404) | nama model salah atau tidak tersedia untuk kunci Anda |
| `Kuota habis` / `Kuota model ini 0` | kuota harian habis, atau paket Anda tidak mencakup model itu (aktifkan penagihan / ganti model) |
| `diblokir filter model` | Gemini menolak halaman itu; sisanya tetap jalan. Coba `KITAB_ATURAN=kajian` atau kerjakan manual |
| `format tak baku — cek manual` | jawaban model tidak mengikuti format; halaman tetap disimpan, mohon dicek |

## Edisi Panel: terjemahan per batch, preview web, dan PDF

Selain jalur otomatis di atas, repo ini punya jalur **per batch** (5 halaman PDF per batch, 21 batch untuk 103 halaman):

| Berkas | Isi |
|---|---|
| `BATCH_NN.md` | sumber kebenaran: Arab berharakat, Latin washal, terjemah Indonesia, syarah, faedah, gambar rajah |
| `rajah/` | potongan gambar rajah/wafaq dari pindaian (latar putih bersih) |
| `preview.html` | pratinjau web: satu kartu per halaman PDF, tombol emas **📥 Unduh PDF Master Panel** |
| `MASTER_PANEL_Batch_NN.pdf` | PDF A4 margin 2 cm; menjadi `KHATAM_TERJEMAHAN_Kitab_Asraru_Sulaimaniyyah.pdf` bila 21 batch lengkap |
| `TERJEMAHAN.md`, `TERJEMAHAN_MATAN_MURNI.md` | gabungan semua batch (yang kedua tanpa syarah/faedah) |
| `fonts/` | font Amiri (SIL OFL) |

```bash
pip install -r requirements-panel.txt
python tools/bangun_panel.py --cek     # periksa mutu BATCH_*.md (harakat, pola Latin, jumlah paragraf, gambar)
python tools/bangun_panel.py           # bangun preview.html, PDF, dan TERJEMAHAN*.md
python tools/server_preview.py         # pratinjau di http://localhost:3000 (tombol unduh PDF di bagian atas)
python -m unittest tools/test_panel.py # uji otomatis
```

Format satu bagian di `BATCH_NN.md` (urutan blok tetap; syarah, faedah, dan gambar boleh tidak ada):

```
## Halaman PDF 3 (= cetak 2)
### Bagian 1 — Judul bagian
**[Teks Arab Asli]**      -> dalam <div dir="rtl">, harakat lengkap
**[Transliterasi Latin Fonetik]**   -> washal; tiap paragraf diapit *…*
**[Terjemahan Indonesia]**
**[Syarah]** / **[Faedah]**  -> diawali "> "
![Rajah Hal. 5 (cetak 4) — keterangan](rajah/rajah_p05_khatam_01.png)
```

Catatan teknis:

- PDF dibuat dengan **PyMuPDF Story (MuPDF + HarfBuzz)** dan font Amiri tertanam, sehingga huruf Arab berharakat tersambung utuh di semua pembaca PDF. Pembangun menulis ulang peta *ToUnicode* dari font supaya teks Arab di PDF **bisa disalin dan dicari** (bawaan MuPDF mengacak huruf Arab kontekstual).
- MuPDF tidak mendukung `page-break-inside` dan membalik `text-align: right` pada blok RTL, jadi tata letak halaman dilakukan oleh `bangun_panel.py` sendiri (blok tidak terbelah, tanpa serpihan di puncak halaman). Ada uji regresi untuk keduanya.
- Resolusi pindaian hanya sekitar 850×1100 px per halaman penuh. Potongan rajah dibuat rapi berlatar putih dan diperbesar halus, tetapi **bukan 300 DPI asli**; rajah yang tidak terbaca ditandai, tidak ditebak.
- Harakat, transliterasi, dan terjemahan dibuat dengan bantuan AI dan **perlu dikoreksi** nahwu/sharaf. Salah cetak di pindaian tidak diperbaiki diam-diam: ditandai `[المطبوع: …]` atau `[كذا]`.

## Menguji skrip tanpa internet

Server Gemini tiruan (`tools/mock_gemini.py`) meniru endpoint kompatibel-OpenAI dan native, termasuk kegagalan
(429, kuota harian, 5xx, timeout, filter keamanan, kunci `AQ.`):

```bash
pip install -r requirements.txt
python -m unittest tools/test_pipeline.py -v      # ±40 detik, tanpa kunci, tanpa biaya
```
