#!/usr/bin/env python3
"""Arka planı silinmiş (alfa kanallı) figürü `frame: "cutout"` için hazırlar.

Figürü alfa sınırına kırpar, 9:16 tuvale alt kenara oturacak şekilde yerleştirir ve earn tarzı beyaz
"sticker" kenarlığı ekler.

  python3 cutout_prep.py girdi.png cikti.png [--width 0.92] [--top 0.30] [--outline 14] [--size 1296x2304]
--width : figürün tuval genişliğine oranı (üst sınır)
--top   : figürün tepesinin tuvalde inebileceği en üst nokta (0 = en üst)
"""
import argparse
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--width", type=float, default=0.92)
ap.add_argument("--top", type=float, default=0.30)
ap.add_argument("--outline", type=int, default=14)
ap.add_argument("--size", default="1296x2304")
ap.add_argument("--fill-holes", default="", help="iç boşlukları bu renkle doldur (#RRGGBB)")
ap.add_argument("--crop-bottom", type=float, default=0.0, help="figürün altından atılacak oran")
a = ap.parse_args()
W, H = (int(v) for v in a.size.split("x"))
im = Image.open(a.src).convert("RGBA")
alpha = im.getchannel("A").point(lambda v: 255 if v > 24 else 0)
im = im.crop(alpha.getbbox())
if a.fill_holes:
    # figürün içinde kalan (dışarıya bağlı olmayan) saydam boşlukları düz renkle doldur
    from PIL import ImageDraw
    al = im.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    pad = Image.new("L", (al.width + 2, al.height + 1), 0)   # üst ve yanlardan dışarıya açık, alt kapalı
    pad.paste(al, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    holes = pad.crop((1, 1, al.width + 1, al.height + 1)).point(lambda v: 255 if v == 0 else 0)
    holes = holes.filter(ImageFilter.MaxFilter(13))  # yarı saydam kenar pikselleri de kapansın
    h = a.fill_holes.lstrip("#")
    im.paste(Image.new("RGBA", im.size, tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)), (0, 0), holes)
if a.crop_bottom:
    im = im.crop((0, 0, im.width, int(im.height * (1 - a.crop_bottom))))
k = min(W * a.width / im.width, H * (1 - a.top) / im.height)
im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
x, y = (W - im.width) // 2, H - im.height
if a.outline:
    m = Image.new("L", (W, H), 0)
    m.paste(im.getchannel("A").point(lambda v: 255 if v > 40 else 0), (x, y))
    m = m.filter(ImageFilter.MaxFilter(a.outline * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    canvas.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), m)
canvas.alpha_composite(im, (x, y))
canvas.save(a.dst)
print(a.dst, canvas.size, "figür", im.size)
