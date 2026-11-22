# Report Task 4: Frequent Pattern Mining (sisi FP-Growth)

| | |
|---|---|
| Penanggung jawab | Mahesa Andre (13523140), sisi FP-Growth. Sisi Apriori: Harfhan Ikhtiar (notebook `03_apriori`). |
| Tanggal selesai | 21 November 2026 |
| Status | Selesai dan di-commit di branch `fp-growth-t4`. Lima perbaikan kecil di notebook masih menunggu (lihat bagian 8). |
| Notebook | `notebooks/04_fpgrowth.ipynb`, dibangkitkan oleh `src/build_fpgrowth_notebook.py` |
| Kode | `src/fpgrowth.py`, `src/fpm_data.py`, `src/validation.py`, test di `tests/` |

---

## 1. Ringkasan

FP-Growth diimplementasikan sendiri dan dijalankan pada author-based transactional database (1.821.757 transaksi, 4.373 item) dengan min support 0,1%, 0,5%, 1%, dan 2%. Hasilnya identik dengan `mlxtend` pada keempat min support.

Temuan utama:
- Hanya min support **0,1%** yang menghasilkan pola kombinasi yang kaya (1.514 itemset, sampai 6 konferensi). Pada 2% tidak ada satu pun pasangan konferensi yang frequent.
- Kombinasi yang frequent **mengelompok per bidang**: machine learning, computer vision, NLP, dan robotika.
- **NeurIPS menjadi penghubung**. Pasangan teratas adalah ICML + NeurIPS (18.503 author).
- **Populer belum tentu terhubung**. EMBC, IGARSS, dan HCI termasuk sepuluh konferensi terbesar, tetapi hampir tidak membentuk pasangan frequent.

---

## 2. Spesifikasi dan pemenuhannya

| Poin soal Task 4 | Status | Bagian notebook |
|---|---|---|
| Implementasi FP-Growth pada Author-Based DB | Selesai, implementasi sendiri, divalidasi `mlxtend` | 3, 5 |
| Eksperimen min support 0,1%, 0,5%, 1%, 2% | Selesai | 4 |
| 1. Frequent itemsets per eksperimen | Selesai | 4 |
| 2. Identifikasi 1-, 2-, 3-itemsets | Selesai | 6.1, 6.2 |
| 3. 10 itemset dengan support tertinggi | Selesai, per min support | 6.2 |
| 4. Pengaruh min support | Selesai, tabel dan grafik | 6.3 |
| 5. Kombinasi yang paling sering muncul bersama | Selesai | 6.4, 6.5 |
| 6. Interpretasi | Selesai, dua klaim perlu dilunakkan | 7 |
| Implementasi Apriori | Bagian Harfhan (`03_apriori`) | |

---

## 3. Metode

### 3.1 Data
- Masukan: `data/processed/tx_author.parquet`, tabel panjang `(tid, item)` dari notebook `02_transactions`, diubah ke bentuk horizontal (list frozenset kode item per transaksi).
- Satu transaksi = satu author, item = konferensi (seri DBLP) tempat author itu pernah publish selama 2015-2025.
- Support sebuah itemset = jumlah author yang transaksinya memuat seluruh item itemset tersebut, dibagi seluruh transaksi (N = 1.821.757). Satu author dihitung sekali, berapa pun jumlah paper-nya.

### 3.2 Ambang
Min count = bilangan bulat terkecil c dengan c / N ≥ min support.

| min support | Hitungan | min count (author) |
|---|---|---|
| 0,1% | 0,001 × 1.821.757 = 1.821,8 | 1.822 |
| 0,5% | 0,005 × 1.821.757 = 9.108,8 | 9.109 |
| 1% | 0,01 × 1.821.757 = 18.217,6 | 18.218 |
| 2% | 0,02 × 1.821.757 = 36.435,1 | 36.436 |

### 3.3 Algoritma
Implementasi di `src/fpgrowth.py`, mengikuti empat aturan mining dari bab metodologi laporan:
1. **Pemangkasan item**: item yang tidak frequent dibuang sebelum mining.
2. **Penyebut tetap N**: transaksi dengan kurang dari dua item frequent tidak dimasukkan ke FP-tree (transaction reduction), tetapi tetap dihitung di penyebut. Support 1-itemset diambil dari pemindaian pertama.
3. **Waktu dipisah**: `t_build` (pemindaian, pemangkasan, pembentukan pohon) dan `t_mine` (penambangan rekursif). Pemuatan data tidak dihitung.
4. **Validasi**: itemset dan count harus identik dengan `mlxtend`.

