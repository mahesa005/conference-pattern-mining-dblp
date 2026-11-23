import json
import sys
import textwrap
from pathlib import Path
from uuid import uuid4

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path(__file__).resolve().parents[1] / "notebooks" / "01_eda.ipynb"
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


def part(title: str, subtitle: str, anchor: str) -> dict:
    return md(
        f"{HR}\n\n{HR}\n\n"
        f"# {title} <a name=\"{anchor}\"></a>\n\n"
        f"*{subtitle}*\n\n"
        f"{HR}\n\n{HR}"
    )


cells = []

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
cells.append(md(f"""
{HR}

# Conference Popularity and Association Pattern Mining pada Dataset DBLP

*Notebook 01: Data Understanding and Preprocessing, lalu Conference Popularity Analysis.*
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

**[Part I: Data Understanding and Preprocessing](#part1)**

3. [**Eksplorasi Dataset**](#3)
4. [**Preprocessing**](#4)
5. [**Statistik Dataset Bersih**](#5)

**[Part II: Conference Popularity Analysis](#part2)**

6. [**Analisis Popularitas Konferensi**](#6)
"""))

# ---------------------------------------------------------------------------
# 1. Introduction
# ---------------------------------------------------------------------------
cells.append(section("Introduction", "1"))

cells.append(md("""
## Overview

*DBLP (Digital Bibliography and Library Project) adalah basis data bibliografi ilmu komputer yang mencatat judul, author, tahun, dan venue setiap publikasi.*

*Notebook ini memahami struktur dataset DBLP, menyiapkan datanya untuk Frequent Pattern Mining dan Association Rule Mining, lalu menganalisis popularitas konferensi. Popularitas diukur dari aktivitas publikasi, yaitu jumlah publikasi dan jumlah author unik.*
"""))

cells.append(md("""
## Aim

1. *Menjelaskan struktur dataset, atribut, jumlah record, dan jenis publikasi yang tersedia.*
2. *Membersihkan data dalam enam tahap preprocessing (konsistensi tahun, missing values, seleksi konferensi dan workshop, normalisasi venue, duplikat, normalisasi author) beserta alasan tiap tahap.*
3. *Menampilkan statistik dataset bersih: total publikasi, author unik, venue unik, distribusi per tahun, dan distribusi per konferensi.*
4. *Menentukan 10 konferensi dengan publikasi terbanyak dan 10 konferensi dengan author unik terbanyak, lalu menganalisis tren per tahun dan membandingkan kedua peringkat.*
5. *Menyimpulkan konferensi terpopuler, hubungan antara jumlah publikasi dan jumlah author unik, serta perubahan aktivitas selama periode pengamatan.*
"""))

cells.append(md("""
## Metric

***Jumlah publikasi** adalah banyaknya paper `inproceedings` setelah preprocessing. **Author unik** adalah banyaknya nama author berbeda, dan **venue unik** adalah banyaknya konferensi berbeda yang diidentifikasi dari `key` DBLP.*

***Retensi** menunjukkan seberapa besar data yang bertahan setelah preprocessing, sedangkan **CAGR** (compound annual growth rate) meringkas laju pertumbuhan publikasi per tahun pada periode lengkap 2015-2024.*

$$\\text{Retensi} = \\frac{N_{\\text{bersih}}}{N_{\\text{mentah}}}
\\qquad
\\text{CAGR} = \\left(\\frac{N_{2024}}{N_{2015}}\\right)^{1/9} - 1$$

*Peringkat konferensi disusun menurut jumlah publikasi dan jumlah author unik. **Paper per author** menunjukkan seberapa sering author yang sama kembali menerbitkan karya di sebuah konferensi.*

$$\\text{Paper per author} = \\frac{\\text{jumlah pasangan paper-author di venue}}{\\text{jumlah author unik di venue}}$$
"""))

cells.append(md("""
## Dataset

*Data bersumber dari DBLP di: https://dblp.org/xml/*

*Dump XML diunduh pada 19 November 2026 (`dblp.xml.gz`, sekitar 1,1 GB, beserta `dblp.dtd`). Dump memuat 13.127.979 record dari sembilan jenis publikasi, dan 2.004.202 di antaranya adalah `inproceedings` pada 2015-2025. Ekstraksi dikerjakan pada notebook `00_extract`.*

*Dataset dipakai untuk mencari konferensi dengan aktivitas publikasi tertinggi dan pola konferensi yang sering dipilih oleh author yang sama.*

**Attributes**

1.  `key`        : ID unik record, mis. `conf/kdd/ChenG16` (atribut XML)
2.  `author`     : nama author, berulang satu tag per orang
3.  `title`      : judul publikasi
4.  `year`       : tahun publikasi
5.  `booktitle`  : nama acara sebagaimana tertulis pada prosiding
6.  `crossref`   : rujukan ke record `proceedings` induk

**Atribut turunan**

`venue` : konferensi tempat paper terbit, diturunkan dari segmen kedua `key` (bukan tag XML)
"""))

cells.append(md("""
## Approach: Eksplorasi, Preprocessing, lalu Statistik

*Notebook ini membaca tabel mentah hasil `00_extract`, menjelaskan kondisinya, membersihkannya dalam enam tahap, lalu menghitung statistik pada data bersih.*

*Setiap tahap menyimpan hasilnya ke disk dan tahap berikutnya hanya membaca, sehingga bagian statistik dapat dijalankan ulang tanpa mengulang preprocessing.*

```
inproceedings_raw.parquet            (00_extract)
    |
    +-- Part I: Data Understanding and Preprocessing
    |     3. Eksplorasi: struktur, jenis publikasi, kondisi data
    |     4. Preprocessing: tahun, missing, seleksi conf/, venue, duplikat, author
    |           -> inproceedings_clean.parquet, paper_author.parquet
    |     5. Statistik: total, per tahun, per konferensi, per author
    |
    +-- Part II: Conference Popularity Analysis
    |     6. Popularitas konferensi: top 10, tren, perbandingan peringkat
    |     7. Ringkasan dan langkah berikutnya
```
"""))

# ---------------------------------------------------------------------------
# 2. Initialization
# ---------------------------------------------------------------------------
cells.append(section("Initialization", "2"))

cells.append(md("""
## Environment Setup

Notebook ini tidak memakai GPU. Seluruh sel dapat dijalankan dalam beberapa menit pada Mac dengan RAM 16 GB. Prasyaratnya adalah notebook `00_extract` sudah dijalankan sehingga `data/processed/inproceedings_raw.parquet` tersedia.
"""))

cells.append(md("Sel berikut memasang semua pustaka yang dipakai notebook ini."))

cells.append(code("""
%pip install -q numpy pandas matplotlib pyarrow
"""))

cells.append(md("""
## Import Libraries

Seluruh `import` untuk notebook ini dikumpulkan di satu sel.
"""))

cells.append(code("""
import json
import os
import random
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, PathPatch, Rectangle
from matplotlib.path import Path as MplPath
from matplotlib.ticker import FuncFormatter
"""))

cells.append(md("""
## Seed Everything

Analisis pada notebook ini bersifat deterministik, tetapi seed tetap ditetapkan agar seluruh notebook dalam proyek ini seragam.
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

Seluruh path, rentang tahun, dan warna dipusatkan di kelas `Settings`. Palet warna memakai biru sebagai aksen utama, jingga untuk penekanan, dan abu-abu untuk konteks.
"""))

cells.append(code("""
class Settings:
    SEED = 42
    ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

    RAW_DIR = ROOT / "data" / "raw"
    PROC_DIR = ROOT / "data" / "processed"
    TAB_DIR = ROOT / "outputs" / "tables"
    FIG_DIR = ROOT / "outputs" / "figures"

    RAW_PARQUET = PROC_DIR / "inproceedings_raw.parquet"
    CLEAN_PARQUET = PROC_DIR / "inproceedings_clean.parquet"
    PAPER_AUTHOR_PARQUET = PROC_DIR / "paper_author.parquet"

    YEAR_MIN = 2015
    YEAR_MAX = 2025
    YEAR_INCOMPLETE = 2025

    INK = "#0b0b0b"
    INK_2 = "#52514e"
    MUTED = "#898781"
    GRID = "#e1e0d9"
    BASELINE = "#c3c2b7"
    SURFACE = "#fcfcfb"
    BLUE = "#2a78d6"
    BLUE_LIGHT = "#9ec5f4"
    ORANGE = "#eb6834"
    AQUA = "#1baf7a"
    GRAY = "#b9b8b2"
    ORDINAL = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]

CFG = Settings()
CFG.TAB_DIR.mkdir(parents=True, exist_ok=True)
CFG.FIG_DIR.mkdir(parents=True, exist_ok=True)
"""))

cells.append(md("""
Gaya grafik dan beberapa fungsi bantu diatur sekali di sini. Angka ditulis dengan pemisah ribuan titik dan desimal koma agar konsisten dengan laporan berbahasa Indonesia.
"""))

cells.append(code("""
plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
    "figure.facecolor": CFG.SURFACE, "axes.facecolor": CFG.SURFACE, "savefig.facecolor": CFG.SURFACE,
    "font.size": 9.5, "text.color": CFG.INK, "axes.labelcolor": CFG.INK_2,
    "xtick.color": CFG.INK_2, "ytick.color": CFG.INK_2, "axes.edgecolor": CFG.BASELINE,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": CFG.GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False,
})
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 80)


def fmt_id(value, digits=0):
    text = f"{value:,.{digits}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def pct_id(value, digits=1):
    return f"{value:.{digits}f}".replace(".", ",") + "%"


def save_fig(fig, name):
    fig.savefig(CFG.FIG_DIR / name)
    plt.show()


def save_table(df, name, index=True):
    df.to_csv(CFG.TAB_DIR / name, index=index)


def id_ticks(ax, axis="y"):
    formatter = FuncFormatter(lambda v, _: fmt_id(v, 0 if float(v).is_integer() else 1))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(formatter)
"""))

cells.append(md("""
## Load Dataset

Berkas hasil `00_extract` dibaca di sini: tabel mentah, identitas dump, hitungan jenis publikasi, dan judul prosiding setiap venue. Tidak ada visualisasi pada tahap ini.
"""))

cells.append(code("""
dump_info = json.loads((CFG.PROC_DIR / "dump_info.json").read_text(encoding="utf-8"))

record_types = (
    pd.read_csv(CFG.TAB_DIR / "record_types_all.csv", index_col="type").rename(columns={"n": "seluruh_dblp"})
    .join(pd.read_csv(CFG.TAB_DIR / "record_types_2015_2025.csv", index_col="type").rename(columns={"n": "periode"}))
    .fillna(0).astype(int)
)
venue_proceedings = pd.read_csv(CFG.PROC_DIR / "venue_proceedings.csv")
raw = pd.read_parquet(CFG.RAW_PARQUET)

print(f"Dump diunduh : {dump_info['downloaded_at']}")
print(f"Total record : {dump_info['total_records']:,}")
print(f"Data mentah  : {len(raw):,} baris x {raw.shape[1]} kolom")
"""))

# ---------------------------------------------------------------------------
# 3. Eksplorasi Dataset
# ---------------------------------------------------------------------------
cells.append(part("PART I | Data Understanding and Preprocessing",
                  "Memahami struktur dataset DBLP, membersihkannya, dan menghitung statistik dataset bersih.", "part1"))

cells.append(section("Eksplorasi Dataset", "3"))

cells.append(md("""
Bagian ini membahas bentuk file dan struktur record DBLP, atribut yang tersedia, jumlah record, dan jenis publikasi. Seluruh contoh record diambil langsung dari dump, bukan ditulis ulang.
"""))

cells.append(md("""
## 3.1 Struktur File dan Record

DBLP menyajikan datanya sebagai satu berkas XML berisi daftar datar record di bawah elemen akar `<dblp>`, dan nama tag setiap record menunjukkan jenis publikasinya. Record `inproceedings` berikut adalah paper XGBoost, diambil apa adanya dari dump.
"""))

cells.append(code("""
print(dump_info["sample_records"]["conf/kdd/ChenG16"])
"""))

cells.append(md("""
Atribut XML (di dalam tag pembuka) dan elemen anak (di antara tag pembuka dan penutup) dipisahkan berikut dengan mem-parsing record contoh di atas.
"""))

cells.append(code("""
sample = ET.fromstring(dump_info["sample_records"]["conf/kdd/ChenG16"])

structure = pd.DataFrame(
    [{"bagian": "atribut XML", "nama": k, "isi": v} for k, v in sample.attrib.items()]
    + [{"bagian": "elemen anak", "nama": child.tag, "isi": (child.text or "")[:70]} for child in sample]
)
structure
"""))

