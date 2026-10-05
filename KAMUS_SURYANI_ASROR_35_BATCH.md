# KAMUS SURYANI — ASROR SULAIMANIYYAH
## Versi inti (berbasis rujukan) · dibangun dari BATCH_01–35 + TERJEMAHAN.md

> **Status berkas.** Ini **bukan** hasil pemulihan `KAMUS_SURYANI_ASROR_35_BATCH.md` yang disebut berisi “+802 baris”. Berkas itu **tidak ditemukan** — tidak di working tree, tidak di histori commit mana pun (`main` 62d1644, `01a10bbe` cb2e13b, `01a10166` c8aa80e, `01a0fd9d` 1f03c40), tidak di `git stash`, dan tidak sebagai objek menggantung (`git fsck --lost-found` kosong). Karena itu kamus ini **dibangun ulang dari rujukan yang benar-benar ada di repo**: catatan editorial batch dan daftar makna nama Suryani yang dicetak kitab sendiri (PDF 44–45). Jumlah baris mengikuti bahan, bukan target 802.

> **Kaidah penyusunan.**
> 1. Hanya entri yang punya rujukan baris di repo. Tidak ada entri hasil karangan.
> 2. Arti yang **tidak** dinyatakan di repo tidak diklaim; ditandai ❔ dan dipisahkan ke daftar periksa (§4).
> 3. Bentuk cetak Arab dipertahankan apa adanya (termasuk harakat hasil AI dan salah cetak); koreksi hanya diberi catatan, tidak diubah diam-diam.
> 4. Penomoran halaman: **PDF** = urutan pindaian; **cetak** = PDF − 1.
> 5. Isi kitab ini adalah klaim penulis naskah, bukan anjuran praktik.

> **Ukuran berkas ini:** 284 baris · **16 entri akar/istilah** (§1) + **57 entri leksikon Suryani menurut kitab** (§2) + lampiran rantai nama tanpa makna (§3).

## 0. Lambang status

| Lambang | Arti |
|---|---|
| ✅ | Dinyatakan di repo (catatan editorial atau teks kitab) |
| ⚠️ | Dugaan/tentatif — repo menyebut “dugaan”, “tentatif”, “tidak dapat dipastikan” |
| ❔ | Belum dirujuk di repo — usulan pemeriksaan, **bukan klaim** |

---

## 1. Akar Ibrani/Aram — entri inti

### 1.1 Tabel ringkas

