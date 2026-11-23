# Report Task 6: Perbandingan Performa Apriori dan FP-Growth

| | |
|---|---|
| Penanggung jawab | Mahesa Andre (13523140): harness pengukuran, sisi FP-Growth, report ini. Harfhan Ikhtiar: Apriori, eksekusi notebook 06, jawaban bagian 8, subbab LaTeX Task 6. |
| Tanggal selesai | 23 November 2026 |
| Status | Selesai dan sudah di `main` (sampai commit `42075ea`). Report ini belum di-commit saat ditulis. |
| Notebook | `notebooks/06_performance.ipynb`, dibangkitkan oleh `src/build_performance_notebook.py` |
| Kode | `src/benchmark.py`, `src/apriori.py`, `src/fpgrowth.py`, `src/rules.py`, `src/validation.py`; test di `tests/test_benchmark.py` dan `tests/test_apriori_contract.py` |

> **Penanda [PU-n]**: klaim yang memakai pengetahuan umum di luar data DBLP dan di luar pengukuran notebook ini. Seluruh angka di report ini berasal dari notebook 06 (dan notebook 03 untuk rincian per level Apriori). Daftar klaim [PU-n] beserta statusnya ada di akhir bagian 6.

---

## 1. Ringkasan

Apriori dan FP-Growth dijalankan pada author-based database yang sama (1.821.757 transaksi) dengan keempat min support (0,1%, 0,5%, 1%, 2%), masing-masing tiga kali.

Temuan utama:
- **Hasil identik.** Frequent itemsets (1.514, 88, 30, 6) dan count-nya sama persis, sehingga rules dengan min confidence 50% juga sama (1.387, 7, 1, 0).
- **Waktu setara.** Selisih median kedua algoritma paling besar 6%, lebih kecil dari derau pengukuran (sampai 14%). Pada 0,1%: Apriori 5,41 detik, FP-Growth 5,19 detik.
- **Waktu turun jauh lebih sedikit daripada jumlah pola.** Dari 0,1% ke 2%, waktu turun 6,3 sampai 6,5 kali, sedangkan jumlah itemset turun 252 kali. Penyebabnya, kedua algoritma selalu memindai seluruh 1.821.757 transaksi di awal.
- **Biaya terbesar ada di tempat berbeda.** Apriori: level 2 (164.451 kandidat pada 0,1%, hanya 0,24% yang frequent). FP-Growth: pembentukan FP-tree (3,33 dari 5,19 detik).
- FP-Growth dipilih sebagai algoritma utama karena tidak membangkitkan kandidat, bukan karena lebih cepat pada pengukuran ini (bagian 5.3).

---

## 2. Spesifikasi dan pemenuhannya

| Poin soal Task 6 | Status | Bagian notebook |
|---|---|---|
| Bandingkan Apriori dan FP-Growth pada database dan min support yang sama | Selesai, author-based, keempat min support | 3, 4 |
| Metrik wajib: jumlah frequent itemsets | Selesai | 5 |
| Metrik wajib: jumlah association rules | Selesai, min confidence 50%, kode rules yang sama untuk keduanya | 6 |
| Metrik tambahan: waktu eksekusi | Selesai, tiga pengulangan, median/min/maks | 4, 7 |
| 1. Pengaruh min support terhadap performa | Selesai | 8.1 |
| 2. Apakah frequent itemsets kedua algoritma sama | Selesai | 8.2 |
| 3. Algoritma mana yang lebih sesuai untuk DBLP | Selesai | 8.3 |

---

## 3. Metode

### 3.1 Data
Masukan kedua algoritma adalah transaksi author-based dalam bentuk horizontal (list `frozenset` kode item) yang dibangun sekali dari `data/processed/tx_author.parquet` dengan `load_horizontal`. N = 1.821.757 transaksi, 4.373 item unik.

### 3.2 Kesetaraan perlakuan
Kedua implementasi dibuat setara agar selisih waktu hanya berasal dari algoritmanya:

| Aspek | Apriori (`src/apriori.py`) | FP-Growth (`src/fpgrowth.py`) |
|---|---|---|
| Ambang | `min_count_for(min_support, N)` | sama |
| Penyebut support | seluruh N transaksi | sama |
| Pemangkasan item tidak frequent | setelah scan pertama | sama |
| Transaksi dengan < 2 item frequent | dilewati untuk k ≥ 2, tetap di penyebut | sama |
| Penggabungan transaksi identik | ya, dihitung sekali dengan bobot (315.694 transaksi unik pada 0,1%) | ya |
| Yang diukur | seluruh level (level 1 termasuk pra-pemrosesan) | pembentukan FP-tree + penambangan, keduanya juga dicatat terpisah |
| Tidak diukur | pemuatan Parquet, pembentukan list horizontal | sama |

