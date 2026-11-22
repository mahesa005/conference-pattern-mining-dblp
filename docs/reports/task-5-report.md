# Report Task 5: Association Rule Mining (sisi FP-Growth)

| | |
|---|---|
| Penanggung jawab | Mahesa Andre (13523140), sisi FP-Growth. Sisi Apriori: Harfhan Ikhtiar. |
| Tanggal selesai | 22 November 2026 |
| Status | Selesai di branch `fp-growth-t4`, belum di-commit saat report ini ditulis. |
| Notebook | `notebooks/05_rules.ipynb`, dibangkitkan oleh `src/build_rules_notebook.py` |
| Kode | `src/rules.py`, `src/validation.py` (fungsi rules), test di `tests/test_rules.py` dan `tests/test_validation.py` |

---

## 1. Ringkasan

Association rules dibangkitkan dari frequent itemsets FP-Growth (Task 4) dengan min confidence 50%, untuk keempat min support. Hasilnya identik dengan `mlxtend`.

Temuan utama:
- Pada min support 0,1% terdapat **1.387 rules**, tetapi hanya **22** yang berbentuk satu-ke-satu (satu konferensi ke satu konferensi). Pada 1% hanya ada satu rule (ICML → NeurIPS), dan pada 2% tidak ada rule.
- **Tidak ada pasangan konferensi yang berlaku dua arah.** Seluruh rule satu-ke-satu mengarah dari konferensi yang lebih kecil ke konferensi utama di bidang yang sama, misalnya EACL → ACL dan BMVC → CVPR.
- **Support tinggi tidak berarti lift tinggi.** Semakin populer sebuah konferensi, semakin rendah lift rules yang menuju kepadanya (Spearman -0,933). NeurIPS memiliki rules terbanyak, tetapi lift-nya termasuk yang terendah.
- Rules satu-ke-satu membentuk **delapan kelompok bidang** yang tidak saling terhubung.

---

## 2. Spesifikasi dan pemenuhannya

| Poin soal Task 5 | Status | Bagian notebook |
|---|---|---|
| Gunakan frequent itemsets untuk membangkitkan rules | Selesai, dari itemset notebook 04 | 4 |
| Min confidence 50% | Selesai | 4 |
| Hitung support, confidence, lift setiap rule | Selesai, disimpan di `outputs/rules/` | 4, 5 |
| 10 rules dengan lift tertinggi | Selesai, ditambah 10 teratas untuk rule satu-ke-satu | 5 |
| 1. Bangkitkan rules | Selesai | 4 |
| 2. Tampilkan rules dengan support, confidence, lift | Selesai | 5 |
| 3. Hubungan antarkonferensi paling menarik | Selesai | 6 |
| 4. Apakah support tinggi selalu lift tinggi | Selesai | 7 |
| 5. Beda interpretasi support, confidence, lift | Selesai | 8 |
| 6. Pola publikasi antarkonferensi | Selesai | 9, 10 |

---

## 3. Metode

### 3.1 Data
Masukan adalah frequent itemsets hasil FP-Growth di `outputs/fpgrowth/itemsets_<tag>.parquet` (Task 4). Transaksi tidak dibaca ulang. N = 1.821.757 author dibaca dari metadata `tx_author_index.parquet`.

### 3.2 Rumus
Untuk rule X → Y:

| Metrik | Rumus | Arti |
|---|---|---|
| Support | count(X ∪ Y) / N | proporsi seluruh author yang publish di semua konferensi X dan Y |
| Confidence | count(X ∪ Y) / count(X) | proporsi author X yang juga publish di Y |
| Lift | confidence / support(Y) = count(X ∪ Y) · N / (count(X) · count(Y)) | berapa kali lebih sering author X publish di Y dibanding author pada umumnya |

Rule disimpan jika confidence ≥ 50% (batas termasuk).

### 3.3 Algoritma
Implementasi di `src/rules.py`:
- Setiap frequent itemset berukuran ≥ 2 dipecah menjadi semua pasangan antecedent X dan consequent Y yang mungkin (2^k − 2 kandidat untuk itemset berukuran k).
- Karena setiap subset dari frequent itemset juga frequent, count X dan Y selalu tersedia, sehingga metrik dihitung dari count bulat tanpa membaca transaksi.
- Rules diurutkan menurut lift, lalu confidence, lalu count.
- Rules dibangkitkan untuk keempat min support (Task 6 membutuhkan jumlah rules per min support). Analisis memakai min support 0,1%, satu-satunya ambang dengan pola kombinasi yang cukup kaya (Task 4).

