# Report Bagian E: Temporal Association Analysis

| | |
|---|---|
| Penanggung jawab | Mahesa Andre (13523140) |
| Tanggal selesai | 23 November 2026 |
| Status | Selesai, belum di-commit saat report ini ditulis. |
| Notebook | `notebooks/07_temporal.ipynb`, dibangkitkan oleh `src/build_temporal_notebook.py` |
| Kode | `src/temporal.py`, memakai `src/fpgrowth.py` dan `src/rules.py`; test di `tests/test_temporal.py` |

> **Penanda [PU-n]**: klaim yang memakai pengetahuan umum di luar data DBLP (misalnya nama bidang sebuah konferensi). Seluruh angka di report ini berasal dari notebook 07. Daftar klaim [PU-n] ada di akhir bagian 6.

---

## 1. Ringkasan

FP-Growth dan association rules (min confidence 50%) dijalankan pada author-year-based database yang dipotong menjadi empat periode, dengan tiga min support (0,01%, 0,02%, 0,05%). Min support utama untuk perbandingan adalah 0,02%.

Temuan utama:
- **Kombinasi konferensi dalam satu tahun makin terpusat pada konferensi AI.** **[PU-1]** Pasangan teratas bergeser dari GLOBECOM + ICC (2015-2017) ke ICLR + NeurIPS (2024-2025). Pada 2024-2025, sembilan dari sepuluh pasangan teratas memuat NeurIPS, ICLR, ICML, ACL, EMNLP, atau AAAI.
- **Hampir semua rules adalah rules baru.** Dari 1.904 rules berbeda, 98% muncul di periode akhir, hanya satu yang bertahan di keempat periode (AISTATS + ICML → NeurIPS), 11 hilang, dan 27 berselang.
- **Rules yang "hilang" tidak benar-benar hilang.** Rules GLOBECOM/ICC memiliki count yang datar, sedangkan database bertambah, sehingga support-nya turun di bawah ambang. Dua rule hilang hanya karena DBLP tidak mencatat ICCC pada 2024-2025.
- **Rules berselang sebagian besar mengikuti jadwal konferensi.** 15 dari 27 memuat konferensi yang tidak tercatat setiap tahun (ICCV pada tahun ganjil, ECCV pada tahun genap, ASRU, SLT, COLING, Odyssey).
- **Tren yang paling dapat dipercaya adalah 95 rules yang muncul pada 2018-2023** dan bertahan sampai 2024-2025 (94% sampai 95% tahan uji ketahanan). Rules yang hanya ada pada 2024-2025 (1.770) lebih rapuh (65% tahan uji).

---

## 2. Spesifikasi dan pemenuhannya

| Poin soal Bagian E | Status | Bagian notebook |
|---|---|---|
| Gunakan author-year-based database dengan empat periode | Selesai, dipotong menurut tahun | 3 |
| 1. Jalankan frequent pattern mining pada setiap periode | Selesai, FP-Growth, tiga min support | 4 |
| 2. Identifikasi frequent itemsets pada setiap periode | Selesai, jumlah per ukuran dan sepuluh teratas | 4 |
| 3. Bangkitkan association rules untuk setiap periode | Selesai, min confidence 50% | 5 |
| 4. Bandingkan rules antarperiode | Selesai, empat kategori | 7 |
| 5. Identifikasi pola yang bertahan dan yang berubah | Selesai, termasuk penyebab rule tidak lolos | 7 |
| 6. Jelaskan kemungkinan perubahan tren publikasi | Selesai | 8 |

---

## 3. Metode

### 3.1 Data per periode
Masukan adalah `tx_author_year.parquet` dan `tx_author_year_index.parquet` dari notebook 02. Task 3 hanya membangun dua database, sehingga periode dibentuk dengan menyaring kolom `year` (`period_transactions`). Penyebut support adalah seluruh transaksi pada periode itu, termasuk transaksi berisi satu konferensi.