cells.append(md("""
#### Insights

> 1. Setiap record memiliki dua atribut XML, yaitu `key` (ID unik) dan `mdate` (tanggal modifikasi terakhir).
> 2. Field lain adalah elemen anak di dalam tag `inproceedings`: `author`, `title`, `pages`, `year`, `booktitle`, `ee`, `crossref`, dan `url`.
> 3. Tag `author` berulang satu kali per orang, sehingga satu paper dapat memiliki satu sampai puluhan author. Karena itu data perlu diubah menjadi tabel pasangan paper-author sebelum dibentuk menjadi transaksi.
> 4. `venue` tidak memiliki tag sendiri. Nilainya diturunkan dari segmen kedua `key` (pada contoh ini `kdd`), sedangkan `booktitle` (`KDD`) disimpan sebagai pembanding.
"""))

cells.append(md("""
## 3.2 Jenis Publikasi

Jenis publikasi dibandingkan pada dua cakupan, yaitu seluruh dump dan hanya periode 2015-2025. Jumlah record antarjenis berbeda dari 27 sampai 4,5 juta, sehingga sumbu horizontal memakai skala logaritmik. Batang terang adalah seluruh dump dan batang gelap adalah bagian pada periode analisis.
"""))

cells.append(code("""
types = record_types.copy()
types["porsi_periode_%"] = types["periode"] / types["seluruh_dblp"] * 100
types["porsi_dari_total_%"] = types["seluruh_dblp"] / types["seluruh_dblp"].sum() * 100
types = types.sort_values("seluruh_dblp", ascending=False)
save_table(types, "t1_jenis_publikasi.csv")
types.round(1)
"""))

cells.append(code(r"""
fig, ax = plt.subplots(figsize=(7.0, 4.0))
order = types.index[::-1]
pos = np.arange(len(order))
ax.barh(pos, types.loc[order, "seluruh_dblp"], color=CFG.GRAY, height=0.64, zorder=2)
ax.barh(pos, types.loc[order, "periode"].clip(lower=1), height=0.64, zorder=3,
        color=[CFG.BLUE if name == "inproceedings" else CFG.INK_2 for name in order])
ax.set_yticks(pos)
ax.set_yticklabels(order)
ax.set_xscale("log")
ax.set_xlim(1, 2e7)
ax.set_xticks([1, 100, 1e4, 1e6])
ax.set_xticklabels(["1", "100", "10 rb", "1 jt"])
ax.set_xlabel("Jumlah record (skala logaritmik)")
ax.grid(axis="y", visible=False)
ax.set_title("Jenis publikasi DBLP")
ax.legend(handles=[Patch(color=CFG.GRAY, label="Seluruh dump"), Patch(color=CFG.INK_2, label="Periode 2015-2025"),
                   Patch(color=CFG.BLUE, label="inproceedings 2015-2025")], loc="lower right", fontsize=8.8)
save_fig(fig, "t1_jenis_publikasi.png")
"""))

cells.append(md("""
#### Insights

> 1. Dump berisi 13.127.979 record. `article` (4,53 juta) dan `www` (4,25 juta) menyumbang sekitar 67%, sedangkan `inproceedings` berjumlah 4.004.309 (sekitar 30,5%).
> 2. Sebanyak 2.004.202 record `inproceedings` (50,1%) berada pada periode 2015-2025 dan menjadi data mentah analisis ini. Artinya setengah dari paper konferensi di DBLP terbit dalam sebelas tahun terakhir.
> 3. `www` hanya memiliki satu record pada periode ini, yaitu halaman profil author yang bukan publikasi. `proceedings` (65.903 record) adalah buku prosiding induk yang dirujuk oleh `crossref`, bukan paper. Keduanya tidak dipakai.
> 4. Porsi periode berbeda antarjenis, dari 26,8% (`book`) sampai 70,5% (`data`).
"""))

cells.append(md("""
## 3.3 Atribut dan Kondisi Data Mentah

Tabel mentah diperiksa dari sisi tipe data, nilai kosong, dan komposisi awalan `key` sebagai dasar keputusan preprocessing.
"""))

cells.append(code("""
empty_text = raw.replace("", np.nan)
raw_profile = pd.DataFrame({"tipe_data": raw.dtypes.astype(str)})
raw_profile["kosong"] = empty_text.isna().sum()
raw_profile["kosong_%"] = raw_profile["kosong"] / len(raw) * 100
raw_profile["contoh"] = [empty_text[c].dropna().iloc[0][:45] for c in raw_profile.index]
save_table(raw_profile, "t1_profil_data_mentah.csv")
raw_profile.round(3)
"""))

cells.append(code("""
parts = raw["key"].str.split("/")
key_profile = pd.DataFrame({
    "prefiks": parts.str[0].value_counts(),
})
key_profile["%"] = key_profile["prefiks"] / len(raw) * 100
print(f"Key unik: {raw['key'].is_unique} | jumlah segmen: {parts.str.len().value_counts().to_dict()}")
key_profile.round(2)
"""))

cells.append(md("""
#### Insights

> 1. Dari 2.004.202 record mentah, `title` dan `year` tidak pernah kosong. `booktitle` kosong pada 190 record, `crossref` pada 2.471, dan `author` pada 2.255, semuanya di bawah 0,13%.
> 2. `year` bertipe teks karena XML tidak memiliki tipe data, sehingga perlu dikonversi menjadi bilangan bulat. `key` unik pada seluruh baris.
> 3. Sebanyak 99,8% record berawalan `conf/`. Sisanya (3.163 record) berawalan `journals/` atau `books/`, yaitu `inproceedings` yang diarsipkan DBLP pada seri jurnal atau buku. Perlakuannya dibahas pada subbagian seleksi konferensi.
"""))

# ---------------------------------------------------------------------------
# 4. Preprocessing
# ---------------------------------------------------------------------------
cells.append(section("Preprocessing", "4"))

cells.append(md(r"""
Preprocessing dikerjakan pada salinan data mentah dalam enam tahap berurutan. Setiap tahap berisi alasan, bukti dari data, hasil, dan insight, dan jumlah paper setelah tiap tahap dicatat untuk menelusuri dampaknya.
"""))

cells.append(md(r"""
## 4.1 Rancangan Tahap

Tabel berikut memetakan setiap tahap ke perlakuan dan alasannya. Urutan tahap sama dengan urutan kode pada subbagian berikutnya.

| # | Tahap | Perlakuan | Alasan |
|---|---|---|---|
| 1 | Konsistensi tahun | Konversi teks ke bilangan bulat, lalu validasi rentang 2015-2025 | `year` di XML bertipe teks sehingga tidak dapat dibandingkan atau dihitung |
| 2 | Missing values | Buang paper tanpa author, kolom lain dibiarkan | Paper tanpa author tidak dapat masuk transaksi dan umumnya bukan paper |
| 3 | Seleksi konferensi dan workshop | Tag `inproceedings` (saat ekstraksi) dan `key` berawalan `conf/` | Menurut dokumentasi DBLP, `conf/*` adalah paper konferensi atau workshop |
| 4 | Normalisasi venue | Venue diambil dari segmen kedua `key` | `booktitle` tidak konsisten, sedangkan `key` stabil antartahun |
| 5 | Duplikat | Buang `key` ganda, lalu judul + tahun + venue ganda | Satu paper tidak boleh terhitung dua kali |
| 6 | Normalisasi author | NFKC dan rapikan spasi, pertahankan sufiks disambiguasi DBLP, lalu pecah menjadi satu baris per author | Menyeragamkan penulisan tanpa menggabungkan orang yang berbeda |
"""))

cells.append(code(r"""
def norm_text(text):
    if text is None or pd.isna(text):
        return None
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None

df = raw.copy()
attrition = [{"tahap": "Data mentah", "paper": len(df), "dibuang": 0}]

def log_step(name, frame):
    attrition.append({"tahap": name, "paper": len(frame), "dibuang": attrition[-1]["paper"] - len(frame)})
"""))

cells.append(md(r"""
## 4.2 Konsistensi Tahun

Kolom `year` dikonversi dari teks menjadi bilangan bulat agar dapat dihitung. Sebelum dan sesudah konversi, nilai dicek berupa empat digit dan berada pada rentang analisis.
"""))

cells.append(code(r"""
four_digit = df["year"].str.fullmatch(r"\d{4}")
print(f"Tipe awal       : {df['year'].dtype} | seluruh nilai empat digit: {four_digit.all()}")
print(f"Nilai unik awal : {sorted(df['year'].unique())}")

df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df = df[df["year"].between(CFG.YEAR_MIN, CFG.YEAR_MAX)]
log_step("Konsistensi tahun", df)

print(f"Tipe akhir      : {df['year'].dtype} | rentang: {df['year'].min()}-{df['year'].max()} | kosong: {df['year'].isna().sum()}")
print(f"Baris dibuang   : {attrition[-1]['dibuang']}")
"""))

cells.append(md(r"""
#### Insights

> 1. Seluruh nilai `year` berupa empat digit dan berada pada 2015-2025, sehingga tidak ada baris yang dibuang. Penyaringan tahun sudah dilakukan saat ekstraksi, jadi tahap ini berfungsi sebagai validasi.
> 2. Bilangan bulat tetap diperlukan untuk agregasi per tahun, garis tren, dan pembagian periode pada analisis temporal.
"""))

cells.append(md(r"""
## 4.3 Missing Values

Nilai kosong diperiksa pada setiap kolom, lalu keputusan diambil per kolom menurut perannya dalam analisis. Kolom `authors` menjadi penentu karena transaksi dibentuk dari author.
"""))

cells.append(code(r"""
missing_plan = pd.DataFrame({
    "kosong": [(df["authors"] == "").sum(), df["booktitle"].isna().sum(), df["crossref"].isna().sum(),
               df["title"].isna().sum(), df["year"].isna().sum()],
    "keputusan": ["buang baris", "dibiarkan", "dibiarkan", "tidak ada yang kosong", "tidak ada yang kosong"],
    "alasan": ["transaksi dibentuk dari author", "venue diambil dari key, bukan booktitle",
               "crossref tidak dipakai pada analisis", "-", "-"],
}, index=["authors", "booktitle", "crossref", "title", "year"])
missing_plan["kosong_%"] = missing_plan["kosong"] / len(df) * 100
save_table(missing_plan, "t1_missing_values.csv")
missing_plan.round(3)
"""))

cells.append(md(r"""
Judul pada record tanpa author diperiksa untuk memastikan record itu bukan paper, lalu satu record contoh ditampilkan dari dump.
"""))

cells.append(code(r"""
no_author = df[df["authors"] == ""]
print("Judul paling sering pada record tanpa author:")
print(no_author["title"].value_counts().head(6).to_string())
print()
print(dump_info["sample_records"]["conf/dac/X22"])
"""))

cells.append(code(r"""
df = df[df["authors"] != ""]
log_step("Missing value (tanpa author)", df)
print(f"Baris dibuang: {attrition[-1]['dibuang']:,} | sisa: {len(df):,}")
"""))

cells.append(md(r"""
#### Insights

> 1. Hanya 2.255 record (0,11%) yang tidak memiliki author. Judulnya menunjukkan halaman depan prosiding, seperti "Front Matter, Table of Contents, Preface, Conference Organization." dan "Preface.", bukan paper.
> 2. Membuang record ini sekaligus membersihkan non-paper dari dataset.
> 3. `booktitle` (190 kosong) dan `crossref` (2.471 kosong) dibiarkan karena tidak dipakai, sebab venue diturunkan dari `key`. `title` dan `year` tidak memiliki nilai kosong.
"""))

cells.append(md(r"""
## 4.4 Seleksi Konferensi dan Workshop

Konferensi dan workshop pada DBLP sama-sama bertag `inproceedings`, dan tag itu sudah dipilih saat ekstraksi. Tahap ini menambah syarat `key` berawalan `conf/`, yang menurut dokumentasi DBLP adalah tempat paper konferensi dan workshop. Record `inproceedings` dengan awalan lain diperiksa dahulu sebelum dibuang.
"""))

cells.append(code(r"""
prefix = df["key"].str.split("/").str[:2].str.join("/")
non_conf = df[~df["key"].str.startswith("conf/")]

non_conf_profile = (
    non_conf.assign(awalan=prefix[non_conf.index])
    .groupby("awalan")
    .agg(paper=("key", "size"), acara_berbeda=("booktitle", "nunique"),
         acara_terbesar=("booktitle", lambda s: s.value_counts().max()))
    .sort_values("paper", ascending=False)
)
save_table(non_conf_profile, "t1_record_non_conf.csv")
print(f"Record bertag inproceedings tetapi key bukan conf/: {len(non_conf):,} ({len(non_conf) / len(df):.2%})")
print("Acara terbanyak:", non_conf["booktitle"].value_counts().head(5).to_dict())
non_conf_profile
"""))