Detail lain:
- Node FP-tree menyimpan `item`, `count`, `parent`, `children`, ditambah header table.
- Urutan item di pohon: count menurun, lalu id item menaik (deterministik).
- Transaksi yang identik setelah dipangkas digabung dan dimasukkan sekali dengan bobotnya.
- Penambangan rekursif dari conditional pattern base, tanpa pembangkitan kandidat.

### 3.4 Pengujian
36 test `pytest` di `tests/`, semuanya lulus:
- Contoh buku teks Han, Kamber, dan Pei (2012): bentuk FP-tree dan 13 frequent itemsets cocok persis.
- 16 kasus acak dibandingkan dengan brute force (menghitung semua subset).
- Transaksi kosong dan transaksi satu item tetap masuk penyebut.
- Kesepakatan dengan `mlxtend`, termasuk kasus id item yang tidak dimulai dari 0.

---

## 4. Hasil

### 4.1 Jumlah frequent itemsets per ukuran

| min support | min count | Total | 1-itemset | 2-itemset | 3-itemset | ≥4 | Terpanjang |
|---|---|---|---|---|---|---|---|
| 0,1% | 1.822 | 1.514 | 574 | 393 | 348 | 199 | 6 item |
| 0,5% | 9.109 | 88 | 66 | 21 | 1 | 0 | 3 item |
| 1% | 18.218 | 30 | 29 | 1 | 0 | 0 | 2 item |
| 2% | 36.436 | 6 | 6 | 0 | 0 | 0 | 1 item |

### 4.2 Validasi dengan mlxtend

| min support | FP-Growth | mlxtend | Hilang | Kelebihan | Count berbeda | Identik |
|---|---|---|---|---|---|---|
| 0,1% | 1.514 | 1.514 | 0 | 0 | 0 | Ya |
| 0,5% | 88 | 88 | 0 | 0 | 0 | Ya |
| 1% | 30 | 30 | 0 | 0 | 0 | Ya |
| 2% | 6 | 6 | 0 | 0 | 0 | Ya |

### 4.3 Waktu (satu kali run, run final notebook)

| min support | t_build | t_mine |
|---|---|---|
| 0,1% | 8,29 s | 5,29 s |
| 0,5% | 3,12 s | 0,99 s |
| 1% | 2,82 s | 0,21 s |
| 2% | 2,33 s | 0,00 s |

Waktu bervariasi antar run (t_build pada 0,1%: 10,65 s, 6,02 s, dan 8,29 s pada tiga run berbeda). Angka ini bukan untuk perbandingan performa. Perbandingan dengan pengukuran berulang dilakukan di Task 6 (`06_performance`).

### 4.4 Sepuluh itemset dengan support tertinggi

Pada 0,1%, 0,5%, dan 1% hasilnya sama, seluruhnya konferensi tunggal:

| # | Konferensi | Author | Support |
|---|---|---|---|
| 1 | NeurIPS | 57.800 | 3,17% |
| 2 | CVPR | 47.664 | 2,62% |
| 3 | AAAI | 46.437 | 2,55% |
| 4 | ICASSP | 42.057 | 2,31% |
| 5 | EMBC | 39.318 | 2,16% |
| 6 | HCI | 37.884 | 2,08% |
| 7 | IGARSS | 35.229 | 1,93% |
| 8 | EMNLP | 33.954 | 1,86% |
| 9 | ICML | 31.896 | 1,75% |
| 10 | IROS | 31.249 | 1,72% |

Pada 2% hanya enam itemset yang lolos, yaitu nomor 1 sampai 6. IGARSS gugur karena 35.229 < 36.436.

Tidak ada kombinasi yang masuk sepuluh besar karena pasangan teratas (18.503 author) masih lebih kecil dari konferensi ke-10 (IROS, 31.249).

### 4.5 Kombinasi yang paling sering muncul bersama (dari run 0,1%)

**Sepuluh pasangan teratas**