| Periode | Tahun | Transaksi | Berisi ≥ 2 konferensi | Rata-rata konferensi | Transaksi ≥ 20 konferensi | Maks |
|---|---|---|---|---|---|---|
| 2015-2017 | 3 | 922.051 | 29,2% | 1,57 | 137 | 43 |
| 2018-2020 | 3 | 1.080.824 | 28,2% | 1,55 | 272 | 48 |
| 2021-2023 | 3 | 1.195.907 | 28,1% | 1,57 | 511 | 70 |
| 2024-2025 | 2 | 886.812 | 30,8% | 1,68 | 582 | 85 |

### 3.2 Mining
- FP-Growth (`src/fpgrowth.py`) saja, sesuai keputusan D2. FP-Growth sudah divalidasi terhadap `mlxtend` pada Task 4, dan Task 6 menunjukkan Apriori memberi hasil yang sama.
- Rules dengan `src/rules.py`, min confidence 50%.
- Min support 0,01%, 0,02%, dan 0,05%. Ambang ini 10 sampai 100 kali lebih rendah daripada Task 4. Pada 0,1% seperti Task 4, tiga periode pertama hanya menghasilkan 1, 0, dan 3 rules, karena 71% transaksi author-year hanya berisi satu konferensi.

### 3.3 Uji ketahanan
Mining diulang setelah transaksi berisi 20 konferensi atau lebih dalam satu tahun dikosongkan, dengan penyebut tetap. Survival adalah porsi rules asli yang tetap ditemukan.

### 3.4 Pemilihan min support utama
Kriteria ditetapkan sebelum melihat pola: setiap periode memiliki minimal 15 rules dan survival minimal 80%, lalu dipilih ambang terkecil yang lolos. Jika tidak ada yang lolos, jumlah rules tetap menjadi syarat, dan dipilih ambang dengan survival minimum tertinggi di antara yang memenuhinya (`choose_main_level`).

### 3.5 Kategori rule
| Kategori | Kemunculan pada empat periode |
|---|---|
| Bertahan | Lolos di keempat periode |
| Muncul | Tidak lolos di awal, lalu lolos terus sampai 2024-2025 |
| Hilang | Lolos di awal, lalu tidak lolos sampai 2024-2025 |
| Berselang | Pola lain |

Untuk setiap rule, support, confidence, dan lift juga dihitung langsung dari transaksi di setiap periode (`rule_metrics`), termasuk periode saat rule tidak lolos. Penyebab tidak lolos dicatat: konferensi tidak tercatat, support di bawah ambang, atau confidence di bawah 50%. Kolom `tahun_lengkap` menghitung jumlah tahun dalam periode yang mencatat semua konferensi rule.

### 3.6 Pengujian
85 test `pytest` lulus, 17 di antaranya untuk `src/temporal.py`: pemotongan periode (termasuk transaksi kosong), pengosongan transaksi besar, penghitungan support dibandingkan brute force, metrik rule pada contoh hitungan tangan, keempat kategori, dan ketiga cabang pemilihan min support.

---

## 4. Hasil

### 4.1 Frequent itemsets per periode

| min support | Periode | Ambang count | Itemsets | 1 item | 2 item | 3 item | ≥ 4 item | Terpanjang |
|---|---|---|---|---|---|---|---|---|
| 0,01% | 2015-2017 | 93 | 3.045 | 2.123 | 824 | 90 | 8 | 4 |
| | 2018-2020 | 109 | 3.286 | 2.154 | 875 | 235 | 22 | 4 |
| | 2021-2023 | 120 | 3.882 | 2.080 | 1.067 | 559 | 176 | 5 |
| | 2024-2025 | 89 | 8.766 | 1.821 | 1.990 | 2.062 | 2.893 | 7 |
| 0,02% | 2015-2017 | 185 | 1.879 | 1.600 | 259 | 19 | 1 | 4 |
| | 2018-2020 | 217 | 1.935 | 1.559 | 322 | 54 | 0 | 3 |
| | 2021-2023 | 240 | 2.130 | 1.468 | 452 | 186 | 24 | 4 |
| | 2024-2025 | 178 | 3.646 | 1.266 | 875 | 795 | 710 | 6 |
| 0,05% | 2015-2017 | 462 | 854 | 812 | 40 | 2 | 0 | 3 |
| | 2018-2020 | 541 | 810 | 729 | 76 | 5 | 0 | 3 |
| | 2021-2023 | 598 | 862 | 697 | 136 | 29 | 0 | 3 |
| | 2024-2025 | 444 | 1.196 | 617 | 287 | 210 | 82 | 5 |

