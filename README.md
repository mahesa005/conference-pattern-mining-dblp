# Conference Popularity and Association Pattern Mining pada Dataset DBLP

Tugas besar Data Mining (STEI ITB): analisis popularitas konferensi dan penambangan pola asosiasi antarkonferensi dari dump XML DBLP, publikasi `inproceedings` 2015-2025.

Anggota: Izhar Alif Akbar (18223129), Harfhan Ikhtiar (18223123), Mahesa Andre (13523140).

## Struktur

```
notebooks/   notebook per tahap (dibangkitkan oleh src/build_*_notebook.py)
src/         skrip pembangun notebook dan pembangkit gambar TikZ laporan
laporan/     laporan LaTeX 12 bab (XeLaTeX + biber), dikompilasi dengan ./build.sh
docs/        report per task (markdown) dari tim
data/        TIDAK ada di repositori, dibagikan sebagai zip
outputs/     tabel dan gambar hasil notebook, dibagikan bersama zip data
```

## Notebook

| Notebook | Isi | Status |
|---|---|---|
| `00_extract` | Ekstraksi `dblp.xml.gz` menjadi tabel mentah | selesai |
| `01_eda` | Task 1 (pemahaman data dan preprocessing) dan Task 2 (popularitas konferensi) | selesai |
| `02_transactions` | Task 3 (dua transactional database) | selesai |
| `03_apriori` | Task 4 (Apriori, validasi mlxtend) | selesai |
| `04_fpgrowth` | Task 4 (FP-Growth, validasi mlxtend) | selesai |
| `05_rules` | Task 5 (association rules) | selesai |
| `06_performance` | Task 6 (perbandingan Apriori dan FP-Growth) | selesai |
| `07_temporal` | Bagian E (analisis temporal) | selesai |

Notebook dibangkitkan dari skrip pembangun: ubah `src/build_<nama>_notebook.py`, lalu jalankan skripnya untuk menulis ulang `.ipynb`. Notebook mencari `data/processed/` dan `outputs/` relatif terhadap akar repositori, jadi jalankan dari akar atau dari folder `notebooks/`.

## Data

Ekstrak zip data ke akar repositori sehingga terbentuk `data/` (berisi `dblp.xml.gz`, `dblp.dtd`, dan `processed/`) dan `outputs/`. Dump DBLP diunduh 19 November 2026 dari https://dblp.org/xml/ (SHA-256 tercatat di `data/processed/dump_info.json`).

## Laporan

PDF final ada di `laporan/Laporan.pdf` (58 halaman). Sumber LaTeX ada di `laporan/`, dengan format dokumen (margin, huruf, judul bab, keterangan gambar, dan gaya sitasi) pada `laporan/format-laporan.cls`. Untuk menyusun ulang PDF:

```
cd laporan && ./build.sh
```

Memerlukan XeLaTeX, biber, dan font Times New Roman. Diagram dan grafik pada `laporan/images/fig-*.tex` ditulis dengan TikZ; sebagian dibangkitkan oleh `src/build_report_figures.py` dari `outputs/tables/*.csv`.