### 3.4 Pengujian
53 test `pytest` lulus (17 baru untuk Task 5):
- Contoh buku teks Han, Kamber, dan Pei (2012): itemset {I1, I2, I5} pada min confidence 70% menghasilkan tepat tiga rule dengan confidence 100%, dan lift I5 → I1 + I2 = 2,25.
- Batas confidence 50% bersifat inklusif (diuji dengan rule yang confidence-nya tepat 0,5).
- 9 kasus acak dibandingkan dengan brute force yang menghitung setiap sisi rule langsung dari transaksi.
- Kesepakatan dengan `mlxtend.association_rules` pada data acak.

---

## 4. Hasil

### 4.1 Jumlah rules per min support

| min support | Itemset ukuran ≥2 | Kandidat rule | Rules (conf ≥50%) | Satu-ke-satu | Dari itemset ukuran 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|---|
| 0,1% | 940 | 6.396 | 1.387 | 22 | 436 | 555 | 313 | 61 |
| 0,5% | 22 | 48 | 7 | 4 | 3 | 0 | 0 | 0 |
| 1% | 1 | 2 | 1 | 1 | 0 | 0 | 0 | 0 |
| 2% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### 4.2 Validasi dengan mlxtend
Keempat min support identik dengan `mlxtend.association_rules`: tidak ada rule yang hilang atau berlebih, dan support, confidence, serta lift sama sampai toleransi relatif 10⁻⁹.

### 4.3 Sepuluh rule dengan lift tertinggi (min support 0,1%)

| # | Rule | Support | Confidence | Lift | Author |
|---|---|---|---|---|---|
| 1 | ECCV + ACM Multimedia + NeurIPS → AAAI + CVPR + ICCV | 0,100% | 61,2% | 172,27 | 1.827 |
| 2 | CVPR + ECCV + ICML → ICCV + ICLR + NeurIPS | 0,101% | 50,2% | 171,81 | 1.849 |
| 3 | CVPR + ICCV + ICML + NeurIPS → ECCV + ICLR | 0,101% | 51,4% | 159,38 | 1.849 |
| 4 | CVPR + ECCV + ICML + NeurIPS → ICCV + ICLR | 0,101% | 59,1% | 157,30 | 1.849 |
| 5 | ECCV + ICCV + ICML → CVPR + ICLR + NeurIPS | 0,101% | 61,4% | 156,21 | 1.849 |
| 6 | ICLR + NAACL-HLT → ACL + EMNLP + NeurIPS | 0,105% | 50,4% | 152,46 | 1.917 |
| 7 | CVPR + ICCV + ACM Multimedia + NeurIPS → AAAI + ECCV | 0,100% | 57,5% | 147,66 | 1.827 |
| 8 | EMNLP + NAACL-HLT + NeurIPS → ACL + ICLR | 0,105% | 54,6% | 146,26 | 1.917 |
| 9 | CVPR + ECCV + ACM Multimedia + NeurIPS → AAAI + ICCV | 0,100% | 68,5% | 145,44 | 1.827 |
| 10 | CVPR + ECCV + ICML → ICCV + ICLR | 0,108% | 53,6% | 142,63 | 1.973 |

Seluruhnya rule panjang dengan consequent dua atau tiga konferensi, dan count-nya hanya 1.827 sampai 1.973 author, sedikit di atas ambang 1.822.

### 4.4 Seluruh rule satu-ke-satu (min support 0,1%)

