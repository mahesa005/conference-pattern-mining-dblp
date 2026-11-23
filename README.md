# Conference Popularity and Association Pattern Mining pada Dataset DBLP

Tugas besar Data Mining, STEI ITB. Proyek ini mengukur popularitas konferensi ilmu komputer dan mencari kombinasi konferensi yang sering dipilih oleh penulis yang sama, memakai Apriori dan FP-Growth pada publikasi `inproceedings` DBLP periode 2015-2025.

**Anggota:** Izhar Alif Akbar (18223129), Harfhan Ikhtiar (18223123), Mahesa Andre (13523140).

## Ringkasan Hasil

| Hal | Hasil |
|---|---|
| Data | 1.997.244 makalah, 1.821.757 penulis unik, 4.373 konferensi (venue) setelah preprocessing |
| Konferensi paling populer | NeurIPS (25.455 makalah, 57.800 penulis unik) |
| Pasangan konferensi paling sering muncul bersama | ICML + NeurIPS (18.503 penulis, support 1,02%) |
| Rule dengan lift tertinggi | ECCV + ACM Multimedia + NeurIPS => AAAI + CVPR + ICCV (lift 172,27) |
| Apriori vs FP-Growth | Hasil identik, waktu setara (selisih median paling besar 6%) |
| Analisis temporal | Pusat asosiasi bergeser dari GLOBECOM + ICC (2015-2017) ke ICLR + NeurIPS (2024-2025) |

Penjelasan lengkap, interpretasi, dan keterbatasan ada pada laporan: [`laporan/Laporan.pdf`](laporan/Laporan.pdf).

## Struktur Repositori

```
notebooks/   delapan notebook, dijalankan berurutan (00 sampai 07)
src/         modul algoritma (apriori, fpgrowth, rules, temporal, benchmark, validation)
             dan skrip pembangun notebook (build_*_notebook.py)
tests/       uji unit untuk modul algoritma (pytest)
docs/        report per task dalam markdown (Task 4, 5, 6, dan analisis temporal)
laporan/     laporan LaTeX (12 bab) beserta PDF final
data/        TIDAK ada di repositori (lihat bagian Data)
outputs/     tabel dan gambar hasil notebook, dibuat saat notebook dijalankan
```

## Notebook

Setiap notebook membaca keluaran notebook sebelumnya dan menyimpan hasilnya, sehingga dijalankan berurutan.

| Notebook | Isi | Spesifikasi | Masukan utama | Keluaran utama |
|---|---|---|---|---|
| `00_extract` | Ekstraksi `dblp.xml.gz` menjadi tabel mentah | Pendukung | dump DBLP | `inproceedings_raw.parquet` |
| `01_eda` | Pemahaman data, preprocessing, dan popularitas konferensi | Task 1, 2 | tabel mentah | `inproceedings_clean`, `paper_author` |
| `02_transactions` | Dua transactional database (author-based dan author-year-based) | Task 3 | `paper_author` | `tx_author*`, `tx_author_year*` |
| `03_apriori` | Apriori beserta validasi `mlxtend` | Task 4 | `tx_author` | itemset Apriori |
| `04_fpgrowth` | FP-Growth beserta validasi `mlxtend` | Task 4 | `tx_author` | itemset FP-Growth |
| `05_rules` | Association rules (min confidence 50%) | Task 5 | itemset FP-Growth | rules dan top 10 lift |
| `06_performance` | Perbandingan Apriori dan FP-Growth | Task 6 | `tx_author` | tabel jumlah pola dan waktu |
| `07_temporal` | Analisis asosiasi empat periode | Bagian E | `tx_author_year` | rules per periode |

Apriori dan FP-Growth diimplementasikan sendiri pada `src/apriori.py` dan `src/fpgrowth.py`, lalu hasilnya divalidasi terhadap `mlxtend` (itemset dan support harus identik). Notebook dibangkitkan dari skrip pembangun: ubah `src/build_<nama>_notebook.py`, lalu jalankan skripnya untuk menulis ulang `.ipynb`.

## Cara Menjalankan

Python 3.9 atau lebih baru.

```
pip install -r requirements.txt
```

1. Letakkan `dblp.xml.gz` dan `dblp.dtd` di `data/raw/`, dan tulis tanggal unduh di `data/raw/DOWNLOAD_DATE.txt`.
2. Jalankan notebook `00_extract` sampai `07_temporal` berurutan, dari akar repositori atau dari folder `notebooks/`. Seed tetap 42, dan notebook `00_extract` memerlukan sekitar dua menit.
3. Uji unit: `pytest tests`.

## Data

Data tidak disertakan karena ukurannya besar (dump 1,1 GB). Sumber: https://dblp.org/xml/ (`dblp.xml.gz` dan `dblp.dtd`), diunduh 19 November 2026, SHA-256 `7f2805bdd04d523caac706b5e20f0a2aac447c24f2cdee54f13e7a1606c5fad1`. Seluruh keluaran dapat dibangkitkan ulang dari dump dengan menjalankan notebook berurutan. Folder `data/processed/` dan `outputs/` dibuat oleh notebook dan tidak di-commit. Nilai SHA-256 yang sama tercatat di `data/processed/dump_info.json`.

## Laporan

PDF final ada di `laporan/Laporan.pdf`. Sumber LaTeX ada di `laporan/`, dengan format dokumen (margin, huruf, judul bab, keterangan gambar, dan gaya sitasi) pada `laporan/format-laporan.cls`. Untuk menyusun ulang PDF:

```
cd laporan && ./build.sh
```

Memerlukan XeLaTeX, biber, dan font Times New Roman. Diagram dan grafik pada `laporan/images/fig-*.tex` ditulis dengan TikZ, dan sebagian dibangkitkan oleh `src/build_report_figures.py` dari `outputs/tables/*.csv`.
