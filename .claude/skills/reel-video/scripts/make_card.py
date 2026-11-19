#!/usr/bin/env python3
"""Yazı kartı zemini üretir: düz renk + kağıt greni + isteğe bağlı kare doku / spot ışığı / yıldız tozu + vinyet.
Referans videolardaki "boş kart" sahneleri için (yalnızca yazı taşıyan, 1-2 saniyelik nefes sahneleri).

  make_card.py -o assets/img/kart_sari.jpg --color "#C8961E" --grid
  make_card.py -o assets/img/kart_koyu.jpg --color "#1A1A1A" --dust
  make_card.py -o assets/img/kart_spot.jpg --color "#7A2E10" --grid --spot 0.5,0.42
  make_card.py -o assets/img/kart_kagit.jpg --color "#E9E2D2"
shotlist'te: {"image": "assets/img/kart_sari.jpg", "move": "none", "caption": false, "title": {...}} ya da frame "scatter".
"""
import argparse, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--out", required=True); ap.add_argument("--color", default="#1A1A1A")
ap.add_argument("--grid", action="store_true", help="ince kare doku"); ap.add_argument("--dust", action="store_true", help="yıldız / toz zerreleri")
ap.add_argument("--spot", default="", help="spot ışığı merkezi: x,y (0-1)"); ap.add_argument("--vignette", type=float, default=0.45)
ap.add_argument("--seed", type=int, default=7); ap.add_argument("--size", default="1296x2304")
a = ap.parse_args()
random.seed(a.seed); W, H = (int(v) for v in a.size.split("x"))
c = a.color.lstrip("#"); rgb = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)); lum = sum(rgb) / 3
im = Image.new("RGB", (W, H), rgb)
# kağıt greni
n = Image.effect_noise((W // 2, H // 2), 26).resize((W, H)).convert("L")
im = ImageChops.overlay(im, Image.merge("RGB", (n, n, n)).point(lambda v: 128 + (v - 128) * 0.35))
# büyük ölçekli leke
b = Image.effect_noise((W // 40, H // 40), 60).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(60)).convert("L")
im = ImageChops.overlay(im, Image.merge("RGB", (b, b, b)).point(lambda v: 128 + (v - 128) * 0.5))
d = ImageDraw.Draw(im, "RGBA")
if a.grid:
    col = (255, 255, 255, 26) if lum < 150 else (0, 0, 0, 22)
    for x in range(0, W, 54): d.line([(x, 0), (x, H)], fill=col, width=2)
    for y in range(0, H, 54): d.line([(0, y), (W, y)], fill=col, width=2)
if a.dust:
    for _ in range(420):
        x, y, r = random.randint(0, W), random.randint(0, H), random.choice([1, 1, 1, 2, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, random.randint(40, 150)))
if a.spot:
    sx, sy = (float(v) for v in a.spot.split(","))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([sx * W - W * 0.55, sy * H - W * 0.62, sx * W + W * 0.55, sy * H + W * 0.62], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(150))
    im = Image.composite(Image.eval(im, lambda v: min(255, int(v * 1.45 + 18))), Image.eval(im, lambda v: int(v * 0.42)), m)
if a.vignette > 0:
    v = Image.new("L", (W, H), 0); ImageDraw.Draw(v).ellipse([-W * 0.25, -H * 0.15, W * 1.25, H * 1.15], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(260))
    im = Image.composite(im, Image.eval(im, lambda x: int(x * (1 - a.vignette))), v)
im.save(a.out, quality=92); print(a.out)