cells.append(md(r"""
Tag dan awalan `key` tidak selalu sejalan. Record contoh berikut bertag `article` tetapi berawalan `conf/`, karena tag mengikuti jenis publikasi (jurnal RLJ) sedangkan `key` mengikuti seri venue. Karena hanya tag `inproceedings` yang diambil, record seperti ini tidak ikut.
"""))

cells.append(code(r"""
for line in dump_info["sample_records"]["conf/rlc/IshfaqT0LLMP024"].splitlines():
    if line.startswith(("<article", "<journal", "<title")):
        print(line[:120])
"""))

cells.append(code(r"""
df = df[df["key"].str.startswith("conf/")].copy()
log_step("Seleksi konferensi (key conf/)", df)
print(f"Baris dibuang: {attrition[-1]['dibuang']:,} | sisa: {len(df):,}")
"""))

cells.append(md(r"""
#### Insights

> 1. Sebanyak 3.161 record (0,16%) bertag `inproceedings` tetapi tidak berawalan `conf/`: 2.734 berawalan `journals/corr`, 387 `journals/entcs`, dan 40 `books/sp`. Semuanya prosiding acara kecil yang diarsipkan DBLP pada seri jurnal atau buku.
> 2. Record ini tersebar pada sekitar 150 acara berbeda (130 pada `journals/corr`, 16 pada `journals/entcs`, dan 2 pada `books/sp`), dan acara terbesarnya hanya 187 paper (MFPS). Angka itu jauh di bawah ambang min support terendah, karena 0,1% dari 1,82 juta author adalah sekitar 1.800 author.
> 3. `key` mereka akan menyatukan 130 acara berbeda menjadi satu venue palsu `corr`, sehingga record ini dibuang.
> 4. Keterbatasan: sebagian record yang dibuang memang prosiding konferensi atau workshop kecil, sehingga ada sedikit workshop yang tidak terambil. Dampaknya pada hasil mining diperkirakan tidak ada.
"""))

cells.append(md(r"""
## 4.5 Normalisasi Venue

Nama venue dinormalisasi dengan mengambil segmen kedua `key` (`conf/kdd/ChenG16` menjadi `kdd`), yang menyatakan seri konferensi yang sama sepanjang waktu. `booktitle` tidak dipakai karena penulisannya berbeda antartahun dan antartrack. Perbandingan keduanya ditunjukkan berikut.
"""))

cells.append(code(r"""
df["venue"] = df["key"].str.split("/").str[1]

bt = df["booktitle"].fillna("(kosong)")
size = df.groupby("venue").size()
variants = bt.groupby(df["venue"]).nunique()
dominant_name = bt.groupby(df["venue"]).agg(lambda s: s.value_counts().index[0])
is_dominant = pd.Series(bt.values == dominant_name.reindex(df["venue"]).values, index=df.index)
off_name = size - is_dominant.groupby(df["venue"]).sum()

venue_norm = pd.Series({
    "nama booktitle berbeda": df["booktitle"].nunique(),
    "venue (segmen kedua key)": df["venue"].nunique(),
    "venue yang memiliki lebih dari satu variasi booktitle": int((variants > 1).sum()),
    "paper dengan booktitle bukan nama dominan venue-nya": int(off_name.sum()),
}, name="jumlah").to_frame()
venue_norm["%"] = [np.nan, np.nan, venue_norm.iloc[2, 0] / df["venue"].nunique() * 100, venue_norm.iloc[3, 0] / len(df) * 100]
save_table(venue_norm, "t1_normalisasi_venue.csv")
venue_norm.round(1)
"""))

cells.append(md(r"""
Perbedaan itu divisualisasikan sebagai stacked column per tahun. Tiga venue dipilih karena masing-masing mewakili satu masalah, yaitu pergantian nama (`nips`), workshop di bawah konferensi induk (`cvpr`), dan track tambahan (`chi`).
"""))

cells.append(code(r"""
panels = [
    ("nips", ["NIPS", "NeurIPS"], "Pergantian nama"),
    ("cvpr", ["CVPR", "CVPR Workshops"], "Workshop di bawah konferensi induk"),
    ("chi", ["CHI", "CHI Extended Abstracts"], "Track tambahan"),
]
colors = [CFG.BLUE, CFG.ORANGE]

fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.9))
for ax, (venue, names, subtitle) in zip(axes, panels):
    sub = df[df["venue"] == venue]
    grouped = sub["booktitle"].fillna("(kosong)").where(lambda s: s.isin(names), "Lainnya")
    table = pd.crosstab(sub["year"].astype(int), grouped).reindex(columns=names + ["Lainnya"], fill_value=0)
    bottom = np.zeros(len(table))
    for column, color in zip(table.columns, colors + [CFG.GRAY]):
        if table[column].sum() == 0:
            continue
        ax.bar(table.index, table[column] / 1e3, bottom=bottom, color=color, width=0.72, label=column, zorder=2)
        bottom += table[column].values / 1e3
    ax.set_title(f"key = {venue}", fontsize=10.5, pad=22)
    ax.text(0, 1.035, subtitle, transform=ax.transAxes, fontsize=8.6, color=CFG.INK_2)
    ax.set_xticks([2015, 2018, 2021, 2024])
    ax.set_ylim(0, bottom.max() * 1.14)
    ax.set_ylabel("Paper (ribu)")
    id_ticks(ax)
    ax.legend(loc="upper left", fontsize=8.2, handlelength=1.1)
axes[0].annotate("2018: NIPS menjadi NeurIPS", xy=(2018, 1.0), xytext=(2015.2, 4.2),
                 fontsize=8.4, color=CFG.INK, arrowprops=dict(arrowstyle="-", color=CFG.INK_2, lw=0.8))
fig.suptitle("Satu key, banyak nama booktitle: alasan venue diambil dari key", x=0.01, ha="left", fontweight="bold", fontsize=11.5, y=1.04)
fig.tight_layout()
save_fig(fig, "t1_normalisasi_venue.png")
"""))

cells.append(md(r"""
Nama tampilan setiap venue untuk grafik dan tabel berikutnya diambil dari `booktitle` yang paling sering dipakai venue itu, setelah menghapus keterangan dalam kurung dan akhiran seperti `Workshops`. Jika beberapa venue mendapat nama sama, venue terbesar memakai nama polos dan lainnya diberi kunci venue dalam kurung siku.
"""))

cells.append(code(r"""
def clean_booktitle(text):
    text = re.sub(r"\s*\(.*?\)\s*$", "", str(text))
    text = re.sub(r"\s+(Workshops?|Extended Abstracts)$", "", text)
    return text.strip()

venue_label = dominant_name.map(clean_booktitle)
largest_for_label = size.groupby(venue_label).idxmax()

def display_name(venue):
    label = venue_label[venue]
    return label if largest_for_label[label] == venue else f"{label} [{venue}]"

venue_label.rename("nama_tampil").rename_axis("venue").to_frame().to_csv(CFG.PROC_DIR / "venue_label.csv")

pd.DataFrame({"venue": ["nips", "hci", "acl", "amcc", "vtc"],
              "nama_tampil": [display_name(v) for v in ["nips", "hci", "acl", "amcc", "vtc"]]})
"""))

cells.append(md(r"""
#### Insights

> 1. `booktitle` memiliki 8.784 nama berbeda, sedangkan `key` hanya menghasilkan 4.373 venue. Memakai `booktitle` akan memecah satu konferensi menjadi beberapa venue.
> 2. Sebanyak 1.270 venue (29%) memiliki lebih dari satu variasi `booktitle`, dan 377.262 paper (18,9%) memakai `booktitle` yang bukan nama utama venue-nya.
> 3. Contoh paling jelas adalah NeurIPS: `booktitle` tercatat `NIPS` pada 2015-2017 dan `NeurIPS` sejak 2018, padahal `key` tetap `nips`. Pada CVPR dan CHI, `booktitle` memisahkan acara utama dari workshop dan extended abstracts.
> 4. Keterbatasan: dengan `key`, workshop dan track tambahan ikut terhitung sebagai konferensi induknya (sekitar 23% paper CVPR dan 44% paper CHI). Hal ini memengaruhi peringkat popularitas pada analisis berikutnya.
"""))

cells.append(md(r"""
## 4.6 Duplikat

Duplikat dicari dalam dua lapis, yaitu `key` ganda (seharusnya tidak ada) dan paper dengan judul, tahun, dan venue sama tetapi `key` berbeda. Judul dinormalisasi lebih dahulu (huruf kecil, spasi dirapikan, titik akhir dibuang) agar perbedaan penulisan kecil tidak menyembunyikan duplikat.
"""))

cells.append(code(r"""
df["title_norm"] = df["title"].map(norm_text).str.lower().str.rstrip(".")
dup_keys = ["title_norm", "year", "venue"]

print(f"Key ganda: {df['key'].duplicated().sum()}")
print(f"Jika daftar author ikut menjadi kunci duplikat, baris yang dibuang: {df.duplicated(dup_keys + ['authors']).sum():,}")

groups = (df[df.duplicated(dup_keys, keep=False)]
          .groupby(dup_keys)
          .agg(baris=("key", "size"), daftar_author=("authors", "nunique")))
groups["dibuang"] = groups["baris"] - 1
same_authors = groups["daftar_author"] == 1

dup_summary = pd.DataFrame({
    "grup": [len(groups), same_authors.sum(), (~same_authors).sum()],
    "baris_dibuang": [groups["dibuang"].sum(), groups.loc[same_authors, "dibuang"].sum(), groups.loc[~same_authors, "dibuang"].sum()],
}, index=["Semua grup judul + tahun + venue ganda", "Daftar author identik", "Daftar author berbeda"])
dup_summary["grup_%"] = dup_summary["grup"] / len(groups) * 100
save_table(dup_summary, "t1_duplikat.csv")
dup_summary.round(1)
"""))

cells.append(md(r"""
Grup dengan daftar author berbeda diperiksa khusus karena berpotensi menghapus paper yang sebenarnya berbeda. Contoh dan judul yang paling sering muncul ditampilkan berikut.
"""))

cells.append(code(r"""
different = groups[~same_authors].reset_index()

for _, row in different.head(5).iterrows():
    members = df[(df["title_norm"] == row["title_norm"]) & (df["year"] == row["year"]) & (df["venue"] == row["venue"])]
    print(f"[{row['venue']} {row['year']}] {row['title_norm'][:62]}")
    for _, member in members.iterrows():
        print("   ", member["key"], "|", member["authors"][:68])

print()
print("Judul yang paling sering pada grup author berbeda:")
print(different["title_norm"].value_counts().head(6).to_string())
"""))

cells.append(code(r"""
df = df.drop_duplicates("key")
df = df[~df.duplicated(dup_keys)]
log_step("Duplikat (key, judul + tahun + venue)", df)
print(f"Baris dibuang: {attrition[-1]['dibuang']:,} | sisa: {len(df):,}")
"""))

cells.append(md(r"""
#### Insights

> 1. Tidak ada `key` ganda, tetapi ada 1.373 grup paper dengan judul, tahun, dan venue sama sehingga 1.542 baris dibuang (0,08% data). Anggota grup memiliki `key` berbeda, biasanya dengan akhiran huruf seperti `...23` dan `...23a`.
> 2. Sebanyak 80% grup memiliki daftar author identik sehingga hampir pasti duplikat. Sekitar 20% grup berbeda daftar author, misalnya urutan author berbeda, ejaan nama berbeda (`Joaquin` dan `Joaquín`), atau subset author.
> 3. Sebagian grup berbeda adalah judul generik seperti "Preface", "Vorwort", dan "Session introduction", yaitu dokumen berbeda yang bukan paper penelitian.
> 4. Aturan dipertahankan karena dampaknya kecil. Jika daftar author ikut menjadi kunci, yang dibuang 1.127 baris, sehingga hanya sekitar 415 baris yang berbeda. Risiko menghapus paper yang berbeda dicatat sebagai keterbatasan.
"""))

cells.append(md(r"""
## 4.7 Normalisasi Author

Nama author dinormalisasi dengan NFKC (menyeragamkan karakter yang setara secara Unicode) dan perapian spasi, lalu setiap paper dipecah menjadi satu baris per author. Sufiks angka seperti `Tianqi Chen 0001` dipertahankan karena itu penanda DBLP bahwa dua orang berbeda bernama sama. Efek normalisasi diukur, bukan diasumsikan.
"""))