| # | Bentuk cetak (Arab) | Latin | Padanan & arti menurut repo | Status | Rujukan |
|---|---|---|---|---|---|
| 1 | أَدُونَيَّا · أدوناي · Adunai | Adunayya · Adonai | Ibrani *Adonai* — “Tuhan”; dalam «أدوناي أصباؤوت إل شداي» = *Adonai Tseva'ot El Shaddai* (“Tuhan semesta kuasa, Allah Yang Mahakuasa”) | ✅ | BATCH_02.md:116 (PDF 7 = cetak 6) · BATCH_02.md:102 · BATCH_06.md:248 (PDF 29 = cetak 28) |
| 2 | أَصْبَاؤُوتِي · أصباؤوت · صَبَاوُوتَ | Ashba-uuti · Tseva'ot | Ibrani *Tseva'ot* — “semesta kuasa” | ✅ | BATCH_02.md:116 · BATCH_04.md:242 (PDF 19 = cetak 18) |
| 3 | إِلْ · إله | El · ilaah | Ibrani *El* — unsur nama ilahi; «إِلْ شَدَّاي» = *El Shaddai* (“Allah Yang Mahakuasa”) | ✅ | BATCH_04.md:242 · BATCH_06.md:248 |
| 4 | شَدَّاي · شَدَايَّا | Shaddai · Syadayya | Ibrani *Shaddai* — “Allah Yang Mahakuasa” | ✅ | BATCH_04.md:242 · BATCH_02.md:102 |
| 5 | آهيا · أَهْيَا | Ahya · Ehyeh | «آهيا شراهيا أدوناي أصباؤت» = *Ehyeh Syerehyah Adonai Tseva'ot* | ✅ | BATCH_06.md:248 · BATCH_04.md:206/212 (PDF 18 = cetak 17) |
| 6 | شَرَاهْيَا · شراهيا | Saraah-yaa · Syerehyah | Menyertai *Ehyeh* dalam rumus «آهيا شراهيا أدوناي أصباؤت» | ✅ | BATCH_06.md:248 · BATCH_04.md:206/212 |
| 7 | ميططرون · إله ميططرون | Mithathrun · Metatron | *El Metatron* — “Metatron”; kitab menyebut “lih. catatan hal. 5” | ✅ | BATCH_06.md:248 · BATCH_02.md:116/138 (PDF 8 = cetak 7) |
| 8 | ملكوتا | malkutha | Aram/Suryani — “kerajaan” | ✅ | BATCH_06.md:248 |
| 9 | مشلامون | mesy-lamun · syallamun | “damai” | ✅ | BATCH_06.md:248 |
| 10 | سُبُّوحٌ قُدُّوسٌ | subbuh quddus | Pujian liturgis Ibrani/Aram — “Mahasuci lagi Mahakudus” | ✅ | BATCH_04.md:242 |
| 11 | مِصْرَابِيمَ | mishrabim | “Mengingatkan pada *ma'arabim*/baratan” (barat) | ⚠️ | BATCH_04.md:242 |
| 12 | عليون | 'Illiyyun · Elyon | “Bisa menyerupai *Elyon* (Ibrani: Yang Mahatinggi) atau *'Illiyyun*; tidak dapat dipastikan” | ⚠️ | BATCH_01.md:353 (PDF 4 = cetak 3) |
| 13 | دهحيثا دهليلوا | deh-hitha · dehlilwa | “Mengingatkan pada” — belum pasti | ⚠️ | BATCH_06.md:248 |
| 14 | أبجد هوز حطي بكد زهج | — (abjad) | “Ejaan abjad Ibrani/Aram urutan alef-bet yang lazim dalam literatur hikmah”; pasangannya «بدوح أجهزط» | ✅ | BATCH_07.md:368 (PDF 35 = cetak 34) |
| 15 | بِـ + nama (mis. بِخَيْطَانَا خَيْطَانَا) | prefiks *b-* | Pola prefiks Aram/Suryani: pasangan kata berawalan ب (بِ + nama) meniru prefiks *b-* | ✅ | BATCH_04.md:242 · contoh BATCH_04.md:176 (PDF 18 = cetak 17) |
| 16 | جَبَرُوت (dalam «العَزِيزُ فِي جَبَرُوتِهِ») | jabaruut | Kitab memakai istilah ini; **asal Aram/Suryani tidak dinyatakan di repo** | ❔ (akar) / ✅ (istilah) | BATCH_09.md:475 (PDF 45 = cetak 44) |

### 1.2 Keterangan per entri

- **(1) Adonai / أدوناي / أَدُونَيَّا.** Bentuk cetak muncul dalam dua ejaan: `أدوناي` pada catatan BATCH_02.md:116 dan `أَدُونَيَّا` pada teks doa BATCH_02.md:102 (hal. PDF 7 = cetak 6). Di BATCH_05 teks Latin menuliskan `Adunaay`/`Adunai` (BATCH_05.md:262, hal. PDF 24 = cetak 23). Repo hanya menyatakan padanan Ibraninya, tidak menurunkan akar hurufnya.
- **(2) Tseva'ot / أصباؤوت.** Tiga ejaan cetak tercatat: `أَصْبَاؤُوتِي` (BATCH_02.md:102), `أَصْبَاؤُوت` (BATCH_06.md:248), dan `صَبَاوُوتَ` (BATCH_04.md:242). Arti “semesta kuasa” dinyatakan repo. Pada BATCH_05.md:128 frasa yang tercetak adalah `أَرْكَاضِ أَصْبَاوْتَ آلَ شَدَّاي` (Latin: *arkaadh ashbaawta aal syaddaay*).
- **(3) El / إل.** Muncul sebagai unsur pertama *El Shaddai* dan pada `إله ميططرون` (*El Metatron*, BATCH_06.md:248).
- **(4) Shaddai / شداي.** Bentuk cetak: `إِلْ شَدَّاي` (BATCH_04.md:242), `شَدَايَّا` (BATCH_02.md:102), Latin `Syaddaay`/`Al Syaddai` (BATCH_05.md:272/280).
- **(5–6) Ehyeh Syerehyah / آهيا شراهيا.** Repo mengutip padanan `Ehyeh Syerehyah Adonai Tseva'ot` (BATCH_06.md:248). Pada rantai “akhir nama yang tersimpan” muncul varian `أَهْيَا شَرَاهْيَا` dengan Latin `Ah-yaa Saraah-yaa` (BATCH_04.md:206/212). Pada BATCH_02.md:108 varian Latinnya `Aahya Syaahya`.
- **(7) Metatron / ميططرون.** Dua bentuk cetak: `ميططرون` (BATCH_06.md:248 — “El Metatron”) dan catatan “lih. catatan hal. 5” (BATCH_02.md:116). Nama panggilan dalam doa ditulis Latin `Maithathruunu`/`Mithathrun` (BATCH_02.md:134/138).
- **(8–9) malkutha, mesy-lamun.** Dua kata Aram/Suryani yang maknanya dinyatakan langsung: “kerajaan” dan “damai” (BATCH_06.md:248).
- **(10) subbuh quddus.** Disebut repo sebagai “pujian liturgis” dengan arti “Mahasuci lagi Mahakudus” (BATCH_04.md:242).
- **(11–13) Entri dugaan.** `مصرابيم` (ma'arabim/baratan), `عليون` (Elyon/'Illiyyun), dan `دهحيثا دهليلوا` (deh-hitha/dehlilwa) semuanya diberi penanda ketidakpastian oleh repo — jangan dikutip seolah pasti.
- **(14) Abjad alef-bet.** Repo mencatat rangkaian `أبجد هوز حطي بكد زهج` sebagai “ejaan abjad Ibrani/Aram urutan alef-bet”, bersama `بدوح أجهزط` dan nama-nama Haikal (BATCH_07.md:368).
- **(15) Prefiks b-.** Pola paling jelas terlihat pada rantai al-Jalb as-Suryani: `بِخَيْطَانَا خَيْطَانَا`, `بِشْلَامِينْ شْلَامِينْ`, `بِصَفِيفْ صَفِيفْ`, dst. (BATCH_04.md:168; catatan: BATCH_04.md:242).
- **(16) jabaruut.** Kata ini muncul di dalam makna entri kitab `بَيْرُوحُ: العَزِيزُ فِي جَبَرُوتِهِ` (BATCH_09.md:475). Karena repo tidak menyatakan akarnya, status akarnya ❔.