Sepuluh pasangan teratas (0,02%):

| # | 2015-2017 | 2018-2020 | 2021-2023 | 2024-2025 |
|---|---|---|---|---|
| 1 | GLOBECOM + ICC | CVPR + ECCV | ICML + NeurIPS | ICLR + NeurIPS |
| 2 | ACC + CDC | GLOBECOM + ICC | ACL + EMNLP | ICML + NeurIPS |
| 3 | ICRA + IROS | ICML + NeurIPS | CVPR + ICCV | CVPR + NeurIPS |
| 4 | ECOC + OFC | ICRA + IROS | ICLR + NeurIPS | ACL + EMNLP |
| 5 | GLOBECOM + VTC Fall | AAAI + IJCAI | CVPR + NeurIPS | ICLR + ICML |
| 6 | ICC + VTC Fall | ACL + EMNLP | AAAI + NeurIPS | AAAI + NeurIPS |
| 7 | AAAI + IJCAI | ICASSP + INTERSPEECH | GLOBECOM + ICC | EMNLP + NeurIPS |
| 8 | ICASSP + INTERSPEECH | ICLR + NeurIPS | AAAI + CVPR | ACL + NeurIPS |
| 9 | CVPR + ICCV | CVPR + NeurIPS | ICLR + ICML | CVPR + ICCV |
| 10 | ICC + WCNC | AAAI + CVPR | ICASSP + INTERSPEECH | AAAI + CVPR |

Support ICLR + NeurIPS: 0,18% (2018-2020) menjadi 1,04% (2024-2025). Support GLOBECOM + ICC: 0,32% (2015-2017) menjadi 0,27% (2021-2023), lalu keluar dari sepuluh besar.

### 4.2 Rules per periode

| min support | 2015-2017 | 2018-2020 | 2021-2023 | 2024-2025 |
|---|---|---|---|---|
| 0,01% | 70 | 130 | 480 | 7.741 |
| 0,02% | 17 | 32 | 113 | 1.874 |
| 0,05% | 2 | 4 | 25 | 282 |

Pada 0,02%, median lift turun dari 49,1 dan 49,2 ke 28,0 dan 20,2, dan rule satu-ke-satu hanya 2, 1, 1, dan 0.

Sepuluh lift tertinggi 2015-2017 (0,02%) tersebar di banyak kelompok: AISTATS + ICML → NeurIPS (lift 113,8), ASRU + ICASSP → INTERSPEECH (104,9), ECOC + ICTON → OFC (77,1), ASRU → INTERSPEECH (72,9), ACC + ECC → CDC (68,0), ECOC → OFC (59,8), dan empat rule GLOBECOM/ICC. Sepuluh lift tertinggi 2024-2025 seluruhnya rule tiga atau empat konferensi menuju dua konferensi yang memuat ACL atau EMNLP bersama ICLR atau ICML, dengan count hanya 184 sampai 279. Contoh teratas: EMNLP + ICLR + ACM Multimedia + NeurIPS → ACL + ICML (lift 161,9).

### 4.3 Uji ketahanan dan min support utama

| min support | 2015-2017 | 2018-2020 | 2021-2023 | 2024-2025 |
|---|---|---|---|---|
| 0,01% | 96% | 100% | 93% | 64% |
| 0,02% | 94% | 100% | 98% | 67% |
| 0,05% | 100% | 100% | 96% | 78% |