cells.append(code(r"""
pairs = (df[["key", "year", "venue", "authors"]]
         .assign(author_raw=df["authors"].str.split("|"))
         .explode("author_raw")
         .drop(columns="authors")
         .reset_index(drop=True))

unique_names = pairs["author_raw"].drop_duplicates()
mapping = dict(zip(unique_names, unique_names.map(norm_text)))
pairs["author"] = pairs["author_raw"].map(mapping)

author_norm = pd.Series({
    "pasangan paper-author sebelum": len(pairs),
    "nama author unik sebelum normalisasi": unique_names.nunique(),
    "nama author unik sesudah normalisasi": pairs["author"].nunique(),
    "nama yang berubah karena NFKC atau spasi": int((pairs["author"] != pairs["author_raw"]).sum()),
}, name="jumlah").to_frame()
author_norm
"""))

cells.append(md(r"""
Karena NFKC dan spasi tidak mengubah satu nama pun, diperiksa pula nama yang berbeda hanya pada huruf besar-kecil atau diakritik (misalnya `A. Gómez` dan `A. Gomez`). Pemeriksaan ini hanya mengukur dan tidak menggabungkan, karena nama serupa belum tentu orang yang sama.
"""))

cells.append(code(r"""
def fold_name(name):
    lowered = unicodedata.normalize("NFKD", name.casefold())
    return "".join(c for c in lowered if not unicodedata.combining(c))

folded = unique_names.map(fold_name)
members = pd.DataFrame({"nama": unique_names.values, "lipat": folded.values})
collision = members.groupby("lipat")["nama"].nunique()
collision = collision[collision > 1]

print(f"Kelompok nama yang bentrok jika huruf besar-kecil dan diakritik dilipat: {len(collision):,} "
      f"({len(collision) / unique_names.nunique():.2%} dari nama unik)")
print("Contoh:")
print(members[members["lipat"].isin(collision.index[:6])].groupby("lipat")["nama"].apply(list).to_string())
"""))

cells.append(code(r"""
paper_author = (pairs.dropna(subset=["author"])
                .drop_duplicates(["key", "author"])[["key", "year", "venue", "author"]]
                .reset_index(drop=True))

has_suffix = paper_author["author"].str.contains(r" \d{4}$")
venues_per_author = paper_author.groupby("author")["venue"].nunique().sort_values(ascending=False)

author_extra = pd.Series({
    "pasangan paper-author ganda dalam satu paper (dibuang)": len(pairs) - len(paper_author),
    "pasangan paper-author akhir": len(paper_author),
    "nama dengan sufiks disambiguasi DBLP": paper_author.loc[has_suffix, "author"].nunique(),
}, name="jumlah").to_frame()
display(author_extra)
print("Author dengan venue terbanyak (calon nama gabungan banyak orang):")
print(venues_per_author.head(5).to_string())
"""))

cells.append(md(r"""
#### Insights

> 1. Normalisasi Unicode dan spasi tidak mengubah satu pun dari 7,87 juta kemunculan nama author (1,82 juta nama unik). DBLP sudah menyajikan nama dalam bentuk bersih, dan tahap ini tetap dijalankan sebagai pengaman dengan hasil nol yang dilaporkan apa adanya.
> 2. Sebanyak 97 pasangan paper-author ganda dalam satu paper dibuang, dan 90.593 nama membawa sufiks disambiguasi DBLP yang dipertahankan. Hasil akhirnya 7.870.902 pasangan paper-author.
> 3. Ada 7.573 kelompok nama (0,4% dari nama unik) yang hanya berbeda huruf besar-kecil atau diakritik. Nama ini tidak digabung karena sebagian besar berupa inisial yang sudah ambigu, dan dampaknya kecil.
> 4. Keterbatasan utama: nama umum tanpa sufiks dapat mewakili banyak orang. `Yang Liu` tercatat pada 332 venue dan `Wei Wang` pada 280 venue, sehingga transaksi untuk nama ini bukan riwayat satu orang.
"""))

cells.append(md(r"""
## 4.8 Hasil Preprocessing dan Penyimpanan

Jumlah paper setelah setiap tahap disusun dalam satu tabel dan divisualisasikan sebagai lollipop chart untuk membandingkan besar pengurangan antartahap.
"""))

cells.append(code(r"""
attrition_df = pd.DataFrame(attrition)
raw_total = attrition_df["paper"].iloc[0]
attrition_df["dibuang_%_dari_mentah"] = attrition_df["dibuang"] / raw_total * 100
attrition_df["retensi_%"] = attrition_df["paper"] / raw_total * 100
save_table(attrition_df, "t1_ringkasan_preprocessing.csv", index=False)
attrition_df.round(3)
"""))

cells.append(code(r"""
steps = attrition_df.iloc[1:].reset_index(drop=True)
final_paper = attrition_df["paper"].iloc[-1]

fig, ax = plt.subplots(figsize=(9.2, 3.2))
y = np.arange(len(steps))[::-1]
ax.hlines(y, 0, steps["dibuang"], color=CFG.BLUE_LIGHT, lw=3.2, zorder=1)
ax.scatter(steps["dibuang"], y, s=110, color=CFG.BLUE, zorder=3)
for yi, (_, row) in zip(y, steps.iterrows()):
    ax.text(row["dibuang"] + 70, yi, f"{fmt_id(row['dibuang'])}  ({pct_id(row['dibuang_%_dari_mentah'], 2)} dari data mentah)",
            va="center", fontsize=9)
ax.set_yticks(y)
ax.set_yticklabels(steps["tahap"])
ax.set_xlim(0, steps["dibuang"].max() * 1.75)
ax.set_xlabel("Paper dibuang pada tahap tersebut")
id_ticks(ax, "x")
ax.grid(axis="y", visible=False)
ax.set_title("Dampak setiap tahap preprocessing")
ax.text(0.99, 0.04, f"Tersisa {fmt_id(final_paper)} dari {fmt_id(raw_total)} paper\nRetensi {pct_id(final_paper / raw_total * 100, 2)}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9.5, fontweight="bold", color=CFG.BLUE)
save_fig(fig, "t1_dampak_preprocessing.png")
"""))

cells.append(md(r"""
Alur seleksi dari seluruh dump sampai dataset bersih digambarkan sebagai sankey diagram. Ketebalan pita sebanding dengan jumlah record, dan aliran yang sangat kecil digambar dengan ketebalan minimum agar tetap terlihat.
"""))

cells.append(code(r"""
n_total = int(record_types["seluruh_dblp"].sum())
n_article = int(record_types.loc["article", "seluruh_dblp"])
n_www = int(record_types.loc["www", "seluruh_dblp"])
n_inproc = int(record_types.loc["inproceedings", "seluruh_dblp"])
n_period = int(record_types.loc["inproceedings", "periode"])
n_other = n_total - n_article - n_www - n_inproc
n_clean = int(final_paper)
n_removed = n_period - n_clean

values = {"article": n_article, "www": n_www, "inproc": n_inproc, "other": n_other,
          "period": n_period, "outside": n_inproc - n_period, "clean": n_clean, "removed": n_removed}
scale = 56 / n_total
min_node, min_flow, gap, node_w = 1.0, 0.45, 3.0, 1.8

height = {k: max(v * scale, min_node) for k, v in values.items()}
height["dblp"] = height["article"] + height["www"] + height["inproc"] + height["other"]

top = 12
pos = {"article": (26, top)}
pos["www"] = (26, pos["article"][1] + height["article"] + gap)
pos["inproc"] = (26, pos["www"][1] + height["www"] + gap)
pos["other"] = (26, pos["inproc"][1] + height["inproc"] + gap)
pos["dblp"] = (1, top + (pos["other"][1] + height["other"] - top - height["dblp"]) / 2)
pos["period"] = (52, pos["inproc"][1])
pos["outside"] = (52, pos["period"][1] + height["period"] + gap)
pos["clean"] = (76, pos["period"][1])
pos["removed"] = (76, pos["clean"][1] + height["clean"] + gap)

used, muted, flagged = CFG.BLUE, CFG.GRAY, CFG.ORANGE
node_color = {"dblp": used, "article": muted, "www": muted, "inproc": used, "other": muted,
              "period": used, "outside": muted, "clean": used, "removed": flagged}
links = [("dblp", "article", used), ("dblp", "www", used), ("dblp", "inproc", used), ("dblp", "other", used),
         ("inproc", "period", used), ("inproc", "outside", used), ("period", "clean", used), ("period", "removed", used)]
link_value = {("dblp", "article"): n_article, ("dblp", "www"): n_www, ("dblp", "inproc"): n_inproc,
              ("dblp", "other"): n_other, ("inproc", "period"): n_period, ("inproc", "outside"): n_inproc - n_period,
              ("period", "clean"): n_clean, ("period", "removed"): n_removed}

labels = {
    "dblp": f"DBLP\n{fmt_id(n_total)} record",
    "article": f"article\n{fmt_id(n_article)}",
    "www": f"www (profil author)\n{fmt_id(n_www)}",
    "inproc": f"inproceedings\n{fmt_id(n_inproc)} ({pct_id(n_inproc / n_total * 100)})",
    "other": f"jenis lain\n{fmt_id(n_other)}",
    "period": f"2015-2025\n{fmt_id(n_period)}",
    "outside": f"di luar periode\n{fmt_id(n_inproc - n_period)}",
    "clean": f"dataset bersih\n{fmt_id(n_clean)} ({pct_id(n_clean / n_period * 100, 2)})",
    "removed": f"dibuang preprocessing\n{fmt_id(n_removed)} ({pct_id(n_removed / n_period * 100, 2)})",
}

fig, ax = plt.subplots(figsize=(11.2, 5.4))
out_offset = {k: 0.0 for k in pos}
in_offset = {k: 0.0 for k in pos}
for src_id, dst_id, color in links:
    thickness = max(link_value[(src_id, dst_id)] * scale, min_flow)
    x0, y0 = pos[src_id][0] + node_w, pos[src_id][1] + out_offset[src_id]
    x1, y1 = pos[dst_id][0], pos[dst_id][1] + in_offset[dst_id]
    out_offset[src_id] += thickness
    in_offset[dst_id] += thickness
    xm = (x0 + x1) / 2
    verts = [(x0, y0), (xm, y0), (xm, y1), (x1, y1), (x1, y1 + thickness), (xm, y1 + thickness),
             (xm, y0 + thickness), (x0, y0 + thickness), (x0, y0)]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.LINETO,
             MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4, MplPath.CLOSEPOLY]
    ribbon_color = flagged if dst_id == "removed" else (CFG.BLUE_LIGHT if dst_id in ("inproc", "period", "clean") or src_id == "dblp" and dst_id == "inproc" else CFG.GRAY)
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=ribbon_color, edgecolor="none",
                           alpha=0.9 if dst_id == "removed" else 0.55, zorder=1))

for node_id, (x, y_top) in pos.items():
    ax.add_patch(Rectangle((x, y_top), node_w, height[node_id], facecolor=node_color[node_id], edgecolor="none", zorder=3))
    ax.text(x + node_w + 1.0, y_top + height[node_id] / 2, labels[node_id], va="center", ha="left", fontsize=8.8, zorder=4,
            fontweight="bold" if node_id in ("inproc", "clean") else "normal",
            bbox=dict(boxstyle="round,pad=0.25", fc=CFG.SURFACE, ec="none", alpha=0.88))

for x, text in [(1, "Seluruh dump"), (26, "Jenis publikasi"), (52, "Periode analisis"), (76, "Hasil preprocessing")]:
    ax.text(x, 6.5, text, fontsize=9.2, color=CFG.MUTED, fontweight="bold")

ax.set_xlim(0, 100)
ax.set_ylim(82, 3)
ax.axis("off")
ax.set_title("Alur seleksi data: dari seluruh dump DBLP sampai dataset bersih", pad=10)
save_fig(fig, "t1_alur_seleksi.png")
"""))

cells.append(md(r"""
Hasil preprocessing disimpan dalam dua tabel. `inproceedings_clean` dipakai untuk perhitungan per paper, dan `paper_author` dipakai untuk perhitungan per author serta pembentukan transaksi. Tabel besar di memori dilepas setelah disimpan, dan bagian berikutnya membaca ulang hanya kolom yang dibutuhkan.
"""))

