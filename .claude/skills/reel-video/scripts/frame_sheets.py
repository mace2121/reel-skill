#!/usr/bin/env python3
"""Videoyu (ya da kare klasörünü) zaman etiketli kare föylerine çevirir: render'ı gözle kontrol etmek ve
referans videoları kare kare incelemek için.

  frame_sheets.py video.mp4 -o build/qc/son [--every 6] [--start 5 --end 8] [--cols 12 --rows 2 --width 180]
  frame_sheets.py kare_klasörü/ -o ref/s --fps 30 --every 4      (frame-000123-... adlı jpg'ler)
"""
import argparse, glob, os, re, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("-o", "--out", required=True)
ap.add_argument("--every", type=int, default=6); ap.add_argument("--fps", type=float, default=30)
ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=1e9)
ap.add_argument("--cols", type=int, default=12); ap.add_argument("--rows", type=int, default=2)
ap.add_argument("--width", type=int, default=180)
a = ap.parse_args()
if os.path.isdir(a.src):
    files = sorted(glob.glob(os.path.join(a.src, "*.jpg")))
    fps = a.fps
else:
    tmp = tempfile.mkdtemp(prefix="sheets_")
    fps = a.fps
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.src, "-vf", f"fps={fps},scale=360:-2", "-q:v", "4",
                    os.path.join(tmp, "f%06d.jpg")], check=True)
    files = sorted(glob.glob(os.path.join(tmp, "*.jpg")))
def num(f, i):
    m = re.search(r"(\d{4,})", os.path.basename(f))
    return int(m.group(1)) if m else i + 1
sel = [(f, (num(f, i) - 1) / fps) for i, f in enumerate(files)]
sel = [x for x in sel if a.start <= x[1] <= a.end][::a.every]
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", max(a.width // 9, 12)) if os.path.exists("/System/Library/Fonts/Helvetica.ttc") else None
per = a.cols * a.rows
for k in range(0, len(sel), per):
    part = sel[k:k + per]
    w0, h0 = Image.open(part[0][0]).size; th = a.width * h0 // w0
    sh = Image.new("RGB", (a.cols * a.width, a.rows * th))
    for i, (f, t) in enumerate(part):
        im = Image.open(f).convert("RGB").resize((a.width, th)); d = ImageDraw.Draw(im)
        d.rectangle((0, 0, a.width * 0.5, a.width // 7 + 4), fill=(0, 0, 0)); d.text((3, 2), f"{t:.1f}s", fill="white", font=font)
        sh.paste(im, ((i % a.cols) * a.width, (i // a.cols) * th))
    sh.save(f"{a.out}_{k // per:02d}.jpg", quality=80)
print(f"{len(sel)} kare, {(len(sel) + per - 1) // per} föy -> {a.out}_NN.jpg")