Tidak ada ambang yang memenuhi kedua kriteria. 0,05% tidak memenuhi syarat jumlah rules (2 dan 4). Di antara 0,01% dan 0,02%, survival minimum tertinggi dimiliki 0,02% (67%), sehingga **0,02% dipilih**. Dari sepuluh lift tertinggi 2024-2025 pada 0,02%, hanya empat yang tahan uji, dan keempat rule yang memuat ACM Multimedia tidak tahan.

### 4.4 Kategori rules

| Kategori | 0,01% | 0,02% (utama) | 0,05% |
|---|---|---|---|
| Bertahan | 13 | 1 | 0 |
| Hilang | 39 | 11 | 2 |
| Berselang | 113 | 27 | 7 |
| Muncul | 7.704 | 1.865 | 281 |

Rules muncul pada 0,02% menurut periode pertama lolos:

| Pola | Rules | Tahan uji pada 2024-2025 |
|---|---|---|
| ✗✓✓✓ (sejak 2018-2020) | 16 | 94% |
| ✗✗✓✓ (sejak 2021-2023) | 79 | 95% |
| ✗✗✗✓ (hanya 2024-2025) | 1.770 | 65% |

### 4.5 Rules bertahan dan hilang (0,02%)

| Kategori | Rule | Confidence 2015-17 / 18-20 / 21-23 / 24-25 | Count 2015-17 / 18-20 / 21-23 / 24-25 | Tahun lengkap |
|---|---|---|---|---|
| Bertahan | AISTATS + ICML → NeurIPS | 60% / 61% / 61% / 58% | 204 / 499 / 716 / 622 | 3 / 3 / 3 / 2 |
| Hilang | ICC + ICCC → GLOBECOM | 56% / 58% / 59% / - | 210 / 256 / 325 / 0 | 3 / 3 / 3 / 0 |
| Hilang | GLOBECOM + ICCC → ICC | 51% / 55% / 47% / - | 210 / 256 / 325 / 0 | 3 / 3 / 3 / 0 |
| Hilang | ECOC + ICTON → OFC | 67% / 62% / - / 64% | 360 / 243 / 0 / 173 | 2 / 2 / 0 / 1 |
| Hilang | ACC + ECC → CDC | 56% / 54% / 49% / 51% | 259 / 276 / 170 / 140 | 2 / 3 / 3 / 2 |
| Hilang | ECOC → OFC | 52% / 47% / 48% / 44% | 1.721 / 1.558 / 600 / 1.180 | 2 / 2 / 1 / 1 |
| Hilang | GLOBECOM + WCSP → ICC | 52% / 47% / 44% / 40% | 240 / 226 / 209 / 78 | 3 / 3 / 3 / 1 |
| Hilang | ICC + WCSP → GLOBECOM | 54% / 49% / 63% / 49% | 240 / 226 / 209 / 78 | 3 / 3 / 3 / 1 |
| Hilang | GLOBECOM + SPAWC → ICC | 63% / 49% / 59% / 54% | 236 / 194 / 203 / 158 | 3 / 3 / 3 / 2 |
| Hilang | ICC + SPAWC → GLOBECOM | 55% / 51% / 56% / 56% | 236 / 194 / 203 / 158 | 3 / 3 / 3 / 2 |
| Hilang | ASRU → INTERSPEECH | 50% / 44% / 44% / 47% | 363 / 221 / 619 / 409 | 2 / 1 / 2 / 1 |
| Hilang | GLOBECOM + WCNC → ICC | 52% / 48% / 50% / 46% | 475 / 521 / 496 / 533 | 3 / 3 / 3 / 2 |

Ambang count pada 0,02%: 185, 217, 240, 178. Penyebab tidak lolos pada rules hilang (28 kombinasi rule-periode): 13 support, 12 confidence, 3 konferensi tidak tercatat.