### 3.3 Pengukuran waktu
Implementasi di `src/benchmark.py` (`time_runs`):
- Jam dinding (`time.perf_counter`) di sekitar pemanggilan fungsi, dengan `gc.collect()` sebelum setiap run.
- `REPEATS = 3` untuk setiap kombinasi algoritma dan min support. Yang dilaporkan median, minimum, dan maksimum.
- Hasil setiap pengulangan diperiksa sama persis; run yang hasilnya berubah ditolak.
- Untuk FP-Growth, waktu internal `t_build` dan `t_mine` juga dicatat.

Notebook 06 dijalankan oleh Harfhan di laptopnya (MacBook Pro), sehingga waktu absolut di report ini berbeda dari waktu FP-Growth di report Task 4, yang diukur di laptop lain.

### 3.4 Perbandingan hasil
- Itemset: `compare_itemsets` (`src/validation.py`) menghitung itemset yang hanya ada di salah satu algoritma dan itemset dengan count berbeda.
- Rules: rules kedua algoritma dibangkitkan dengan `generate_rules` (`src/rules.py`) yang sama, lalu dibandingkan dengan `compare_rules`. Dengan begitu perbedaan rules hanya dapat berasal dari perbedaan itemset.

### 3.5 Pengujian
68 test `pytest` lulus (di laptop Mahesa, 23 November 2026):
- `tests/test_benchmark.py` (7 test): pemuat Apriori (modul asli, pengganti sementara jika `src/apriori.py` belum ada, dependensi yang hilang tidak disembunyikan), pencatatan pengulangan, penolakan run yang hasilnya berubah.
- `tests/test_apriori_contract.py` (8 test, aktif sejak `src/apriori.py` ada): contoh buku teks Han, Kamber, dan Pei (2012), transaksi kosong tetap dihitung di penyebut, dan 6 kasus acak dibandingkan dengan brute force.

---

## 4. Hasil

### 4.1 Jumlah frequent itemsets dan rules

| min support | Itemsets Apriori | Itemsets FP-Growth | Hanya Apriori | Hanya FP-Growth | Count berbeda | Rules Apriori | Rules FP-Growth | Metrik rules berbeda | Identik |
|---|---|---|---|---|---|---|---|---|---|
| 0,1% | 1.514 | 1.514 | 0 | 0 | 0 | 1.387 | 1.387 | 0 | ya |
| 0,5% | 88 | 88 | 0 | 0 | 0 | 7 | 7 | 0 | ya |
| 1% | 30 | 30 | 0 | 0 | 0 | 1 | 1 | 0 | ya |
| 2% | 6 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | ya |

### 4.2 Waktu eksekusi (detik, tiga pengulangan)

| min support | Apriori: median (min–maks) | FP-Growth: median (min–maks) | FP-Growth: FP-tree | FP-Growth: penambangan | Lebih cepat | Selisih | Rentang min–maks |
|---|---|---|---|---|---|---|---|
| 0,1% | 5,41 (5,39–5,56) | 5,19 (5,09–5,20) | 3,33 | 1,75 | FP-Growth | 4% | terpisah |
| 0,5% | 1,37 (1,36–1,40) | 1,35 (1,33–1,41) | 1,11 | 0,23 | FP-Growth | 1% | bertumpuk |
| 1% | 1,00 (0,99–1,19) | 1,06 (1,02–1,08) | 1,00 | 0,06 | Apriori | 6% | bertumpuk |
| 2% | 0,83 (0,81–0,88) | 0,83 (0,82–0,84) | 0,83 | 0,00006 | sama | 0% | bertumpuk |

Selisih = (median yang lebih lambat − median yang lebih cepat) / median yang lebih lambat. "Terpisah" berarti run Apriori yang tercepat tetap lebih lambat dari run FP-Growth yang terlambat.

### 4.3 Rincian per level Apriori (dari notebook 03, satu kali eksekusi)

