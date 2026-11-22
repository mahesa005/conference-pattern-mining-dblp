"""Membangkitkan grafik TikZ untuk laporan dari CSV hasil notebook.

Keluaran: laporan/images/fig-*.tex (isi tikzpicture), diinput oleh bab laporan.
Jalankan: .venv/bin/python src/build_report_figures.py
Atau hanya gambar tertentu: .venv/bin/python src/build_report_figures.py fig_t4_itemset_ukuran fig_t5_arah_rules
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "outputs" / "tables"
OUT = ROOT / "laporan" / "images"

BLUE, BLUE_L, ORANGE, GRAY = "bluemain", "bluelight", "orangemain", "graymid"
RAMP7 = ["CDE2FB", "9EC5F4", "6DA7EC", "3987E5", "2A78D6", "1C5CAB", "104281"]
RAMP5 = ["86B6EF", "5598E7", "2A78D6", "1C5CAB", "104281"]


def idn(value, digits=0):
    text = f"{value:,.{digits}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value, digits=1):
    return idn(value, digits) + "\\%"


def esc(text):
    return str(text).replace("&", "\\&").replace("%", "\\%").replace("#", "\\#").replace("_", "\\_")


def rgb(hex_code):
    """Nama warna yang didefinisikan pada preamble Laporan.tex (hxRRGGBB)."""
    return "hx" + hex_code


def legend(items, x, y, max_width=13.4, size=0.26):
    """items: (jenis, warna, label). Mengembalikan baris TikZ dan koordinat y terbawah."""
    lines = [f"\\node[anchor=west,inner sep=0pt,font=\\scriptsize\\bfseries] at ({x},{y}) {{Legenda:}};"]
    cx, cy = x + 1.55, y
    for kind, color, label in items:
        width = size + 0.2 + 0.14 * len(label) + 0.45
        if cx + width > x + max_width:
            cx, cy = x + 1.55, cy - 0.5
        if kind == "rect":
            lines.append(f"\\fill[{color}] ({cx},{cy - size / 2}) rectangle ({cx + size},{cy + size / 2});")
        elif kind == "hatch":
            lines.append(f"\\fill[white] ({cx},{cy - size / 2}) rectangle ({cx + size},{cy + size / 2});")
            lines.append(f"\\fill[pattern=north east lines,pattern color={color}] ({cx},{cy - size / 2}) rectangle ({cx + size},{cy + size / 2});")
            lines.append(f"\\draw[{color},line width=0.5pt] ({cx},{cy - size / 2}) rectangle ({cx + size},{cy + size / 2});")
        elif kind == "dot":
            lines.append(f"\\fill[{color}] ({cx + size / 2},{cy}) circle (0.1);")
        elif kind == "hollow":
            lines.append(f"\\draw[{color},fill=white,line width=0.9pt] ({cx + size / 2},{cy}) circle (0.1);")
        elif kind == "line":
            lines.append(f"\\draw[{color},line width=1.4pt] ({cx},{cy}) -- ({cx + size},{cy});")
        elif kind == "dash":
            lines.append(f"\\draw[{color},dashed,line width=1pt] ({cx},{cy}) -- ({cx + size},{cy});")
        lines.append(f"\\node[anchor=west,inner sep=0pt,font=\\scriptsize] at ({cx + size + 0.12},{cy}) {{{label}}};")
        cx += width
    return lines, cy


def write(name, body):
    text = "\\begin{tikzpicture}[font=\\scriptsize]\n" + "\n".join(body) + "\n\\end{tikzpicture}\n"
    (OUT / f"fig-{name}.tex").write_text(text, encoding="utf-8")
    print("ditulis", f"fig-{name}.tex", f"({len(text.splitlines())} baris)")


# ----------------------------------------------------------------------------
def fig_jenis_publikasi():
    df = pd.read_csv(TAB / "t1_jenis_publikasi.csv", index_col=0).sort_values("seluruh_dblp", ascending=False)
    x0, scale, row_h = 2.7, 1.15, 0.55
    bottom = -row_h * (len(df) - 0.4)
    body = []
    for decade, label in ((0, "1"), (2, "100"), (4, "10 rb"), (6, "1 jt")):
        x = x0 + decade * scale
        body.append(f"\\draw[grayline] ({x},{row_h * 0.6}) -- ({x},{bottom});")
        body.append(f"\\node[below,inner sep=2pt] at ({x},{bottom}) {{{label}}};")
    body.append(f"\\node[below,inner sep=2pt] at ({x0 + 3 * scale},{bottom - 0.4}) {{Jumlah record (skala logaritmik)}};")
    for i, (name, row) in enumerate(df.iterrows()):
        y = -i * row_h
        xa = x0 + np.log10(max(row["periode"], 1)) * scale
        xb = x0 + np.log10(row["seluruh_dblp"]) * scale
        used = name == "inproceedings"
        color = BLUE if used else GRAY
        font = "\\scriptsize\\bfseries" if used else "\\scriptsize"
        width = "1.6pt" if used else "1pt"
        dot = BLUE if used else "black!70"
        text = pct(row["porsi_periode_%"], 0)
        body.append(f"\\node[anchor=east,inner sep=1pt,font={font}] at ({x0 - 0.15},{y}) {{\\texttt{{{esc(name)}}}}};")
        body.append(f"\\draw[{color},line width={width}] ({xa},{y}) -- ({xb},{y});")
        body.append(f"\\draw[black!70,fill=white,line width=0.9pt] ({xb},{y}) circle (0.1);")
        body.append(f"\\fill[{dot}] ({xa},{y}) circle (0.1);")
        body.append(f"\\node[anchor=west,inner sep=2pt,font={font}] at ({xb + 0.15},{y}) {{{text}}};")
    items, ylow = legend([("hollow", "black!70", "seluruh dump"), ("dot", "black!70", "periode 2015--2025"),
                          ("line", BLUE, "jenis yang dipakai"), ("line", GRAY, "jenis lain")], 0, bottom - 1.3)
    note = f"\\node[anchor=west,inner sep=0pt,font=\\scriptsize] at (0,{ylow - 0.55}) {{Angka di kanan titik adalah porsi record yang terbit pada 2015--2025.}};"
    write("jenis-publikasi", body + items + [note])


def fig_publikasi_tahun():
    df = pd.read_csv(TAB / "t1_publikasi_per_tahun.csv", index_col=0)
    width, height, k = 0.72, 4.6, 4.6 / 250
    body = []
    for g in range(0, 251, 50):
        body.append(f"\\draw[grayline] (0,{g * k}) -- (11.4,{g * k});")
        body.append(f"\\node[left,inner sep=2pt] at (0,{g * k}) {{{g}}};")
    body.append(f"\\node[rotate=90] at (-0.85,{height / 2}) {{Publikasi (ribu)}};")
    trend = []
    for i, (year, row) in enumerate(df.iterrows()):
        x = 0.15 + i * 1.0
        value = row["publikasi"] / 1000
        if year < 2025:
            body.append(f"\\fill[{BLUE}] ({x},0) rectangle ({x + width},{value * k});")
        else:
            body.append(f"\\fill[white] ({x},0) rectangle ({x + width},{value * k});")
            body.append(f"\\fill[pattern=north east lines,pattern color={BLUE}] ({x},0) rectangle ({x + width},{value * k});")
            body.append(f"\\draw[{BLUE},line width=0.6pt] ({x},0) rectangle ({x + width},{value * k});")
        body.append(f"\\node[below,inner sep=2pt] at ({x + width / 2},0) {{{year}}};")
        label_color = "white" if year < 2025 else "black"
        body.append(f"\\node[{label_color},inner sep=1pt,font=\\tiny\\bfseries,anchor=south] at ({x + width / 2},0.08) {{{idn(value, 1)}}};")
        trend.append(f"({x + width / 2},{row['tren_linear'] / 1000 * k})")
    body.append("\\draw[black,dashed,line width=0.9pt] " + " -- ".join(trend) + ";")
    x2020 = 0.15 + 5 * 1.0 + width / 2
    body.append(f"\\draw[black!60] ({x2020},{171.8 * k + 0.05}) -- ({x2020},{205 * k});")
    body.append(f"\\node[above,inner sep=1pt] at ({x2020},{205 * k}) {{2020: $-$8,8\\%}};")
    body.append(f"\\node[anchor=west,inner sep=0pt,font=\\scriptsize\\bfseries,text={BLUE}] at (0.2,{height - 0.15}) {{CAGR 2015--2024: +3,2\\% per tahun}};")
    items, _ = legend([("rect", BLUE, "tahun lengkap"), ("hatch", BLUE, "2025 (data belum lengkap)"), ("dash", "black", "tren linear 2015--2024")], 0, -1.0)
    write("publikasi-tahun", body + items)


def hbar(name, rows, vmax, ticks, tick_label, xlabel, legend_items, label_w=3.0, width=5.6, row_h=0.6):
    k = width / vmax
    body = []
    for t in ticks:
        x = label_w + t * k
        body.append(f"\\draw[grayline] ({x},0.45) -- ({x},{-row_h * (len(rows) - 0.4)});")
        body.append(f"\\node[below,inner sep=2pt] at ({x},{-row_h * (len(rows) - 0.4)}) {{{tick_label(t)}}};")
    body.append(f"\\node[below,inner sep=2pt] at ({label_w + width / 2},{-row_h * (len(rows) - 0.4) - 0.45}) {{{xlabel}}};")
    for i, (label, value, dark, note) in enumerate(rows):
        y = -i * row_h
        body.append(f"\\node[anchor=east,inner sep=2pt] at ({label_w - 0.1},{y}) {{{label}}};")
        body.append(f"\\fill[{BLUE if dark else BLUE_L}] ({label_w},{y - 0.2}) rectangle ({label_w + value * k},{y + 0.2});")
        body.append(f"\\node[anchor=west,inner sep=2pt] at ({label_w + value * k + 0.05},{y}) {{{note}}};")
    items, _ = legend(legend_items, 0, -row_h * len(rows) - 1.3)
    write(name, body + items)


def fig_top10():
    stats = pd.read_csv(TAB / "t2_statistik_venue.csv", index_col=0)
    pub = stats.sort_values("rank_publikasi").head(10)
    aut = stats.sort_values("rank_author").head(10)
    shared = set(pub.index) & set(aut.index)
    rows = [(f"\\#{i + 1}\\;\\; {esc(r['nama'])}", r["publikasi"], v in shared,
             f"{idn(r['publikasi'])} | peringkat penulis \\#{int(r['rank_author'])}") for i, (v, r) in enumerate(pub.iterrows())]
    hbar("top10-publikasi", rows, 40000, [0, 10000, 20000, 30000], lambda t: idn(t / 1000), "Publikasi (ribu)",
         [("rect", BLUE, "juga masuk 10 besar ukuran lain"), ("rect", BLUE_L, "hanya masuk 10 besar ukuran ini")])
    rows = [(f"\\#{i + 1}\\;\\; {esc(r['nama'])}", r["author_unik"], v in shared,
             f"{idn(r['author_unik'])} | peringkat publikasi \\#{int(r['rank_publikasi'])}") for i, (v, r) in enumerate(aut.iterrows())]
    hbar("top10-author", rows, 80000, [0, 20000, 40000, 60000], lambda t: idn(t / 1000), "Penulis unik (ribu)",
         [("rect", BLUE, "juga masuk 10 besar ukuran lain"), ("rect", BLUE_L, "hanya masuk 10 besar ukuran ini")])


def fig_cagr():
    g = pd.read_csv(TAB / "t2_tren_top10.csv", index_col=0).sort_values("cagr_%", ascending=False)
    overall = (213328 / 160800) ** (1 / 9) * 100 - 100
    k, x0, row_h = 0.16, 5.2, 0.6
    body = []
    for t in (-5, 0, 10, 20, 30):
        x = x0 + t * k
        body.append(f"\\draw[grayline] ({x},0.45) -- ({x},{-row_h * (len(g) - 0.4)});")
        body.append(f"\\node[below,inner sep=2pt] at ({x},{-row_h * (len(g) - 0.4)}) {{{'$-$5' if t < 0 else t}}};")
    body.append(f"\\node[below,inner sep=2pt] at ({x0 + 12 * k},{-row_h * (len(g) - 0.4) - 0.45}) {{CAGR publikasi 2015--2024 (\\%)}};")
    for i, (venue, r) in enumerate(g.iterrows()):
        y = -i * row_h
        value = r["cagr_%"]
        color = BLUE if value >= 0 else ORANGE
        body.append(f"\\node[anchor=east,inner sep=2pt] at (1.6,{y}) {{{esc(r['nama'])}}};")
        body.append(f"\\fill[{color}] ({x0},{y - 0.2}) rectangle ({x0 + value * k},{y + 0.2});")
        sign = "+" if value >= 0 else "$-$"
        label = f"{sign}{idn(abs(value), 1)}\\% (x{idn(r['kali_lipat'], 1)})"
        if value >= 0:
            body.append(f"\\node[anchor=west,inner sep=2pt] at ({x0 + value * k + 0.05},{y}) {{{label}}};")
        else:
            body.append(f"\\node[anchor=east,inner sep=2pt] at ({x0 + value * k - 0.05},{y}) {{{label}}};")
    body.append(f"\\draw[black,dashed,line width=0.9pt] ({x0 + overall * k},0.45) -- ({x0 + overall * k},{-row_h * (len(g) - 0.4)});")
    body.append(f"\\draw[black!70,line width=0.5pt] ({x0},0.45) -- ({x0},{-row_h * (len(g) - 0.4)});")
    items, _ = legend([("rect", BLUE, "pertumbuhan positif"), ("rect", ORANGE, "penurunan"),
                       ("dash", "black", f"CAGR seluruh dataset (+{idn(overall, 1)}\\%)")], 0, -row_h * len(g) - 1.3)
    write("cagr-top10", body + items)


def fig_slope():
    df = pd.read_csv(TAB / "t2_perbandingan_peringkat.csv", index_col=0)
    xl, xr, step = 3.6, 8.6, 0.36
    body = [f"\\node[font=\\scriptsize\\bfseries,align=center] at ({xl},0.7) {{peringkat jumlah\\\\publikasi}};",
            f"\\node[font=\\scriptsize\\bfseries,align=center] at ({xr},0.7) {{peringkat jumlah\\\\penulis unik}};"]
    for venue, r in df.iterrows():
        a, b = int(r["rank_publikasi"]), int(r["rank_author"])
        color = BLUE if a > b else (ORANGE if a < b else GRAY)
        ya, yb = -a * step + step, -b * step + step
        body.append(f"\\draw[{color},line width=1.4pt] ({xl},{ya}) -- ({xr},{yb});")
        body.append(f"\\fill[{color}] ({xl},{ya}) circle (0.08); \\fill[{color}] ({xr},{yb}) circle (0.08);")
        body.append(f"\\node[anchor=east,inner sep=3pt] at ({xl},{ya}) {{{esc(r['nama'])}\\;\\#{a}}};")
        body.append(f"\\node[anchor=west,inner sep=3pt] at ({xr},{yb}) {{\\#{b}\\;{esc(r['nama'])}}};")
    bottom = -19 * step + step - 0.9
    items, _ = legend([("line", BLUE, "naik pada peringkat penulis unik"), ("line", ORANGE, "turun"), ("line", GRAY, "peringkat sama")], 0, bottom)
    write("slope-peringkat", body + items)


def fig_komposisi():
    table = pd.read_csv(TAB / "t3_distribusi_item_per_transaksi.csv", header=[0, 1], index_col=0)
    labels = list(table.index)
    body, width = [], 9.0
    for row, (name, text) in enumerate((("Author-based", "Author-based"), ("Author-year-based", "Author-year-based"))):
        y = -row * 1.35
        total = int(table[("transaksi", name)].sum())
        body.append(f"\\node[anchor=east,align=right,inner sep=2pt] at (3.0,{y}) {{{text}\\\\({idn(total)} transaksi)}};")
        left = 0.0
        for i, lab in enumerate(labels):
            share = float(table[("persen", name)].iloc[i])
            w = width * share / 100
            body.append(f"\\fill[{rgb(RAMP7[i])}] ({3.1 + left},{y - 0.4}) rectangle ({3.1 + left + w},{y + 0.4});")
            if share >= 5:
                color = "white" if i >= 4 else "black"
                body.append(f"\\node[{color},font=\\scriptsize] at ({3.1 + left + w / 2},{y}) {{{idn(share, 1)}\\%}};")
            left += w
    for t in (0, 20, 40, 60, 80, 100):
        x = 3.1 + width * t / 100
        body.append(f"\\node[below,inner sep=2pt] at ({x},-1.95) {{{t}}};")
    body.append(f"\\node[below,inner sep=2pt] at ({3.1 + width / 2},-2.4) {{Porsi transaksi (\\%)}};")
    items, _ = legend([("rect", rgb(RAMP7[i]), f"{lab} item") for i, lab in enumerate(labels)], 0, -3.6)
    write("komposisi-transaksi", body + items)


def waffle_counts(shares, total=100):
    exact = np.asarray(shares, dtype=float) / np.sum(shares) * total
    counts = np.floor(exact).astype(int)
    for i in np.argsort(-(exact - counts))[: total - counts.sum()]:
        counts[i] += 1
    return counts


def fig_waffle():
    t = pd.read_csv(TAB / "t1_produktivitas_author.csv", index_col=0)
    cell, gap = 0.36, 0.05
    body = []
    for panel, (col, title) in enumerate((("author_%", "Porsi penulis"), ("pasangan_%", "Porsi pasangan makalah-penulis"))):
        x0 = panel * 7.6
        counts = waffle_counts(t[col].to_numpy())
        body.append(f"\\node[anchor=west,font=\\scriptsize\\bfseries] at ({x0},0.6) {{{title} (1 kotak = 1\\%)}};")
        index = 0
        for tier, count in enumerate(counts):
            for _ in range(count):
                row, c = divmod(index, 10)
                x, y = x0 + c * (cell + gap), -row * (cell + gap)
                body.append(f"\\fill[{rgb(RAMP5[tier])}] ({x},{y}) rectangle ({x + cell},{y - cell});")
                index += 1
    heavy_author, heavy_pairs = t["author_%"].iloc[3:].sum(), t["pasangan_%"].iloc[3:].sum()
    body.append(f"\\node[anchor=north west,font=\\scriptsize\\bfseries,text width=6.8cm] at (0,-4.2) {{{pct(t['author_%'].iloc[0])} penulis hanya menulis 1 makalah}};")
    body.append(f"\\node[anchor=north west,font=\\scriptsize\\bfseries,text width=6.8cm] at (7.6,-4.2) {{{pct(heavy_author)} penulis (11 makalah atau lebih) menyumbang {pct(heavy_pairs)} pasangan}};")
    items, _ = legend([("rect", rgb(RAMP5[i]), f"{name.replace('paper', 'makalah')} ({idn(int(r['author']))} penulis)") for i, (name, r) in enumerate(t.iterrows())], 0, -5.5, max_width=14.0)
    write("waffle-author", body + items)


def dumbbell(name, rows, xmax, ticks, scale, xlabel, legend_items, label_w=2.9, row_h=0.55, fmt_value=None):
    body = []
    n = len(rows)
    for t in ticks:
        x = label_w + t * scale
        body.append(f"\\draw[grayline] ({x},0.4) -- ({x},{-row_h * (n - 0.4)});")
        body.append(f"\\node[below,inner sep=2pt] at ({x},{-row_h * (n - 0.4)}) {{{idn(t, 1) if t % 1 else idn(t)}}};")
    body.append(f"\\node[below,inner sep=2pt] at ({label_w + xmax * scale / 2},{-row_h * (n - 0.4) - 0.45}) {{{xlabel}}};")
    for i, (label, a, b, note_a, note_b) in enumerate(rows):
        y = -i * row_h
        xa, xb = label_w + a * scale, label_w + b * scale
        body.append(f"\\node[anchor=east,inner sep=2pt] at ({label_w - 0.1},{y}) {{{label}}};")
        body.append(f"\\draw[{GRAY},line width=1.4pt] ({xa},{y}) -- ({xb},{y});")
        body.append(f"\\fill[{BLUE}] ({xa},{y}) circle (0.1); \\fill[{ORANGE}] ({xb},{y}) circle (0.1);")
        body.append(f"\\node[anchor=west,inner sep=2pt,text={BLUE}] at ({xa + 0.12},{y}) {{{note_a}}};")
        body.append(f"\\node[anchor=east,inner sep=2pt,text={ORANGE}] at ({xb - 0.12},{y}) {{{note_b}}};")
    items, _ = legend(legend_items, 0, -row_h * n - 1.3)
    write(name, body + items)


def fig_dumbbells():
    s = pd.read_csv(TAB / "t3_support_item_top50.csv").head(15)
    prepared = [(esc(r["nama"]), r["support_author"], r["support_author_year"],
                 pct(r["support_author"], 2), pct(r["support_author_year"], 2)) for _, r in s.iterrows()]
    dumbbell("support-item", prepared, 3.6, [0, 1, 2, 3], 2.9, "Support (\\% transaksi yang memuat venue)",
             [("dot", BLUE, "author-based"), ("dot", ORANGE, "author-year-based")], label_w=2.0)
    p = pd.read_csv(TAB / "t3_pasangan_teratas_dua_representasi.csv")
    prepared = [(esc(r["pasangan venue"]), r["support_author_%"], r["support_author_year_%"],
                 idn(r["support_author_%"], 2) + "\\% (x" + idn(r["rasio_support"], 2) + ")",
                 idn(r["support_author_year_%"], 2) + "\\%") for _, r in p.iterrows()]
    dumbbell("support-pasangan", prepared, 1.3, [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2], 7.0, "Support pasangan venue (\\% transaksi)",
             [("dot", BLUE, "author-based (rasio terhadap author-year dalam kurung)"), ("dot", ORANGE, "author-year-based")], label_w=2.9)


def arrow(text):
    return esc(text).replace("→", "$\\Rightarrow$")


def fig_t4_itemset_ukuran():
    df = pd.read_csv(TAB / "t4_fpgrowth_ringkasan.csv")
    cols = [("k1", BLUE, "1 item"), ("k2", ORANGE, "2 item"), ("k3", BLUE_L, "3 item"), ("k4+", GRAY, "4 sampai 6 item")]
    height, vmax, bar, group = 4.6, 600, 0.55, 3.0
    k = height / vmax
    body = []
    for g in range(0, vmax + 1, 100):
        body.append(f"\\draw[grayline] (0,{g * k}) -- ({group * len(df)},{g * k});")
        body.append(f"\\node[left,inner sep=2pt] at (0,{g * k}) {{{idn(g)}}};")
    body.append(f"\\node[rotate=90] at (-0.9,{height / 2}) {{Jumlah \\textit{{frequent itemsets}}}};")
    for i, (_, r) in enumerate(df.iterrows()):
        x0 = 0.3 + i * group
        for j, (col, color, _) in enumerate(cols):
            x, v = x0 + j * bar, int(r[col])
            body.append(f"\\fill[{color}] ({x},0) rectangle ({x + bar * 0.9},{v * k});")
            body.append(f"\\node[above,inner sep=1pt,font=\\tiny] at ({x + bar * 0.45},{v * k}) {{{idn(v)}}};")
        label = pct(r["min_support"] * 100, 1).replace(",0\\%", "\\%")
        body.append(f"\\node[below,inner sep=2pt] at ({x0 + bar * 2},0) {{\\textit{{min\\_sup}} {label}}};")
        body.append(f"\\node[below,inner sep=2pt,text=black!60] at ({x0 + bar * 2},-0.4) {{total {idn(int(r['itemsets']))}}};")
    items, _ = legend([("rect", c, lab) for _, c, lab in cols], 0, -1.4)
    write("t4-itemset-ukuran", body + items)


def fig_t4_pasangan():
    p = pd.read_csv(TAB / "t4_fpgrowth_pasangan_teratas.csv")
    rows = [(esc(r["names"]), r["count"], r["bertahan_sampai"] == "1,0%",
             f"{idn(r['count'])} ({pct(r['support'] * 100, 2)})") for _, r in p.iterrows()]
    hbar("t4-pasangan", rows, 20000, [0, 5000, 10000, 15000, 20000], lambda t: idn(t / 1000),
         "Penulis yang menerbitkan di kedua konferensi (ribu)",
         [("rect", BLUE, "masih frequent pada min\\_sup 1\\%"), ("rect", BLUE_L, "frequent sampai min\\_sup 0,5\\%")], label_w=3.0)


def fig_t5_arah_rules():
    r = pd.read_csv(TAB / "t5_rules_satu_ke_satu_arah.csv")
    r["rule"] = r["rule"].str.replace("Conference on Designing Interactive Systems", "DIS", regex=False)
    rows = [(f"{arrow(x['rule'])} (\\textit{{lift}} {idn(x['lift'], 1)})", x["confidence"] * 100, x["confidence_balik"] * 100,
             pct(x["confidence"] * 100, 0), pct(x["confidence_balik"] * 100, 0)) for _, x in r.iterrows()]
    dumbbell("t5-arah-rules", rows, 80, [0, 20, 40, 60, 80], 0.1, "\\textit{Confidence} (\\%)",
             [("dot", BLUE, "$A \\Rightarrow B$ (arah rule)"), ("dot", ORANGE, "$B \\Rightarrow A$ (arah balik, di bawah 50\\%)")],
             label_w=4.4, row_h=0.42)


def fig_t5_lift_konferensi():
    c = pd.read_csv(TAB / "t5_support_vs_lift_consequent.csv")
    lo, hi, width, height = 0.5, 3.5, 10.0, 5.6

    def px(s):
        return (s * 100 - lo) / (hi - lo) * width

    def py(v):
        return v / 100 * height

    body = []
    for t in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
        body.append(f"\\draw[grayline] ({px(t / 100)},0) -- ({px(t / 100)},{height});")
        body.append(f"\\node[below,inner sep=2pt] at ({px(t / 100)},0) {{{idn(t, 1)}}};")
    for t in range(0, 101, 20):
        body.append(f"\\draw[grayline] (0,{py(t)}) -- ({width},{py(t)});")
        body.append(f"\\node[left,inner sep=2pt] at (0,{py(t)}) {{{t}}};")
    body.append(f"\\node[below,inner sep=2pt] at ({width / 2},-0.45) {{\\textit{{Support}} konferensi (\\% penulis)}};")
    body.append(f"\\node[rotate=90] at (-0.85,{height / 2}) {{Median \\textit{{lift}} rules yang menuju konferensi}};")
    labelled = {"NeurIPS", "CVPR", "AAAI", "ICASSP", "ACL", "ECCV", "ICCV", "CDC", "OFC", "INTERSPEECH", "WCNC"}
    for _, r in c.iterrows():
        x, y = px(r["support_konferensi"]), py(r["lift_median"])
        dark = r["konferensi"] in labelled
        body.append(f"\\fill[{BLUE if dark else BLUE_L}] ({x},{y}) circle (0.08);")
        if dark:
            body.append(f"\\node[anchor=west,inner sep=2pt] at ({x + 0.08},{y}) {{{esc(r['konferensi'])} ({idn(r['lift_median'], 1)})}};")
    body.append(f"\\node[anchor=north east,font=\\scriptsize\\bfseries] at ({width},{height}) {{Spearman $\\rho = -0{{,}}933$ (26 konferensi)}};")
    items, _ = legend([("dot", BLUE, "konferensi yang diberi label"), ("dot", BLUE_L, "konferensi lain")], 0, -1.3)
    write("t5-lift-konferensi", body + items)


def fig_t4_apriori_kandidat():
    lv = pd.read_csv(TAB / "t4_apriori_level.csv")
    lv = lv[lv["min_support"] == 0.001]
    height, decades, group, bar = 4.2, 6, 1.9, 0.75
    k = height / decades
    body = []
    for d in range(decades + 1):
        body.append(f"\\draw[grayline] (0,{d * k}) -- ({group * len(lv)},{d * k});")
        body.append(f"\\node[left,inner sep=2pt] at (0,{d * k}) {{{idn(10 ** d)}}};")
    body.append(f"\\node[rotate=90] at (-1.25,{height / 2}) {{Jumlah \\textit{{itemset}} (skala log)}};")
    for i, (_, r) in enumerate(lv.iterrows()):
        x0 = 0.2 + i * group
        for j, (col, color) in enumerate((("kandidat", GRAY), ("frequent", BLUE))):
            x, v = x0 + j * bar, int(r[col])
            y = np.log10(v) * k if v > 0 else 0
            body.append(f"\\fill[{color}] ({x},0) rectangle ({x + bar * 0.9},{y});")
            body.append(f"\\node[above,inner sep=1pt,font=\\tiny] at ({x + bar * 0.45},{y}) {{{idn(v)}}};")
        body.append(f"\\node[below,inner sep=2pt] at ({x0 + bar},0) {{$k = {int(r['k'])}$}};")
    items, _ = legend([("rect", GRAY, "kandidat $C_k$"), ("rect", BLUE, "\\textit{frequent} $L_k$")], 0, -1.0)
    write("t4-apriori-kandidat", body + items)


def fig_t6_waktu():
    raw = pd.read_csv(TAB / "t6_waktu_mentah.csv")
    height, vmax, group, bar = 4.2, 6, 3.0, 0.9
    k = height / vmax
    body = []
    for g in range(0, vmax + 1):
        body.append(f"\\draw[grayline] (0,{g * k}) -- ({group * 4},{g * k});")
        body.append(f"\\node[left,inner sep=2pt] at (0,{g * k}) {{{g}}};")
    body.append(f"\\node[rotate=90] at (-0.7,{height / 2}) {{Waktu (detik)}};")
    for i, (ms, runs) in enumerate(raw.groupby("min_support", sort=True)):
        x0 = 0.5 + i * group
        for j, algo in enumerate(("Apriori", "FP-Growth")):
            r = runs[runs["algorithm"] == algo].sort_values("seconds").iloc[1]  # run median dari tiga pengulangan
            x = x0 + j * (bar + 0.15)
            if algo == "Apriori":
                body.append(f"\\fill[{ORANGE}] ({x},0) rectangle ({x + bar},{r['seconds'] * k});")
            else:
                body.append(f"\\fill[{BLUE}] ({x},0) rectangle ({x + bar},{r['t_build'] * k});")
                body.append(f"\\fill[{BLUE_L}] ({x},{r['t_build'] * k}) rectangle ({x + bar},{r['seconds'] * k});")
            body.append(f"\\node[above,inner sep=1pt,font=\\tiny] at ({x + bar / 2},{r['seconds'] * k}) {{{idn(r['seconds'], 2)}}};")
        label = pct(ms * 100, 1).replace(",0\\%", "\\%")
        body.append(f"\\node[below,inner sep=2pt] at ({x0 + bar + 0.075},0) {{\\textit{{min\\_sup}} {label}}};")
    items, _ = legend([("rect", ORANGE, "Apriori (total)"), ("rect", BLUE, "FP-Growth: pembentukan FP-tree"),
                       ("rect", BLUE_L, "FP-Growth: penambangan")], 0, -1.0)
    write("t6-waktu", body + items)


FIGURES = [fig_jenis_publikasi, fig_publikasi_tahun, fig_top10, fig_cagr, fig_slope, fig_komposisi, fig_waffle,
           fig_dumbbells, fig_t4_itemset_ukuran, fig_t4_pasangan, fig_t5_arah_rules, fig_t5_lift_konferensi,
           fig_t4_apriori_kandidat, fig_t6_waktu]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = set(sys.argv[1:])
    for figure in FIGURES:
        if not wanted or figure.__name__ in wanted:
            figure()
