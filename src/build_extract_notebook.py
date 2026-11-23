import json
import sys
import textwrap
from pathlib import Path
from uuid import uuid4

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path(__file__).resolve().parents[1] / "notebooks" / "00_extract.ipynb"
HR = "---"


def src(text: str) -> str:
    return textwrap.dedent(text).strip("\n")


def md(source: str) -> dict:
    return {"cell_type": "markdown", "id": uuid4().hex[:8], "metadata": {}, "source": src(source)}


def code(source: str) -> dict:
    return {
        "cell_type": "code", "execution_count": None, "id": uuid4().hex[:8],
        "metadata": {}, "outputs": [], "source": src(source),
    }


def section(title: str, anchor: str) -> dict:
    return md(f"{HR}\n\n# {title} <a name=\"{anchor}\"></a>\n\n{HR}")


cells = []

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
cells.append(md(f"""
{HR}

# Conference Popularity and Association Pattern Mining pada Dataset DBLP

*Notebook 00: ekstraksi dump XML DBLP menjadi tabel inproceedings 2015-2025.*
"""))

cells.append(md(f"""
{HR}

## Kelompok Tugas Besar Data Mining

- Izhar Alif Akbar (18223129)
- Harfhan Ikhtiar (18223123)
- Mahesa Andre (13523140)
"""))

cells.append(md(f"""
{HR}

## Table of Contents

1. [**Introduction**](#1)
2. [**Initialization**](#2)
3. [**Informasi Dump**](#3)
4. [**Parsing XML**](#4)
5. [**Validasi dan Penyimpanan**](#5)
"""))

# ---------------------------------------------------------------------------
# 1. Introduction
# ---------------------------------------------------------------------------
cells.append(section("Introduction", "1"))

cells.append(md("""
## Overview

*Notebook ini adalah langkah pertama alur tugas besar. Dump XML DBLP yang berukuran sekitar 1,1 GB dibaca secara streaming, lalu hanya record `inproceedings` pada 2015-2025 yang disimpan sebagai tabel parquet.*

*Notebook berikutnya (`01_eda`) membaca tabel tersebut tanpa mem-parsing XML lagi, sehingga eksplorasi dan preprocessing dapat dijalankan ulang dengan cepat.*
"""))

cells.append(md("""
## Aim

*Menghasilkan data mentah yang dapat direproduksi, lengkap dengan catatan sumber dump (tanggal unduh, ukuran, dan checksum) serta jumlah record untuk setiap jenis publikasi.*
"""))

cells.append(md("""
## Dataset

*Data bersumber dari DBLP di: https://dblp.org/xml/*

*Dump terdiri atas `dblp.xml.gz` (data) dan `dblp.dtd` (aturan struktur dan definisi entitas karakter). Dump diunduh pada 19 November 2026.*

*Dataset dipakai untuk mencari konferensi dengan aktivitas publikasi tertinggi dan pola konferensi yang sering dipilih oleh author yang sama.*

**Attributes**

1.  `key`        : ID unik record, mis. `conf/kdd/ChenG16` (atribut XML)
2.  `author`     : nama author, berulang satu tag per orang
3.  `title`      : judul publikasi
4.  `year`       : tahun publikasi
5.  `booktitle`  : nama acara sebagaimana tertulis pada prosiding
6.  `crossref`   : rujukan ke record `proceedings` induk
"""))

cells.append(md("""
## Approach: Streaming Parser

*DBLP menyimpan jutaan record dalam satu berkas XML, sehingga berkas tidak dimuat ke memori sekaligus. `lxml.etree.iterparse` membaca satu record, mengambil field yang dibutuhkan, lalu membuang record itu dari memori sebelum lanjut ke record berikutnya.*

*Parser memuat `dblp.dtd` agar entitas karakter seperti `&ccedil;` terbaca sebagai huruf yang benar. Seluruh jenis record dihitung untuk keperluan deskripsi dataset, tetapi hanya `inproceedings` dengan tahun 2015-2025 yang disimpan.*

```
dblp.xml.gz + dblp.dtd
    |
    +-- hitung semua jenis record -> record_types_*.csv
    +-- simpan inproceedings 2015-2025 -> inproceedings_raw.parquet
    +-- simpan judul proceedings konferensi -> venue_proceedings.csv
    +-- catat identitas dump -> dump_info.json
```
"""))