### 1.3 Daftar periksa Semitik (❔ belum dirujuk di repo — usulan, bukan klaim)

Tabel berikut **bukan hasil repo**; ini daftar kerja untuk pemeriksaan lanjutan. Jangan dikutip sebagai isi repo sebelum diverifikasi ke sumber yang bisa dirujuk.

| Bentuk cetak | Bacaan | Usulan padanan yang layak dicek |
|---|---|---|
| آهيا | Ehyeh | Ibrani אֶהְיֶה (ʾehyeh) |
| أدوناي | Adonai | Ibrani אֲדֹנָי (ʾăḏōnāy) |
| أصباؤوت | Tseva'ot | Ibrani צְבָאוֹת (ṣəḇāʾôṯ) |
| شداي | Shaddai | Ibrani שַׁדַּי (šaday) |
| ميططرون | Metatron | Ibrani/aram מֶטָטְרוֹן (meṭaṭrôn) |
| ملكوتا | malkutha | Aram מַלְכוּתָא (malkūṯā) |
| مشلامون | syallamun | Aram שְׁלָמָא (šəlāmā) |
| عليون | Elyon | Ibrani עֶלְיוֹן (ʿelyôn) |

---

## 2. Leksikon nama Suryani menurut kitab sendiri (PDF 44–45 = cetak 43–44)

Kitab membuka bagian ini dengan kalimat: *“Dan untuk menyempurnakan faedah, kami sebutkan makna nama-nama Suryani yang dibawanya; dan Allah Maha Mengetahui.”* (BATCH_09.md:445, hal. PDF 44 = cetak 43). Daftar dimulai dari **Aj** dan berakhir pada **'Aithla**, terbagi dua halaman.

**Cara membaca tabel:** kolom “Makna menurut kitab” adalah makna **Arab cetak** yang diberikan kitab untuk nama di sebelah kirinya; kolom “Terjemah” adalah terjemahan Indonesia dari repo. Baris bernomor dengan harakat: harakat adalah tambahan AI repo, bukan cetak.

### 2.1 Halaman PDF 44 (= cetak 43) — dari «Aj» sampai «Ta'dad»