| Rule | Lift | Confidence | Confidence arah balik | Author |
|---|---|---|---|---|
| ECOC → OFC | 80,12 | 66,5% | 30,0% | 4.530 |
| ASRU → INTERSPEECH | 74,17 | 72,7% | 11,0% | 1.961 |
| CoRL → ICRA | 37,11 | 58,1% | 7,3% | 2.084 |
| EACL → ACL | 36,59 | 59,6% | 9,9% | 2.924 |
| SPAWC → ICC | 36,23 | 53,0% | 7,2% | 1.926 |
| Conference on Designing Interactive Systems → CHI | 33,99 | 55,8% | 10,6% | 3.167 |
| SPAWC → GLOBECOM | 33,80 | 50,3% | 6,7% | 1.828 |
| EACL → EMNLP | 32,85 | 61,2% | 8,8% | 3.004 |
| NAACL-HLT → ACL | 32,13 | 52,3% | 25,7% | 7.629 |
| IJCNLP-AACL → ACL | 30,98 | 50,5% | 6,4% | 1.886 |
| AISTATS → ICML | 30,44 | 53,3% | 14,3% | 4.558 |
| NAACL-HLT → EMNLP | 30,05 | 56,0% | 24,0% | 8.162 |
| IJCNLP-AACL → EMNLP | 27,71 | 51,6% | 5,7% | 1.930 |
| 3DV → CVPR | 25,02 | 65,5% | 4,1% | 1.961 |
| ECCV → CVPR | 22,28 | 58,3% | 28,9% | 13.752 |
| ICCV → CVPR | 21,80 | 57,0% | 32,4% | 15.441 |
| BMVC → CVPR | 20,34 | 53,2% | 9,4% | 4.491 |
| ACCV → CVPR | 19,37 | 50,7% | 5,2% | 2.475 |
| AISTATS → NeurIPS | 19,29 | 61,2% | 9,1% | 5.234 |
| ICML → NeurIPS | 18,28 | 58,0% | 32,0% | 18.503 |
| ICLR → NeurIPS | 18,06 | 57,3% | 30,9% | 17.852 |
| UAI → NeurIPS | 17,68 | 56,1% | 4,6% | 2.654 |

Confidence arah balik adalah confidence B → A. Semuanya di bawah 50%, sehingga arah balik tidak menjadi rule.

### 4.5 Rules pada 0,5% dan 1%

Pada 0,5% (7 rules): ICLR + NeurIPS → ICML (lift 33,32), ICML + NeurIPS → ICLR (32,91), ICLR + ICML → NeurIPS (25,35; confidence 80,4%), ECCV → CVPR (22,28), ICCV → CVPR (21,80), ICML → NeurIPS (18,28), ICLR → NeurIPS (18,06).

Pada 1%: hanya ICML → NeurIPS (confidence 58,0%, lift 18,28). Pada 2%: tidak ada rule.

### 4.6 Support dan lift

Menurut ukuran consequent (0,1%):

| Consequent | Rules | Median support | Median lift | Lift maks |
|---|---|---|---|---|
| 1 konferensi | 1.114 | 0,131% | 31,40 | 92,90 |
| 2 konferensi | 260 | 0,117% | 81,42 | 159,38 |
| 3 konferensi | 13 | 0,102% | 137,19 | 172,27 |

Korelasi Spearman:

| Hubungan | rho | Jumlah |
|---|---|---|
| Support rule vs lift | -0,209 | 1.387 rules |
| Support konferensi vs median lift rules yang menuju kepadanya | -0,933 | 26 konferensi |
| Support konferensi vs median lift rules yang berangkat darinya | -0,517 | 17 konferensi |

Konferensi sebagai consequent tunggal (contoh):

| Konferensi | Support | Rules menuju | Median lift |
|---|---|---|---|
| NeurIPS | 3,17% | 240 | 23,61 |
| CVPR | 2,62% | 160 | 30,21 |
| AAAI | 2,55% | 189 | 25,28 |
| ICASSP | 2,31% | 5 | 22,85 |
| ACL | 1,63% | 53 | 43,27 |
| ECCV | 1,30% | 70 | 48,17 |
| CDC | 0,79% | 1 | 92,90 |

Lift terendah dari seluruh rules adalah 15,83. Batas bawah teoretisnya 0,5 / 3,17% ≈ 15,76, karena confidence minimal 50% dan tidak ada konferensi dengan support di atas 3,17%.

### 4.7 Kelompok konferensi dari rules satu-ke-satu

| Kelompok | Konferensi | Rules |
|---|---|---|
| Computer vision | CVPR, ICCV, ECCV, BMVC, ACCV, 3DV | 5 |
| NLP | ACL, EMNLP, NAACL-HLT, EACL, IJCNLP-AACL | 6 |
| Machine learning | NeurIPS, ICML, ICLR, AISTATS, UAI | 5 |
| Komunikasi nirkabel | ICC, GLOBECOM, SPAWC | 2 |
| Komunikasi optik | OFC, ECOC | 1 |
| Pengenalan suara | INTERSPEECH, ASRU | 1 |
| Robotika | ICRA, CoRL | 1 |
| Interaksi manusia-komputer | CHI, Conference on Designing Interactive Systems | 1 |

