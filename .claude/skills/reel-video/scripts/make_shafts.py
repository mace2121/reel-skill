#!/usr/bin/env python3
"""hex stili için ışık huzmesi dokusu üretir: yumuşak dikey ışık bantları yavaşça yana kayar (multiply ile kullanılır).

  make_shafts.py -o assets/shafts.mp4 [--seconds 44] [--base 158] [--seed 4]
--base: bantlar arasındaki karanlığın düzeyi (0-255; düşük = daha koyu gölge). Video süresinden uzun üret (döngü atlar).
"""
import argparse, random, subprocess, tempfile, os
from PIL import Image, ImageDraw, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--out", required=True); ap.add_argument("--seconds", type=int, default=44)
ap.add_argument("--base", type=int, default=158); ap.add_argument("--seed", type=int, default=4)
a = ap.parse_args()
random.seed(a.seed); PW = 1080 * 3 + 400
band = Image.new("L", (PW, 1920), a.base); d = ImageDraw.Draw(band); x = 60
while x < PW:
    w = random.randint(170, 420); sk = random.randint(-120, 120)
    d.polygon([(x + sk, 0), (x + w + sk, 0), (x + w - sk // 2, 1920), (x - sk // 2, 1920)], fill=255)
    x += w + random.randint(260, 520)
tmp = os.path.join(tempfile.mkdtemp(prefix="shafts_"), "band.png"); band.filter(ImageFilter.GaussianBlur(70)).save(tmp)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", tmp, "-t", str(a.seconds), "-vf",
                f"crop=1080:1920:'(iw-1080)*(t/{a.seconds})':0,format=yuv420p", "-r", "30", "-c:v", "libx264", "-crf", "24",
                "-preset", "fast", a.out], check=True)
print(a.out)