cells.append(code(r"""
df.drop(columns=["title_norm"]).to_parquet(CFG.CLEAN_PARQUET, index=False)
paper_author.to_parquet(CFG.PAPER_AUTHOR_PARQUET, index=False)

print(f"inproceedings_clean.parquet : {len(df):,} paper    ({CFG.CLEAN_PARQUET.stat().st_size / 1e6:,.0f} MB)")
print(f"paper_author.parquet        : {len(paper_author):,} pasangan ({CFG.PAPER_AUTHOR_PARQUET.stat().st_size / 1e6:,.0f} MB)")

del raw, df, pairs, paper_author
"""))

cells.append(md(r"""
#### Insights

> 1. Preprocessing membuang 6.958 dari 2.004.202 paper, sehingga retensi 99,65%. Rinciannya: 3.161 bukan berawalan `conf/` (45%), 2.255 tanpa author (32%), dan 1.542 duplikat (22%). Tahap konsistensi tahun tidak membuang apa pun.
> 2. Penyempitan terbesar terjadi sebelum preprocessing, yaitu saat memilih `inproceedings` (30,5% dari seluruh dump) dan periode 2015-2025 (separuhnya). Hasil analisis karenanya hampir sepenuhnya ditentukan aturan seleksi pada ekstraksi.
> 3. Hasil akhirnya 1.997.244 paper dan 7.870.902 pasangan paper-author. Keduanya disimpan dan menjadi masukan bagian berikutnya.
"""))

# ---------------------------------------------------------------------------
# 5. Statistik Dataset Bersih
# ---------------------------------------------------------------------------
cells.append(section("Statistik Dataset Bersih", "5"))

cells.append(md(r"""
Seluruh angka dihitung dari parquet hasil preprocessing, dan hanya kolom yang dibutuhkan dimuat ke memori. Bagian ini dapat dijalankan ulang tanpa mengulang preprocessing.
"""))

cells.append(md(r"""
## 5.1 Ringkasan Statistik

Total publikasi, author unik, dan venue unik dihitung bersama ukuran pendukung yang menjelaskan bentuk data, yaitu jumlah author per paper dan jumlah paper per author.
"""))

cells.append(code(r"""
clean = pd.read_parquet(CFG.CLEAN_PARQUET, columns=["key", "year", "venue"])
pa = pd.read_parquet(CFG.PAPER_AUTHOR_PARQUET, columns=["key", "year", "venue", "author"])

venue_label = pd.read_csv(CFG.PROC_DIR / "venue_label.csv", index_col="venue")["nama_tampil"]
largest_for_label = clean.groupby("venue").size().groupby(venue_label).idxmax()

def display_name(venue):
    label = venue_label[venue]
    return label if largest_for_label[label] == venue else f"{label} [{venue}]"

authors_per_paper = pa.groupby("key").size()
papers_per_author = pa.groupby("author").size()

summary = pd.Series({
    "Total publikasi": len(clean),
    "Total author unik": pa["author"].nunique(),
    "Total conference/venue unik": clean["venue"].nunique(),
    "Pasangan paper-author": len(pa),
    "Author per paper (median)": authors_per_paper.median(),
    "Author per paper (rata-rata)": authors_per_paper.mean(),
    "Paper per author (median)": papers_per_author.median(),
    "Paper per author (rata-rata)": papers_per_author.mean(),
    "Author dengan satu paper (%)": (papers_per_author == 1).mean() * 100,
}, name="nilai").to_frame()
save_table(summary, "t1_ringkasan_statistik.csv")
summary.round(2)
"""))

cells.append(md(r"""
#### Insights

> 1. Dataset bersih memuat 1.997.244 publikasi dari 1.821.757 author unik dan 4.373 venue unik, dengan 7.870.902 pasangan paper-author.
> 2. Paper umumnya ditulis berkelompok (median 4 author per paper, rata-rata 3,94), sedangkan author umumnya muncul sekali: median paper per author 1 dan 51,4% author hanya memiliki satu paper.
> 3. Rata-rata paper per author (4,32) jauh di atas median karena sebagian kecil author sangat produktif.
> 4. Pasangan paper-author (7,87 juta) hampir empat kali jumlah paper. Karena itu publikasi dihitung dari tabel paper dan author dari tabel pasangan, agar paper tidak terhitung berkali-kali.
"""))

cells.append(md(r"""
## 5.2 Distribusi Publikasi per Tahun

Jumlah publikasi per tahun ditampilkan sebagai column chart dengan garis tren linear yang dihitung hanya dari tahun lengkap (2015-2024). Tahun 2025 diarsir karena indeks DBLP untuk tahun itu belum lengkap.
"""))

cells.append(code(r"""
per_year = clean.groupby("year").size().rename("publikasi")
per_year.index = per_year.index.astype(int)
complete = per_year.loc[CFG.YEAR_MIN:CFG.YEAR_INCOMPLETE - 1]

slope, intercept = np.polyfit(complete.index.values.astype(float), complete.values.astype(float), 1)
cagr = (complete.iloc[-1] / complete.iloc[0]) ** (1 / (len(complete) - 1)) - 1

year_table = pd.DataFrame({
    "publikasi": per_year,
    "perubahan_yoy_%": per_year.pct_change() * 100,
    "tren_linear": slope * per_year.index + intercept,
})
year_table["selisih_dari_tren_%"] = (year_table["publikasi"] / year_table["tren_linear"] - 1) * 100
save_table(year_table, "t1_publikasi_per_tahun.csv")

print(f"CAGR 2015-2024: {cagr:.2%} | tambahan rata-rata: {slope:,.0f} paper per tahun | "
      f"kenaikan 2015 ke 2024: {complete.iloc[-1] / complete.iloc[0] - 1:.1%}")
year_table.round(1)
"""))

cells.append(md(r"""
Penurunan 2025 diperiksa pada tingkat konferensi dengan menghitung konferensi yang aktif pada 2024 tetapi tidak memiliki paper pada 2025. Sebabnya bisa berbeda, yaitu prosiding konferensi tahunan yang belum terindeks atau konferensi dua tahunan yang memang tidak diadakan. Pola tahun demi tahun konferensi terbesar di kelompok ini diperlihatkan untuk membedakan keduanya.
"""))

cells.append(code(r"""
by_venue_year = clean.groupby(["venue", "year"]).size().unstack(fill_value=0)
by_venue_year.columns = by_venue_year.columns.astype(int)
last_full, partial = CFG.YEAR_INCOMPLETE - 1, CFG.YEAR_INCOMPLETE

silent_2025 = by_venue_year[(by_venue_year[last_full] > 0) & (by_venue_year[partial] == 0)]
new_2025 = by_venue_year[(by_venue_year[last_full] == 0) & (by_venue_year[partial] > 0)]
lost = int(silent_2025[last_full].sum())
adjusted_change = per_year.loc[partial] / (per_year.loc[last_full] - lost) - 1

print(f"Venue aktif {last_full} tetapi kosong {partial}: {len(silent_2025):,} venue, {lost:,} paper pada {last_full} ({lost / per_year.loc[last_full]:.1%} dari total {last_full})")
print(f"Venue kosong {last_full} tetapi aktif {partial}: {len(new_2025):,} venue, {int(new_2025[partial].sum()):,} paper pada {partial}")
print(f"Perubahan {partial} terhadap {last_full}: {per_year.loc[partial] / per_year.loc[last_full] - 1:+.1%} (semua venue) | "
      f"{adjusted_change:+.1%} (hanya venue yang punya data {partial})")

biggest_silent = silent_2025[last_full].sort_values(ascending=False).head(8).index
silent_table = by_venue_year.loc[biggest_silent, 2019:2025]
silent_table.insert(0, "nama", [display_name(v) for v in biggest_silent])
save_table(silent_table, "t1_venue_kosong_2025.csv")
silent_table
"""))

cells.append(code(r"""
years = per_year.index.values
values = per_year.values

fig, ax = plt.subplots(figsize=(7.2, 4.4))
bar_colors = [CFG.BLUE if y < CFG.YEAR_INCOMPLETE else CFG.BLUE_LIGHT for y in years]
bars = ax.bar(years, values / 1e3, color=bar_colors, width=0.7, zorder=2)
bars[-1].set_hatch("///")
bars[-1].set_edgecolor(CFG.BLUE)
bars[-1].set_linewidth(0.8)
ax.plot(years, (slope * years + intercept) / 1e3, color=CFG.INK, ls="--", lw=1.5, zorder=3)
ax.set_ylim(0, values.max() / 1e3 * 1.12)
ax.set_xticks(years)
ax.set_ylabel("Publikasi (ribu)")
ax.set_title("Publikasi inproceedings per tahun")
ax.legend(handles=[Patch(color=CFG.BLUE, label="Tahun lengkap"),
                   Patch(facecolor=CFG.BLUE_LIGHT, hatch="///", edgecolor=CFG.BLUE, label="2025 (belum lengkap)"),
                   Line2D([], [], color=CFG.INK, ls="--", label="Tren linear 2015-2024")],
          loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.26), fontsize=8.8)
save_fig(fig, "t1_publikasi_per_tahun.png")
"""))

cells.append(md(r"""
#### Insights

> 1. Publikasi naik dari 160.800 pada 2015 menjadi 213.328 pada 2024 (+32,7%). Itu setara CAGR 3,2% per tahun atau sekitar 4.800 paper tambahan setiap tahun.
> 2. Pertumbuhan tidak mulus. 2020 turun 8,8% dan jumlahnya tetap di bawah garis tren sampai 2022 (-5,7%, -4,7%, dan -7,1%), lalu melonjak 13,1% pada 2023 hingga kembali di atas tren. Penurunan 2020 mungkin terkait pandemi, tetapi data tidak memuat penyebabnya sehingga hubungan itu hanya dugaan.
> 3. Penurunan 2025 (-6,5%) bukan turunnya aktivitas. Ada 789 konferensi aktif pada 2024 tetapi kosong pada 2025, dan konferensi itu menyumbang 49.328 paper (23,1% dari total 2024). Konferensi dua tahunan genap seperti ECCV dan ICPR hanya memiliki data pada 2020, 2022, dan 2024, sedangkan IGARSS, EMBC, dan ICCCNT memiliki data setiap tahun sampai 2024 lalu kosong pada 2025, tanda prosidingnya belum terindeks.
> 4. Tanpa konferensi yang kosong, paper 2025 21,7% di atas 2024. Angka ini bukan ukuran pertumbuhan yang adil karena 322 konferensi yang hanya aktif pada 2025 (umumnya dua tahunan ganjil, 17.785 paper) ikut terhitung. Karena itu 2025 diarsir dan tidak dipakai untuk menghitung tren.
"""))

cells.append(md(r"""
## 5.3 Distribusi Publikasi per Konferensi

Distribusi per konferensi dibaca dari tiga sisi: bar chart 10 konferensi terbesar, kurva kumulatif untuk konsentrasi publikasi, dan histogram berskala logaritmik untuk bentuk distribusi ukuran konferensi. Nama lengkap konferensi dicantumkan pada tabel dari judul prosiding terbaru di dump.
"""))

cells.append(code(r"""
pub_venue = clean.groupby("venue").size().sort_values(ascending=False)
share = pub_venue / pub_venue.sum() * 100
cum = share.cumsum()
proceedings_title = venue_proceedings.set_index("venue")["proceedings_title"]

top20 = pd.DataFrame({
    "venue": pub_venue.head(20).index,
    "nama": [display_name(v) for v in pub_venue.head(20).index],
    "publikasi": pub_venue.head(20).values,
    "porsi_%": share.head(20).values,
    "kumulatif_%": cum.head(20).values,
    "judul_prosiding_terbaru": [str(proceedings_title.get(v, ""))[:72] for v in pub_venue.head(20).index],
})
save_table(top20, "t1_top20_venue.csv", index=False)
save_table(pub_venue.rename("publikasi").to_frame(), "t1_publikasi_per_venue.csv")

rank_50 = int((cum < 50).sum() + 1)
rank_80 = int((cum < 80).sum() + 1)
n_small = int((pub_venue < 50).sum())
print(f"Venue untuk 50% publikasi: {rank_50:,} ({rank_50 / len(pub_venue):.1%}) | untuk 80%: {rank_80:,} ({rank_80 / len(pub_venue):.1%})")
print(f"Median {pub_venue.median():,.0f} paper | rata-rata {pub_venue.mean():,.0f} | maksimum {pub_venue.max():,} | venue < 50 paper: {n_small:,} ({n_small / len(pub_venue):.1%})")
top20
"""))