| # | Pasangan | Author | Support | Masih frequent sampai |
|---|---|---|---|---|
| 1 | ICML + NeurIPS | 18.503 | 1,02% | 1% |
| 2 | ICLR + NeurIPS | 17.852 | 0,98% | 0,5% |
| 3 | AAAI + NeurIPS | 15.973 | 0,88% | 0,5% |
| 4 | CVPR + NeurIPS | 15.640 | 0,86% | 0,5% |
| 5 | CVPR + ICCV | 15.441 | 0,85% | 0,5% |
| 6 | ACL + EMNLP | 14.557 | 0,80% | 0,5% |
| 7 | CVPR + ECCV | 13.752 | 0,75% | 0,5% |
| 8 | ICLR + ICML | 12.947 | 0,71% | 0,5% |
| 9 | AAAI + CVPR | 12.169 | 0,67% | 0,5% |
| 10 | ICRA + IROS | 11.860 | 0,65% | 0,5% |

**Sepuluh triple teratas**

| # | Triple | Author |
|---|---|---|
| 1 | ICLR + ICML + NeurIPS | 10.413 (satu-satunya triple yang frequent di 0,5%) |
| 2 | CVPR + ECCV + ICCV | 8.474 |
| 3 | CVPR + ICCV + NeurIPS | 8.407 |
| 4 | AAAI + ICML + NeurIPS | 7.585 |
| 5 | AAAI + ICLR + NeurIPS | 7.371 |
| 6 | AAAI + CVPR + NeurIPS | 7.301 |
| 7 | CVPR + ECCV + NeurIPS | 7.272 |
| 8 | CVPR + ICLR + NeurIPS | 7.157 |
| 9 | AAAI + CVPR + ICCV | 6.477 |
| 10 | CVPR + ICML + NeurIPS | 6.259 |

**Itemset terpanjang (6 konferensi)**

| Itemset | Author |
|---|---|
| AAAI + CVPR + ECCV + ICCV + ICLR + NeurIPS | 2.005 |
| CVPR + ECCV + ICCV + ICLR + ICML + NeurIPS | 1.849 |
| AAAI + CVPR + ECCV + ICCV + ACM Multimedia + NeurIPS | 1.827 |

### 4.6 Keterhubungan konferensi

Konferensi yang besar belum tentu sering dipasangkan dengan konferensi lain. Dari 574 konferensi yang frequent pada 0,1%, hanya **105** yang muncul pada minimal satu pasangan frequent.

Jumlah pasangan frequent untuk sepuluh konferensi terbesar:

| Konferensi | Author | Pasangan frequent |
|---|---|---|
| NeurIPS | 57.800 | 42 |
| CVPR | 47.664 | 34 |
| AAAI | 46.437 | 44 |
| ICASSP | 42.057 | 41 |
| EMBC | 39.318 | 4 |
| HCI | 37.884 | 1 |
| IGARSS | 35.229 | 4 |
| EMNLP | 33.954 | 25 |
| ICML | 31.896 | 24 |
| IROS | 31.249 | 14 |

Perbandingan lima konferensi dengan ukuran mirip (dihitung saat review, belum masuk notebook):

| Konferensi | Pasangan frequent | Author yang hanya publish di konferensi ini | Median jumlah konferensi per author |
|---|---|---|---|
| NeurIPS | 42 | 11,6% | 6 |
| ICASSP | 41 | 10,6% | 6 |
| EMBC | 4 | 37,4% | 2 |
| HCI | 1 | 40,8% | 2 |
| IGARSS | 4 | 54,2% | 1 |

Author NeurIPS dan ICASSP biasanya publish di sekitar enam konferensi, sehingga banyak pasangan yang lolos ambang. Author EMBC, HCI, dan IGARSS biasanya hanya publish di satu atau dua konferensi, dan yang publish di tempat lain tersebar ke banyak konferensi berbeda, sehingga tidak ada pasangan yang mencapai 1.822 author.

---|---|---|---|---|
| NeurIPS | 57.800 | 42 | 11,6% | 6 |
| CVPR | 47.664 | 34 | | |
| AAAI | 46.437 | 44 | | |
| ICASSP | 42.057 | 41 | 10,6% | 6 |
| EMBC | 39.318 | 4 | 37,4% | 2 |
| HCI | 37.884 | 1 | 40,8% | 2 |
| IGARSS | 35.229 | 4 | 54,2% | 1 |
| EMNLP | 33.954 | 25 | | |
| ICML | 31.896 | 24 | | |
| IROS | 31.249 | 14 | | |

Dua kolom terakhir hanya dihitung untuk lima konferensi pembanding (diperiksa saat review, belum masuk notebook).