Consequent terbanyak dari 1.114 rules dengan consequent tunggal: NeurIPS (240 rules, 21,5%), AAAI (189, 17,0%), CVPR (160, 14,4%), ICCV (101), ICLR (91).

---

## 5. Jawaban pertanyaan Task 5

**1. Bangkitkan association rules.** Dengan min confidence 50%: 1.387 rules pada 0,1%, 7 pada 0,5%, 1 pada 1%, dan 0 pada 2%. Pada 0,1%, 1.387 dari 6.396 kandidat (21,7%) lolos, dan hanya 22 yang berbentuk satu-ke-satu.

**2. Rules dengan support, confidence, dan lift.** Seluruh rules disimpan di `outputs/rules/rules_<tag>.parquet` dan ditampilkan di notebook bagian 5. Sepuluh lift tertinggi ada di bagian 4.3 report ini, dipimpin ECCV + ACM Multimedia + NeurIPS → AAAI + CVPR + ICCV (lift 172,27).

**3. Hubungan antarkonferensi paling menarik.** Definisi awal ("rule berlaku ke dua arah dengan confidence ≥ 50%") tidak menghasilkan apa pun: tidak ada satu pun pasangan yang berlaku dua arah. Karena itu ada dua jenis hubungan yang paling menarik:
- *Lift tertinggi:* ECOC → OFC (lift 80,12; 66,5% author ECOC publish di OFC) dan ASRU → INTERSPEECH (lift 74,17; 72,7%). Keduanya pasangan di bidang sempit (komunikasi optik dan pengenalan suara), sehingga author-nya sangat terkonsentrasi.
- *Paling mendekati timbal balik:* ICCV → CVPR, ICML → NeurIPS, ICLR → NeurIPS, ECOC → OFC, dan ECCV → CVPR, dengan confidence arah balik 28,9% sampai 32,4%. Ini konferensi utama dengan ukuran mirip di bidang yang sama.

**4. Apakah support tinggi selalu menghasilkan lift tinggi?** Tidak, justru sebaliknya. Semakin besar support sebuah konferensi, semakin rendah lift rules yang menuju kepadanya (Spearman -0,933 pada 26 konferensi). NeurIPS (support 3,17%) menjadi tujuan 240 rules, terbanyak, tetapi median lift-nya hanya 23,61, kedua terendah. CDC (support 0,79%) memiliki median lift 92,90. Penyebabnya rumus lift = confidence / support(Y): konferensi besar sudah memiliki support tinggi, sehingga rule yang menuju kepadanya sulit mencapai lift tinggi. Lift juga membesar ketika consequent berisi beberapa konferensi (median 31,40 untuk satu konferensi, 137,19 untuk tiga), karena kombinasi konferensi selalu jarang.

**5. Perbedaan interpretasi support, confidence, dan lift.** Dengan contoh ICML → NeurIPS (18.503 author):
- *Support 1,016%*: seberapa umum kombinasi ICML dan NeurIPS di antara seluruh author. Tidak berarah.
- *Confidence 58,0%*: dari author ICML, 58% juga publish di NeurIPS. Berarah; NeurIPS → ICML hanya 32,0%.
- *Lift 18,28*: author ICML 18 kali lebih mungkin publish di NeurIPS dibanding author pada umumnya. Tidak berarah.

Support menjawab "seberapa sering", confidence menjawab "seberapa sering B jika A", dan lift menjawab "seberapa kuat hubungan dibanding jika tidak berkaitan". Pada data ini lift tidak menyaring rules (setiap rule otomatis memiliki lift minimal sekitar 15,8), sehingga lift dipakai untuk mengurutkan kekuatan hubungan.

**6. Pola publikasi antarkonferensi.**
- *Hubungan kuat hanya terjadi di dalam satu bidang.* Rules satu-ke-satu membentuk delapan kelompok bidang (computer vision, NLP, machine learning, komunikasi nirkabel, komunikasi optik, pengenalan suara, robotika, HCI), tanpa satu pun rule yang menghubungkan dua kelompok.
- *Arahnya dari konferensi yang lebih kecil ke konferensi utama.* Mayoritas author EACL, BMVC, AISTATS, CoRL, dan konferensi lain yang lebih kecil juga publish di konferensi utama bidangnya, tetapi tidak sebaliknya.
- *Konferensi utama yang ukurannya mirip paling mendekati timbal balik:* CVPR dengan ICCV dan ECCV, serta NeurIPS dengan ICML dan ICLR.
- *Kombinasi beberapa konferensi mengarah ke NeurIPS, AAAI, dan CVPR.* AAAI tidak menjadi tujuan rule satu-ke-satu mana pun, tetapi menjadi tujuan 189 rules dari kombinasi dua konferensi atau lebih.