### 4.6 Rules berselang dan jadwal konferensi
Author unik per tahun menunjukkan ICCV hanya tercatat pada tahun ganjil dan ECCV pada tahun genap, sehingga 2015-2017 dan 2021-2023 memiliki dua edisi ICCV dan satu edisi ECCV, sedangkan 2018-2020 sebaliknya. 15 dari 27 rule berselang memuat konferensi dengan jumlah edisi berbeda antarperiode:
- Keenam rule ICCV (misalnya BMVC + ICCV → CVPR, ICCV + MICCAI → CVPR) hanya lolos pada 2021-2023.
- Tiga rule ACCV/BMVC dengan ECCV hanya lolos pada 2018-2020.
- SLT → INTERSPEECH, Odyssey → INTERSPEECH, dan AAAI + COLING → EMNLP lolos pada periode dengan edisi terbanyak.
- Pengecualian: dua rule ASRU dan ECCV + WACV → CVPR juga lolos pada 2024-2025 dengan satu edisi.

12 rule sisanya (NLP, AAAI, GLOBECOM/ICC) memiliki edisi lengkap di setiap periode, dan berselang karena confidence atau support-nya berada di sekitar ambang.

### 4.7 Konferensi per kategori (0,02%)

| Kategori | Konferensi yang paling sering terlibat |
|---|---|
| Muncul (1.865) | NeurIPS 67%, ICLR 47%, ACL 45%, AAAI 43%, EMNLP 42%, ICML 40%, CVPR 35% |
| Hilang (11) | GLOBECOM 64%, ICC 64%, lalu ECOC, ICCC, OFC, SPAWC, WCSP masing-masing 18% |
| Berselang (27) | CVPR 41%, ICCV 22%, AAAI, GLOBECOM, ICC masing-masing 19% |

---

## 5. Jawaban pertanyaan Bagian E

**1-2. Frequent pattern mining dan frequent itemsets per periode.** FP-Growth dijalankan pada empat periode dan tiga ambang (12 run). Pada 0,02%, itemset kombinasi berjumlah 279, 376, 662, dan 2.380. Jumlah konferensi tunggal yang frequent justru turun (1.600 ke 1.266) meskipun ambang count 2024-2025 paling rendah, sehingga author makin terkumpul pada konferensi yang sama. Pasangan teratas bergeser dari GLOBECOM + ICC, ACC + CDC, ICRA + IROS, dan ECOC + OFC pada 2015-2017 ke ICLR + NeurIPS, ICML + NeurIPS, CVPR + NeurIPS, dan ACL + EMNLP pada 2024-2025.

**3. Association rules per periode.** Pada 0,02%: 17, 32, 113, dan 1.874 rules. Median lift turun dari 49,1 ke 20,2, karena rules baru menuju konferensi besar yang support-nya tinggi (temuan yang sama dengan Task 5).

**4. Perbandingan rules antarperiode.** Dari 1.904 rules berbeda, 1.865 (98%) muncul, 1 bertahan, 11 hilang, dan 27 berselang. Gambaran yang sama terlihat pada 0,01% dan 0,05%: rules muncul 97% sampai 98%, dan rules bertahan sangat sedikit (13, 1, 0). Jumlah pasti rules bertahan bergantung pada ambang, tetapi polanya tidak.

**5. Pola yang bertahan dan yang berubah.**
- *Bertahan:* AISTATS + ICML → NeurIPS. Sekitar 60% author-tahun yang publish di AISTATS dan ICML juga publish di NeurIPS pada tahun yang sama, di setiap periode, sementara count-nya naik dari 204 menjadi 716.
- *Hilang:* 11 rules, didominasi GLOBECOM dan ICC. Penyebabnya bukan hubungan yang berhenti. Count rules ini relatif datar (GLOBECOM + WCNC → ICC: 475, 521, 496, 533), sedangkan ambang count naik karena database bertambah. Confidence-nya setelah tidak lolos tetap 40% sampai 64%. Dua rule ICCC hilang karena DBLP tidak mencatat ICCC pada 2024-2025, dan rules ECOC/ICTON dipengaruhi tahun yang tidak tercatat. Hanya ACC + ECC → CDC yang count-nya juga turun secara absolut (259 ke 140).
- *Berselang:* 15 dari 27 mengikuti jumlah edisi konferensi yang tidak tercatat setiap tahun, sehingga lebih mencerminkan jadwal daripada perubahan minat.
- *Muncul:* 95 rules yang muncul sejak 2018-2020 atau 2021-2023 dan bertahan sampai 2024-2025, 94% sampai 95% tahan uji. Ditambah 1.770 rules yang hanya ada pada 2024-2025, 65% tahan uji.