---

## 5. Jawaban pertanyaan Task 4

**1. Frequent itemsets yang memenuhi min support.** 1.514 (0,1%), 88 (0,5%), 30 (1%), dan 6 (2%).

**2. 1-, 2-, dan 3-itemsets.** 574, 393, 348 pada 0,1%; 66, 21, 1 pada 0,5%; 29, 1, 0 pada 1%; 6, 0, 0 pada 2%. Pada 0,1% juga ada 199 itemset berukuran 4 sampai 6.

**3. Sepuluh itemset dengan support tertinggi.** Pada 0,1%, 0,5%, dan 1% seluruhnya konferensi tunggal, dipimpin NeurIPS (57.800 author), CVPR (47.664), dan AAAI (46.437). Pada 2% hanya enam konferensi yang lolos. Tidak ada kombinasi yang masuk sepuluh besar karena pasangan teratas (18.503) lebih kecil dari konferensi ke-10 (31.249).

**4. Pengaruh min support.** Jumlah itemset turun 17,2 kali dari 0,1% ke 0,5% dan 252 kali dari 0,1% ke 2%. Itemset besar hilang lebih dulu: ukuran ≥4 hanya ada pada 0,1%, triple hilang setelah 0,5%, dan pasangan hilang setelah 1%. Penyebabnya, 58,4% author hanya publish di satu venue, sehingga support kombinasi jauh lebih kecil dari support item penyusunnya. Hanya 0,1% yang menghasilkan pola kombinasi yang cukup kaya; pada 1% dan 2% hasilnya hanya mengulang peringkat popularitas Task 2.

**5. Kombinasi yang paling sering muncul bersama.** Pasangan teratas ICML + NeurIPS (18.503 author), satu-satunya pasangan yang masih frequent pada 1%. Triple teratas ICLR + ICML + NeurIPS (10.413), satu-satunya triple yang frequent pada 0,5%. Itemset terpanjang berisi enam konferensi: AAAI + CVPR + ECCV + ICCV + ICLR + NeurIPS (2.005 author).

**6. Interpretasi.**

*Kombinasi yang sering muncul berasal dari bidang yang sama.* Kombinasi yang lolos ambang hampir selalu berasal dari satu bidang riset: machine learning (ICML + NeurIPS, 18.503 author), computer vision (CVPR + ICCV, 15.441), NLP (ACL + EMNLP, 14.557), dan robotika (ICRA + IROS, 11.860). Kombinasi lintas bidang yang sering muncul hanya terjadi antara bidang yang dekat, yaitu machine learning dengan computer vision dan AI umum, misalnya CVPR + NeurIPS (15.640). Artinya, di antara kombinasi yang cukup besar untuk lolos ambang, author biasanya publish di beberapa konferensi dalam bidang yang sama.

*NeurIPS adalah pusatnya.* NeurIPS muncul pada 4 dari 10 pasangan teratas, 8 dari 10 triple teratas, dan 35 dari 40 itemset berisi lima atau enam konferensi. Kombinasi panjang hanya terbentuk di sekitar machine learning dan computer vision, misalnya AAAI + CVPR + ECCV + ICCV + ICLR + NeurIPS (2.005 author). Artinya, NeurIPS menjadi tempat bertemunya author dari machine learning, computer vision, dan AI umum.

*Konferensi besar belum tentu terhubung.* EMBC, IGARSS, dan HCI termasuk sepuluh konferensi terbesar, tetapi hanya punya 4, 4, dan 1 pasangan frequent, karena author di sana biasanya hanya publish di satu atau dua konferensi (author NeurIPS biasanya di enam). Artinya, popularitas tidak menjamin konferensi sering dipasangkan dengan konferensi lain.

*Batasan interpretasi.* Support hanya mengukur seberapa sering dua konferensi muncul bersama, bukan seberapa kuat hubungannya. Dua konferensi besar bisa sering muncul bersama hanya karena keduanya besar; kekuatan hubungan diukur dengan lift pada Task 5. Kombinasi lintas bidang juga bisa banyak secara total tetapi tersebar ke banyak pasangan kecil yang tidak lolos ambang, sehingga hasil ini tidak membuktikan bahwa author jarang berpindah bidang.

---

## 6. Keterbatasan