cells.append(code(r"""
fig, (ax_bar, ax_cum) = plt.subplots(1, 2, figsize=(10.4, 4.4), gridspec_kw={"width_ratios": [1.1, 1]})

t = top20.head(10).iloc[::-1].reset_index(drop=True)
ax_bar.barh(np.arange(len(t)), t["publikasi"] / 1e3, color=CFG.BLUE, height=0.66, zorder=2)
ax_bar.set_yticks(np.arange(len(t)))
ax_bar.set_yticklabels(t["nama"], fontsize=9.4)
ax_bar.set_xlabel("Publikasi (ribu)")
ax_bar.grid(axis="y", visible=False)
ax_bar.set_title("10 konferensi terbesar")

ranks = np.arange(1, len(cum) + 1)
ax_cum.fill_between(ranks, cum.values, color=CFG.BLUE_LIGHT, alpha=0.5, zorder=1)
ax_cum.plot(ranks, cum.values, color=CFG.BLUE, lw=2.2, zorder=3)
marks = (10, rank_50, rank_80)
for rank, color in zip(marks, (CFG.INK, CFG.ORANGE, CFG.ORANGE)):
    ax_cum.scatter(rank, cum.iloc[rank - 1], s=46, color=color, zorder=4,
                   label=f"{fmt_id(rank)} venue = {pct_id(cum.iloc[rank - 1], 0)} publikasi")
ax_cum.set_xscale("log")
ax_cum.set_xticks([1, 10, 100, 1000])
ax_cum.set_xticklabels(["1", "10", "100", "1.000"])
ax_cum.set_ylim(0, 102)
ax_cum.set_xlabel("Jumlah venue terbesar (skala logaritmik)")
ax_cum.set_ylabel("Porsi kumulatif publikasi (%)")
ax_cum.set_title("Porsi kumulatif publikasi")
ax_cum.legend(loc="lower right", fontsize=8.6)
fig.tight_layout()
save_fig(fig, "t1_publikasi_per_konferensi.png")
"""))

cells.append(code(r"""
bins = np.logspace(0, np.log10(pub_venue.max() * 1.05), 28)
counts, edges = np.histogram(pub_venue.values, bins=bins)

fig, ax = plt.subplots(figsize=(6.8, 4.6))
ax.axvspan(1, 50, color=CFG.GRAY, alpha=0.18, zorder=0, label="kurang dari 50 paper")
ax.bar(edges[:-1], counts, width=np.diff(edges), align="edge", color=CFG.BLUE, edgecolor=CFG.SURFACE, linewidth=0.6, zorder=2)
ax.axvline(pub_venue.median(), color=CFG.ORANGE, lw=1.6, ls="--", zorder=3, label=f"median ({fmt_id(pub_venue.median())} paper)")
ax.axvline(pub_venue.mean(), color=CFG.INK, lw=1.6, ls="--", zorder=3, label=f"rata-rata ({fmt_id(pub_venue.mean())} paper)")
ax.set_xscale("log")
ax.set_xlim(1, bins[-1])
ax.set_xticks([1, 10, 100, 1000, 10000])
ax.set_xticklabels(["1", "10", "100", "1.000", "10.000"])
ax.set_xlabel("Jumlah publikasi per venue, 2015-2025 (skala logaritmik)")
ax.set_ylabel("Jumlah venue")
ax.set_title("Distribusi ukuran konferensi")
ax.legend(loc="upper right", fontsize=8.8)
save_fig(fig, "t1_distribusi_ukuran_venue.png")
"""))

cells.append(md(r"""
#### Insights

> 1. Publikasi sangat terkonsentrasi. Sepuluh konferensi teratas menghasilkan 9,4% seluruh paper dan 20 teratas 15,6%. Sebanyak 231 dari 4.373 venue (5,3%) menghasilkan separuh publikasi, dan 1.011 venue (23,1%) menghasilkan 80%.
> 2. Ekor panjangnya tebal. Median venue hanya 134 paper, jauh di bawah rata-rata 457 yang ditarik venue raksasa (maksimum 25.455 paper), dan 1.358 venue (31%) memiliki kurang dari 50 paper dalam sebelas tahun.
> 3. NeurIPS (25.455), CVPR (22.751), ICASSP (21.606), HCI (HCI International, 19.912), IGARSS (19.685), dan AAAI (19.274) membentuk kelompok atas di atas 19.000 paper.
> 4. Peringkat 7 sampai 10 berada rapat pada 14.300 sampai 14.800 paper, sehingga selisih antarperingkat di sana sangat kecil.
"""))

cells.append(md(r"""
## 5.4 Distribusi Author

Produktivitas author menentukan seberapa padat transaksi yang dibentuk pada analisis berikutnya. Dua stacked bar 100% disandingkan dengan warna sama, yaitu porsi jumlah author dan porsi pasangan paper-author yang mereka tulis, dibagi menjadi tiga kelompok produktivitas.
"""))

cells.append(code(r"""
tiers = pd.cut(papers_per_author, bins=[0, 1, 3, 10, 50, np.inf],
               labels=["1 paper", "2-3 paper", "4-10 paper", "11-50 paper", ">50 paper"])
tier_table = pd.DataFrame({
    "author": tiers.value_counts().sort_index(),
    "pasangan_paper_author": papers_per_author.groupby(tiers, observed=False).sum(),
})
tier_table["author_%"] = tier_table["author"] / tier_table["author"].sum() * 100
tier_table["pasangan_%"] = tier_table["pasangan_paper_author"] / tier_table["pasangan_paper_author"].sum() * 100
save_table(tier_table, "t1_produktivitas_author.csv")
print(f"Author paling produktif: {papers_per_author.idxmax()} ({papers_per_author.max()} paper)")
tier_table.round(1)
"""))

cells.append(code(r"""
groups = {"1 paper": [0], "2-10 paper": [1, 2], "11+ paper": [3, 4]}
tier_colors = [CFG.BLUE_LIGHT, "#5a9be6", "#104281"]

fig, ax = plt.subplots(figsize=(6.4, 4.2))
for row, (title, col) in enumerate((("Pasangan paper-author", "pasangan_%"), ("Author", "author_%"))):
    left = 0.0
    for color, (label, idx) in zip(tier_colors, groups.items()):
        width = tier_table[col].iloc[idx].sum()
        ax.barh(row, width, left=left, color=color, edgecolor=CFG.SURFACE, linewidth=1.8, height=0.62)
        ax.text(left + width / 2, row, pct_id(width, 1), ha="center", va="center", fontsize=9.6, fontweight="bold",
                color="#ffffff" if color != CFG.BLUE_LIGHT else CFG.INK)
        left += width
ax.set_yticks([0, 1])
ax.set_yticklabels(["Pasangan\npaper-author", "Author"])
ax.set_xlim(0, 100)
ax.set_xlabel("Porsi (%)")
ax.grid(axis="y", visible=False)
ax.set_title("Porsi author dan pasangan paper-author")
ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(tier_colors, groups)], loc="upper center",
          bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=8.8, title="Jumlah paper per author", title_fontsize=8.8)
save_fig(fig, "t1_produktivitas_author.png")
"""))

cells.append(md(r"""
#### Insights

> 1. Produktivitas author sangat timpang. Sebanyak 51,4% author hanya menulis satu paper dan menyumbang 11,9% pasangan paper-author.
> 2. Sebanyak 8,3% author yang menulis 11 paper atau lebih (150.894 orang) menyumbang 52,6% pasangan.
> 3. Pola konferensi yang muncul bersama kelak diperkirakan lebih banyak dibentuk oleh kelompok kecil author yang menerbitkan di banyak konferensi, bukan oleh mayoritas yang hanya sekali menerbitkan.
> 4. Author paling produktif adalah `Yang Liu` (725 paper), nama umum yang kemungkinan menggabungkan banyak orang berbeda (lihat bagian 4.7).
"""))

# ---------------------------------------------------------------------------
# 6. Analisis Popularitas Konferensi
# ---------------------------------------------------------------------------
cells.append(part("PART II | Conference Popularity Analysis",
                  "Mengidentifikasi konferensi dengan aktivitas publikasi tertinggi dan menganalisis tren serta perbandingan peringkatnya.", "part2"))

cells.append(section("Analisis Popularitas Konferensi", "6"))

cells.append(md(r"""
Popularitas konferensi diukur dari aktivitas publikasi dengan dua ukuran yang saling melengkapi. Jumlah publikasi menunjukkan banyaknya karya yang diterbitkan, sedangkan jumlah author unik menunjukkan luasnya komunitas yang terlibat. Seluruh perhitungan memakai data hasil preprocessing, dengan venue yang diidentifikasi dari `key` DBLP.
"""))

cells.append(md(r"""
## 6.1 Sepuluh Konferensi dengan Publikasi Terbanyak

Peringkat disusun dari jumlah paper per konferensi dan ditampilkan sebagai bar chart horizontal dengan nilai di ujung batang. Warna gelap menandai konferensi yang juga masuk 10 besar menurut jumlah author unik. Perbandingan kedua peringkat dibahas pada subbagian 6.4.
"""))

cells.append(code(r"""
auth_venue = pa.groupby("venue")["author"].nunique()
pairs_venue = pa.groupby("venue").size()

venue_stats = pd.DataFrame({"publikasi": pub_venue, "author_unik": auth_venue, "pasangan_paper_author": pairs_venue})
venue_stats["rank_publikasi"] = venue_stats["publikasi"].rank(ascending=False, method="min").astype(int)
venue_stats["rank_author"] = venue_stats["author_unik"].rank(ascending=False, method="min").astype(int)
venue_stats["porsi_publikasi_%"] = venue_stats["publikasi"] / venue_stats["publikasi"].sum() * 100
venue_stats["paper_per_author"] = venue_stats["pasangan_paper_author"] / venue_stats["author_unik"]
venue_stats["author_unik_per_paper"] = venue_stats["author_unik"] / venue_stats["publikasi"]
venue_stats["nama"] = [display_name(v) for v in venue_stats.index]
save_table(venue_stats.sort_values("rank_publikasi"), "t2_statistik_venue.csv")

top_pub = venue_stats.sort_values("rank_publikasi").head(10)
top_auth = venue_stats.sort_values("rank_author").head(10)
shared = set(top_pub.index) & set(top_auth.index)

print(f"Batas 10 besar jelas (tanpa seri): publikasi {top_pub['publikasi'].min() > venue_stats['publikasi'].drop(top_pub.index).max()}, "
      f"author {top_auth['author_unik'].min() > venue_stats['author_unik'].drop(top_auth.index).max()}")
top_pub[["nama", "publikasi", "porsi_publikasi_%", "rank_author", "author_unik"]].round(2)
"""))

cells.append(code(r"""
def rank_bar(ax, table, value_col, xlabel, title):
    t = table.iloc[::-1]
    colors = [CFG.BLUE if venue in shared else CFG.BLUE_LIGHT for venue in t.index]
    ax.barh(np.arange(len(t)), t[value_col] / 1e3, color=colors, height=0.68, zorder=2)
    offset = t[value_col].max() / 1e3 * 0.012
    for y, (venue, row) in enumerate(t.iterrows()):
        ax.text(row[value_col] / 1e3 + offset, y, fmt_id(row[value_col]), va="center", fontsize=9, color=CFG.INK_2)
    ax.set_yticks(np.arange(len(t)))
    ax.set_yticklabels(t["nama"], fontsize=9.6)
    ax.set_xlim(0, t[value_col].max() / 1e3 * 1.18)
    ax.set_xlabel(xlabel)
    ax.grid(axis="y", visible=False)
    ax.set_title(title)
    ax.legend(handles=[Patch(color=CFG.BLUE, label="Juga masuk 10 besar ukuran lain"),
                       Patch(color=CFG.BLUE_LIGHT, label="Hanya masuk 10 besar ukuran ini")],
              loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=8.4)

fig, ax = plt.subplots(figsize=(6.4, 4.9))
rank_bar(ax, top_pub, "publikasi", "Publikasi (ribu)", "10 konferensi dengan publikasi terbanyak")
save_fig(fig, "t2_top10_publikasi.png")
"""))

cells.append(md(r"""
#### Insights

> 1. NeurIPS menerbitkan paling banyak paper (25.455, atau 1,27% dari seluruh dataset), disusul CVPR (22.751), ICASSP (21.606), HCI (19.912), IGARSS (19.685), dan AAAI (19.274).
> 2. Sepuluh konferensi teratas menghasilkan 9,4% seluruh publikasi. Daftarnya lintas bidang, dan kecerdasan buatan hanya menempati empat dari sepuluh tempat (NeurIPS, CVPR, AAAI, EMNLP).
> 3. Batas 10 besar sangat tipis. ICC di peringkat 10 (14.329 paper) hanya unggul 86 paper dari GLOBECOM di peringkat 11 (14.243).
> 4. Daftar ini bergantung pada keputusan menggabungkan workshop ke konferensi induknya, yang diuji pada subbagian 6.5.
"""))