| # | Nama (Arab cetak) | Latin | Makna menurut kitab (Arab) | Terjemah Indonesia | Rujukan |
|---|---|---|---|---|---|
| 1 | آجِ | Aaj | اللهُ | Allah | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 2 | أوحِ | Auh ma'naahul-Ahad | الأَحَدُ | Yang Esa | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 3 | جَلْ جَلْيُوثُ | Jal Jalyuuts | البَدِيعُ | Yang Maha Pencipta tanpa contoh | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 4 | جَلْجَلَثُ | Jaljalats | القَادِرُ | Yang Mahakuasa | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 5 | هَيَ | Hay | الكَافِي | Yang Mencukupi | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 6 | هَلْ | Hall | الوَدُودُ | Yang Maha Mengasihi | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 7 | هَلْهَلْتَ | Halhalt | البَاسِطُ | Yang Melapangkan | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 8 | طَيْطَفْتَ | Thaithaft | الحَيُّ | Yang Mahahidup | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 9 | غَلْمَهَثُ | Ghalamats | القَهَّارُ ذُو البَطْشِ الشَّدِيدِ | Yang Mahamenundukkan, pemilik kekerasan yang hebat | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 10 | شَمَاخُ | Syamaakh | الحَلِيمُ | Yang Mahapenyantun | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 11 | أَشْمَخُ | Asymakh | الخَالِقُ | Yang Maha Mencipta | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 12 | سَلْمَةُ سَمْتُ | Salmatu Samat | السَّلَامُ | Yang Mahasejahtera | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 13 | صَمْصَامُ | Shamshaam | البَارِي | Yang Maha Mengadakan | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 14 | مِهْرَاشُ | Mihraasy | الثَّابِتُ | Yang Mahatetap | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 15 | طَمْطَامُ | Thamthaam | القَوِيُّ المَتِينُ | Yang Mahakuat lagi Mahakokoh | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 16 | بَازَخُ | Baazakh | الجَلِيلُ | Yang Mahaagung | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 17 | شَرْنْطَخُ | Syarnthakh | الحَيُّ البَاقِي | Yang Mahahidup lagi Mahakekal | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 18 | بَهُوثْتُ | Bahauts | الرَّحِيمُ — riwayat lain: وفِي رِوَايَةٍ شَدِيدُ العَذَابِ | Yang Mahapenyayang — dan dalam satu riwayat: Yang Keras siksa-Nya | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 19 | يَاوِ | Yaruw | هُوَ اللهُ | Dialah Allah | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 20 | يَرُو | Namuu-u | الأَوَّلُ والآخِرُ | Yang Pertama dan Yang Terakhir | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 21 | نَمُوءُ | Ashaalyaa | الظَّاهِرُ | Yang Mahanyata | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 22 | أَصَالْيَا | Najaa 'Aalyaa | البَاطِنُ | Yang Mahabatin | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 23 | نَجَا عَالْيَا | Shalshalt | الوَكِيلُ | Yang Maha Memelihara | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 24 | صَلْصَلَتْ | Hasamats | الكَافِي | Yang Mencukupi | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 25 | حَسْمَثُ | Hausam | القَابِضُ | Yang Menggenggam | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 26 | حَوْسَمُ | Darasam | الرَّحْمَنُ | Yang Mahapengasih | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 27 | دَرْسَمُ | Baraasam | الرَّحِيمُ | Yang Mahapenyayang | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 28 | بَرَاسَمُ | Syalmahats | الظَّهِيرُ | Yang Menolong | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 29 | شَلْمَهَثُ | Azmakht | الفَتَّاحُ | Yang Membuka | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 30 | أَزْمَخْتُ | Ta'daad | الغَنِيُّ المُغْنِي | Yang Mahakaya lagi Memperkaya | BATCH_09.md:453 · PDF 44 = cetak 43 |
| 31 | تَعْدَادُ | — | القَوِيُّ | Yang Mahakuat — … | BATCH_09.md:453 · PDF 44 = cetak 43 |

### 2.2 Halaman PDF 45 (= cetak 44) — dari «Abram» sampai «'Aithla»