**6. Kemungkinan perubahan tren publikasi.**
1. *Konferensi AI menjadi pusat kombinasi.* **[PU-1]** NeurIPS terlibat pada 67% rules yang muncul, diikuti ICLR, ACL, AAAI, EMNLP, ICML, dan CVPR. Ini sejalan dengan Task 2, tempat NeurIPS, ICML, EMNLP, ACL, CVPR, dan ICLR tumbuh paling cepat dan porsi sepuluh konferensi teratas naik dari 7,0% ke 11,7%.
2. *Author AI makin sering publish di beberapa konferensi besar pada tahun yang sama.* Itemset berukuran empat atau lebih naik dari 1 (2015-2017) ke 710 (2024-2025) pada 0,02%, dan kombinasinya melintasi NLP dan machine learning (misalnya ACL + EMNLP + ICLR + ICML). **[PU-1]** Rata-rata konferensi per transaksi hanya naik sedikit (1,57 ke 1,68), sehingga perubahan ini terkonsentrasi pada konferensi AI, bukan pada seluruh author.
3. *Bidang lain stabil secara absolut tetapi mengecil secara relatif.* **[PU-2]** Kombinasi telekomunikasi, kendali, dan komunikasi optik memiliki count yang relatif tetap, sementara jumlah author-tahun bertambah, sehingga support-nya turun di bawah ambang.
4. *Sebagian perubahan berasal dari data, bukan tren.* Jadwal konferensi yang tidak tahunan, tahun yang tidak tercatat di DBLP, data 2025 yang belum lengkap, dan transaksi besar pada 2024-2025 ikut membentuk kategori rules.

**Kaitan dengan pertanyaan kesimpulan.**
- *H.5 (perbedaan author-based dan author-year-based):* Author-year-based memerlukan min support 10 sampai 100 kali lebih rendah. Pada 0,1%, author-based menghasilkan 1.387 rules, sedangkan setiap periode author-year menghasilkan 0 sampai 60. Author-based menangkap riwayat publikasi seumur periode (misalnya ICCV dan ECCV dalam satu transaksi), sedangkan author-year hanya menangkap konferensi pada tahun yang sama. Karena itu author-year tidak pernah memasangkan ICCV dan ECCV, tetapi dapat memperlihatkan perubahan pola dari periode ke periode. Kelompok konferensi yang ditemukan sama pada kedua representasi (NeurIPS-ICML-ICLR, ACL-EMNLP, CVPR-ICCV/ECCV, GLOBECOM-ICC).
- *H.7 (insight utama):* bagian ini menambahkan dimensi waktu: asosiasi konferensi makin terpusat pada konferensi AI, dan sebagian besar pola baru muncul pada 2021-2025.

---

## 6. Keterbatasan