| min support | Level | Kandidat | Frequent | Frequent / kandidat | Waktu (detik) |
|---|---|---|---|---|---|
| 0,1% | 1 | 4.373 | 574 | 13,13% | 1,60 |
| | 2 | 164.451 | 393 | 0,24% | 2,98 |
| | 3 | 1.228 | 348 | 28,34% | 0,78 |
| | 4 | 337 | 159 | 47,18% | 0,40 |
| | 5 | 54 | 37 | 68,52% | 0,16 |
| | 6 | 5 | 3 | 60,00% | 0,10 |
| 0,5% | 1 / 2 / 3 | 4.373 / 2.145 / 13 | 66 / 21 / 1 | | 1,31 / 0,37 / 0,05 |
| 1% | 1 / 2 | 4.373 / 406 | 29 / 1 | | 0,87 / 0,12 |
| 2% | 1 / 2 | 4.373 / 15 | 6 / 0 | | 0,81 / 0,00 |

Level 1 termasuk pemangkasan dan penggabungan transaksi. Total waktu per level pada 0,1% adalah 6,02 detik, bukan 5,41 detik seperti di tabel 4.2, karena berasal dari run yang berbeda.

### 4.4 Besar derau pengukuran (uji A/A)
Sebelum Apriori tersedia, harness diuji dengan menjalankan FP-Growth melawan dirinya sendiri di laptop Mahesa. Kedua median seharusnya sama, tetapi berbeda sampai 14% pada satu run dan di bawah 2% pada run berikutnya. Jadi selisih di bawah sekitar 15% tidak dapat dibedakan dari derau. Seluruh selisih di tabel 4.2 (paling besar 6%) berada di bawah batas ini.

---

## 5. Jawaban pertanyaan Task 6

**1. Pengaruh min support terhadap performa.** Min support yang lebih tinggi mempercepat kedua algoritma, tetapi waktu turun jauh lebih sedikit daripada jumlah pola. Dari 0,1% ke 2%:

| | 0,1% | 2% | Turun |
|---|---|---|---|
| Waktu Apriori | 5,41 detik | 0,83 detik | 6,5 kali |
| Waktu FP-Growth | 5,19 detik | 0,83 detik | 6,3 kali |
| Jumlah frequent itemsets | 1.514 | 6 | 252 kali |

Waktu tidak bisa turun sebanyak jumlah pola karena ada pekerjaan yang selalu sama di setiap min support: memindai 1.821.757 transaksi untuk menghitung support setiap item, lalu memangkas dan menggabungkan transaksi. Pada 2%, pekerjaan tetap ini hampir seluruh waktunya. Penambangan FP-Growth hanya 0,00006 detik, dan Apriori berhenti di level 2 karena 15 kandidatnya tidak ada yang frequent.

Makin rendah min support, makin besar pekerjaan yang bergantung padanya. Kedua algoritma menanggungnya di tahap yang berbeda:
- **Apriori: level 2.** Pada 0,1% ada 574 item frequent, sehingga semua 164.451 pasangannya menjadi kandidat. Prune tidak membuang satu pun, karena setiap item tunggal sudah frequent. Hanya 393 pasangan (0,24%) yang frequent, dan level 2 memakan sekitar separuh waktu Apriori. Mulai level 3, prune membuat kandidat tinggal sedikit (1.228, 337, 54, 5).
- **FP-Growth: pembentukan FP-tree.** Pada 0,1%, pembentukan pohon 3,33 detik dan penambangan 1,75 detik. Pada 0,5% ke atas, pembentukan pohon mengambil 82% sampai 100% waktu.

**2. Apakah frequent itemsets kedua algoritma sama?** Ya, pada keempat min support. Tidak ada itemset yang hanya ditemukan satu algoritma, dan tidak ada count yang berbeda. Karena itu rules-nya juga sama, termasuk support, confidence, dan lift. Keduanya juga sama dengan `mlxtend` (notebook 03 dan 04). Ini sesuai harapan: keduanya algoritma eksak dengan definisi support dan ambang yang sama, jadi yang berbeda hanya cara menghitungnya.

**3. Algoritma mana yang lebih sesuai untuk DBLP?** Dari segi waktu, keduanya setara pada keempat min support. Selisih median paling besar 6% (Apriori lebih cepat pada 1%), sedangkan derau pengukuran mencapai 14% (bagian 4.4). Pada 0,1%, FP-Growth lebih cepat di ketiga run, tetapi selisihnya hanya 4%, masih di bawah derau.