**Kaitan dengan pertanyaan kesimpulan.**
- *H.2 (apakah konferensi terpopuler juga memiliki asosiasi terkuat):* tidak. NeurIPS memiliki asosiasi terbanyak tetapi lift-nya termasuk yang terendah; asosiasi terkuat ada pada pasangan konferensi bidang sempit (ECOC → OFC, ASRU → INTERSPEECH).
- *H.4 (rule dengan lift tertinggi dan maknanya):* ECCV + ACM Multimedia + NeurIPS → AAAI + CVPR + ICCV (lift 172,27). Dari 2.983 author yang publish di ECCV, ACM Multimedia, dan NeurIPS, 61,2% juga publish di AAAI, CVPR, dan ICCV, atau 172 kali lebih sering dibanding author pada umumnya. Rule ini hanya berlaku untuk 1.827 author dan rapuh (lihat keterbatasan 4). Untuk rule satu-ke-satu, lift tertinggi adalah ECOC → OFC (80,12).

---

## 6. Keterbatasan

1. Seluruh keterbatasan Task 4 tetap berlaku: item adalah key DBLP (workshop dapat terpisah dari konferensi utamanya), identitas author mengikuti disambiguasi DBLP, support menghitung author bukan paper, dan author-based menggabungkan seluruh 2015-2025.
2. Rules hanya ada untuk kombinasi yang lolos min support 0,1%. Hubungan kuat antara dua konferensi kecil tidak terlihat.
3. Dengan min confidence 50% dan support setiap konferensi di bawah 3,2%, setiap rule otomatis memiliki lift minimal sekitar 15,8. Lift yang tinggi pada data ini sebagian besar mencerminkan kecilnya support konferensi, sehingga lift lebih tepat dipakai untuk membandingkan rules daripada sebagai ukuran mutlak.
4. **Sepuluh rule dengan lift tertinggi rapuh.** Count-nya hanya 1.827 sampai 1.973 author terhadap ambang 1.822. Pengecekan terhadap 291 profil author gabungan di DBLP (keterbatasan 2 Task 4) menunjukkan profil tersebut menyumbang 54 sampai 60 author pada setiap rule itu. Tanpa profil gabungan, **7 dari 10** rule tersebut tidak lagi lolos min support 0,1%. Hasil tetap dilaporkan apa adanya, sesuai keputusan pada Task 4. Rule satu-ke-satu lebih kokoh karena count-nya lebih besar (1.828 sampai 18.503), walaupun yang terkecil juga dekat ambang.

---

## 7. Keputusan dan penyimpangan dari plan

| Kode | Keputusan |
|---|---|
| D0 | Seluruh langkah dikerjakan sekaligus dan direview di akhir (permintaan user). Default untuk pertanyaan terbuka: perbaikan Task 4 dikerjakan lebih dulu, tetap di branch `fp-growth-t4`, rules untuk keempat min support dengan analisis pada 0,1%. |
| D1 | Pembangkitan rules di modul sendiri `src/rules.py`, dipakai ulang oleh notebook 06 dan 07. |
| D2 | Metrik dihitung dari count bulat; batas confidence inklusif; urutan lift, confidence, count. |
| D3 | 14 test untuk `src/rules.py`, termasuk brute force langsung dari transaksi. |
| D4 | Validasi dengan `mlxtend.association_rules` untuk keempat min support; seluruhnya identik. |
| D5 | Sepuluh lift tertinggi ditampilkan dua versi: seluruh rule (sesuai soal) dan rule satu-ke-satu (mudah dibaca). |
| D6 | **Penyimpangan**: definisi "paling menarik" di plan (rule berlaku dua arah) diganti karena tidak ada pasangan dua arah. Penggantinya: lift tertinggi, ditambah confidence arah balik untuk melihat hubungan yang paling mendekati timbal balik. |
| D7 | Task 5.4 dijawab pada dua tingkat: per rule (support rule vs lift) dan per konferensi (support konferensi vs median lift), dengan korelasi Spearman. |
| D8 | Kelompok konferensi (5.6) dibentuk dari rules satu-ke-satu sebagai garis antarkonferensi (komponen terhubung). |