| # | Nama (Arab cetak) | Latin | Makna menurut kitab (Arab) | Terjemah Indonesia | Rujukan |
|---|---|---|---|---|---|
| 1 | أَبْرَامُ | Abraam | المَتِينُ | Yang Mahakokoh | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 2 | سَنَادُ كَاهِرَ | Sanaad Kaahir | المُجِيبُ | Yang Mengabulkan | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 3 | بَهْرَاةُ تَبْرِيزَ | Bahraatu Tabriiz | الأَوَّلُ والآخِرُ | Yang Pertama dan Yang Terakhir | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 4 | تَاكِرُ | Taakir | النُّورُ | Cahaya | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 5 | أَبَارِيخُ | Abaariikh | الحَكَمُ | Yang Mahamenetapkan hukum | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 6 | بَيْرُوخُ | Bairuukh | العَدْلُ | Yang Mahaadil | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 7 | بَيْرُوحُ | Bairuuh | العَزِيزُ فِي جَبَرُوتِهِ | Yang Mahaperkasa dalam jabarut-Nya | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 8 | بَرْخُوَا | Barakhwaa | المُعِزُّ | Yang Memuliakan | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 9 | شَمَارِيخُ | Syamaariikh | المُبْدِئُ | Yang Memulai | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 10 | شَيْرَاخُ | Syairaakh | القَرِيبُ | Yang Mahadekat | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 11 | نَشْمَخْتُ | Nasyamakht | عَالِمُ السِّرِّ | Yang Mengetahui rahasia | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 12 | يَمْلِيخُ | Yamliikh | القَيُّومُ | Yang Mahamengurus | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 13 | شَمْيَانَا | Syamyaanaa | الحَقُّ | Yang Mahabenar | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 14 | يَانُوخُ | Yaanukh | الوَكِيلُ | Yang Maha Memelihara | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 15 | دَامِيخُ | Daamiikh | الكَرِيمُ | Yang Mahamulia | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 16 | يَشْمُوخُ | Yasymuukh | الحَنَانُ | Yang Maha Mengasih | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 17 | `عَلَى مَا نَرِمُ حَفَّاً يَرُونَ بِقَنْصَبَ` † | 'alaa maa narmu haffan yaruuna biqanashab | اللهُ غَالِبٌ عَلَى أَمْرِهِ | Allah Maha Mengalahkan atas urusan-Nya | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 18 | تَانٍ | Taan | الحَسِيبُ | Yang Maha Menghitung | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 19 | كَمَاهْ | Kamaah | رَبِّي | Tuhanku | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 20 | أَوَاهْ | Awaah | المُحْيِي | Yang Menghidupkan | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 21 | هِشْكَاخُ هِشْكَاخُ | Hisykaakh Hisykaakh | الوَالِي المُتَعَالِ | Yang Menguasai lagi Mahatinggi | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 22 | بَهْرَامُ | Bahraam | العَزِيزُ | Yang Mahaperkasa | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 23 | سَمْخَثَا | Samakh-tsaa | الرَّحْمَنُ | Yang Mahapengasih | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 24 | شَلْمَخَا | Syalmakhaa | المُغْنِي | Yang Memperkaya | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 25 | شَلْمَخُ | Syalmakh | المُعِزُّ | Yang Memuliakan | BATCH_09.md:475 · PDF 45 = cetak 44 |
| 26 | عَيْطَلَا | 'Aithlaa | القَوِيُّ القَهَّارُ | Yang Mahakuat lagi Mahamenundukkan. | BATCH_09.md:475 · PDF 45 = cetak 44 |

### 2.3 Catatan atas leksikon

