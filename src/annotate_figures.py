"""Membuat versi beranotasi (highlight merah + insight) dari gambar mentah notebook.

Masukan : outputs/figures/*.png (mentah, dari notebook)
Keluaran: outputs/figures/annotated/*.png (mentah tidak diubah)
Jalankan: python3 src/annotate_figures.py
"""
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "outputs" / "figures"
OUT = RAW / "annotated"
OUT.mkdir(exist_ok=True)
HL = RAW / "highlight"
HL.mkdir(exist_ok=True)

import matplotlib
FONT = str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf")
FONT_B = str(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSans-Bold.ttf")

RED = (214, 39, 40)
BLUE = (42, 120, 214)
BLUE_L = (158, 197, 244)
ORANGE = (235, 104, 52)
NAVY = (16, 66, 129)
PALE = (205, 226, 251)


def mask_of(img, rgb, tol=22):
    a = np.asarray(img.convert("RGB")).astype(int)
    return (np.abs(a - np.array(rgb)).sum(axis=2) <= tol)


def components(mask, min_area=200):
    labeled, n = ndimage.label(mask)
    boxes = []
    for i, sl in enumerate(ndimage.find_objects(labeled), start=1):
        area = int((labeled[sl] == i).sum())
        if area >= min_area:
            y, x = sl
            boxes.append((x.start, y.start, x.stop, y.stop, area))
    return sorted(boxes, key=lambda b: b[4], reverse=True)


def box(draw, b, pad=10, width=6):
    x0, y0, x1, y1 = b[:4]
    draw.rounded_rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], radius=10, outline=RED, width=width)


def label(draw, xy, text, size, anchor="la", bold=True):
    font = ImageFont.truetype(FONT_B if bold else FONT, size)
    x, y = xy
    l, t, r, b = draw.textbbox((x, y), text, font=font, anchor=anchor)
    draw.rounded_rectangle([l - 8, t - 5, r + 8, b + 5], radius=8, fill=(255, 255, 255), outline=RED, width=3)
    draw.text((x, y), text, font=font, fill=RED, anchor=anchor)