Hasil ini berbeda dari gambaran umum bahwa FP-Growth jauh lebih cepat daripada Apriori **[PU-1]**. Ada tiga sifat data DBLP yang menjelaskannya:
1. *Transaksi pendek.* 58,4% author hanya publish di satu venue (notebook 02). Pada 0,1%, hanya 536.543 transaksi yang berisi minimal dua item frequent, dan setelah transaksi identik digabung tersisa 315.694. Hanya transaksi ini yang dipindai Apriori di setiap level.
2. *Pola pendek.* Itemset terpanjang berisi enam item, jadi Apriori cukup menjalankan enam level.
3. *Optimasi yang sama.* Kedua implementasi memakai pra-pemrosesan yang sama. Apriori juga memilih cara menghitung kandidat yang lebih murah untuk setiap transaksi. Tanpa pilihan ini, transaksi terpanjang (187 item frequent pada 0,1%) menghasilkan terlalu banyak subset.

FP-Growth tetap dipilih sebagai algoritma utama, dengan dua alasan:
- *Tidak membangkitkan kandidat.* Biaya kandidat Apriori tumbuh kuadratik terhadap jumlah item frequent: dari 2% ke 0,1%, item frequent naik 96 kali, tetapi kandidat level 2 naik sekitar 11.000 kali. Jika min support diturunkan di bawah 0,1%, biaya ini diperkirakan tumbuh lebih cepat daripada biaya FP-tree. **Perkiraan ini belum diukur** (keterbatasan 3).
- *Penambangannya lebih ringan.* Penambangan FP-Growth pada 0,1% memakan 1,75 detik, sedangkan level 2 ke atas Apriori 4,42 detik. Total waktunya tetap setara karena FP-Growth menghabiskan lebih banyak waktu untuk membangun pohon. Perbandingan ini kasar: kedua angka berasal dari run berbeda (notebook 06 dan 03), dan level 1 Apriori tidak melakukan pekerjaan yang persis sama dengan pembentukan FP-tree.

**Kaitan dengan pertanyaan kesimpulan.**
- *H.6 (algoritma dengan performa terbaik):* pada data ini keduanya setara dalam waktu dan identik dalam hasil. FP-Growth dipilih karena tidak membangkitkan kandidat. Jawaban ini sudah ada di `laporan/bab/bab5-kesimpulan.tex` butir 6.

---

## 6. Keterbatasan

1. **Satu mesin, tiga pengulangan.** Notebook 06 dijalankan di satu laptop, tiga kali per kombinasi. Run terlambat dan tercepat bisa berbeda sampai 19% (Apriori pada 1%), dan uji A/A di laptop lain menunjukkan selisih sampai 14%. Karena itu selisih di bawah sekitar 15% dianggap setara.
2. **Python murni satu thread.** Waktu absolut mencerminkan overhead interpreter dan dapat berbeda pada implementasi C atau Java **[PU-2]**. Kedua implementasi juga memakai optimasi (penggabungan transaksi identik, pemilihan cara penghitungan kandidat) yang tidak selalu ada pada implementasi buku teks **[PU-3]**, sehingga hasil ini tidak menggambarkan perbandingan Apriori dan FP-Growth versi dasar.
3. **Rentang min support terbatas.** Hanya empat min support dari spesifikasi yang diukur. Klaim bahwa Apriori akan tertinggal pada min support di bawah 0,1% adalah perkiraan dari pertumbuhan kandidat, bukan hasil pengukuran.
4. **Hanya waktu.** Penggunaan memori tidak diukur.
5. **Rincian per level dari run terpisah.** Tabel 4.3 berasal dari satu kali eksekusi notebook 03, bukan dari pengukuran berulang notebook 06. Angka itu hanya dipakai untuk melihat porsi waktu per level.
6. Seluruh keterbatasan Task 4 dan 5 tetap berlaku (item adalah key DBLP, identitas author mengikuti disambiguasi DBLP, author-based menggabungkan 2015-2025).

### Klaim berbasis pengetahuan umum

