#!/usr/bin/env python3
"""timeline.json -> hızlı önizleme MP4 (After Effects gerekmez).

After Effects'e geçmeden önce zamanlamayı, sahne sırasını, altyazıları ve sesi kontrol etmek için.
Ayrıca AE kurulu olmayan makinede yedek teslim yolu olarak kullanılabilir (geçişler ffmpeg xfade ile
yaklaşık yapılır, kalite AE çıktısından düşüktür).

Kullanım:
  python3 preview_ffmpeg.py timeline.json -o build/preview.mp4 [--fonts-dir fonts/] [--scale 0.5]
"""
import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from styles import resolve

XFADE = {  # geçiş -> (ffmpeg xfade adı, süre)
    "cut": (None, 0), "blur_whip": ("slideup", 0.18), "slide_up": ("slideup", 0.25),
    "zoom_blur": ("zoomin", 0.25), "flash": ("fadewhite", 0.2), "fade": ("fade", 0.3),
    "light_leak": ("fade", 0.35), "circle_reveal": ("circleopen", 0.35),
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("ffmpeg hata:\n" + " ".join(cmd)[:600] + "\n" + r.stderr[-2500:])


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def find_font(names, fonts_dir=None):
    cands = []
    if fonts_dir:
        cands += [p for p in Path(fonts_dir).glob("*.[ot]tf")]
    for n in names:
        for p in cands:
            if n.lower().replace("-", "") in p.stem.lower().replace("-", ""):
                return str(p)
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", names[-1]], capture_output=True, text=True).stdout
        if out:
            return out
    except FileNotFoundError:
        pass
    return None


def cover(img, w, h):
    return ImageOps.fit(img.convert("RGB"), (w, h), Image.LANCZOS)


def baked_title(sc, st, W, H, title_font_path, style):
    """cutout sahnelerinde figürün ARKASINDA kalan başlığı durağan olarak çizer (RGBA katman)."""
    t = sc.get("title") or {}
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not (t and title_font_path):
        return layer
    txt = t.get("text", "")
    if style == "earn" and not t.get("keep_case"):
        txt = tr_upper(txt)
    longest = max((len(x) for x in txt.split("\n")), default=1)
    size = int(min(t.get("size", st["title"]["size"]), 0.88 * 1080 / max(longest * 0.47, 1)) * W / 1080)
    c = st["colors"].get(t.get("color", st["title"]["color"]), t.get("color", "#FFD21F"))
    posy = {"top": 0.20, "upper": 0.30, "center": 0.45, "lower": 0.60, "bottom": 0.66}
    y = int(posy.get(t.get("pos", st["title"]["pos"]), 0.2) * H)
    font = ImageFont.truetype(title_font_path, size)
    d = ImageDraw.Draw(layer)
    d.text((W / 2 + 5, y + 7), txt, fill=(0, 0, 0, 150), anchor="mm", font=font)
    d.text((W / 2, y), txt, fill=c, anchor="mm", font=font)
    anim = t.get("anim", st["title"]["anim"])
    if anim == "stamp":
        bb = d.textbbox((W / 2, y), txt, anchor="mm", font=font)
        d.rectangle((bb[0] - 30, bb[1] - 18, bb[2] + 30, bb[3] + 18), outline=c, width=max(int(7 * W / 1080), 2))
        layer = layer.rotate(t.get("rotate", 6) if t.get("rotate") else 6, resample=Image.BICUBIC, center=(W / 2, y))
    return layer


def scene_frame(sc, W, H, font_path, st=None, title_font_path=None, style="earn"):
    img = Image.open(sc["image"]) if sc.get("image") and Path(sc["image"]).exists() else None
    if img is None:
        im = Image.new("RGB", (W, H), (60, 55, 50))
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(font_path, 60) if font_path else None
        d.text((W / 2, H / 2), f"{sc['id']} görsel eksik", fill="white", anchor="mm", font=f)
        return im
    frame = sc.get("frame", "full")
    if frame == "full":
        return cover(img, W, H)
    if frame == "cutout":
        # arka plan + (istenirse) başlık + alfa kanallı figür; figür alt kenara oturur
        if sc.get("bg") and Path(sc["bg"]).exists():
            base = cover(Image.open(sc["bg"]), W, H).point(lambda v: int(v * 0.72))
        else:
            base = Image.new("RGB", (W, H), (24, 22, 22))
        base = base.convert("RGBA")
        if (sc.get("title") or {}).get("behind") and st:
            base.alpha_composite(baked_title(sc, st, W, H, title_font_path, style))
        fg = img.convert("RGBA")
        k = max(W / fg.width, H / fg.height)
        fg = fg.resize((int(fg.width * k + 0.5), int(fg.height * k + 0.5)), Image.LANCZOS)
        base.alpha_composite(fg.crop(((fg.width - W) // 2, fg.height - H, (fg.width - W) // 2 + W, fg.height)))
        return base.convert("RGB")
    bg_src = Image.open(sc["bg"]) if sc.get("bg") and Path(sc["bg"]).exists() else img
    bg = cover(bg_src, W, H)
    if not sc.get("bg"):
        bg = bg.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.5))
    cy = int(H * 0.46)
    if frame == "circle":
        dia = int(W * 0.78)
        c = cover(img, dia, dia)
        mask = Image.new("L", (dia, dia), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, dia - 1, dia - 1), fill=255)
        bg.paste(c, (W // 2 - dia // 2, cy - dia // 2), mask)
        r = dia // 2 + 23
        ImageDraw.Draw(bg).ellipse((W // 2 - r, cy - r, W // 2 + r, cy + r), outline=(255, 255, 255), width=3)
        return bg
    if frame == "polaroid":
        cw = int(W * 0.66); ch = int(cw * 1.18); iw = int(cw * 0.88)
        card = Image.new("RGBA", (cw, ch), (247, 245, 238, 255))
        card.paste(cover(img, iw, iw), ((cw - iw) // 2, int(cw * 0.06)))
        if sc.get("label") and font_path:
            d = ImageDraw.Draw(card)
            d.text((cw / 2, ch - cw * 0.12), sc["label"], fill=(40, 34, 30), anchor="mm",
                   font=ImageFont.truetype(font_path, 44))
        card = card.rotate(sc.get("tilt", -4), expand=True, resample=Image.BICUBIC)
        bg.paste(card, (W // 2 - card.width // 2, cy - card.height // 2), card)
        return bg
    if frame == "split":
        img2 = Image.open(sc["image2"]) if sc.get("image2") and Path(sc["image2"]).exists() else img
        a, b = cover(img, W, H), cover(img2, W, H)
        mask = Image.new("L", (W, H), 0)
        off = math.tan(math.radians(8)) * H / 2
        ImageDraw.Draw(mask).polygon([(W / 2 + off, 0), (W, 0), (W, H), (W / 2 - off, H)], fill=255)
        a.paste(b, (0, 0), mask)
        ImageDraw.Draw(a).line([(W / 2 + off, 0), (W / 2 - off, H)], fill=(255, 255, 255), width=8)
        return a
    return cover(img, W, H)


def zoompan_expr(move, n):
    p = f"(on/{max(n - 1, 1)})"
    if move == "push_in":
        return f"1.0+0.14*{p}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if move == "pull_out":
        return f"1.16-0.14*{p}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if move in ("pan_left", "pan_right"):
        sgn = "-" if move == "pan_left" else "+"
        return "1.15", f"iw/2-(iw/zoom/2){sgn}(iw*0.06)*({p}-0.5)*2*-1", "ih/2-(ih/zoom/2)"
    if move in ("pan_up", "pan_down"):
        sgn = "+" if move == "pan_up" else "-"
        return "1.15", "iw/2-(iw/zoom/2)", f"ih/2-(ih/zoom/2){sgn}(ih*0.04)*({p}-0.5)*2*-1"
    if move == "parallax":
        return f"1.06+0.11*{p}", f"iw/2-(iw/zoom/2)+(iw*0.02)*({p}-0.5)", f"ih/2-(ih/zoom/2)-(ih*0.012)*({p}-0.5)"
    return "1.02", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"


def ass_color(rgb_hex, alpha=0):
    h = rgb_hex.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(tl, st, W, H, cap_font, title_font):
    cap = st["caption"]
    col = st["colors"]
    style = tl["style"]
    is_hex = style == "hex"
    fs_cap = int(cap["size"] * W / 1080)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
        "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
        "MarginL, MarginR, MarginV, Encoding",
    ]
    if is_hex:
        lines.append(f"Style: Cap,{cap_font},{fs_cap},{ass_color(col['white'])},&H000000FF,&H00000000,"
                     f"&H80000000,0,1,0,0,100,100,1,0,1,0,3,5,40,40,0,1")
    else:
        lines.append(f"Style: Cap,{cap_font},{fs_cap},{ass_color(col['white'])},&H000000FF,"
                     f"{ass_color(cap.get('pill', '#1E1E1E'), 0x40)},{ass_color(cap.get('pill', '#1E1E1E'), 0x40)},"
                     f"1,0,0,0,100,100,0,0,3,14,0,5,40,40,0,1")
    lines.append(f"Style: Title,{title_font},{int(150 * W / 1080)},{ass_color(col['yellow'])},&H000000FF,"
                 f"&H00000000,&HA0000000,1,{1 if is_hex else 0},0,0,100,100,0,0,1,0,6,5,40,40,0,1")
    lines += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    key_col = ass_color(col.get(cap["key_color"], col["red"]))
    cy = int(cap["y"] * H)
    for c in tl["captions"]:
        words = [tl["words"][i] for i in c["words"]]
        txt = " ".join((f"{{\\c{key_col}}}{w['w']}{{\\r}}" if w.get("key") else w["w"]) for w in words)
        end = max(c["end"], c["start"] + 0.18)
        if is_hex:
            big = any(w.get("key") for w in words)
            sc = 140 if big else 100
            fx = f"{{\\an5\\pos({W // 2},{cy})\\fad(70,60)\\fscx{int(sc * .92)}\\fscy{int(sc * .92)}" \
                 f"\\t(\\fscx{sc}\\fscy{sc})}}"
        else:
            fx = f"{{\\an5\\pos({W // 2},{cy})}}"
        lines.append(f"Dialogue: 2,{ts(c['start'])},{ts(end)},Cap,,0,0,0,,{fx}{txt}")
    posy = {"top": 0.20, "upper": 0.30, "center": 0.45, "lower": 0.60, "bottom": 0.66}
    for sc in tl["scenes"]:
        t = sc.get("title")
        if not t:
            continue
        if t.get("behind") and sc.get("frame") == "cutout":
            continue  # figürün arkasında: sahne karesine gömülü çizildi
        txt = t.get("text", "")
        if style == "earn" and not t.get("keep_case"):
            txt = tr_upper(txt)
        longest = max((len(x) for x in txt.split("\n")), default=1)
        size = int(min(t.get("size", st["title"]["size"]), 0.88 * 1080 / max(longest * 0.47, 1)) * W / 1080)
        c = st["colors"].get(t.get("color", st["title"]["color"]), t.get("color", "#FFD21F"))
        if not str(c).startswith("#"):
            c = "#FFD21F"
        a = sc["start"] + t.get("delay", 0.08)
        b = sc["start"] + t["until"] if t.get("until") else sc["end"]
        y = int(posy.get(t.get("pos", st["title"]["pos"]), 0.2) * H)
        anim = t.get("anim", st["title"]["anim"])
        rot = f"\\frz{-t['rotate']}" if t.get("rotate") else ("\\frz6" if anim == "stamp" else "")
        if anim in ("slam", "stamp"):
            fx = f"\\fscx260\\fscy260\\alpha&HFF&\\t(0,160,\\fscx100\\fscy100\\alpha&H00&)"
        elif anim == "pop":
            fx = "\\fscx0\\fscy0\\t(0,160,\\fscx106\\fscy106)\\t(160,260,\\fscx100\\fscy100)"
        else:
            fx = "\\fad(300,100)"
        border = "\\bord6\\3c&HFFFFFF&" if anim == "stamp" else ""
        body = txt.replace("\n", "\\N")
        lines.append(f"Dialogue: 3,{ts(a)},{ts(b)},Title,,0,0,0,,{{\\an5\\pos({W // 2},{y})\\fs{size}"
                     f"\\c{ass_color(c)}{rot}{border}{fx}}}{body}")
    o = tl.get("outro")
    if o:
        for k, line in enumerate(o.get("text", [])):
            txt = tr_upper(line) if style == "earn" else line
            size = int((120 if k == 0 else 64) * W / 1080)
            y = int(H * (0.40 + k * 0.09))
            a = o["start"] + 0.15 + k * 0.25
            lines.append(f"Dialogue: 3,{ts(a)},{ts(o['end'])},Title,,0,0,0,,{{\\an5\\pos({W // 2},{y})\\fs{size}"
                         f"\\fscx0\\fscy0\\t(0,160,\\fscx100\\fscy100)}}{txt}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("-o", "--out", default="build/preview.mp4")
    ap.add_argument("--fonts-dir")
    ap.add_argument("--scale", type=float, default=1.0, help="0.5 = yarım çözünürlükte hızlı önizleme")
    ap.add_argument("--keep", action="store_true", help="ara dosyaları sakla")
    a = ap.parse_args()
    tl = json.loads(Path(a.timeline).read_text(encoding="utf-8"))
    st = resolve(tl["style"], {"fonts": tl.get("fonts") or {}})
    W0, H0 = tl["size"]
    W, H = int(W0 * a.scale) // 2 * 2, int(H0 * a.scale) // 2 * 2
    fps = tl["fps"]
    tmp = Path(tempfile.mkdtemp(prefix="reel_prev_"))
    body_font = find_font(["Poppins-SemiBold", "DejaVuSans-Bold", "DejaVu Sans:bold"], a.fonts_dir)
    cap_family = "Playfair Display" if tl["style"] == "hex" else "Poppins"
    title_family = "Playfair Display" if tl["style"] == "hex" else "Anton"
    if not find_font([cap_family.replace(" ", "")], a.fonts_dir):
        cap_family = "DejaVu Serif" if tl["style"] == "hex" else "DejaVu Sans"
    if not find_font([title_family.replace(" ", "")], a.fonts_dir):
        title_family = "DejaVu Serif" if tl["style"] == "hex" else "DejaVu Sans"

    # 1) sahne klipleri
    items = list(tl["scenes"])
    if tl.get("outro"):
        o = dict(tl["outro"]); o.setdefault("id", "outro"); o.setdefault("move", "push_in")
        o.setdefault("transition", "flash"); o["text"] = []  # yazılar ASS'te
        items.append(o)
    clips = []
    for i, sc in enumerate(items):
        nxt = items[i + 1] if i + 1 < len(items) else None
        xname, xd = XFADE.get((nxt or {}).get("transition", "cut"), (None, 0))
        ext = xd if (nxt and xname) else 0
        dur = sc["end"] - sc["start"] + ext
        n = max(int(round(dur * fps)), 2)
        out = tmp / f"c{i:03d}.mp4"
        if sc.get("video") and Path(sc["video"]).exists():
            vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={fps},tpad=stop_mode=clone:stop_duration=30"
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", sc["video"], "-t", f"{dur:.3f}", "-vf", vf, "-an",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)])
        else:
            title_path = find_font(["Anton-Regular", "Anton"], a.fonts_dir)
            frame = scene_frame(sc, W, H, body_font, st, title_path, tl["style"])
            fp = tmp / f"f{i:03d}.png"
            frame.save(fp)
            z, x, y = zoompan_expr(sc.get("move", st["default_move"]), n)
            vf = (f"scale={W * 2}:{H * 2},zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={fps},"
                  f"format=yuv420p")
            run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(fp), "-vf", vf, "-frames:v", str(n),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", str(out)])
        clips.append((out, sc))

    # 2) xfade zinciri + grad + altyazı
    inputs = []
    for p, _ in clips:
        inputs += ["-i", str(p)]
    # concat ve xfade aynı zaman tabanını ister: hepsini AVTB'ye sabitle
    fc = [f"[{i}:v]fps={fps},setpts=PTS-STARTPTS,settb=AVTB[s{i}]" for i in range(len(clips))]
    last = "[s0]"
    for i in range(1, len(clips)):
        sc = clips[i][1]
        xname, xd = XFADE.get(sc.get("transition", "cut"), (None, 0))
        if not xname:
            fc.append(f"{last}[s{i}]concat=n=2:v=1:a=0,settb=AVTB[v{i}]")
        else:
            fc.append(f"{last}[s{i}]xfade=transition={xname}:duration={xd}:offset={sc['start']:.3f},settb=AVTB[v{i}]")
        last = f"[v{i}]"
    g = st["grade"]
    grade = []
    if g.get("tint"):
        k = g["tint"] / 100.0
        S = [[.393, .769, .189], [.349, .686, .168], [.272, .534, .131]]
        m = [[(1 - k) * (1 if r == c else 0) + k * S[r][c] for c in range(3)] for r in range(3)]
        grade.append("colorchannelmixer=rr={0:.3f}:rg={1:.3f}:rb={2:.3f}:gr={3:.3f}:gg={4:.3f}:gb={5:.3f}:"
                     "br={6:.3f}:bg={7:.3f}:bb={8:.3f}".format(*[v for row in m for v in row]))
    if g.get("noise"):
        grade.append(f"noise=alls={int(g['noise'] * 2)}:allf=t")
    if g.get("vignette"):
        grade.append(f"vignette=angle={0.3 + g['vignette'] / 200:.2f}")
    ass = tmp / "subs.ass"
    ass.write_text(build_ass(tl, st, W, H, cap_family, title_family), encoding="utf-8")
    fdir = f":fontsdir={a.fonts_dir}" if a.fonts_dir else ""
    has_ass = " ass " in subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    if not has_ass:
        print("⚠ bu ffmpeg libass içermiyor: önizlemede altyazı ve başlık yok (AE çıktısında olacak)")
    chain = ",".join(grade + ([f"ass={ass}{fdir}"] if has_ass else [])) or "null"
    fc.append(f"{last}{chain},trim=duration={tl['duration']:.3f}[vout]")

    # 3) ses
    ai = len(clips)
    amix = []
    if tl.get("voiceover") and Path(tl["voiceover"]).exists():
        inputs += ["-i", tl["voiceover"]]; amix.append(f"[{ai}:a]volume=1.0[a{ai}]"); ai += 1
    mus = (tl.get("music") or {}).get("file")
    if mus and Path(mus).exists():
        db = (tl.get("music") or {}).get("db", st["music_db"])
        inputs += ["-stream_loop", "-1", "-i", mus]
        amix.append(f"[{ai}:a]volume={db}dB,atrim=0:{tl['duration']:.3f},"
                    f"afade=t=out:st={max(tl['duration'] - 1.2, 0):.2f}:d=1.2[a{ai}]")
        ai += 1
    sfxmap = st["sfx_map"]
    events = []
    for i, sc in enumerate(tl["scenes"]):
        if i and sc.get("transition", "cut") != "cut":
            events.append((sfxmap["transition"], sc["start"] - 0.12, -10))
        t = sc.get("title")
        if t and t.get("anim", st["title"]["anim"]) in ("slam", "stamp"):
            events.append((sfxmap["slam"], sc["start"] + t.get("delay", 0.08), -6))
        if sc.get("frame") in ("circle", "polaroid", "cutout"):
            events.append((sfxmap["pop"], sc["start"], -8))
        for s in sc.get("sfx", []):
            nm, off = (s, 0) if isinstance(s, str) else (s["name"], s.get("at", 0))
            events.append((nm, sc["start"] + off, -6))
    for nm, t, db in events:
        p = (tl.get("sfx") or {}).get(nm)
        if p and Path(p).exists():
            inputs += ["-i", p]
            ms = int(max(t, 0) * 1000)
            amix.append(f"[{ai}:a]adelay={ms}|{ms},volume={db}dB[a{ai}]")
            ai += 1
    if amix:
        fc += amix
        labels = "".join(x[x.rindex("["):] for x in amix)
        fc.append(f"{labels}amix=inputs={len(amix)}:normalize=0:duration=longest,"
                  f"atrim=0:{tl['duration']:.3f}[aout]")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[vout]"]
    if amix:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(fps),
            "-movflags", "+faststart", a.out]
    run(cmd)
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"{a.out} yazıldı ({W}x{H}, {tl['duration']:.1f} sn, {len(clips)} klip, {len(amix)} ses izi)")


if __name__ == "__main__":
    main()