def annotate(name, shapes=None, labels=None, insight=None):
    img = Image.open(RAW / f"{name}.png").convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    for b in shapes or []:
        box(draw, b, width=max(5, w // 330))
    for xy, text, anchor in labels or []:
        label(draw, xy, text, max(24, w // 62), anchor)
    img.save(HL / f"{name}.png")
    if insight:
        size = max(26, w // 62)
        font = ImageFont.truetype(FONT, size)
        chars = max(30, int(w / (size * 0.58)))
        text = textwrap.fill("Insight: " + insight, width=chars)
        tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        l, t, r, b = tmp.multiline_textbbox((0, 0), text, font=font, spacing=8)
        pad = size
        canvas = Image.new("RGB", (w, h + (b - t) + pad * 3), (252, 252, 251))
        canvas.paste(img, (0, 0))
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle([pad // 2, h + pad // 2, w - pad // 2, h + (b - t) + pad * 2.2], radius=14, fill=(227, 239, 252))
        d.multiline_text((pad, h + pad), text, font=font, fill=(11, 11, 11), spacing=8)
        img = canvas
    img.save(OUT / f"{name}.png")
    print("ok", name, img.size)


def largest(mask, k=1, min_area=200, region=None):
    m = mask.copy()
    if region:
        x0, y0, x1, y1 = region
        keep = np.zeros_like(m)
        keep[int(y0):int(y1), int(x0):int(x1)] = True
        m &= keep
    return components(m, min_area)[:k]


def get(name):
    return Image.open(RAW / f"{name}.png").convert("RGB")


# 1. Jenis publikasi: kotak merah pada inproceedings
img = get("t1_jenis_publikasi"); w, h = img.size
b = largest(mask_of(img, BLUE), 1, 2000)[0]
annotate("t1_jenis_publikasi", [b], None,
         "inproceedings hanya 30,5% isi dump; separuhnya (2.004.202 record) terbit 2015 sampai 2025 dan menjadi bahan analisis.")

# 2. Publikasi per tahun: 2025 belum lengkap
img = get("t1_publikasi_per_tahun"); w, h = img.size
m = mask_of(img, BLUE_L, 30)
m = ndimage.binary_closing(m, iterations=6)
b = largest(m, 1, 3000, region=(w * 0.8, 0, w, h * 0.8))[0]
annotate("t1_publikasi_per_tahun", [b], [((b[0] - 10, b[1] - 40), "2025 belum lengkap", "rb")],
         "Naik 3,2% per tahun sampai 2024. Penurunan 2025 adalah efek data belum lengkap (konferensi dua tahunan dan yang belum terindeks), bukan penurunan aktivitas.")

# 3. Distribusi ukuran venue
annotate("t1_distribusi_ukuran_venue", None, None,
         "231 dari 4.373 venue (5,3%) menghasilkan separuh publikasi; median hanya 134 paper, jauh di bawah rata-rata 457.")

# 4. Produktivitas author: 11+ paper
img = get("t1_produktivitas_author"); w, h = img.size
bs = largest(mask_of(img, NAVY, 20), 2, 4000)
annotate("t1_produktivitas_author", bs, None,
         "8,3% author (11+ paper) menyumbang 52,6% pasangan paper-author, sedangkan 51,4% author hanya menulis satu paper.")

# 5. Top 10 publikasi: NeurIPS
img = get("t2_top10_publikasi"); w, h = img.size
bars = sorted(largest(mask_of(img, BLUE), 12, 3000), key=lambda b: b[1])
annotate("t2_top10_publikasi", [bars[0]], None,
         "NeurIPS teratas dengan 25.455 paper; 8 dari 10 konferensi ini juga masuk 10 besar author unik.")

# 6. Top 10 author unik: ICML dan IROS (hanya masuk di ukuran ini)
img = get("t2_top10_author"); w, h = img.size
light = [b for b in largest(mask_of(img, BLUE_L, 20), 6, 3000) if b[2] - b[0] > w * 0.2]
annotate("t2_top10_author", light, None,
         "ICML dan IROS menggantikan CHI dan ICC pada 10 besar author unik; NeurIPS tetap nomor satu (57.800 author unik).")

# 7. Tren: panel NeurIPS
img = get("t2_tren_top10"); w, h = img.size
m = mask_of(img, BLUE, 30)
b = largest(m, 1, 300, region=(0, h * 0.1, w * 0.2, h * 0.55))[0]
annotate("t2_tren_top10", [(int(w * 0.012), b[1] - 60, int(w * 0.2), int(h * 0.50), 0)], None,
         "NeurIPS, EMNLP, CVPR, dan AAAI tumbuh 10,2x, 7,6x, 4,8x, dan 3,6x; HCI datar; ICC dan EMBC menurun.")

# 8. CAGR: batang menurun
img = get("t2_cagr_top10"); w, h = img.size
bs = largest(mask_of(img, ORANGE, 30), 3, 800, region=(0, 0, w, h * 0.85))
bs = [b for b in bs if b[2] - b[0] > w * 0.04][:2]
annotate("t2_cagr_top10", bs, None,
         "Empat konferensi AI dan NLP tumbuh jauh di atas seluruh dataset (+3,2% per tahun); ICC dan EMBC justru menurun.")

# 9. Heatmap
annotate("t2_heatmap_tren_top20", None, None,
         "Konferensi machine learning dan NLP (NeurIPS, ICML, EMNLP) naik 7 sampai 8 kali dari level awal; CDC, ICC, EMBC, dan IECON di bawah level awal.")

# 10. Slope: ICC
img = get("t2_slope_peringkat"); w, h = img.size
m = mask_of(img, ORANGE, 30)
m[:, : int(w * 0.6)] = False
ys, xs = np.nonzero(m)
j = ys.argmax()
ex, ey = xs[j], ys[j]
annotate("t2_slope_peringkat", [(ex - 25, ey - 25, ex + 140, ey + 25, 0)], None,
         "Dua peringkat sangat selaras (Spearman 0,987); ICC turun paling jauh (peringkat 10 menjadi 19), AAAI dan EMBC naik.")

# 11. Scatter: klaster 10 besar
img = get("t2_scatter_publikasi_author"); w, h = img.size
m = mask_of(img, BLUE, 30)
keep = np.zeros_like(m); keep[: int(h * 0.35), int(w * 0.75):] = True
ys, xs = np.nonzero(m & keep)
annotate("t2_scatter_publikasi_author", [(xs.min(), ys.min(), xs.max(), ys.max(), 0)], None,
         "Hampir semua konferensi berada di sekitar 2 author unik per paper; konferensi 10 besar (biru) berada di ujung kanan atas.")

# 12. Distribusi ukuran transaksi: 1 item
img = get("t3_distribusi_item_per_transaksi"); w, h = img.size
bs = largest(mask_of(img, PALE, 12), 3, 5000)
bs = [b for b in bs if b[3] < h * 0.8][:2]
annotate("t3_distribusi_item_per_transaksi", bs, None,
         "Mayoritas transaksi hanya berisi 1 item (58,4% pada author-based dan 71,0% pada author-year-based).")

# 13. Item frequent per ambang
annotate("t3_item_frequent_per_min_support", None, None,
         "Hanya 574 dari 4.373 venue lolos 0,1% dan 6 venue lolos 2%; author-year-based meloloskan lebih sedikit item pada ambang yang sama.")

# 14. Support pasangan: pasangan teratas
img = get("t3_support_pasangan_dua_representasi"); w, h = img.size
bl = sorted(largest(mask_of(img, BLUE, 30), 12, 150), key=lambda b: b[1])
orr = sorted(largest(mask_of(img, ORANGE, 30), 12, 150), key=lambda b: b[1])
bl = [b for b in bl if b[3] - b[1] < 60 and b[1] < h * 0.8]
orr = [b for b in orr if b[3] - b[1] < 60 and b[1] < h * 0.8]
top_b, top_o = bl[0], orr[0]
annotate("t3_support_pasangan_dua_representasi",
         [(min(top_o[0], top_b[0]), min(top_o[1], top_b[1]), max(top_o[2], top_b[2]), max(top_o[3], top_b[3]), 0)], None,
         "Support pasangan turun sekitar 0,3 kali pada author-year-based, tetapi urutan teratas hampir sama: ICML + NeurIPS tetap nomor satu.")

# 15. Konsentrasi beban
annotate("t3_konsentrasi_beban_kombinasi", None, None,
         "0,1% transaksi terbesar menanggung sekitar 28% beban kombinasi pada author-based (1% terbesar: 56%).")