1. **Data 2025 belum lengkap dan periode terakhir hanya dua tahun.** Support relatif terhadap jumlah transaksi periode, tetapi tidak mengoreksi edisi 2025 yang belum tercatat.
2. **Cakupan DBLP per tahun tidak lengkap** untuk ICCC (2024-2025), ECOC (2016, 2019, 2022-2024), ICTON (2021-2022), WCSP dan workshop ICCV (2025), dan ICLR (2015-2016).
3. **Konferensi yang tidak tercatat setiap tahun** (ICCV, ECCV, ASRU, SLT, COLING, Odyssey) membuat jumlah edisi per periode berbeda.
4. **Rules 2024-2025 kurang tahan uji.** Hanya 67% rules 2024-2025 pada 0,02% yang tetap ditemukan tanpa 582 transaksi berisi 20 konferensi atau lebih. Kriteria survival 80% tidak terpenuhi pada periode ini (keputusan D6).
5. **Kategori peka terhadap ambang.** Banyak rule memiliki confidence di sekitar 50%, dan jumlah rules bertahan berubah dari 13 ke 0 antara 0,01% dan 0,05%.
6. **Transaksi tidak saling bebas.** Author yang aktif setiap tahun muncul di banyak transaksi (keterbatasan author-year-based dari notebook 02).
7. Keterbatasan Task 4 tetap berlaku: item adalah key DBLP, dan identitas author mengikuti disambiguasi DBLP.

### Klaim berbasis pengetahuan umum

| Kode | Klaim | Sumber | Dukungan data DBLP | Status |
|---|---|---|---|---|
| PU-1 | NeurIPS, ICLR, ICML, AAAI, ACL, EMNLP, dan CVPR disebut "konferensi AI", dan ACL/EMNLP/NAACL disebut NLP, NeurIPS/ICML/ICLR disebut machine learning | Pengetahuan umum penulis | Judul proceedings di `data/processed/venue_proceedings.csv` memuat "Computational Linguistics", "Machine Learning", dan "Computer Vision" (diperiksa pada Task 5). Istilah payung "konferensi AI" dan AAAI belum diperiksa | Sebagian didukung; istilah "konferensi AI" adalah pengelompokan penulis |
| PU-2 | GLOBECOM/ICC/WCNC/SPAWC disebut telekomunikasi, ACC/CDC/ECC disebut kendali, ECOC/OFC disebut komunikasi optik, ICRA/IROS disebut robotika | Pengetahuan umum penulis | Untuk ECOC/OFC, GLOBECOM/ICC/SPAWC, dan ICRA ("Robotics and Automation") didukung judul proceedings (Task 5 PU-1). ACC/CDC/ECC dan IROS belum diperiksa | Sebagian didukung; ACC/CDC/ECC dan IROS belum diperiksa |

---

## 7. Keputusan dan penyimpangan dari plan

| Kode | Keputusan |
|---|---|
| D1 | Periode dibentuk saat runtime dengan menyaring `year`; tidak ada file data baru. |
| D2 | FP-Growth saja, tanpa validasi `mlxtend` (keputusan user). |
| D3 | Tiga min support (0,01%, 0,02%, 0,05%), dijalankan semua, lalu min support utama dipilih dengan kriteria yang ditetapkan sebelumnya. |
| D4 | Empat kategori rule dan metrik langsung dari transaksi untuk periode saat rule tidak lolos. |
| D5 | Uji ketahanan dengan mengosongkan transaksi berisi 20 konferensi atau lebih. |
| D6 | **Penyimpangan**: tidak ada ambang yang lolos kriteria survival 80% karena 2024-2025. Aturan cadangan awal (survival minimum tertinggi) memilih 0,05% yang hanya memiliki 2 dan 4 rules di periode awal. Aturan cadangan diubah agar jumlah rules tetap menjadi syarat, sehingga terpilih 0,02% (pilihan user). |
| D7 | Penyebab rule tidak lolos dan `tahun_lengkap` ditambahkan setelah hasil pertama menunjukkan beberapa rule hilang karena konferensi tidak tercatat. |

---

## 8. Pekerjaan tersisa

- PU-2 untuk ACC/CDC/ECC dan IROS belum diperiksa ke judul proceedings.
- Bagian E belum memakai Apriori; jika dosen meminta kedua algoritma untuk setiap eksperimen, Apriori dapat dijalankan pada 12 kombinasi yang sama.

---

## 9. File, reproduksi, dan commit

`data/` dan `outputs/` tidak masuk git (dibagikan lewat zip).

**File input**