# ---------------------------------------------------------------------------
# 2. Initialization
# ---------------------------------------------------------------------------
cells.append(section("Initialization", "2"))

cells.append(md("""
## Environment Setup

Notebook ini tidak memakai GPU. Parsing XML memakan waktu sekitar dua menit dengan memori di bawah 2 GB pada Mac dengan RAM 16 GB.
"""))

cells.append(md("Sel berikut memasang semua pustaka yang dipakai notebook ini."))

cells.append(code("""
%pip install -q lxml pyarrow pandas numpy
"""))

cells.append(md("""
## Import Libraries

Seluruh `import` untuk notebook ini dikumpulkan di satu sel.
"""))

cells.append(code("""
import gzip
import hashlib
import json
import os
import random
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from lxml import etree
"""))

cells.append(md("""
## Seed Everything

Proses ekstraksi bersifat deterministik, tetapi seed tetap ditetapkan agar seluruh notebook dalam proyek ini seragam.
"""))

cells.append(code("""
def seed_everything(seed: int = 42):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)

seed_everything(42)
"""))

cells.append(md("""
## Settings

Seluruh path dan parameter ekstraksi dipusatkan di kelas `Settings`, sehingga perubahan rentang tahun atau lokasi data cukup dilakukan di satu tempat.
"""))

cells.append(code("""
class Settings:
    SEED = 42
    ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

    RAW_DIR = ROOT / "data" / "raw"
    PROC_DIR = ROOT / "data" / "processed"
    TAB_DIR = ROOT / "outputs" / "tables"

    XML_GZ = RAW_DIR / "dblp.xml.gz"
    DTD = RAW_DIR / "dblp.dtd"
    DOWNLOAD_DATE = RAW_DIR / "DOWNLOAD_DATE.txt"
    SOURCE_URL = "https://dblp.org/xml/"

    YEAR_MIN = 2015
    YEAR_MAX = 2025
    RECORD_TAGS = ("article", "inproceedings", "proceedings", "book", "incollection",
                   "phdthesis", "mastersthesis", "www", "data")
    SAMPLE_KEYS = ("conf/kdd/ChenG16", "conf/cvpr/SunTNP11", "conf/dac/X22",
                   "conf/rlc/IshfaqT0LLMP024")

CFG = Settings()
CFG.PROC_DIR.mkdir(parents=True, exist_ok=True)
CFG.TAB_DIR.mkdir(parents=True, exist_ok=True)
"""))

cells.append(md("""
## Load Dataset

Pemeriksaan awal memastikan kedua berkas dump tersedia sebelum parsing dimulai. Tidak ada pembacaan isi data pada tahap ini.
"""))

cells.append(code("""
for path in (CFG.XML_GZ, CFG.DTD, CFG.DOWNLOAD_DATE):
    print(f"{path.name:18s} ada={path.exists()}  ukuran={path.stat().st_size / 1e6:,.1f} MB")
"""))

# ---------------------------------------------------------------------------
# 3. Informasi Dump
# ---------------------------------------------------------------------------
cells.append(section("Informasi Dump", "3"))

cells.append(md("""
## 3.1 Identitas Berkas

Tanggal unduh, ukuran, dan checksum SHA-256 dicatat agar siapa pun dapat memastikan bahwa dump yang dipakai sama dengan dump yang dianalisis di laporan. DBLP memperbarui dump secara berkala, sehingga angka pada dump lain akan berbeda.
"""))

cells.append(code("""
def sha256_of(path, chunk=1 << 24):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            digest.update(block)
    return digest.hexdigest()

dump_info = {
    "source_url": CFG.SOURCE_URL,
    "downloaded_at": CFG.DOWNLOAD_DATE.read_text().strip(),
    "xml_gz_bytes": CFG.XML_GZ.stat().st_size,
    "xml_gz_sha256": sha256_of(CFG.XML_GZ),
    "dtd_bytes": CFG.DTD.stat().st_size,
}
pd.Series(dump_info, name="nilai").to_frame()
"""))

cells.append(md("""
## 3.2 Header XML dan DTD

Tiga baris pertama XML menunjukkan encoding, rujukan ke DTD, dan elemen akar. DTD kemudian mendefinisikan elemen apa saja yang boleh berada di bawah akar.
"""))