| Kode | Klaim | Sumber | Dukungan data | Status |
|---|---|---|---|---|
| PU-1 | "Gambaran umum" bahwa FP-Growth jauh lebih cepat daripada Apriori | Literatur dan pengetahuan umum penulis (Han et al., 2000 melaporkan FP-Growth jauh lebih cepat pada data sintetis dan min support rendah) | Tidak diuji. Notebook 06 hanya menunjukkan bahwa pada DBLP dengan keempat min support keduanya setara | Klaim tentang literatur, bukan tentang DBLP. Perlu sitasi (`han2000`) jika dipertahankan; di LaTeX sudah dirumuskan sebagai "gambaran umum" tanpa angka |
| PU-2 | Waktu absolut dapat berbeda pada implementasi C atau Java | Pengetahuan umum penulis | Tidak diuji | Tidak didukung data; dirumuskan sebagai kemungkinan, bukan fakta |
| PU-3 | Penggabungan transaksi identik dan pemilihan cara penghitungan kandidat tidak selalu ada pada implementasi buku teks | Pengetahuan umum penulis. Han, Kamber, dan Pei (2012) menyajikan Apriori dasar lalu membahas teknik peningkatan efisiensi (misalnya transaction reduction) sebagai variasi | Tidak diuji; dampak kedua optimasi pada waktu tidak diukur | Wajar tetapi belum diperiksa ke halaman buku; dirumuskan sebagai "tidak selalu ada", bukan "tidak ada" |

---

## 7. Keputusan dan penyimpangan dari plan

| Kode | Keputusan |
|---|---|
| D0 | Harness dibangun sebelum Apriori ada (pilihan user, 22 November 2026), agar Task 6 tinggal dijalankan begitu Apriori tersedia. |
| D1 | `load_apriori()` memakai `src/apriori.py` jika ada; jika belum, FP-Growth dipakai sebagai pengganti sementara dengan label "PENGGANTI SEMENTARA" di setiap tabel dan grafik. Pada run final, kolom `sumber_apriori` bernilai `src/apriori.py`. |
| D2 | Waktu dengan jam dinding di sekitar pemanggilan, `gc.collect()` sebelum setiap run, tiga pengulangan, median/min/maks. Pemuatan data tidak diukur. Rules kedua algoritma dari `src/rules.py` yang sama. |
| D3 | Test kontrak untuk Apriori ditulis sebelum implementasinya ada (`tests/test_apriori_contract.py`, otomatis di-skip sampai modul ada). |
| D4 | Penggabungan transaksi identik: dilakukan oleh kedua algoritma (keputusan Harfhan di `src/apriori.py`), sehingga perbandingan adil. |
| D5 | Jawaban bagian 8 notebook dan subbab LaTeX Task 6 ditulis oleh Harfhan setelah run final; report ini ditulis Mahesa dari notebook yang sudah di-commit. |
| D6 | Kolom rasio (median Apriori / median FP-Growth) diganti kolom "lebih cepat" beserta selisih dalam persen, di report ini dan di Tabel `tab:t6-waktu` LaTeX, karena arah rasio membingungkan. Di LaTeX (`bab4-task6.tex`, `bab5-kesimpulan.tex` butir 6) alasan utama memilih FP-Growth diubah menjadi "tidak membangkitkan kandidat", dan klaim "FP-Growth konsisten lebih cepat pada 0,1%" diganti karena selisih 4% lebih kecil dari variasi antarpengulangan. Tabel juga dipersempit agar tidak melewati margin. |

---

## 8. Pekerjaan tersisa

- **Output lokal di laptop Mahesa masih hasil pengganti sementara.** `outputs/tables/t6_*.csv` dan `outputs/figures/t6_waktu_per_min_support.png` di laptop Mahesa berasal dari run dengan FP-Growth sebagai pengganti Apriori (kolom `sumber_apriori` = "PENGGANTI SEMENTARA (FP-Growth)"). Angka final hanya ada di notebook yang di-commit dan di laptop Harfhan. Selama itu, **jangan menjalankan `src/build_report_figures.py` di laptop Mahesa**, karena `fig-t6-waktu.tex` akan dibangkitkan ulang dari CSV pengganti. Perbaikan: jalankan ulang notebook 03 dan 06 di laptop Mahesa (waktu akan berbeda dari LaTeX), atau minta Harfhan membagikan `outputs/` miliknya.
- PU-1 di LaTeX (`bab4-task6.tex`, "gambaran umum bahwa FP-Growth jauh lebih cepat") belum diberi sitasi.

---

## 9. File, reproduksi, dan commit

`data/` dan `outputs/` tidak masuk git (dibagikan lewat zip).

**File input**

| File | Asal | Isi |
|---|---|---|
| `data/processed/tx_author.parquet` | notebook 02 | Author-based database, tabel panjang `(tid, item)`; dibaca dengan `load_horizontal` |
| `data/processed/tx_items.csv` | notebook 02 | Nama konferensi per `item_id` |
| `outputs/tables/t4_apriori_level.csv` | notebook 03 | Rincian kandidat dan waktu per level Apriori. Tidak dibaca kode notebook 06; angkanya dikutip manual di bagian 8 notebook dan bagian 4.3 report ini. Belum ada di laptop Mahesa (notebook 03 belum dijalankan di sana) |