cells.append(md(r"""
## 6.2 Sepuluh Konferensi dengan Author Unik Terbanyak

Ukuran kedua menghitung berapa orang berbeda yang pernah menerbitkan paper di sebuah konferensi. Satu author dihitung sekali per konferensi, sehingga ukuran ini mencerminkan luas komunitas, bukan volume karya. Bentuk chart dan kode warna sama dengan subbagian sebelumnya.
"""))

cells.append(code(r"""
top_auth[["nama", "author_unik", "rank_publikasi", "publikasi", "paper_per_author"]].round(2)
"""))

cells.append(code(r"""
fig, ax = plt.subplots(figsize=(6.4, 4.9))
rank_bar(ax, top_auth, "author_unik", "Author unik (ribu)", "10 konferensi dengan author unik terbanyak")
save_fig(fig, "t2_top10_author.png")
"""))

cells.append(md(r"""
#### Insights

> 1. NeurIPS juga terbanyak pada author unik (57.800), diikuti CVPR (47.664), AAAI (46.437), ICASSP (42.057), dan EMBC (39.318).
> 2. Pada semua konferensi di daftar ini, author unik lebih banyak daripada paper karena satu paper ditulis beberapa orang.
> 3. IGARSS (2,64) dan CVPR (2,50) memiliki paper per author tertinggi, artinya rata-rata author menerbitkan 2 sampai 3 paper di sana.
> 4. AAAI, HCI, IROS, dan EMBC terendah (sekitar 1,83), artinya komunitasnya lebih luas dan lebih banyak author yang hanya muncul satu kali.
"""))

cells.append(md(r"""
## 6.3 Tren Publikasi per Tahun

Tren dianalisis untuk 10 konferensi dengan publikasi terbanyak, satu panel per konferensi dengan sumbu vertikal yang sama sehingga ukuran dan kemiringannya dapat dibandingkan langsung. Setiap panel memuat garis jumlah paper, garis tren linear 2015-2024, dan titik berongga untuk 2025 yang indeksnya belum lengkap.
"""))

cells.append(code(r"""
trend = clean.groupby(["venue", "year"]).size().unstack(fill_value=0)
trend.columns = trend.columns.astype(int)
top_venues = list(top_pub.index)
trend_top = trend.loc[top_venues]

def growth_stats(row):
    series = row.loc[CFG.YEAR_MIN:CFG.YEAR_INCOMPLETE - 1]
    slope_v, _ = np.polyfit(series.index.values.astype(float), series.values.astype(float), 1)
    ratio = series.iloc[-1] / series.iloc[0]
    return pd.Series({
        "publikasi_2015": series.iloc[0],
        "publikasi_2024": series.iloc[-1],
        "kali_lipat": ratio,
        "cagr_%": (ratio ** (1 / (len(series) - 1)) - 1) * 100,
        "tambahan_per_tahun": slope_v,
        "publikasi_2025": row.loc[CFG.YEAR_INCOMPLETE],
        "perubahan_2025_vs_2024_%": (row.loc[CFG.YEAR_INCOMPLETE] / row.loc[CFG.YEAR_INCOMPLETE - 1] - 1) * 100,
    })

growth = trend_top.apply(growth_stats, axis=1)
growth.insert(0, "nama", [display_name(v) for v in growth.index])
save_table(growth, "t2_tren_top10.csv")

top10_share = (trend_top.sum() / per_year * 100).rename("porsi_top10_%")
print("Porsi 10 konferensi teratas terhadap seluruh publikasi per tahun (%):")
print(top10_share.round(2).to_string())
growth.round(1)
"""))

cells.append(code(r"""
fig, axes = plt.subplots(2, 5, figsize=(10.6, 4.6), sharex=True, sharey=True)
full_years = np.arange(CFG.YEAR_MIN, CFG.YEAR_INCOMPLETE)

for ax, venue in zip(axes.flat, top_venues):
    row = trend_top.loc[venue]
    series = row.loc[CFG.YEAR_MIN:CFG.YEAR_INCOMPLETE - 1].values / 1e3
    slope_v, intercept_v = np.polyfit(full_years.astype(float), series, 1)
    ax.plot(full_years, slope_v * full_years + intercept_v, color=CFG.INK_2, ls="--", lw=1.0, zorder=2)
    ax.plot(full_years, series, color=CFG.BLUE, lw=2.4, zorder=3)
    ax.scatter([CFG.YEAR_INCOMPLETE], [row.loc[CFG.YEAR_INCOMPLETE] / 1e3], s=30, facecolor=CFG.SURFACE,
               edgecolor=CFG.BLUE, lw=1.4, zorder=4)
    ax.set_title(display_name(venue), fontsize=10.5)
    ax.set_xticks([2015, 2020, 2025])
    ax.set_xticklabels(["15", "20", "25"])
for ax in axes[:, 0]:
    ax.set_ylabel("Paper (ribu)")
fig.legend(handles=[Line2D([], [], color=CFG.BLUE, lw=2.4, label="Publikasi per tahun"),
                    Line2D([], [], color=CFG.INK_2, ls="--", lw=1.0, label="Tren linear 2015-2024"),
                    Line2D([], [], color=CFG.BLUE, ls="", marker="o", mfc=CFG.SURFACE, mec=CFG.BLUE, label="2025 (belum lengkap)")],
           loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01), fontsize=9)
fig.suptitle("Tren publikasi 10 konferensi teratas", x=0.01, ha="left", fontweight="bold", fontsize=11.5, y=1.0)
fig.tight_layout(rect=(0, 0.04, 1, 0.97))
save_fig(fig, "t2_tren_top10.png")
"""))

cells.append(md(r"""
Laju pertumbuhan tahunan (CAGR) 10 konferensi dibandingkan dalam satu chart. Garis putus-putus menandai CAGR seluruh dataset sebagai pembanding.
"""))

cells.append(code(r"""
order = growth.sort_values("cagr_%")

fig, ax = plt.subplots(figsize=(6.4, 4.7))
ax.barh(np.arange(len(order)), order["cagr_%"], color=[CFG.BLUE if v >= 0 else CFG.ORANGE for v in order["cagr_%"]],
        height=0.66, zorder=2)
ax.axvline(0, color=CFG.BASELINE, lw=1)
ax.axvline(cagr * 100, color=CFG.INK, lw=1.4, ls="--", zorder=3)
for y, (_, row) in enumerate(order.iterrows()):
    ha, dx = ("left", 0.5) if row["cagr_%"] >= 0 else ("right", -0.5)
    ax.text(row["cagr_%"] + dx, y, f"{row['cagr_%']:+.1f}%".replace(".", ","), va="center", ha=ha, fontsize=9, color=CFG.INK_2)
ax.set_yticks(np.arange(len(order)))
ax.set_yticklabels(order["nama"], fontsize=9.6)
ax.set_xlim(order["cagr_%"].min() - 6, order["cagr_%"].max() + 8)
ax.set_xlabel("CAGR publikasi 2015-2024 (%)")
ax.grid(axis="y", visible=False)
ax.set_title("Laju pertumbuhan per tahun")
ax.legend(handles=[Patch(color=CFG.BLUE, label="Tumbuh"), Patch(color=CFG.ORANGE, label="Menurun"),
                   Line2D([], [], color=CFG.INK, ls="--", label=f"Seluruh dataset (+{cagr * 100:.1f}%)".replace(".", ","))],
          loc="lower right", fontsize=8.6)
save_fig(fig, "t2_cagr_top10.png")
"""))

cells.append(md(r"""
Pola yang sama dilihat pada lebih banyak konferensi lewat heatmap 12 dari 20 konferensi terbesar (8 dengan indeks 2024 tertinggi dan 4 terendah). Setiap sel adalah indeks jumlah paper terhadap rata-rata 2015-2017 konferensi itu sendiri, dengan 100 berarti sama dengan awal periode. Biru berarti di atas awal periode, merah di bawahnya, dan kolom 2025 diarsir karena belum lengkap. Konferensi yang tidak tercatat pada salah satu tahun 2015-2017 dikeluarkan karena rata-rata awalnya tidak dapat dihitung secara adil, dan penggantinya diambil dari peringkat berikutnya.
"""))

cells.append(code(r"""
complete_base = trend.loc[pub_venue.index, 2015:2017].gt(0).all(axis=1)
excluded = [display_name(v) for v in pub_venue.head(20).index if not complete_base[v]]
top20_venues = list(pub_venue[complete_base].head(20).index)
print("Dikeluarkan karena tidak tercatat pada salah satu tahun 2015-2017:", excluded)
baseline = trend.loc[top20_venues, 2015:2017].mean(axis=1)
heat = trend.loc[top20_venues].div(baseline, axis=0) * 100
heat = heat.loc[heat[2024].sort_values(ascending=False).index]
save_table(heat.round(1), "t2_indeks_tren_top20.csv")
show = pd.concat([heat.head(8), heat.tail(4)])

cmap = LinearSegmentedColormap.from_list("merah_netral_biru", ["#e34948", "#f0efec", "#2a78d6"])
norm = TwoSlopeNorm(vcenter=100, vmin=40, vmax=800)

fig, ax = plt.subplots(figsize=(6.4, 5.0))
image = ax.imshow(show.values, cmap=cmap, norm=norm, aspect="auto")
ax.add_patch(Rectangle((show.shape[1] - 1.5, -0.5), 1, show.shape[0], fill=False, hatch="///", edgecolor=CFG.MUTED, lw=0, zorder=2))
ax.set_xticks(np.arange(show.shape[1]))
ax.set_xticklabels([str(int(c))[2:] for c in show.columns])
ax.set_yticks(np.arange(show.shape[0]))
ax.set_yticklabels([display_name(v) for v in show.index], fontsize=9.4)
ax.grid(False)
for spine in ax.spines.values():
    spine.set_visible(False)
colorbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02, ticks=[50, 100, 200, 400, 800])
colorbar.set_label("Indeks (100 = rata-rata 2015-2017)")
ax.set_title("Indeks publikasi terhadap awal periode (kolom 2025 diarsir)", pad=10, fontsize=10.2)
save_fig(fig, "t2_heatmap_tren_top20.png")
"""))

cells.append(md(r"""
#### Insights

> 1. Pertumbuhan terkonsentrasi pada konferensi kecerdasan buatan. NeurIPS tumbuh 10,2 kali (440 menjadi 4.494 paper pada 2024, CAGR 29,5%), EMNLP 7,6 kali (324 menjadi 2.450, CAGR 25,2%), CVPR 4,8 kali (CAGR 19,1%), dan AAAI 3,6 kali (CAGR 15,5%), jauh di atas CAGR seluruh dataset sebesar 3,2%.
> 2. Konferensi bidang lain tumbuh lebih lambat atau menyusut. ICASSP tumbuh 2,4 kali (CAGR 10,3%), IGARSS 1,9 kali (7,5%), CHI 1,8 kali (7,0%), dan HCI hampir datar (1,1 kali, 0,6%). ICC (0,7 kali, -3,3%) dan EMBC (0,7 kali, -4,0%) menurun.
> 3. Porsi 10 konferensi teratas terhadap seluruh publikasi naik dari 7,0% (2015) menjadi 11,7% (2024), dan 12,9% pada 2025. Kenaikan sudah terlihat sejak 2017, sehingga tidak semata-mata akibat data 2025 yang tidak lengkap.
> 4. Heatmap memperkuat pola ini. NeurIPS, ICML, EMNLP, dan ACL berindeks 524 sampai 788 pada 2024, sedangkan IECON (85), EMBC (88), ICC (91), dan CDC (95) di bawah level awal. ICLR dikeluarkan dari heatmap karena tidak tercatat di DBLP pada 2015 dan 2016, dan sejak 2017 tumbuh dari 309 menjadi 2.454 paper pada 2024.
> 5. Pada 2025, NeurIPS (5.823, +29,6%), EMNLP (3.491, +42,5%), dan AAAI (3.508, +21,7%) melanjutkan kenaikan. IGARSS dan EMBC bernilai nol karena prosiding 2025 belum terindeks, bukan karena berhenti diselenggarakan.
"""))

cells.append(md(r"""
## 6.4 Perbandingan Peringkat Publikasi dan Author Unik

Perbandingan dilakukan dalam tiga bentuk. Tabel memuat semua konferensi yang masuk 10 besar pada salah satu ukuran. Slope chart menunjukkan pergeseran peringkat dari ukuran publikasi ke ukuran author unik. Scatter plot menampilkan seluruh konferensi, dengan area biru menandai rentang 1 sampai 4 author unik per paper dan konferensi 10 besar berwarna biru tua.
"""))

