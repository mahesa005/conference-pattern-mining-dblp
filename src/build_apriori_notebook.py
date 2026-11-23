import json
import sys
import textwrap
from pathlib import Path
from uuid import uuid4

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path(__file__).resolve().parents[1] / "notebooks" / "03_apriori.ipynb"
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

*Notebook 03: Frequent Pattern Mining dengan Apriori.*
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
3. [**Implementasi Apriori**](#3)
4. [**Eksperimen Empat Min Support**](#4)
5. [**Validasi dengan mlxtend dan FP-Growth**](#5)
6. [**Analisis Frequent Itemsets**](#6)
7. [**Interpretasi Pola**](#7)
"""))

# ---------------------------------------------------------------------------
# 1. Introduction
# ---------------------------------------------------------------------------
cells.append(section("Introduction", "1"))

cells.append(md("""
## Overview

*Notebook ini mencari kombinasi venue yang sering muncul bersama dalam riwayat publikasi author, memakai algoritma Apriori pada author-based transactional database dari notebook `02_transactions`. Algoritma FP-Growth dikerjakan pada notebook `04_fpgrowth`, dan perbandingan performa keduanya pada notebook `06_performance`.*
"""))

cells.append(md("""
## Aim

*Notebook ini bertujuan untuk:*

1. *menemukan frequent itemsets pada min support 0,1%, 0,5%, 1%, dan 2%, lalu memvalidasinya dengan `mlxtend` dan FP-Growth.*
2. *memisahkan 1-, 2-, dan 3-itemsets, lalu menampilkan 10 itemsets dengan support tertinggi.*
3. *menganalisis pengaruh min support terhadap jumlah itemsets dan kandidat, serta mengidentifikasi kombinasi venue yang paling sering muncul bersama.*
4. *menginterpretasikan pola yang ditemukan.*
"""))

cells.append(md(r"""
## Metric

***Support** itemset $X$ adalah proporsi transaksi yang memuat seluruh item pada $X$. Penyebutnya selalu seluruh transaksi author-based, yaitu 1.821.757, termasuk transaksi yang dilewati saat penghitungan kandidat.*

$$\text{support}(X) = \frac{|\{t \in D : X \subseteq t\}|}{|D|}$$

*Itemset frequent jika support-nya minimal min support. Dalam hitungan transaksi, ambangnya adalah bilangan bulat terkecil $c$ dengan $c / |D| \ge \text{min\_sup}$, sama dengan FP-Growth (`fpgrowth.min_count_for`).*
"""))

cells.append(md("""
## Approach

*Apriori bekerja per level. Level $k$ membangkitkan kandidat $C_k$ dari frequent $(k-1)$-itemsets $L_{k-1}$ (langkah join), membuang kandidat yang memiliki subset $(k-1)$ tidak frequent (langkah prune, sifat Apriori), lalu memindai database untuk menghitung support kandidat yang tersisa. Proses berhenti ketika $L_k$ kosong.*

*Pra-pemrosesan dibuat sama dengan FP-Growth agar perbandingan waktu di `06_performance` adil: item yang tidak frequent dipangkas, transaksi dengan kurang dari dua item frequent dilewati (tetap dihitung di penyebut), dan transaksi yang identik setelah dipangkas digabung lalu dihitung sekali dengan bobotnya. Saat menghitung kandidat, setiap transaksi memakai cara yang lebih murah: mengenumerasi $k$-subset transaksi, atau memeriksa setiap kandidat sebagai subset transaksi.*

*Kode algoritma berada pada modul `apriori` dan ditampilkan lengkap pada bagian 3. Modul ini sudah diuji dengan contoh buku teks, transaksi kosong di penyebut, dan perbandingan terhadap brute force.*
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
%pip install -q --disable-pip-version-check numpy pandas scipy matplotlib pyarrow mlxtend
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

Apriori bersifat deterministik. Seed tetap ditetapkan agar konsisten dengan notebook lain.
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
    APR_DIR = ROOT / "outputs" / "apriori"

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
for d in (CFG.TAB_DIR, CFG.FIG_DIR, CFG.APR_DIR):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CFG.SRC_DIR))
import apriori as apriori_module
from apriori import apriori
from fpgrowth import fpgrowth, to_frame
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

Tabel panjang author-based diubah ke bentuk horizontal, yaitu list frozenset kode item per transaksi. Bentuk ini sama dengan masukan FP-Growth pada `04_fpgrowth`. Waktu pemuatan tidak termasuk pengukuran.
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
cells.append(section("Implementasi Apriori", "3"))

cells.append(md("""
## 3.1 Kode

Seluruh kode modul `apriori` ditampilkan di bawah. `generate_candidates` menjalankan langkah join dan prune, `count_candidates` memindai database berbobot, dan `apriori` mengulang keduanya per level. Hasilnya mencatat jumlah kandidat $|C_k|$ dan waktu setiap level.
"""))

cells.append(code("""
print(inspect.getsource(apriori_module))
"""))

cells.append(md("""
## 3.2 Contoh Kecil

Sebelum dijalankan pada data DBLP, Apriori diperiksa pada contoh buku teks Han, Kamber, dan Pei (2012), sembilan transaksi dengan item I1 sampai I5 dan min support 2/9. Buku tersebut menghasilkan $|C_1| = 5$, $|C_2| = 10$, dan $|C_3| = 2$ setelah prune (I1 I2 I3 dan I1 I2 I5), dengan total 13 frequent itemsets.
"""))

cells.append(code("""
toy = [frozenset(t) for t in ([1, 2, 5], [2, 4], [2, 3], [1, 2, 4], [1, 3], [2, 3], [1, 3], [1, 2, 3, 5], [1, 2, 3])]
toy_names = {i: f"I{i}" for i in range(1, 6)}
toy_result = apriori(toy, 2 / 9)
toy_frame = to_frame(toy_result, toy_names)
print("Kandidat per level:", toy_result.n_candidates)
print("Frequent per level:", toy_frame["length"].value_counts().sort_index().tolist())
toy_frame[["names", "length", "count", "support"]]
"""))

# ---------------------------------------------------------------------------
# 4. Eksperimen
# ---------------------------------------------------------------------------
cells.append(section("Eksperimen Empat Min Support", "4"))

cells.append(md("""
Apriori dijalankan sekali untuk setiap min support, dengan jumlah kandidat, jumlah frequent itemsets, dan waktu setiap level dicatat. Waktu level 1 sudah termasuk pra-pemrosesan (pemindaian pertama, pemangkasan, dan penggabungan transaksi). Pengukuran berulang untuk perbandingan performa dilakukan pada `06_performance`.
"""))

cells.append(code("""
results = {}
for ms in CFG.MIN_SUPPORTS:
    res = apriori(transactions, ms)
    results[ms] = res
    print(f"min_sup {pct_id(ms * 100)} | min_count {fmt_id(res.min_count)} | itemsets {fmt_id(len(res.itemsets))} "
          f"| level {len(res.level_seconds)} | total {sum(res.level_seconds):.2f} s")

frames = {ms: to_frame(res, names) for ms, res in results.items()}
for ms, df in frames.items():
    df.assign(itemset=df["itemset"].apply(list)).to_parquet(CFG.APR_DIR / f"itemsets_{tag(ms)}.parquet", index=False)
"""))

cells.append(md("""
Tabel berikut merinci setiap level: jumlah kandidat $|C_k|$, jumlah frequent itemsets $|L_k|$, persentase kandidat yang ternyata frequent, dan waktu level tersebut.
"""))

cells.append(code("""
level_rows = []
for ms, res in results.items():
    lk = frames[ms]["length"].value_counts()
    for k, (cands, secs) in enumerate(zip(res.n_candidates, res.level_seconds), start=1):
        level_rows.append({"min_support": ms, "k": k, "kandidat": cands, "frequent": int(lk.get(k, 0)),
                           "frequent_pct": round(100 * lk.get(k, 0) / cands, 2), "detik": round(secs, 3)})
levels = pd.DataFrame(level_rows)
save_table(levels, "t4_apriori_level.csv", index=False)
levels
"""))

# ---------------------------------------------------------------------------
# 5. Validasi
# ---------------------------------------------------------------------------
cells.append(section("Validasi dengan mlxtend dan FP-Growth", "5"))

cells.append(md("""
Setiap hasil dibandingkan dengan `mlxtend.frequent_patterns.fpgrowth` dan dengan modul `fpgrowth` proyek pada database yang sama. Itemset dan count harus identik dengan keduanya.
"""))

cells.append(code("""
check_rows = []
for ms, res in results.items():
    for ref_name, ref in (("mlxtend", mlxtend_reference(transactions, ms)),
                          ("fpgrowth", fpgrowth(transactions, ms, keep_tree=False).itemsets)):
        check_rows.append({"min_support": ms, "pembanding": ref_name, **compare_itemsets(res.itemsets, ref)})
checks = pd.DataFrame(check_rows)
save_table(checks, "t4_apriori_validasi.csv", index=False)
assert checks["identical"].all(), "hasil Apriori berbeda dengan pembanding"
checks
"""))

# ---------------------------------------------------------------------------
# 6. Analisis
# ---------------------------------------------------------------------------
cells.append(section("Analisis Frequent Itemsets", "6"))

cells.append(md("""
## 6.1 Jumlah Itemset per Ukuran

Itemset dikelompokkan menurut ukurannya. Kolom `k4+` menampung itemset berisi empat item atau lebih.
"""))

cells.append(code("""
def length_counts(df):
    return df["length"].clip(upper=4).value_counts().reindex([1, 2, 3, 4], fill_value=0)

summary = pd.DataFrame([
    {"min_support": ms, "min_count": res.min_count, "itemsets": len(res.itemsets),
     **dict(zip(["k1", "k2", "k3", "k4+"], length_counts(frames[ms]).tolist())),
     "max_length": int(frames[ms]["length"].max()),
     "kandidat_total": sum(res.n_candidates[1:]), "t_total_s": round(sum(res.level_seconds), 3)}
    for ms, res in results.items()
])
save_table(summary, "t4_apriori_ringkasan.csv", index=False)
summary
"""))

cells.append(md("""
#### Insights

> 1. Jumlah dan ukuran itemset sama persis dengan FP-Growth pada `04_fpgrowth`. Terdapat 1.514 itemset pada 0,1% (574 1-itemset, 393 pasangan, 348 triple, dan 199 itemset berukuran empat sampai enam), 88 pada 0,5%, 30 pada 1%, dan 6 pada 2%.
> 2. Yang khas Apriori adalah kolom `kandidat_total`, yaitu jumlah kandidat level 2 ke atas yang support-nya harus dihitung. Nilainya 166.075 pada 0,1%, 2.158 pada 0,5%, 406 pada 1%, dan 15 pada 2%.
> 3. Untuk menemukan 940 itemset berukuran dua atau lebih pada 0,1%, Apriori menghitung 166.075 kandidat, 177 kali jumlah itemset yang akhirnya frequent.
"""))

cells.append(md("""
## 6.2 Sepuluh Itemset dengan Support Tertinggi

Sepuluh itemset teratas ditampilkan untuk semua ukuran dan untuk itemset berukuran dua atau lebih, seperti pada `04_fpgrowth`.
"""))

cells.append(code("""
cols = ["names", "length", "count", "support"]
for ms, df in frames.items():
    top = df.head(CFG.TOP_K)[cols]
    top_k2 = df[df["length"] >= 2].head(CFG.TOP_K)[cols]
    save_table(top, f"t4_apriori_top10_{tag(ms)}.csv", index=False)
    save_table(top_k2, f"t4_apriori_top10_k2plus_{tag(ms)}.csv", index=False)
    print(f"\\nmin_sup {pct_id(ms * 100)}: semua ukuran")
    display(top.style.format({"support": "{:.4%}"}))
    print(f"min_sup {pct_id(ms * 100)}: ukuran >= 2 ({len(df[df['length'] >= 2])} itemset)")
    display(top_k2.style.format({"support": "{:.4%}"}))
"""))

cells.append(md("""
#### Insights

> 1. Sepuluh itemset teratas pada setiap min support selalu berupa venue tunggal, dipimpin NeurIPS (57.800 author, support 3,17%), CVPR (47.664), dan AAAI (46.437).
> 2. Pasangan teratas, ICML + NeurIPS (18.503 author, support 1,02%), masih lebih kecil dari venue ke-10, IROS (31.249 author).
> 3. Hasil ini sama dengan `04_fpgrowth` karena kedua algoritma menghasilkan itemset dan count yang identik.
"""))

cells.append(md("""
## 6.3 Kandidat dan Frequent Itemsets per Level

Ciri khas Apriori adalah jumlah kandidat yang harus dihitung. Grafik batang berikut membandingkan $|C_k|$ dan $|L_k|$ per level untuk setiap min support, dengan sumbu y berskala log.
"""))

cells.append(code("""
fig, axes = plt.subplots(1, len(CFG.MIN_SUPPORTS), figsize=(9.6, 3.4), sharey=True)
for ax, ms in zip(axes, CFG.MIN_SUPPORTS):
    lv = levels[levels["min_support"] == ms]
    x = lv["k"].to_numpy()
    ax.bar(x - 0.2, lv["kandidat"], 0.4, color=CFG.GRAY, label="kandidat $C_k$")
    ax.bar(x + 0.2, lv["frequent"], 0.4, color=CFG.BLUE, label="frequent $L_k$")
    for k in x[lv["frequent"].to_numpy() == 0]:
        ax.annotate("0", (k + 0.2, 1), ha="center", va="bottom", fontsize=8, color=CFG.INK_2)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xlabel("k")
    ax.set_title(f"min support {pct_id(ms * 100)}", fontsize=9.5)
id_ticks(axes[0], "y")
axes[0].set_ylabel("jumlah itemset")
axes[0].legend(loc="upper right", fontsize=8)
fig.suptitle("Kandidat dan frequent itemsets per level Apriori", x=0.01, y=1.03, ha="left", fontweight="bold")
save_fig(fig, "t4_apriori_kandidat_level.png")
"""))

cells.append(md(r"""
#### Insights

> 1. Pada 0,1% terdapat 574 item frequent, sehingga $C_2$ berisi seluruh $574 \times 573 / 2 = 164.451$ pasangan. Prune tidak dapat membuang apa pun di level 2 karena setiap subset berukuran satu sudah frequent.
> 2. Hanya 393 pasangan (0,24%) yang ternyata frequent, dan level 2 menjadi level termahal, hampir separuh total waktu.
> 3. Mulai level 3 prune bekerja efektif. Dari 393 pasangan hanya terbentuk 1.228 kandidat, dan persentase kandidat yang frequent naik dari 28% di level 3 menjadi 69% di level 5.
> 4. Pada min support yang lebih tinggi, $L_1$ jauh lebih kecil (66, 29, dan 6 item), sehingga $C_2$ ikut mengecil secara kuadratik (2.145, 406, dan 15). Waktu kemudian didominasi level 1, yaitu pemindaian pertama 1,8 juta transaksi beserta pemangkasan dan penggabungannya, yang biayanya hampir tetap untuk semua min support.
> 5. Penurunan min support dari 2% ke 0,1% menaikkan $|L_1|$ sekitar 96 kali, tetapi $|C_2|$ naik sekitar 11.000 kali. Inilah sumber biaya utama Apriori yang dibandingkan dengan FP-Growth pada `06_performance`.
"""))

cells.append(md("""
## 6.4 Kombinasi Venue yang Paling Sering Muncul Bersama

Pasangan dan triple teratas diambil dari hasil min support 0,1%. Kolom `bertahan_sampai` menunjukkan min support tertinggi tempat kombinasi tersebut masih frequent.
"""))

cells.append(code("""
base = frames[min(CFG.MIN_SUPPORTS)]

def survives(itemset):
    kept = [ms for ms in CFG.MIN_SUPPORTS if frozenset(itemset) in results[ms].itemsets]
    return pct_id(max(kept) * 100)

pairs = base[base["length"] == 2].head(CFG.TOP_K).copy()
triples = base[base["length"] == 3].head(CFG.TOP_K).copy()
for t in (pairs, triples):
    t["bertahan_sampai"] = t["itemset"].map(survives)
save_table(pairs[["names", "count", "support", "bertahan_sampai"]], "t4_apriori_pasangan_teratas.csv", index=False)
save_table(triples[["names", "count", "support", "bertahan_sampai"]], "t4_apriori_triple_teratas.csv", index=False)
display(pairs[["names", "count", "support", "bertahan_sampai"]].style.format({"support": "{:.4%}"}))
display(triples[["names", "count", "support", "bertahan_sampai"]].style.format({"support": "{:.4%}"}))
"""))

cells.append(md("""
#### Insights

> 1. Pasangan dan triple teratas sama dengan `04_fpgrowth`.
> 2. Pasangan teratas membentuk kelompok bidang, yaitu machine learning (ICML + NeurIPS, ICLR + NeurIPS, ICLR + ICML), computer vision (CVPR + ICCV, CVPR + ECCV), NLP (ACL + EMNLP), dan robotika (ICRA + IROS).
> 3. ICML + NeurIPS adalah satu-satunya pasangan yang masih frequent pada 1%, dan ICLR + ICML + NeurIPS (10.413 author) satu-satunya triple yang masih frequent pada 0,5%.
> 4. Analisis keterhubungan venue dan itemset terpanjang ada pada `04_fpgrowth` dan tidak diulang di sini karena hasilnya identik.
"""))

# ---------------------------------------------------------------------------
# 7. Interpretasi
# ---------------------------------------------------------------------------
cells.append(section("Interpretasi Pola", "7"))

cells.append(md("""
#### Insights

> 1. Frequent itemsets Apriori identik dengan FP-Growth, sehingga interpretasi polanya sama dengan `04_fpgrowth`. Kombinasi venue yang frequent hampir seluruhnya terjadi di dalam satu bidang atau di antara bidang yang bertetangga dekat.
> 2. NeurIPS menjadi penghubung inti AI, machine learning, dan computer vision, sedangkan venue populer seperti EMBC, IGARSS, dan HCI hampir tidak membentuk pasangan frequent.
> 3. Ekor panjang data DBLP membuat banyak venue lolos sebagai 1-itemset pada 0,1%, tetapi sangat sedikit pasangan yang lolos. Ini kasus terburuk bagi Apriori karena kandidat level 2 tumbuh kuadratik terhadap $|L_1|$, sementara 99,76% di antaranya tidak frequent. Sebaliknya, karena pasangan frequent sedikit dan terkumpul di beberapa bidang, prune pada level 3 ke atas membuang hampir semua kombinasi sehingga level berikutnya murah.
> 4. Waktu yang tercatat sudah memakai pra-pemrosesan yang sama dengan FP-Growth, yaitu pemangkasan item, pelewatan transaksi pendek, dan penggabungan transaksi identik yang memadatkan 536.543 transaksi berisi minimal dua item frequent menjadi 315.694 transaksi unik pada 0,1%. Pemilihan cara penghitungan kandidat per transaksi juga diperlukan, karena transaksi terpanjang (187 item frequent pada 0,1%) membuat enumerasi subset meledak. Perbandingan waktu dengan FP-Growth secara berulang dilakukan pada `06_performance`.
> 5. Keterbatasan data sama dengan `04_fpgrowth`. Item adalah seri venue berdasarkan key DBLP, identitas author mengikuti disambiguasi DBLP, support menghitung author bukan paper, dan transaksi author-based menggabungkan seluruh 2015-2025.
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