**File output: tabel** (`outputs/tables/`)

| File | Baris | Isi |
|---|---|---|
| `t6_waktu_mentah.csv` | 24 | Setiap run. Kolom: `algorithm`, `min_support`, `repeat`, `seconds`, `n_itemsets`, `t_build`, `t_mine` (hanya FP-Growth), `sumber_apriori` |
| `t6_waktu_ringkasan.csv` | 8 | Per algoritma dan min support. Kolom: `min_support`, `algorithm`, `median_s`, `min_s`, `max_s`, `t_build_median_s`, `t_mine_median_s`, `itemsets`, `rasio_apriori_fpgrowth`, `sumber_apriori` |
| `t6_perbandingan_itemset.csv` | 4 | Kolom: `min_support`, `itemsets_apriori`, `itemsets_fpgrowth`, `hanya_apriori`, `hanya_fpgrowth`, `count_berbeda`, `identik`, `sumber_apriori` |
| `t6_perbandingan_rules.csv` | 4 | Kolom: `min_support`, `rules_apriori`, `rules_fpgrowth`, `hanya_apriori`, `hanya_fpgrowth`, `metrik_berbeda`, `identik`, `sumber_apriori` |

**File output: gambar** (`outputs/figures/`): `t6_waktu_per_min_support.png` (waktu per min support, skala log, garis min–maks).

**Laporan LaTeX** (masuk git, ditulis Harfhan)

| File | Isi |
|---|---|
| `laporan/bab/bab4-task6.tex` | Subbab Task 6 (Tabel `tab:t6-jumlah`, `tab:t6-waktu`, jawaban) |
| `laporan/images/fig-t6-waktu.tex` | Grafik TikZ waktu, dibangkitkan `src/build_report_figures.py` dari `t6_waktu_mentah.csv` |
| `laporan/bab/bab5-kesimpulan.tex` | Butir 6 dan keterbatasan pengukuran waktu |

**Kode dan notebook** (masuk git)

| File | Isi |
|---|---|
| `src/benchmark.py` | `load_apriori`, `standin_apriori`, `time_runs`, `TimedRun`, `itemsets_of` |
| `src/apriori.py` | `apriori`, `generate_candidates`, `count_candidates`, `AprioriResult` |
| `src/fpgrowth.py`, `src/rules.py`, `src/validation.py`, `src/fpm_data.py` | Dipakai ulang dari Task 4 dan 5 |
| `src/build_performance_notebook.py` | Pembangkit notebook 06 |
| `tests/test_benchmark.py`, `tests/test_apriori_contract.py` | Test `pytest` (total 68 test di `tests/`) |
| `notebooks/06_performance.ipynb` | Notebook hasil eksekusi (run final oleh Harfhan) |
| `docs/reports/task-6-report.md` | Report ini |

**Reproduksi** (dari akar repo):
```bash
.venv/Scripts/python -m pytest tests
.venv/Scripts/python src/build_performance_notebook.py
.venv/Scripts/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=dm-dblp --ExecutePreprocessor.timeout=-1 notebooks/06_performance.ipynb
```
Waktu akan berbeda antar mesin; jumlah itemset dan rules harus sama persis.

**Commit**

| Commit | Penulis | Isi |
|---|---|---|
| `83f6b42`, `bfa0f37` | Mahesa | Harness notebook 06, `src/benchmark.py`, test |
| `144c6be`, `a14dad4`, `b51ce88` | Harfhan | `src/apriori.py`, notebook 03, perbaikan pengecekan panjang transaksi |
| `f3eda7a` | Harfhan | Eksekusi notebook 06 dan jawaban bagian 8 |
| `42075ea` | Harfhan | LaTeX Task 4 Apriori dan Task 6 |

---

## 10. Langkah berikutnya

- **Bagian E (`07_temporal`)**: FP-Growth dan rules per periode (2015-2017, 2018-2020, 2021-2023, 2024-2025) pada author-year-based database. Karena Task 6 menunjukkan keduanya identik dalam hasil, Bagian E cukup memakai FP-Growth.
- Selesaikan butir di bagian 8 (output lokal, sitasi PU-1, kompilasi LaTeX).