1. Item adalah seri konferensi berdasarkan key DBLP. Beberapa acara dipecah DBLP menjadi konferensi utama dan workshop dengan key berbeda, misalnya `iccv` (ICCV) dan `iccvw` (ICCV Workshops), sehingga author yang hanya publish di workshop tidak terhitung pada konferensi utamanya. Sebaliknya, beberapa key dengan singkatan sama adalah konferensi yang memang berbeda, misalnya `icis` (Information Systems), `ACISicis` (Computer and Information Science), dan `icis2` (Intelligence Science); ketiganya benar dipisah, dan nama tampilnya dibedakan dengan akhiran `[key]`.
2. Identitas author mengikuti disambiguasi DBLP. Dua orang bernama sama dapat tergabung menjadi satu transaksi, dan satu orang dapat tercatat dengan dua nama sehingga riwayatnya terbelah. Kasus pertama terlihat jelas pada data:
   - Lima belas transaksi terbesar seluruhnya milik nama yang sangat umum tanpa nomor disambiguasi DBLP, misalnya Yang Liu (332 konferensi, 725 paper), Wei Wang (280), dan Lei Wang (262). Jumlah ini tidak wajar untuk satu orang, sehingga kemungkinan besar setiap nama tersebut menampung paper banyak orang berbeda.
   - Terdapat 291 transaksi dengan 100 konferensi atau lebih, dan hanya satu di antaranya yang memiliki nomor disambiguasi.
   - Pengaruhnya pada hasil min support 0,1%: median kontribusi ke-291 transaksi ini terhadap count sebuah itemset adalah 0,6% (1-itemset), 3,0% (pasangan), dan 3,9% (triple ke atas), dengan maksimum 11,5%. Tanpa transaksi ini, 109 dari 1.514 itemset (7%) akan jatuh di bawah ambang 1.822 author, yaitu 5 1-itemset, 31 pasangan, 42 triple, dan 31 itemset berukuran empat ke atas. Sepuluh pasangan teratas hanya mendapat 0,8% sampai 1,8% count-nya dari transaksi ini (contoh: ICML + NeurIPS turun dari 18.503 menjadi 18.348).
   - Kesimpulan utama Task 4 tidak berubah, tetapi itemset yang nyaris lolos ambang pada 0,1% sebagian bergantung pada profil gabungan ini. Hasil tetap dilaporkan apa adanya, tanpa membuang transaksi tersebut.
3. Support menghitung author, bukan paper.
4. Author-based menggabungkan seluruh 2015-2025, sehingga dua konferensi bisa muncul bersama walaupun dipakai pada tahun berbeda. Pengaruh waktu dianalisis di Bagian E (author-year-based).
5. Frequent itemsets pada ambang tinggi didominasi konferensi besar. Kombinasi lintas bidang bisa saja banyak secara total tetapi tersebar, sehingga tidak ada yang lolos ambang.

---

## 7. Keputusan dan penyimpangan dari plan

Ringkasan keputusan selama pengerjaan:

| Kode | Keputusan |
|---|---|
| D1 | `.venv` lokal (Python 3.12, pandas 3.1.1, mlxtend 0.25.0), kernel `dm-dblp`. Kode tetap kompatibel Python 3.9. |
| D2 | FP-Growth di modul sendiri `src/fpgrowth.py`, dipakai ulang oleh notebook 05, 06, 07. |
| D3 | Urutan item di pohon: count menurun, lalu id item menaik. |
| D4 | Transaction reduction dengan jalur berbobot; support 1-itemset dari pemindaian pertama. |
| D5 | Waktu dipisah `t_build` dan `t_mine`. |
| D6 | Validasi `mlxtend` pada seluruh database di keempat min support. |
| D7 | **Penyimpangan**: run notebook pertama gagal `MemoryError` (RAM bebas laptop hanya sekitar 2 GB). Solusi: `keep_tree=False` untuk run data asli, dan `mlxtend` hanya diberi baris yang memuat item frequent dengan ambang yang dikonversi agar tetap eksak. |
| D8 | Satu kali pengukuran waktu di notebook 04; skema output itemset (lihat bagian 9). |
| D9 | Top 10 ditampilkan untuk semua ukuran dan untuk ukuran ≥2. |
| D10 | Kombinasi diambil dari run 0,1% dengan kolom "masih frequent sampai". |
| D11 | **Penyimpangan**: subbagian 6.5 baru (keterhubungan dan itemset terpanjang) agar setiap klaim interpretasi punya angka pendukung. |
| D12 | Pilihan isi interpretasi. |

