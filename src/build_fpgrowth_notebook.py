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

*Notebook 04: Frequent Pattern Mining dengan FP-Growth.*
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
4. [**Eksperimen Empat Min Support**](#4)
5. [**Validasi dengan mlxtend**](#5)
6. [**Analisis Frequent Itemsets**](#6)
7. [**Interpretasi Pola**](#7)
"""))

# ---------------------------------------------------------------------------
# 1. Introduction
# ---------------------------------------------------------------------------
cells.append(section("Introduction", "1"))

cells.append(md("""
## Overview

*Notebook ini mencari kombinasi konferensi yang sering muncul bersama dalam riwayat publikasi author. FP-Growth dijalankan pada author-based transactional database dari notebook `02_transactions`. Algoritma Apriori dikerjakan pada notebook `03_apriori`, dan perbandingan keduanya pada notebook `06_performance`.*
"""))

cells.append(md("""
## Aim

*Notebook ini bertujuan untuk:*

1. *menemukan frequent itemsets pada min support 0,1%, 0,5%, 1%, dan 2%.*
2. *memisahkan 1-, 2-, dan 3-itemsets, lalu menampilkan 10 itemsets dengan support tertinggi.*
3. *menganalisis pengaruh min support terhadap jumlah itemsets dan mengidentifikasi kombinasi konferensi yang paling sering muncul bersama.*
4. *menginterpretasikan pola yang ditemukan.*
"""))

cells.append(md(r"""
## Metric

***Support** itemset $X$ adalah proporsi transaksi yang memuat seluruh item pada $X$. Penyebutnya selalu seluruh transaksi author-based, yaitu 1.821.757, termasuk transaksi yang dilewati saat membangun FP-tree.*

$$\text{support}(X) = \frac{|\{t \in D : X \subseteq t\}|}{|D|}$$

*Itemset frequent jika support-nya minimal min support. Dalam hitungan transaksi, ambangnya adalah bilangan bulat terkecil $c$ dengan $c / |D| \ge \text{min\_sup}$.*
"""))

cells.append(md("""
## Approach

*FP-Growth memadatkan database menjadi FP-tree dalam dua pemindaian, lalu menambang pola secara rekursif dari conditional pattern base tanpa membangkitkan kandidat. Item yang tidak frequent dipangkas lebih dulu, transaksi dengan kurang dari dua item frequent tidak dimasukkan ke pohon (support 1-itemset tetap dari pemindaian pertama), dan waktu pembentukan pohon dilaporkan terpisah dari waktu penambangan.*

*Kode algoritma berada di modul `fpgrowth.py` agar dapat dipakai ulang oleh notebook berikutnya, dan sudah diuji dengan `pytest` (contoh buku teks, brute force, dan `mlxtend`). Isi modul ditampilkan pada bagian 3.*
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

Tabel panjang author-based diubah ke bentuk horizontal, yaitu list frozenset kode item per transaksi. Bentuk ini sama dengan masukan Apriori pada notebook `03_apriori`. Waktu pemuatan tidak termasuk pengukuran.
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

Seluruh isi modul `fpgrowth.py` ditampilkan di bawah. Setiap node FP-tree menyimpan `item`, `count`, `parent`, dan `children`, dan header table memetakan item ke daftar node-nya.
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
cells.append(section("Eksperimen Empat Min Support", "4"))

cells.append(md("""
FP-Growth dijalankan sekali untuk setiap min support. Waktu pembentukan pohon (`t_build`) dan waktu penambangan (`t_mine`) dicatat terpisah. Pengukuran berulang untuk perbandingan performa dilakukan pada notebook `06_performance`. FP-tree tidak disimpan setelah penambangan (`keep_tree=False`) agar memori cukup untuk validasi.
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
     "t_build_s": round(res.t_build, 3), "t_mine_s": round(res.t_mine, 3)}
    for ms, res in results.items()
])
save_table(summary, "t4_fpgrowth_ringkasan.csv", index=False)
summary
"""))

cells.append(md("""
#### Insights

> 1. Pada min support 0,1% ditemukan 1.514 frequent itemsets: 574 1-itemset, 393 pasangan, 348 triple, dan 199 itemset berukuran empat sampai enam.
> 2. Pada 0,5% tersisa 88 itemset dengan hanya satu triple, dan pada 1% tersisa 30 itemset dengan hanya satu pasangan.
> 3. Pada 2% hanya ada enam konferensi tunggal tanpa satu pun pasangan.
> 4. Jadi 3-itemset hanya ada pada 0,1% dan 0,5%, dan tidak ada sama sekali pada 1% dan 2%.
"""))

cells.append(md("""
## 6.2 Sepuluh Itemset dengan Support Tertinggi

Sepuluh teratas secara keseluruhan hampir pasti berisi 1-itemset, karena support sebuah itemset tidak pernah melebihi support item penyusunnya. Karena itu ditampilkan juga sepuluh teratas untuk itemset berukuran dua atau lebih.
"""))

cells.append(code("""
cols = ["names", "length", "count", "support"]
for ms, df in frames.items():
    top = df.head(CFG.TOP_K)[cols]
    top_k2 = df[df["length"] >= 2].head(CFG.TOP_K)[cols]
    save_table(top, f"t4_fpgrowth_top10_{tag(ms)}.csv", index=False)
    save_table(top_k2, f"t4_fpgrowth_top10_k2plus_{tag(ms)}.csv", index=False)
    print(f"\\nmin_sup {pct_id(ms * 100)}: semua ukuran")
    display(top.style.format({"support": "{:.4%}"}))
    print(f"min_sup {pct_id(ms * 100)}: ukuran >= 2 ({len(df[df['length'] >= 2])} itemset)")
    display(top_k2.style.format({"support": "{:.4%}"}))
"""))

cells.append(md("""
#### Insights

> 1. Sepuluh itemset teratas pada setiap min support selalu berupa konferensi tunggal, dipimpin NeurIPS (57.800 author, support 3,17%), CVPR (47.664), dan AAAI (46.437).
> 2. Tidak ada kombinasi yang masuk sepuluh besar. Pasangan teratas, ICML + NeurIPS, hanya memiliki 18.503 author (support 1,02%), lebih kecil dari konferensi ke-10, IROS (31.249 author).
> 3. Support pasangan itu sekitar sepertiga support NeurIPS sendiri.
"""))

cells.append(md("""
## 6.3 Pengaruh Min Support

Sumbu y memakai skala symlog agar jumlah nol tetap terlihat dan rentang ratusan sampai ribuan dapat dibandingkan.
"""))

cells.append(code("""
fig, ax = plt.subplots(figsize=(7.2, 3.8))
x = np.arange(len(CFG.MIN_SUPPORTS))
width = 0.2
for j, (col, color) in enumerate(zip(["k1", "k2", "k3", "k4+"], [CFG.BLUE, CFG.ORANGE, CFG.BLUE_LIGHT, CFG.GRAY])):
    vals = summary[col].to_numpy()
    bars = ax.bar(x + (j - 1.5) * width, vals, width, color=color, label=col)
    for b, v in zip(bars, vals):
        ax.annotate(fmt_id(v), (b.get_x() + b.get_width() / 2, max(v, 0.5)), ha="center", va="bottom", fontsize=7.5, color=CFG.INK_2)
ax.set_yscale("symlog", linthresh=1)
id_ticks(ax, "y")
ax.set_xticks(x, [pct_id(ms * 100) for ms in CFG.MIN_SUPPORTS])
ax.set_xlabel("min support")
ax.set_ylabel("jumlah frequent itemsets")
ax.set_title("Jumlah frequent itemsets per ukuran dan min support")
ax.legend(ncol=4, loc="upper right")
save_fig(fig, "t4_fpgrowth_jumlah_itemset.png")
"""))

cells.append(md("""
#### Insights

> 1. Dari 0,1% ke 0,5% jumlah itemset berkurang 17,2 kali (1.514 menjadi 88), dan dari 0,1% ke 2% berkurang 252 kali (1.514 menjadi 6).
> 2. Itemset berukuran besar hilang lebih dulu: ukuran empat ke atas hanya ada pada 0,1%, triple hilang setelah 0,5%, dan pasangan hilang setelah 1%.
> 3. Penyebabnya adalah ekor panjang data. Notebook `02_transactions` menunjukkan 58,4% transaksi author-based hanya berisi satu venue, sehingga hanya sebagian kecil transaksi yang dapat memuat kombinasi dan support kombinasi jauh di bawah support item penyusunnya.
> 4. Min support 0,1% adalah satu-satunya ambang yang menghasilkan pola kombinasi yang cukup kaya untuk dianalisis.
> 5. Pada 1% dan 2% hasilnya praktis hanya mengulang peringkat popularitas konferensi.
"""))

cells.append(md("""
## 6.4 Kombinasi Konferensi yang Paling Sering Muncul Bersama

Hasil pada min support 0,1% memuat seluruh hasil pada min support yang lebih tinggi, sehingga pasangan dan triple teratas diambil dari sana. Kolom `bertahan_sampai` menunjukkan min support tertinggi tempat kombinasi tersebut masih frequent.
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
save_table(pairs[["names", "count", "support", "bertahan_sampai"]], "t4_fpgrowth_pasangan_teratas.csv", index=False)
save_table(triples[["names", "count", "support", "bertahan_sampai"]], "t4_fpgrowth_triple_teratas.csv", index=False)
display(pairs[["names", "count", "support", "bertahan_sampai"]].style.format({"support": "{:.4%}"}))
display(triples[["names", "count", "support", "bertahan_sampai"]].style.format({"support": "{:.4%}"}))

fig, ax = plt.subplots(figsize=(7.2, 3.8))
plot = pairs.iloc[::-1]
ax.barh(plot["names"], plot["count"], color=CFG.BLUE)
for y, v in enumerate(plot["count"]):
    ax.annotate(fmt_id(v), (v, y), xytext=(3, 0), textcoords="offset points", va="center", fontsize=7.5, color=CFG.INK_2)
id_ticks(ax, "x")
ax.set_xlabel("jumlah author")
ax.set_title("Sepuluh pasangan konferensi teratas (min support 0,1%)")
save_fig(fig, "t4_fpgrowth_pasangan_teratas.png")
"""))

cells.append(md("""
#### Insights

> 1. Sepuluh pasangan teratas membentuk kelompok bidang yang jelas. Machine learning diwakili ICML + NeurIPS (18.503 author), ICLR + NeurIPS (17.852), dan ICLR + ICML (12.947). Computer vision diwakili CVPR + ICCV (15.441) dan CVPR + ECCV (13.752). NLP diwakili ACL + EMNLP (14.557), dan robotika diwakili ICRA + IROS (11.860).
> 2. NeurIPS muncul pada empat dari sepuluh pasangan teratas dan delapan dari sepuluh triple teratas, sehingga menjadi penghubung antara machine learning, computer vision, dan AI umum (AAAI).
> 3. ICML + NeurIPS adalah satu-satunya pasangan yang masih frequent pada 1%, dan ICLR + ICML + NeurIPS (10.413 author) adalah satu-satunya triple yang masih frequent pada 0,5%.
> 4. Pasangan lainnya hanya frequent sampai 0,5%, dan triple lainnya hanya sampai 0,1%.
"""))

cells.append(md("""
## 6.5 Keterhubungan dan Itemset Terpanjang

Konferensi yang populer belum tentu sering muncul bersama konferensi lain. Tabel pertama menghitung, untuk sepuluh konferensi dengan support tertinggi, jumlah pasangan frequent pada min support 0,1% yang memuatnya, persentase author yang hanya publish di konferensi itu, dan median jumlah konferensi per author. Tabel kedua menampilkan itemset terpanjang yang ditemukan.
"""))

cells.append(code("""
pair_items = base[base["length"] == 2]["itemset"]
degree = pd.Series([i for s in pair_items for i in s]).value_counts()
top_items = base[base["length"] == 1].head(CFG.TOP_K)
connect = pd.DataFrame({
    "konferensi": top_items["names"].to_numpy(),
    "author": top_items["count"].to_numpy(),
    "pasangan_frequent": [int(degree.get(s[0], 0)) for s in top_items["itemset"]],
})
breadth = [np.fromiter((len(t) for t in transactions if s[0] in t), dtype=np.int32) for s in top_items["itemset"]]
connect["author_hanya_di_sini_pct"] = [round(float((b == 1).mean()) * 100, 1) for b in breadth]
connect["median_konferensi_per_author"] = [float(np.median(b)) for b in breadth]
save_table(connect, "t4_fpgrowth_keterhubungan_top10.csv", index=False)
print(f"Item yang muncul pada minimal satu pasangan frequent: {degree.size} dari {(base['length'] == 1).sum()} item frequent")
display(connect)

longest = base[base["length"] >= 5][["names", "length", "count", "support"]]
save_table(longest, "t4_fpgrowth_itemset_terpanjang.csv", index=False)
venue_freq = pd.Series([v for s in longest["names"] for v in s.split(" + ")]).value_counts()
print(f"Itemset berukuran 5 atau lebih: {len(longest)}, melibatkan {venue_freq.size} konferensi")
print(venue_freq.to_string())
display(longest[longest["length"] == longest["length"].max()].style.format({"support": "{:.4%}"}))
display(longest[longest["length"] == 5].head(CFG.TOP_K // 2).style.format({"support": "{:.4%}"}))
"""))

cells.append(md("""
#### Insights

> 1. Hanya 105 dari 574 konferensi frequent yang muncul pada minimal satu pasangan frequent, sehingga popularitas tidak sama dengan keterhubungan.
> 2. AAAI (44 pasangan), NeurIPS (42), ICASSP (41), dan CVPR (34) terhubung luas. Sebaliknya, EMBC dan IGARSS, yang termasuk sepuluh konferensi terbesar, masing-masing hanya muncul pada empat pasangan, dan HCI hanya pada satu pasangan.
> 3. Author EMBC, HCI, dan IGARSS biasanya hanya publish di satu atau dua konferensi (median 2, 2, dan 1), dan 37,4%, 40,8%, serta 54,2% di antaranya tidak pernah publish di konferensi lain. Yang publish di tempat lain tersebar ke banyak konferensi berbeda, sehingga tidak ada pasangan yang mencapai 1.822 author.
> 4. Author NeurIPS dan ICASSP biasanya publish di enam konferensi, dan hanya 11,6% serta 10,6% yang publish di satu konferensi saja.
> 5. Itemset terpanjang berisi enam konferensi, yaitu AAAI + CVPR + ECCV + ICCV + ICLR + NeurIPS (2.005 author) dan dua itemset lain dengan count di atas 1.800. Seluruh 40 itemset berukuran lima atau enam hanya melibatkan 14 konferensi, dan NeurIPS ada pada 35 di antaranya, sehingga pola panjang hanya muncul di inti AI, machine learning, dan computer vision.
"""))

# ---------------------------------------------------------------------------
# 7. Interpretasi
# ---------------------------------------------------------------------------
cells.append(section("Interpretasi Pola", "7"))

cells.append(md("""
#### Insights

> 1. Kombinasi konferensi yang frequent hampir seluruhnya terjadi di dalam satu bidang (machine learning, computer vision, NLP, robotika) atau di antara bidang yang bertetangga dekat, yaitu machine learning dengan computer vision dan AI umum. Hasil ini tidak membuktikan bahwa author jarang berpindah bidang, karena kombinasi lintas bidang dapat banyak secara total tetapi tersebar ke banyak pasangan kecil yang tidak lolos ambang.
> 2. NeurIPS, ICML, ICLR, AAAI, CVPR, ICCV, dan ECCV adalah satu-satunya kelompok yang menghasilkan itemset berukuran lima dan enam, dan NeurIPS menjadi titik temu kelompok tersebut.
> 3. Konferensi besar seperti EMBC, IGARSS, dan HCI hampir tidak membentuk pasangan frequent, sedangkan ICASSP terhubung dengan 41 konferensi lain. Support pasangan yang tinggi juga dapat muncul hanya karena kedua konferensinya besar, sehingga kekuatan asosiasi diukur dengan lift pada notebook `05_rules`.
> 4. Hanya min support 0,1% yang menghasilkan pola kombinasi yang cukup kaya, sehingga notebook `05_rules` memakai hasil 0,1% sebagai dasar utama.
>
> **Keterbatasan**
>
> 1. Item adalah seri konferensi berdasarkan key DBLP. Beberapa acara dipecah DBLP menjadi konferensi utama dan workshop dengan key berbeda, misalnya `iccv` (ICCV) dan `iccvw` (ICCV Workshops), sehingga author yang hanya publish di workshop tidak terhitung pada konferensi utamanya. Key dengan singkatan sama, misalnya `icis`, `ACISicis`, dan `icis2`, adalah konferensi yang memang berbeda dan benar dipisah.
> 2. Identitas author mengikuti disambiguasi DBLP. Dua orang dengan nama sama dapat tergabung, dan satu orang dapat tercatat dengan dua nama.
> 3. Support menghitung author, bukan paper. Author yang menerbitkan satu paper dan author yang menerbitkan puluhan paper di konferensi yang sama dihitung sama.
> 4. Transaksi author-based menggabungkan seluruh 2015-2025, sehingga dua konferensi dapat muncul bersama walaupun dipakai pada tahun yang berbeda. Pengaruh waktu dapat dianalisis dengan author-year-based database.
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