cells.append(code("""
with gzip.open(CFG.XML_GZ, "rt", encoding="iso-8859-1") as fh:
    for _ in range(3):
        print(next(fh).rstrip())

print()
for line in CFG.DTD.read_text(encoding="iso-8859-1").splitlines():
    if line.startswith(("<!ELEMENT dblp", "<!ELEMENT inproceedings", "<!ATTLIST inproceedings")) or "article|inproceedings" in line:
        print(line)
"""))

cells.append(md("""
#### Insights

> 1. Berkas XML dibuka dengan encoding ISO-8859-1 dan rujukan ke `dblp.dtd`, sehingga DTD harus berada di folder yang sama dengan `dblp.xml.gz` dan dimuat oleh parser.
> 2. Elemen akar `dblp` berisi daftar datar jenis record, dan `inproceedings` hanya mewajibkan atribut `key`.
> 3. Field lain (`author`, `title`, `year`, `booktitle`) opsional menurut DTD, sehingga nilai kosong diperiksa pada preprocessing.
"""))

# ---------------------------------------------------------------------------
# 4. Parsing XML
# ---------------------------------------------------------------------------
cells.append(section("Parsing XML", "4"))

cells.append(md("""
Fungsi `parse_dump` membaca dump satu kali dari awal sampai akhir. Untuk setiap record, fungsi menambah hitungan jenis publikasi, menyimpan `inproceedings` yang berada pada rentang tahun, mengambil judul prosiding konferensi, dan menyalin beberapa record contoh yang dipakai pada penjelasan struktur di notebook EDA.
"""))

cells.append(code("""
def parse_dump(path, year_min, year_max, sample_keys):
    counts_all, counts_period = Counter(), Counter()
    rows, samples, proceedings = [], {}, {}
    started = time.time()

    with gzip.open(path, "rb") as fh:
        context = etree.iterparse(fh, events=("end",), tag=CFG.RECORD_TAGS,
                                  load_dtd=True, resolve_entities=True, huge_tree=True)
        for i, (_, el) in enumerate(context):
            tag, key = el.tag, el.get("key")
            counts_all[tag] += 1

            year_text = el.findtext("year")
            year = int(year_text) if year_text and year_text.strip().isdigit() else None

            if key in sample_keys:
                samples[key] = etree.tostring(el, encoding="unicode", with_tail=False).strip()

            if year is not None and year_min <= year <= year_max:
                counts_period[tag] += 1
                title_el = el.find("title")
                title = "".join(title_el.itertext()) if title_el is not None else None
                if tag == "inproceedings":
                    rows.append({
                        "key": key,
                        "title": title,
                        "year": year_text,
                        "booktitle": el.findtext("booktitle"),
                        "crossref": el.findtext("crossref"),
                        "authors": "|".join("".join(a.itertext()) for a in el.findall("author")),
                    })
                elif tag == "proceedings" and key.startswith("conf/"):
                    proceedings[key] = {"year": year, "title": title}

            el.clear()
            while el.getprevious() is not None:
                del el.getparent()[0]

            if i and i % 3_000_000 == 0:
                print(f"{i:>10,} record dibaca | {len(rows):>9,} inproceedings | {time.time() - started:5.0f} dtk")

    return rows, counts_all, counts_period, samples, proceedings, time.time() - started
"""))

cells.append(code("""
rows, counts_all, counts_period, samples, proceedings, elapsed = parse_dump(
    CFG.XML_GZ, CFG.YEAR_MIN, CFG.YEAR_MAX, CFG.SAMPLE_KEYS
)
print(f"Selesai dalam {elapsed:.0f} detik")
print(f"Total record: {sum(counts_all.values()):,} | inproceedings 2015-2025: {len(rows):,}")
"""))

cells.append(md("""
#### Insights

> 1. Parser membaca seluruh record dalam satu lintasan, dan record dibuang dari memori setelah diproses sehingga memori tetap kecil.
> 2. Jumlah baris tabel `inproceedings` harus sama dengan hitungan `inproceedings` pada rentang tahun, dan kesesuaian ini diperiksa pada bagian berikutnya.
"""))