Bug yang ditemukan dan diperbaiki: `mlxtend` menolak nama kolom integer yang tidak dimulai dari 0; kolom diubah ke string dan ditambah test regresi.

---

## 8. Hasil review dan pekerjaan tersisa

Review ulang (21 November 2026) memastikan seluruh angka di notebook benar. Yang masih perlu diperbaiki di notebook (belum dikerjakan, menunggu persetujuan):
1. **Sedang**: klaim "author cenderung menerbitkan dalam komunitas yang sama, bukan berpindah ke bidang yang jauh" (bagian 7) terlalu kuat untuk dibuktikan dengan support. Dilunakkan menjadi "pola yang melewati ambang berada di dalam satu bidang".
2. **Sedang**: frasa "komunitasnya relatif tertutup" untuk HCI, EMBC, IGARSS (6.5) diganti dengan angka di bagian 4.6 report ini (persentase author satu venue dan median jumlah venue).
3. **Rendah**: alasan di 6.2 diganti dari "sifat anti-monoton" ke perbandingan langsung pasangan teratas (18.503) dengan konferensi ke-10 (31.249).
4. **Rendah**: output sel `%pip` menampilkan path lokal Windows; tambah `--disable-pip-version-check`.
5. **Sedang**: keterbatasan nomor 1 di bagian 7 notebook ("satu konferensi nyata dapat terpecah menjadi beberapa key") diganti dengan versi di bagian 6 report ini. Pengecekan `venue_proceedings.csv` menunjukkan key dengan singkatan sama (contoh ICIS) adalah konferensi berbeda, bukan satu konferensi yang terpecah.
6. **Open issue**: satu run notebook pernah gagal dengan error terpotong; run berikutnya berhasil. Dugaan RAM, belum terbukti.

Jawaban di bagian 5 report ini sudah memakai versi yang diperbaiki.

---

## 9. File, reproduksi, dan commit

**File**

| File | Isi |
|---|---|
| `src/fpgrowth.py` | Algoritma FP-Growth |
| `src/fpm_data.py` | Pemuat transaksi dan nama item |
| `src/validation.py` | Pembanding dengan `mlxtend` |
| `src/build_fpgrowth_notebook.py` | Pembangkit notebook 04 |
| `tests/` | 36 test `pytest` |
| `notebooks/04_fpgrowth.ipynb` | Notebook hasil eksekusi |
| `outputs/fpgrowth/itemsets_{0p1,0p5,1,2}.parquet` | Frequent itemsets; kolom `itemset` (list id item terurut), `length`, `count`, `support`, `names` |
| `outputs/tables/t4_fpgrowth_*.csv` | Tabel ringkasan, top 10, validasi, pasangan dan triple teratas |
| `outputs/figures/t4_fpgrowth_jumlah_itemset.png`, `t4_fpgrowth_pasangan_teratas.png` | Grafik |

`outputs/` dan `data/` tidak masuk git (dibagikan lewat zip).

**Reproduksi** (dari akar repo):
```bash
.venv/Scripts/python -m pytest tests
.venv/Scripts/python src/build_fpgrowth_notebook.py
.venv/Scripts/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=dm-dblp --ExecutePreprocessor.timeout=-1 notebooks/04_fpgrowth.ipynb
```

**Commit** (branch `fp-growth-t4`)

| Commit | Isi |
|---|---|
| `3b652dc` | FP-tree, ambang min_count, render pohon |
| `cae1eda` | Penambangan rekursif dan tabel hasil |
| `848c8d5` | Pemuat data dan validasi mlxtend |
| `e3729cd` | Notebook 04 eksperimen dan validasi |
| `33619e3` | Analisis itemset per ukuran, top 10, kombinasi teratas |
| `3cd2bf1` | Interpretasi dan ringkasan |

---

## 10. Langkah berikutnya

- **Koordinasi dengan Harfhan**: bagikan skema `outputs/fpgrowth/itemsets_<tag>.parquet` agar output Apriori memakai format yang sama untuk Task 6.
- **Task 5 (`05_rules`)**: association rules dengan min confidence 50% dari itemset 0,1% sebagai dasar utama; jawab apakah konferensi terpopuler juga punya asosiasi terkuat (lift).
- **Task 6 (`06_performance`)**: perbandingan Apriori dan FP-Growth dengan pengukuran waktu berulang.
