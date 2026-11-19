#!/usr/bin/env python3
"""Fotoğraf + maske -> hizalı cutout katmanları (frame: "cutout", "registered": true için).

  layer_prep.py foto.jpg maske.png -o assets/img/s04 [--crop x0,y0,x1,y1] [--inpaint] [--color-bg] [--bw-fg]

Çıktılar (hepsi aynı piksel boyutunda):
  <o>_bg.jpg  arka plan: siyah-beyaz + halftone (--color-bg ile renkli kalır)
  <o>_fg.png  konu: renkli, alfa kanallı (--bw-fg ile siyah-beyaz)
  <o>_ol.png  yalnızca beyaz kontur halkası (AE'de silinerek "çizilir")
--inpaint: konu sallanacak / yer değiştirecekse arka plandaki kopyasını doldurur (opencv gerekir).
Maske: Magnific images_segment (SAM) çıktısı gibi siyah zemin / beyaz konu.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument("photo"); ap.add_argument("mask"); ap.add_argument("-o", "--out", required=True)
ap.add_argument("--crop"); ap.add_argument("--inpaint", action="store_true")
ap.add_argument("--color-bg", action="store_true"); ap.add_argument("--bw-fg", action="store_true")
ap.add_argument("--outline", type=int, default=11); ap.add_argument("--dim", type=float, default=0.78)
ap.add_argument("--halftone", default=str(Path(__file__).resolve().parent.parent / "assets/doku/halftone.jpg"))
a = ap.parse_args()
im = Image.open(a.photo).convert("RGB"); m = Image.open(a.mask).convert("L").resize(im.size)
if a.crop:
    box = tuple(int(v) for v in a.crop.split(",")); im = im.crop(box); m = m.crop(box)
m = m.point(lambda v: 255 if v > 127 else 0)
bg = im
if a.inpaint:
    import cv2, numpy as np
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR); mk = np.array(m.filter(ImageFilter.MaxFilter(31)))
    small = cv2.resize(arr, None, fx=0.5, fy=0.5); mks = cv2.resize(mk, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
    r = cv2.GaussianBlur(cv2.resize(cv2.inpaint(small, mks, 7, cv2.INPAINT_TELEA), (arr.shape[1], arr.shape[0])), (0, 0), 6)
    bg = Image.fromarray(cv2.cvtColor(np.where(mk[..., None] > 0, r, arr), cv2.COLOR_BGR2RGB))
if a.color_bg:
    bgo = ImageEnhance.Brightness(bg).enhance(0.9)
else:
    g = ImageEnhance.Brightness(ImageEnhance.Contrast(ImageOps.grayscale(bg)).enhance(1.15)).enhance(a.dim)
    if Path(a.halftone).exists():
        ht = ImageOps.fit(Image.open(a.halftone).convert("L"), g.size).point(lambda v: int(90 + v * 165 / 255))
        g = ImageChops.multiply(g, ht)
    bgo = g.convert("RGB")
bgo.save(a.out + "_bg.jpg", quality=92)
src = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.15).convert("RGB") if a.bw_fg else ImageEnhance.Color(im).enhance(1.12)
fg = src.convert("RGBA"); fg.putalpha(m.filter(ImageFilter.GaussianBlur(1.4))); fg.save(a.out + "_fg.png")
ring = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(a.outline * 2 + 1)), m.filter(ImageFilter.MinFilter(3))).filter(ImageFilter.GaussianBlur(1.0))
ol = Image.new("RGBA", im.size, (255, 255, 255, 0)); ol.putalpha(ring); ol.save(a.out + "_ol.png")
print(a.out, im.size, "konu sınırı", m.getbbox())