---

## 8. Pekerjaan tersisa

- Keterbatasan 4 (kerapuhan sepuluh lift tertinggi terhadap profil author gabungan) hanya dicatat di report ini, tidak dihitung di notebook, mengikuti keputusan yang sama dengan Task 4.

---

## 9. File, reproduksi, dan commit

`data/` dan `outputs/` tidak masuk git (dibagikan lewat zip).

**File input**

| File | Asal | Isi |
|---|---|---|
| `outputs/fpgrowth/itemsets_{0p1,0p5,1,2}.parquet` | notebook 04 | Frequent itemsets per min support |
| `data/processed/tx_items.csv` | notebook 02 | Nama konferensi per `item_id` |
| `data/processed/tx_author_index.parquet` | notebook 02 | Hanya jumlah barisnya dibaca, sebagai N = 1.821.757 |

**File output: data**

| File | Isi | Dipakai oleh |
|---|---|---|
| `outputs/rules/rules_{0p1,0p5,1,2}.parquet` | Association rules per min support, min confidence 50% (1.387 / 7 / 1 / 0 baris). Kolom: `antecedent`, `consequent` (list `item_id`), `n_antecedent`, `n_consequent`, `count`, `antecedent_count`, `consequent_count`, `support`, `confidence`, `lift`, `rule` | rencana 06 (jumlah rules) |

**File output: tabel** (`outputs/tables/`)

| File | Isi |
|---|---|
| `t5_jumlah_rules.csv` | Jumlah kandidat dan rules per min support, per ukuran itemset asal |
| `t5_validasi_mlxtend.csv` | Perbandingan dengan mlxtend per min support |
| `t5_top10_lift.csv` | 10 rules dengan lift tertinggi (0,1%) |
| `t5_rules_satu_ke_satu.csv` | Seluruh 22 rule satu-ke-satu (0,1%) |
| `t5_rules_satu_ke_satu_arah.csv` | Rule satu-ke-satu dengan confidence arah balik dan rasio ukuran |
| `t5_lift_per_ukuran_consequent.csv` | Median support dan lift menurut ukuran consequent |
| `t5_support_vs_lift_consequent.csv` | Support konferensi vs lift rules yang menuju kepadanya |
| `t5_support_vs_lift_antecedent.csv` | Support konferensi vs lift rules yang berangkat darinya |
| `t5_contoh_metrik.csv` | Tiga contoh rule dengan count di balik metriknya |
| `t5_kelompok_konferensi.csv` | Delapan kelompok konferensi dari rules satu-ke-satu |
| `t5_consequent_terbanyak.csv` | Jumlah rules yang menuju setiap konferensi |

**File output: gambar** (`outputs/figures/`): `t5_rules_satu_ke_satu.png`, `t5_support_vs_lift.png`

**Kode dan notebook** (masuk git)

| File | Isi |
|---|---|
| `src/rules.py` | `load_itemsets`, `generate_rules`, `rule_label` |
| `src/validation.py` | Ditambah `mlxtend_rules_reference` dan `compare_rules` |
| `src/build_rules_notebook.py` | Pembangkit notebook 05 |
| `tests/test_rules.py`, `tests/test_validation.py` | Test `pytest` (total 53 test di `tests/`) |
| `notebooks/05_rules.ipynb` | Notebook hasil eksekusi |
| `docs/reports/task-5-report.md` | Report ini |

**Reproduksi** (dari akar repo, setelah notebook 04 dijalankan):
```bash
.venv/Scripts/python -m pytest tests
.venv/Scripts/python src/build_rules_notebook.py
.venv/Scripts/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=dm-dblp --ExecutePreprocessor.timeout=-1 notebooks/05_rules.ipynb
```

**Commit**: belum di-commit saat report ini ditulis.

---

## 10. Langkah berikutnya

- **Task 6 (`06_performance`)**: bandingkan Apriori (Harfhan) dan FP-Growth pada keempat min support: jumlah frequent itemsets, jumlah rules (pakai `src/rules.py` agar sama), dan waktu dengan pengukuran berulang. Sepakati dengan Harfhan apakah Apriori juga menggabungkan transaksi yang identik.
- **Bagian E (`07_temporal`)**: rules per periode pada author-year-based database dengan `src/rules.py`.
