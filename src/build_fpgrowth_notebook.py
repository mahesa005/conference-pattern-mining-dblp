import json
import sys
import textwrap
from pathlib import Path
from uuid import uuid4

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path(__file__).resolve().parents[1] / "notebooks" / "04_fpgrowth.ipynb"
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

*Notebook 04: Task 4, Frequent Pattern Mining dengan FP-Growth.*
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
3. [**Implementasi FP-Growth**](#3)
4. [**Eksperimen Empat Min Support (Task 4.1)**](#4)
5. [**Validasi dengan mlxtend**](#5)
6. [**Analisis Frequent Itemsets (Task 4.2 sampai 4.5)**](#6)
7. [**Interpretasi (Task 4.6)**](#7)
8. [**Ringkasan dan Langkah Berikutnya**](#8)
"""))

# ---------------------------------------------------------------------------
# 1. Introduction
# ---------------------------------------------------------------------------
cells.append(section("Introduction", "1"))

cells.append(md("""
## Overview

*Task 4 mencari kombinasi konferensi yang sering muncul bersama dalam riwayat publikasi author. Notebook ini mengerjakan sisi FP-Growth pada author-based transactional database dari notebook `02_transactions`. Sisi Apriori dikerjakan pada notebook `03_apriori`, dan perbandingan keduanya pada notebook `06_performance`.*
"""))

cells.append(md("""
## Aim

*Task 4.1: menemukan frequent itemsets pada min support 0,1%, 0,5%, 1%, dan 2%.*

*Task 4.2 dan 4.3: memisahkan 1-, 2-, dan 3-itemsets, lalu menampilkan 10 itemsets dengan support tertinggi.*

*Task 4.4 dan 4.5: menganalisis pengaruh min support terhadap jumlah itemsets dan mengidentifikasi kombinasi konferensi yang paling sering muncul bersama.*

*Task 4.6: menginterpretasikan pola yang ditemukan.*
"""))

cells.append(md(r"""
## Metric

***Support** itemset $X$ adalah proporsi transaksi yang memuat seluruh item pada $X$. Penyebutnya selalu seluruh transaksi author-based, yaitu 1.821.757, termasuk transaksi yang dilewati saat membangun FP-tree.*

$$\text{support}(X) = \frac{|\{t \in D : X \subseteq t\}|}{|D|}$$

*Itemset frequent jika support-nya minimal min support. Dalam hitungan transaksi, ambangnya adalah bilangan bulat terkecil $c$ dengan $c / |D| \ge \text{min\_sup}$.*
"""))

cells.append(md("""
## Approach

*FP-Growth memadatkan database menjadi FP-tree dalam dua pemindaian, lalu menambang pola secara rekursif dari conditional pattern base tanpa membangkitkan kandidat. Implementasi mengikuti aturan bab metodologi: item yang tidak frequent dipangkas lebih dulu, transaksi dengan kurang dari dua item frequent tidak dimasukkan ke pohon (support 1-itemset tetap dari pemindaian pertama), dan waktu pembentukan pohon dilaporkan terpisah dari waktu penambangan.*

*Kode algoritma berada di `src/fpgrowth.py` agar dapat dipakai ulang oleh notebook 05, 06, dan 07, dan sudah diuji dengan `pytest` (contoh buku teks, brute force, dan `mlxtend`). Isi modul ditampilkan pada bagian 3.*
"""))

# ---------------------------------------------------------------------------
# 2. Initialization
# ---------------------------------------------------------------------------
cells.append(section("Initialization", "2"))

cells.append(md("""
## Environment Setup

Notebook ini tidak memakai GPU. Prasyaratnya adalah notebook `02_transactions` sudah dijalankan sehingga `data/processed/tx_author.parquet` dan `tx_items.csv` tersedia.
"""))

cells.append(md("Sel berikut memasang semua pustaka yang dipakai notebook ini."))

cells.append(code("""
%pip install -q numpy pandas scipy matplotlib pyarrow mlxtend
"""))

cells.append(md("""
## Import Libraries

Seluruh `import` untuk notebook ini dikumpulkan di satu sel. Modul proyek di `src/` diimpor setelah `Settings` menetapkan path-nya.
"""))

cells.append(code("""
import inspect
import os
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
"""))

cells.append(md("""
## Seed Everything

FP-Growth bersifat deterministik. Seed tetap ditetapkan agar konsisten dengan notebook lain.
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

Seluruh path, ambang min support, dan warna dipusatkan di kelas `Settings`. Palet warna sama dengan notebook sebelumnya.
"""))

cells.append(code("""
class Settings:
    SEED = 42
    ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()

    SRC_DIR = ROOT / "src"
    PROC_DIR = ROOT / "data" / "processed"
    TAB_DIR = ROOT / "outputs" / "tables"
    FIG_DIR = ROOT / "outputs" / "figures"
    FPM_DIR = ROOT / "outputs" / "fpgrowth"

    ITEMS = PROC_DIR / "tx_items.csv"
    TX_AUTHOR = PROC_DIR / "tx_author.parquet"

    MIN_SUPPORTS = [0.001, 0.005, 0.01, 0.02]
    TOP_K = 10

    INK = "#0b0b0b"
    INK_2 = "#52514e"
    MUTED = "#898781"
    GRID = "#e1e0d9"
    BASELINE = "#c3c2b7"
    SURFACE = "#fcfcfb"
    BLUE = "#2a78d6"
    BLUE_LIGHT = "#9ec5f4"
    ORANGE = "#eb6834"
    GRAY = "#b9b8b2"

CFG = Settings()
for d in (CFG.TAB_DIR, CFG.FIG_DIR, CFG.FPM_DIR):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CFG.SRC_DIR))
import fpgrowth as fpgrowth_module
from fpgrowth import fpgrowth, render_tree, to_frame
from fpm_data import load_horizontal, load_item_names
from validation import compare_itemsets, mlxtend_reference
"""))

cells.append(md("""
Gaya grafik dan fungsi bantu diatur sekali di sini. Angka ditulis dengan pemisah ribuan titik dan desimal koma agar konsisten dengan notebook sebelumnya.
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
pd.set_option("display.max_colwidth", 90)


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


def id_ticks(ax, axis="x"):
    formatter = FuncFormatter(lambda v, _: fmt_id(v, 0 if float(v).is_integer() else 1))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(formatter)


def tag(ms):
    return f"{ms * 100:g}".replace(".", "p")
"""))

cells.append(md("""
## Load Dataset

Tabel panjang author-based diubah ke bentuk horizontal, yaitu list frozenset kode item per transaksi. Bentuk ini sama dengan masukan Apriori pada notebook 03. Waktu pemuatan tidak termasuk pengukuran.
"""))

cells.append(code("""
transactions = load_horizontal(CFG.TX_AUTHOR)
names = load_item_names(CFG.ITEMS)
N = len(transactions)
print(f"Transaksi: {fmt_id(N)} | item unik: {fmt_id(len(names))}")
"""))

# ---------------------------------------------------------------------------
# 3. Implementasi
# ---------------------------------------------------------------------------
cells.append(section("Implementasi FP-Growth", "3"))

cells.append(md("""
## 3.1 Kode

Seluruh isi `src/fpgrowth.py` ditampilkan di bawah. Setiap node FP-tree menyimpan `item`, `count`, `parent`, dan `children`, dan header table memetakan item ke daftar node-nya.
"""))

cells.append(code("""
print(inspect.getsource(fpgrowth_module))
"""))

cells.append(md("""
## 3.2 Contoh Kecil

Sebelum dijalankan pada data DBLP, FP-Growth diperiksa pada contoh buku teks Han, Kamber, dan Pei (2012), sembilan transaksi dengan item I1 sampai I5 dan min support 2/9. Hasil yang benar adalah 13 frequent itemsets.
"""))

cells.append(code("""
toy = [frozenset(t) for t in ([1, 2, 5], [2, 4], [2, 3], [1, 2, 4], [1, 3], [2, 3], [1, 3], [1, 2, 3, 5], [1, 2, 3])]
toy_names = {i: f"I{i}" for i in range(1, 6)}
toy_result = fpgrowth(toy, 2 / 9)
print(render_tree(toy_result.tree, toy_names))
to_frame(toy_result, toy_names)[["names", "length", "count", "support"]]
"""))

# ---------------------------------------------------------------------------
# 4. Eksperimen
# ---------------------------------------------------------------------------
cells.append(section("Eksperimen Empat Min Support (Task 4.1)", "4"))

cells.append(md("""
FP-Growth dijalankan sekali untuk setiap min support. Waktu pembentukan pohon (`t_build`) dan waktu penambangan (`t_mine`) dicatat terpisah. Pengukuran berulang untuk perbandingan performa dilakukan pada notebook 06. FP-tree tidak disimpan setelah penambangan (`keep_tree=False`) agar memori cukup untuk validasi.
"""))

cells.append(code("""
results = {}
for ms in CFG.MIN_SUPPORTS:
    res = fpgrowth(transactions, ms, keep_tree=False)
    results[ms] = res
    print(f"min_sup {pct_id(ms * 100)} | min_count {fmt_id(res.min_count)} | itemsets {fmt_id(len(res.itemsets))} "
          f"| build {res.t_build:.2f} s | mine {res.t_mine:.2f} s")

frames = {ms: to_frame(res, names) for ms, res in results.items()}
for ms, df in frames.items():
    df.assign(itemset=df["itemset"].apply(list)).to_parquet(CFG.FPM_DIR / f"itemsets_{tag(ms)}.parquet", index=False)
"""))

# ---------------------------------------------------------------------------
# 5. Validasi
# ---------------------------------------------------------------------------
cells.append(section("Validasi dengan mlxtend", "5"))

cells.append(md("""
Setiap hasil dibandingkan dengan `mlxtend.frequent_patterns.fpgrowth` pada database yang sama. Itemset dan count harus identik.
"""))

cells.append(code("""
checks = pd.DataFrame([
    {"min_support": ms, **compare_itemsets(res.itemsets, mlxtend_reference(transactions, ms))}
    for ms, res in results.items()
])
save_table(checks, "t4_fpgrowth_validasi_mlxtend.csv", index=False)
assert checks["identical"].all(), "hasil FP-Growth berbeda dengan mlxtend"
checks
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