- **†** Entri nomor 17 pada tabel 2.2 (`عَلَى مَا نَرِمُ حَفَّاً يَرُونَ بِقَنْصَبَ`) bukan satu nama, melainkan **frasa** yang diterjemahkan kitab sebagai “Allah Maha Mengalahkan atas urusan-Nya”. Repo menandainya sebagai rangkaian yang perlu kehati-hatian.
- **Salah cetak yang dicatat repo:** kata pengantar bagian ini tercetak `ولتنميم` dan dianggap seharusnya `ولِتَتْمِيمِ` (BATCH_09.md:441/445).
- **Riwayat ganda:** entri `بَهُوثْتُ` (Bahauts) punya dua makna menurut riwayat: “Yang Mahapenyayang” dan “Yang Keras siksa-Nya” (BATCH_09.md:453/463).
- **Tanda “…” pada entri terakhir halaman 44** (`تَعْدَادُ`: “Yang Mahakuat — …”) menunjukkan daftar **bersambung** ke halaman berikutnya, bukan terputus.
- **❔ Belum ditemukan lanjutan** setelah `عَيْطَلَا` (entri 26 tabel 2.2): BATCH_10–11 tidak memuat sisa daftar makna. Perlu diperiksa ke halaman cetak 45 (PDF 46) dan seterusnya pada pindaian bila daftar berlanjut.
- **Cakupan makna:** seluruh 57 entri adalah **nama-nama sifat ketuhanan** (al-asma' al-husna) dalam bahasa Suryani menurut kitab, bukan nama malaikat. Daftar nama malaikat/nama rahasia ada di lampiran §3.
- **Status akar:** repo memberi **makna**, bukan **akar huruf Semitik** tiap nama. Karena itu kamus ini tidak mengklaim akar untuk 57 entri di atas; lihat §4.

---

## 3. Lampiran — rantai nama tanpa makna menurut kitab

Bagian ini memuat nama-nama yang **dibaca** kitab tetapi **tidak diberi makna** olehnya (atau hanya diberi pelafalan tentatif). Semua entri berstatus ⚠️/❔: bentuk cetak dipertahankan, pelafalan diberi tanda tentatif oleh repo.

### 3.1 Hijab Sulaiman — nama kunci (PDF 22 = cetak 21)

Di antara sumpahnya, hijab ini memuat frasa kunci yang menghubungkan ke §1: **`بِحَقِّ أَرْكَاضِ أَصْبَاوْتَ آلَ شَدَّاي`** (“dengan hak arkaadh ashbaawta aal syaddaay”) — BATCH_05.md:128. Nama-nama seruan pada hijab yang sama:

> تَعْطِرَ يَايِلُ تَعْطِرَ يَايِلُ، طَرْطَيَائِيلُ طَرْطَيَائِيلُ، زَنْقِيطُ زَنْقِيطُ، مُطَاهُوشُ مُطَاهُوشُ، جَلْجَمِيشُ جَلْجَمِيشُ، رَاهِمُ رَاهِمُ، جِرْجَيَائِيلُ جِرْجَيَائِيلُ

Status: ⚠️ pelafalan tentatif; kitab tidak memberi makna. Nama berakhiran `-يَائِيل` (`-yaa-iil`) berpola nama malaikat, tetapi repo tidak menyatakan identifikasinya.

### 3.2 Rantai utama al-Jalb as-Suryani (PDF 17 = cetak 16)

Judul cetak: **«وَهَذَا هُوَ الجَلْبُ السُّرْيَانِيُّ»** (“Inilah al-Jalb as-Suryani”), dibaca setelah “penyucian diri (tanzih) ruhani yang pertama”. Teks Arab rantai ini ada di BATCH_04.md:142; rantai Latin menurut repo (BATCH_04.md:152):

> *Taquulu ba'dat-tanziihil-awwalir-ruuhaaniyy: Araa araa kafiitaa kafiitaa syalsyiisy syalsyiisy malsyiisy malsyiisy ahiliil ahiliil haibuul haibuul maltiin maltiin kalkiyaam kalkiyaam ahiil ahiil kalkatsum kalkatsum ariiri ariiri ajbini ajbini akyaahuum akyaa-huum kalkiaa-iil kalkiaa-iil bidamlaakh baraakh baraakh haithaa-iil haithaa-iil arbaab biyaarab bahaitanaakh haitanaakh multiyaahuukh multiyaahuukh baaqithah 'aithalah ajriyaa-iil thailahuub thailahuub thaithuub thail'uub haibaa-uuth [phonetic reading is tentative; printed consonants are retained]* …

Status: ⚠️ “pelafalan nama atau istilah belum pasti; bentuk cetak dipertahankan”. Kitab tidak memberi makna satu pun.

### 3.3 Sambungan rantai + pola prefiks b- (PDF 18 = cetak 17)

Sambungan rantai ini adalah bukti terkuat pola prefiks *b-* Aram/Suryani yang dicatat repo (BATCH_04.md:242). Rantai Latin menurut repo (BATCH_04.md:176):

> *Haibaa-uuth kiilyaa-iil kiilyaa-iil kalmiyaa-iil (2) bidamlaakh damlaakh baraakh baraakh juulaa juulaa hiilaa hiilaa syamlaa syamlaa bistathaaf sathaaf bishafiif shafiif bimathuuf mathuuf khaththaaf khaththaaf thaa-if thaa-if sya'diyaasy syaqdiyaasy wardiyaasy syar'uun syar'uun juuhasyaam juuhasyaam miilaa miilaa bisulthaaliin sulthaaliin mahlawaan mahlawaan bikhaythaanaa khaythaanaa baaburuusy jaruusy bikluusy kuluusy bithaqsyar taqsyar bisylaamiin sylaamiin rathqasy rathqasy bisyliim syliim biksyaasyuuna ksyaasyuuna yiitalah haitalah bihaitiluumi haitiluumi bimultaahaa multaahaa bihyaala hyaala bihan han bikhaf khaf bisydah sydah bidhaif dhaif bidalkham dalkham kasykam kasykam biruuqaa biruuqaa bikisytah kisytah kasylaa kasylaa kasyandaa kasyandaa bi'aqtihim 'aqtihim yuuqtam yuuqtam taquufah taquufah dartyaaub dartyaaub.*

Perhatikan pasangan `bi-… / …` yang berulang (mis. `bikhaythaanaa khaythaanaa`, `bisylaamiin sylaamiin`, `bithaifsyar tafsyar`), sama polanya dengan catatan BATCH_04.md:242.

### 3.4 «Nama yang cepat lagi tersimpan» (PDF 18 = cetak 17)

Teks cetak (BATCH_04.md:188):

> وَهَذَا هُوَ الاسْمُ السَّرِيعُ المَكْنُونُ الَّذِي تَذْكُرُهُ العُلَمَاءُ يُوهِ يُوهِ بِهْيَهْلِيُوهِ هْيَهْلِيُوهِ الأَرْكِيَاظْ الأَرْكِيَاظْ هَيْبُورْ هَيْبُورْ كَسْرِيَاوُبْ كَسْرِيَاوُبْ عَلْشَقُومْ عَلْشَقُومْ عَلْشَافَشْ عَلْشَافَشْ مِهْرَاقَشْ مِهْرَاقَشْ.

Latin (BATCH_04.md:194):

> *Wa haadza huwal-ismus-sarii'ul-maknuunul-ladzii tadzkuruhul-'ulamaa-u: Yuuhi yuuhi bihyahliyuhi hyahliyuhi al-arkiyaazh al-arkiyaazh haibuur haibuur kasriyaaub kasriyaaub 'alsyqaum 'alsyqaum 'alsyaafasy 'alsyaafasy mihraaqasy mihraaqasy.*

Status: ⚠️ kitab menyebut “yang disebut oleh para ulama (ahli)”; tidak ada makna.

### 3.5 «Akhir nama yang tersimpan» (PDF 18 = cetak 17)

Teks cetak (BATCH_04.md:206) — memuat `أَهْيَا شَرَاهْيَا` yang dirujuk di §1 entri 5–6:

> <div dir="rtl">

Latin (BATCH_04.md:212):

> *Wa haadza aakhirul-ismil-maknuun: Aqsyaamaqasy 'aqasy thahsyiiz Ah-yaa Saraah-yaa Qudduus Qudduus rabbul-malaa-ikati war-ruuh Ahaitaan Raksyaan Kasy-lakh Qasy-lamaqamsy qasy-lamaqamsy Raasy Iisyaayaqasy Tadar Tiyaar tiyaar Kiitaal Wah-yaahuum Wayaashuum 'Alyaa-ham Wahaayim Thalthiyaakh Ah-yaakam Rifyaadiim 'Asyaaram Bij-ryaakam Bij-baruut jabaruut* …

Status: ⚠️ kitab tidak memberi makna; sebagian unsur (Ah-yaa Saraah-yaa, Bij-baruut jabaruut) bersinggungan dengan §1 dan §4.

### 3.6 Rujukan silang di indeks kitab

| Entri indeks | Indonesia (repo) | Rujukan |
|---|---|---|
| 16 · الجلب السرياني | Pemanggilan/penarikan berbahasa Suryani | BATCH_35.md:312 (PDF 103 = cetak 102) |

---

## 4. Belum teridentifikasi / daftar periksa lanjutan (❔)

1. **Akar Semitik 57 nama leksikon §2.** Kitab hanya memberi makna Arab; akar Ibrani/Aram tiap nama belum diverifikasi di repo. Usulan langkah: bandingkan tiap entri dengan leksikon Aram/Suryani (mis. *malkutha*, *šəlāmā* sudah cocok dengan §1 entri 8–9) dan catat mana yang berpadanan — **jangan** menaikkan status sebelum ada rujukan.
2. **Lanjutan daftar makna setelah `عَيْطَلَا`.** Periksa pindaian halaman cetak 45–46 (PDF 46–47) untuk memastikan daftar memang berhenti.
3. **Nama seruan pada BATCH_02.md:134/138** (`Ghasyyaal, Hadriyaal, Lahfayaal, Barqiyaal, Nuuriyaal, 'Asyyaal, Ghasyyaal, Falaayaal, 'an Tiriyaal, Sarhiyaal`) — tanpa makna; pelafalan tentatif.
4. **Nama-nama Haikal** (`بعلشاقش`, `أقشامقش`, dst.) yang disebut BATCH_07.md:368 sebagai telah muncul di halaman-halaman sebelumnya — cocokkan dengan rantai §3.5.
5. **`جَبَرُوت` (jabaruut)** — istilah dipakai kitab; akar Aram `g'vurta` layak dicek, tetapi belum dirujuk repo.
6. **Rumus «Syallim Namuwaah»** (BATCH_02.md:108) — bunyinya mengingatkan *syallamun* (§1 entri 9), tetapi repo **tidak** menghubungkan keduanya; status ❔.

---

## 5. Cara mengaudit berkas ini

Semua entri dapat diraba ulang dari repo dengan perintah berikut:

```bash
# 1) seluruh catatan editorial bertema Ibrani/Aram/Suryani
grep -n -iE 'Ibrani|Aram|Suryani' BATCH_*.md TERJEMAHAN.md

# 2) leksikon makna nama Suryani (sumber §2)
sed -n '429,485p' BATCH_09.md

# 3) rantai al-Jalb as-Suryani (sumber §3.2–3.5)
sed -n '136,218p' BATCH_04.md

# 4) hijab Sulaiman (sumber §3.1)
sed -n '126,130p' BATCH_05.md

# 5) pastikan tidak ada berkas KAMUS lain di seluruh histori
git log --all --diff-filter=A --name-only -- '*KAMUS*'
git log --all --diff-filter=A --name-only -- '*SURYANI*'
```

Cara memeriksa status lakuna (kenapa berkas “802 baris” tidak ada): lihat pesan commit di `git show --stat cb2e13b` dan riwayat PR #1–#3 pada repo — tidak ada commit yang memuat berkas bernama `KAMUS_SURYANI_ASROR_35_BATCH.md`.

---

## 6. Rujukan lengkap

| Sumber | Isi yang dipakai |
|---|---|
| BATCH_01.md:353 (PDF 4 = cetak 3) | `عليون` — Elyon/'Illiyyun (⚠️) |
| BATCH_02.md:102/108/116 (PDF 7 = cetak 6) | `يَا هِيًا شَرًا هِيًا أَدُونَيَّا أَصْبَاؤُوتِي عَلِي شَدَايَّا`; Adonai Tseva'ot El Shaddai; Metatron |
| BATCH_02.md:134/138 (PDF 8 = cetak 7) | daftar nama malaikat tanpa makna |
| BATCH_04.md:136–156 (PDF 17 = cetak 16) | al-Jalb as-Suryani — judul + rantai utama |
| BATCH_04.md:164–176 (PDF 18 = cetak 17) | sambungan rantai + pola prefiks *b-* |
| BATCH_04.md:182–194 (PDF 18 = cetak 17) | «nama yang cepat lagi tersimpan» |
| BATCH_04.md:202–216 (PDF 18 = cetak 17) | «akhir nama yang tersimpan» |
| BATCH_04.md:242 (PDF 19 = cetak 18) | catatan Ibrani/Aram: El Shaddai, subbuh quddus, Tseva'ot, ma'arabim, prefiks *b-* |
| BATCH_05.md:128 (PDF 22 = cetak 21) | hijab Sulaiman: `أَرْكَاضِ أَصْبَاوْتَ آلَ شَدَّاي` |
| BATCH_05.md:262–280 (PDF 24 = cetak 23) | hijab kekuatan: `Ashbaa'uta Aala Syaddaay` / `Adunaay` |
| BATCH_06.md:248 (PDF 29 = cetak 28) | Aram/Suryani: malkutha, deh-hitha/dehlilwa, El Metatron, Ehyeh Syerehyah Adonai Tseva'ot, syallamun |
| BATCH_07.md:368 (PDF 35 = cetak 34) | abjad alef-bet `أبجد هوز حطي بكد زهج` + `بدوح أجهزط` |
| BATCH_09.md:429–485 (PDF 44–45 = cetak 43–44) | **leksikon 57 nama Suryani** (sumber utama §2) |
| BATCH_35.md:312 (PDF 103 = cetak 102) | indeks: `الجلب السرياني` |
| TERJEMAHAN.md (paralel) | salinan catatan yang sama dengan batch di atas |

---

*Dibangun pada 2026-10-05 di branch `arena/01a10c17-kitab-asrorsulaimaniyyah`. Berkas ini menggantikan sementara `KAMUS_SURYANI_ASROR_35_BATCH.md` yang hilang; bila berkas asli ditemukan/diunggah, gabungkan entri tambahannya ke §2–§4 dengan tetap menyertakan rujukan baris.*