# ---------------------------------------------------------------------------
# 5. Validasi dan Penyimpanan
# ---------------------------------------------------------------------------
cells.append(section("Validasi dan Penyimpanan", "5"))

cells.append(md("""
## 5.1 Validasi Hasil Parsing

Sebelum disimpan, jumlah baris dicocokkan dengan hitungan jenis record, lalu kondisi kolom diperiksa. Tabel jenis publikasi di bawah ini dipakai ulang di notebook EDA.
"""))

cells.append(code("""
raw = pd.DataFrame(rows)
assert len(raw) == counts_period["inproceedings"], "jumlah baris tidak sama dengan hitungan inproceedings"
print(f"Baris: {len(raw):,} | kolom: {list(raw.columns)}")

pd.DataFrame({
    "tipe_data": raw.dtypes.astype(str),
    "kosong": raw.isna().sum().where(raw.columns != "authors", (raw["authors"] == "").sum()),
})
"""))

cells.append(code("""
record_types = pd.DataFrame({
    "seluruh_dblp": pd.Series(counts_all),
    "periode_2015_2025": pd.Series(counts_period),
}).fillna(0).astype(int).sort_values("seluruh_dblp", ascending=False)
record_types.loc["TOTAL"] = record_types.sum()
record_types
"""))

cells.append(md("""
## 5.2 Penyimpanan

Tabel mentah disimpan sebagai parquet agar tipe data dan ukuran file efisien. Hitungan jenis publikasi, judul prosiding, dan identitas dump disimpan sebagai berkas kecil yang dibaca notebook EDA. Untuk setiap venue dipilih judul prosiding edisi utama terbaru, yaitu `key` berbentuk `conf/venue/tahun`, agar bukan volume workshop yang terambil.
"""))

cells.append(code("""
raw.to_parquet(CFG.PROC_DIR / "inproceedings_raw.parquet", index=False)

for name, counts in (("record_types_all.csv", counts_all), ("record_types_2015_2025.csv", counts_period)):
    (pd.Series(counts, name="n").sort_values(ascending=False)
       .rename_axis("type").to_csv(CFG.TAB_DIR / name))

venue_proceedings = (
    pd.DataFrame([{"proceedings_key": k, "venue": k.split("/")[1], **v} for k, v in proceedings.items()])
    .assign(is_main=lambda d: d["proceedings_key"].str.fullmatch(r"conf/[^/]+/\\d{4}(-\\d+)?"))
    .sort_values(["venue", "is_main", "year", "proceedings_key"], ascending=[True, False, False, True])
    .drop_duplicates("venue")
    .drop(columns="is_main")
    .rename(columns={"title": "proceedings_title"})
)
venue_proceedings.to_csv(CFG.PROC_DIR / "venue_proceedings.csv", index=False)

dump_info.update({
    "parsed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "parse_seconds": round(elapsed),
    "total_records": int(sum(counts_all.values())),
    "inproceedings_2015_2025": int(len(raw)),
    "sample_records": samples,
})
(CFG.PROC_DIR / "dump_info.json").write_text(json.dumps(dump_info, indent=2, ensure_ascii=False), encoding="utf-8")

print("Tersimpan:", *sorted(p.name for p in CFG.PROC_DIR.glob("*") if p.suffix in (".parquet", ".csv", ".json")), sep="\\n  ")
print(f"Venue dengan judul prosiding: {len(venue_proceedings):,}")
"""))

cells.append(md("""
#### Insights

> 1. Dump berisi 13.127.979 record dari sembilan jenis publikasi, dengan 4.004.309 `inproceedings` di antaranya.
> 2. Sebanyak 2.004.202 `inproceedings` berada pada 2015-2025 dan menjadi data mentah untuk notebook berikutnya.
> 3. Jenis `www` hanya satu record pada rentang tahun karena berupa halaman profil author yang umumnya tidak bertahun.
> 4. Kolom `year` tersimpan sebagai teks karena XML tidak bertipe data, dan dikonversi ke bilangan bulat pada preprocessing.
"""))

# ---------------------------------------------------------------------------
# Notebook writer
# ---------------------------------------------------------------------------
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python (dm-dblp)", "language": "python", "name": "dm-dblp"},
        "language_info": {"name": "python", "version": "3.9"},
    },
    "cells": cells,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(cells)} cells -> {OUT}")