cells.append(code(r"""
union = list(top_pub.index) + [v for v in top_auth.index if v not in top_pub.index]
compare = venue_stats.loc[union, ["nama", "publikasi", "rank_publikasi", "author_unik", "rank_author",
                                  "paper_per_author", "author_unik_per_paper"]].copy()
compare["selisih_rank"] = compare["rank_publikasi"] - compare["rank_author"]
compare["masuk_10_besar"] = np.where(compare.index.isin(shared), "kedua ukuran",
                                     np.where(compare["rank_publikasi"] <= 10, "hanya publikasi", "hanya author unik"))
save_table(compare, "t2_perbandingan_peringkat.csv")

rho = venue_stats[["publikasi", "author_unik"]].corr(method="spearman").iloc[0, 1]
r_log = np.corrcoef(np.log10(venue_stats["publikasi"]), np.log10(venue_stats["author_unik"]))[0, 1]
print(f"Irisan 10 besar: {len(shared)} dari 10 venue | korelasi peringkat Spearman ({len(venue_stats):,} venue): {rho:.3f} | "
      f"korelasi log-log: {r_log:.3f}")
compare.round(2)
"""))

cells.append(code(r"""
fig, ax = plt.subplots(figsize=(6.0, 5.6))
for venue, row in compare.iterrows():
    shift = row["selisih_rank"]
    color = CFG.BLUE if shift > 0 else (CFG.ORANGE if shift < 0 else CFG.GRAY)
    ax.plot([0, 1], [row["rank_publikasi"], row["rank_author"]], color=color, lw=2.4, marker="o", ms=6, zorder=3)
    ax.text(-0.04, row["rank_publikasi"], f"{row['nama']}  #{int(row['rank_publikasi'])}", ha="right", va="center", fontsize=9.6)
    ax.text(1.04, row["rank_author"], f"#{int(row['rank_author'])}  {row['nama']}", ha="left", va="center", fontsize=9.6)
ax.set_xlim(-0.75, 1.75)
ax.set_ylim(compare[["rank_publikasi", "rank_author"]].max().max() + 1, 0.2)
ax.axis("off")
ax.text(0, -0.2, "Peringkat\npublikasi", ha="center", va="bottom", fontsize=10, fontweight="bold", color=CFG.INK_2)
ax.text(1, -0.2, "Peringkat\nauthor unik", ha="center", va="bottom", fontsize=10, fontweight="bold", color=CFG.INK_2)
ax.legend(handles=[Line2D([], [], color=CFG.BLUE, lw=2.4, label="Naik"),
                   Line2D([], [], color=CFG.ORANGE, lw=2.4, label="Turun"),
                   Line2D([], [], color=CFG.GRAY, lw=2.4, label="Sama")],
          loc="lower center", bbox_to_anchor=(0.5, -0.04), ncol=3, fontsize=9)
save_fig(fig, "t2_slope_peringkat.png")
"""))

cells.append(code(r"""
fig, ax = plt.subplots(figsize=(6.0, 5.4))
guide_x = np.array([8, 7e4])
ax.fill_between(guide_x, 1 * guide_x, 4 * guide_x, color=CFG.BLUE_LIGHT, alpha=0.25, zorder=0, linewidth=0)
ax.plot(guide_x, 2 * guide_x, color=CFG.MUTED, lw=1.2, ls="--", zorder=1)
ax.scatter(venue_stats["publikasi"], venue_stats["author_unik"], s=9, color=CFG.GRAY, alpha=0.4, linewidths=0, zorder=2)
highlight = venue_stats.loc[union]
ax.scatter(highlight["publikasi"], highlight["author_unik"], s=44, color=CFG.BLUE, zorder=4)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(8, 7e4)
ax.set_ylim(8, 1.2e5)
ax.set_xlabel("Jumlah publikasi (skala logaritmik)")
ax.set_ylabel("Jumlah author unik (skala logaritmik)")
ax.set_title("Publikasi dan author unik per konferensi")
ax.legend(handles=[Line2D([], [], marker="o", ls="", color=CFG.GRAY, ms=5, label="Venue lain"),
                   Line2D([], [], marker="o", ls="", color=CFG.BLUE, ms=7, label="Venue 10 besar (salah satu ukuran)"),
                   Patch(color=CFG.BLUE_LIGHT, alpha=0.4, label="1 sampai 4 author unik per paper"),
                   Line2D([], [], color=CFG.MUTED, ls="--", label="2 author unik per paper")],
          loc="lower right", fontsize=8.4)
save_fig(fig, "t2_scatter_publikasi_author.png")
"""))

cells.append(md(r"""
#### Insights

> 1. Kedua peringkat sangat selaras. Korelasi peringkat Spearman pada 4.373 konferensi adalah 0,987, dan 8 dari 10 konferensi teratas sama. NeurIPS dan CVPR berada di posisi 1 dan 2 pada keduanya, dan EMNLP tetap di posisi 8.
> 2. Perbedaan muncul di peringkat tengah. AAAI naik dari peringkat 6 ke 3 dan EMBC dari 9 ke 5 pada author unik, karena author unik per paper keduanya tinggi (2,41 dan 2,68).
> 3. CHI turun dari 7 ke 12 dan ICC dari 10 ke 19, sehingga keduanya keluar dari 10 besar author dan digantikan ICML (dari 12 ke 9) dan IROS (dari 14 ke 10). ICC mengalami penurunan terbesar (9 peringkat), dan 22,8% papernya adalah paper workshop (lihat 6.5).
> 4. Pada scatter plot, hampir semua konferensi berada di antara garis 1 dan 4 author unik per paper dan mengelompok di sekitar 2. Perbedaan peringkat berasal dari variasi rasio ini, bukan dari hubungan yang berbeda antara kedua ukuran.
"""))

cells.append(md(r"""
## 6.5 Uji Sensitivitas terhadap Keputusan Venue

Venue diidentifikasi dari `key`, sehingga workshop dan acara pendamping ikut terhitung sebagai konferensi induknya. Agar kesimpulan peringkat tidak bergantung pada keputusan itu, peringkat dihitung ulang tanpa acara satelit. Acara satelit dikenali dari kata kunci pada `booktitle` (Workshop, `@`, Extended Abstracts, Companion, Doctoral, Tutorial, Demo, Poster, Student, Competition, dan Challenge), sehingga hasilnya bersifat pendekatan.

Pendekatan lain, yaitu akhiran huruf pada `crossref` (misalnya `conf/cvpr/2011w`), juga diuji dan dibandingkan di tabel. Pendekatan ini ditinggalkan karena menandai volume Findings pada EMNLP dan ACL sebagai satelit, padahal Findings adalah bagian dari konferensi utama.
"""))

cells.append(code(r"""
meta = pd.read_parquet(CFG.CLEAN_PARQUET, columns=["venue", "booktitle", "crossref"])
satellite_pattern = r"Workshop|@|Extended Abstracts|Companion|Doctoral|Tutorial|Demo|Poster|Student|Competition|Challenge"
satellite = meta["booktitle"].fillna("").str.contains(satellite_pattern, case=False)
satellite_crossref = meta["crossref"].fillna("").str.contains(r"/\d{4}[a-z]+\d*$")

pub_main = (~satellite).groupby(meta["venue"]).sum()
crossref_share = satellite_crossref.groupby(meta["venue"]).mean() * 100

sens = pd.DataFrame({"publikasi_seluruh_key": pub_venue, "publikasi_tanpa_satelit": pub_main}).fillna(0).astype(int)
sens["rank_seluruh_key"] = sens["publikasi_seluruh_key"].rank(ascending=False, method="min").astype(int)
sens["rank_tanpa_satelit"] = sens["publikasi_tanpa_satelit"].rank(ascending=False, method="min").astype(int)
sens["porsi_satelit_booktitle_%"] = (1 - sens["publikasi_tanpa_satelit"] / sens["publikasi_seluruh_key"]) * 100
sens["porsi_satelit_crossref_%"] = crossref_share
sens["nama"] = [display_name(v) for v in sens.index]
save_table(sens.sort_values("rank_seluruh_key"), "t2_sensitivitas_satelit.csv")

top10_without_satellite = set(sens.sort_values("rank_tanpa_satelit").head(10).index)
print(f"Paper dari acara satelit menurut booktitle: {satellite.sum():,} ({satellite.mean():.1%}) | menurut crossref: {satellite_crossref.sum():,} ({satellite_crossref.mean():.1%})")
print(f"Irisan 10 besar sebelum dan sesudah satelit dikeluarkan: {len(set(top_pub.index) & top10_without_satellite)} dari 10")
print("Masuk 10 besar:", sorted(display_name(v) for v in top10_without_satellite - set(top_pub.index)))
print("Keluar dari 10 besar:", sorted(display_name(v) for v in set(top_pub.index) - top10_without_satellite))
sens.sort_values("rank_seluruh_key").head(12)[["nama", "publikasi_seluruh_key", "publikasi_tanpa_satelit", "porsi_satelit_booktitle_%",
                                               "porsi_satelit_crossref_%", "rank_seluruh_key", "rank_tanpa_satelit"]].round(1)
"""))

cells.append(md(r"""
#### Insights

> 1. Peringkat teratas relatif kuat. Setelah acara satelit dikeluarkan (144.549 paper atau 7,2% dataset), 8 dari 10 konferensi teratas tetap sama dan NeurIPS tetap nomor satu (25.178 paper). ICASSP naik ke peringkat 2, HCI ke 3, IGARSS ke 4, dan AAAI ke 5.
> 2. Yang berubah adalah konferensi dengan banyak acara pendamping. CVPR turun dari peringkat 2 ke 6 (23,4% papernya workshop), ICC dari 10 ke 18 (22,8%), dan CHI dari 7 ke 29 (44,0% papernya Extended Abstracts). ICML dan IROS masuk 10 besar sebagai gantinya.
> 3. Posisi CVPR sebagai konferensi paling populer kedua bergantung pada definisi. Pernyataan itu benar jika workshop dihitung sebagai bagian konferensi, sesuai pengelompokan DBLP, tetapi tidak benar jika hanya acara utama yang dihitung. Analisis memakai definisi berbasis `key`, dan hasil alternatifnya dilaporkan di sini.
> 4. Pendekatan berbasis akhiran `crossref` ditolak karena menandai 39,9% paper EMNLP sebagai satelit, padahal kata kunci `booktitle` hanya menemukan 5,0%. Selisihnya adalah volume Findings, yang merupakan bagian dari konferensi utama.
"""))

cells.append(md(r"""
## 6.6 Ringkasan Temuan Popularitas

Subbagian ini merangkum temuan 6.1 sampai 6.5 tentang konferensi terpopuler, hubungan antara publikasi dan author unik, serta perubahan aktivitas dari waktu ke waktu. Seluruh temuan memakai definisi venue berbasis `key`, dan dampak definisi lain dijelaskan pada subbagian 6.5.
"""))

cells.append(md(r"""
#### Insights

> 1. NeurIPS adalah konferensi terpopuler menurut jumlah publikasi, dengan 25.455 paper (1,27% dari seluruh dataset 2015-2025), disusul CVPR (22.751) dan ICASSP (21.606). NeurIPS tetap nomor satu setelah workshop dan acara satelit dikeluarkan.
> 2. Publikasi terbanyak umumnya diikuti author unik terbanyak. NeurIPS (57.800 author unik) dan CVPR tetap di posisi 1 dan 2, 8 dari 10 konferensi teratas sama, dan korelasi peringkat Spearman pada seluruh venue adalah 0,987.
> 3. Perbedaan terjadi di peringkat tengah. AAAI dan EMBC lebih tinggi pada author unik, sedangkan CHI dan ICC lebih tinggi pada jumlah paper, sehingga ICC di peringkat 10 pada publikasi hanya di peringkat 19 pada author unik.
> 4. Jumlah publikasi keseluruhan tumbuh 32,7% dari 2015 ke 2024 (CAGR 3,2%), dengan penurunan 8,8% pada 2020. Pertumbuhan sangat tidak merata: NeurIPS, EMNLP, CVPR, dan AAAI tumbuh 3,6 sampai 10,2 kali, HCI hampir datar, dan ICC serta EMBC menurun, sehingga porsi 10 konferensi teratas naik dari 7,0% menjadi 11,7% pada 2024.
> 5. Angka 2025 tidak dipakai untuk menyimpulkan tren karena sebagian konferensi dua tahunan tidak diadakan dan sebagian konferensi tahunan belum terindeks.
"""))

# @@APPEND@@

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