| File | Asal | Isi |
|---|---|---|
| `data/processed/tx_author_year.parquet` | notebook 02 | Author-year-based database, tabel panjang `(tid, item)` |
| `data/processed/tx_author_year_index.parquet` | notebook 02 | `tid`, `author`, `year`, `n_paper`; hanya `tid` dan `year` dipakai |
| `data/processed/tx_items.csv` | notebook 02 | Nama konferensi per `item_id` |

**File output: data** (`outputs/temporal/`)

| File | Isi |
|---|---|
| `itemsets_<periode>_<tag>.parquet` (12 file) | Frequent itemsets per periode dan min support. Kolom: `itemset` (list `item_id`), `count`, `support`. Periode: `2015-2017`, `2018-2020`, `2021-2023`, `2024-2025`; tag: `0p01`, `0p02`, `0p05` |
| `rules_<periode>_<tag>.parquet` (12 file) | Rules per periode dan min support. Kolom sama dengan `outputs/rules/` Task 5: `antecedent`, `consequent`, `n_antecedent`, `n_consequent`, `count`, `antecedent_count`, `consequent_count`, `support`, `confidence`, `lift`, `rule` |

**File output: tabel** (`outputs/tables/`)

| File | Isi |
|---|---|
| `t7_profil_periode.csv` | Profil transaksi per periode (4 baris) |
| `t7_itemset_per_periode.csv` | Jumlah itemsets per ukuran, per periode dan min support (12 baris) |
| `t7_top_itemset.csv` | Sepuluh itemset ≥ 2 konferensi teratas per periode, 0,02% (40 baris) |
| `t7_rules_per_periode.csv` | Jumlah rules, rule satu-ke-satu, median lift (12 baris) |
| `t7_top_rules.csv` | Sepuluh lift tertinggi per periode, 0,02% (40 baris) |
| `t7_robustness.csv` | Jumlah rules dan survival per periode dan min support (12 baris) |
| `t7_kategori_rules.csv` | 1.904 rules pada min support utama: pola, kategori, confidence/lift/count di keempat periode, tahan uji 2024-2025 |
| `t7_kategori_sensitivitas.csv` | Jumlah per kategori pada ketiga min support |
| `t7_alasan_tidak_lolos.csv` | Per rule dan periode: tahun lengkap, count, confidence, alasan (7.616 baris) |
| `t7_berselang_edisi.csv` | Tahun lengkap per periode untuk 27 rule berselang |
| `t7_konferensi_kategori.csv` | Jumlah dan porsi rules per konferensi per kategori |
| `t7_cv_per_tahun.csv` | Author unik per tahun untuk CVPR, ICCV, ECCV |

**File output: gambar** (`outputs/figures/`): `t7_rules_per_periode.png`, `t7_rules_bertahan_hilang.png`

**Kode dan notebook** (masuk git)

| File | Isi |
|---|---|
| `src/temporal.py` | `PERIODS`, `period_transactions`, `drop_large`, `support_counts`, `rule_metrics`, `classify_presence`, `choose_main_level` |
| `src/build_temporal_notebook.py` | Pembangkit notebook 07 |
| `tests/test_temporal.py` | 17 test (total 85 di `tests/`) |
| `notebooks/07_temporal.ipynb` | Notebook hasil eksekusi |
| `docs/reports/task-E-report.md` | Report ini |
| `laporan/bab/bab4-taskE.tex`, `laporan/images/hasil/t7_rules_per_periode.png` | Subbab IV.7 laporan; Bab I, III, dan V ikut diperbarui |

**Reproduksi** (dari akar repo):
```bash
.venv/Scripts/python -m pytest tests
.venv/Scripts/python src/build_temporal_notebook.py
.venv/Scripts/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=dm-dblp --ExecutePreprocessor.timeout=-1 notebooks/07_temporal.ipynb
```

**Commit**: belum di-commit saat report ini ditulis.

---

## 10. Langkah berikutnya

- Laporan LaTeX Subbab IV.7 dan jawaban kesimpulan 5 dan 7 di Bab V.
- Periksa PU-2 untuk ACC/CDC/ECC dan IROS.
