#!/usr/bin/env python3
"""shotlist.json + seslendirme kelime zamanları -> timeline.json

Kullanım:
  python3 timeline.py shotlist.json -o timeline.json [--words words.json] [--audio vo.mp3]

--words şu biçimlerden birini kabul eder:
  * ElevenLabs "with-timestamps" çıktısı: {"alignment": {"characters": [...],
    "character_start_times_seconds": [...], "character_end_times_seconds": [...]}}
  * Whisper / faster-whisper: {"segments": [{"words": [{"word", "start", "end"}]}]}
  * Düz liste: [{"word" | "text", "start", "end"}, ...]
--words verilmezse süre seslendirme dosyasından (ffprobe) okunur ve kelimelere
harf sayısına göre orantılı dağıtılır (noktalama işaretlerinde kısa duraklama).
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

PUNCT_PAUSE = {".": 0.35, "!": 0.35, "?": 0.35, ",": 0.15, ";": 0.2, ":": 0.2, "…": 0.35}


def tr_lower(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def norm(tok):
    return re.sub(r"[^\wçğıöşü]", "", tr_lower(tok))


def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def load_words(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    al = d.get("alignment") if isinstance(d, dict) else None
    if al is None and isinstance(d, dict) and "characters" in d:
        al = d
    if al:  # ElevenLabs karakter hizalaması -> kelimeler
        chars = al["characters"]
        st = al["character_start_times_seconds"]
        en = al["character_end_times_seconds"]
        words, cur, s0, e0 = [], "", None, None
        for c, a, b in zip(chars, st, en):
            if c.isspace():
                if cur:
                    words.append({"w": cur, "start": s0, "end": e0})
                cur, s0 = "", None
                continue
            if s0 is None:
                s0 = a
            cur += c
            e0 = b
        if cur:
            words.append({"w": cur, "start": s0, "end": e0})
        return words
    items = []
    if isinstance(d, dict) and "segments" in d:
        for seg in d["segments"]:
            items += seg.get("words", [])
    elif isinstance(d, dict) and "words" in d:
        items = d["words"]
    elif isinstance(d, list):
        items = d
    return [{"w": (i.get("word") or i.get("text") or "").strip(), "start": float(i["start"]),
             "end": float(i["end"])} for i in items if (i.get("word") or i.get("text") or "").strip()]


def estimate_times(tokens, total, lead=0.15, tail=0.25):
    """Seslendirme süresini harf sayısı + noktalama duraklamalarına göre dağıt."""
    weights = [max(len(norm(t)), 1) + 1.5 for t in tokens]
    pauses = [PUNCT_PAUSE.get(t[-1], 0.0) if t else 0.0 for t in tokens]
    speak = max(total - lead - tail - sum(pauses), 0.5)
    unit = speak / sum(weights)
    t, out = lead, []
    for tok, w, p in zip(tokens, weights, pauses):
        out.append({"w": tok, "start": round(t, 3), "end": round(t + w * unit, 3)})
        t += w * unit + p
    return out


def align(script_tokens, asr):
    """Senaryo kelimelerini ASR kelimelerine eşle; eşleşmeyenleri komşulardan enterpole et."""
    a = [norm(t) for t in script_tokens]
    b = [norm(w["w"]) for w in asr]
    times = [None] * len(a)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w = asr[blk.b + k]
            times[blk.a + k] = (w["start"], w["end"])
    # Eşleşmeyen aralıkları doldur
    n = len(a)
    i = 0
    first = asr[0]["start"] if asr else 0.0
    last = asr[-1]["end"] if asr else 1.0
    while i < n:
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < n and times[j] is None:
            j += 1
        left = times[i - 1][1] if i > 0 else first
        right = times[j][0] if j < n else last
        step = max(right - left, 0.05) / (j - i)
        for k in range(i, j):
            s = left + (k - i) * step
            times[k] = (s, s + step * 0.9)
        i = j
    return [{"w": t, "start": round(s, 3), "end": round(e, 3)} for t, (s, e) in zip(script_tokens, times)]


def is_keyword(word, keywords):
    w = norm(word)
    return any(w.startswith(norm(k)) for k in keywords if norm(k))


def chunk_captions(words, style, mode=None):
    """earn: 1-3 kelimelik hap altyazı; hex: tek kelime; mode="phrase": 2-4 kelimelik öbek (kelime kelime belirir)."""
    maxw = 4 if mode == "phrase" else 3
    if style == "hex" and mode != "phrase":
        return [{"text": w["w"], "start": w["start"], "end": w["end"], "words": [i]}
                for i, w in enumerate(words)]
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        end_punct = w["w"][-1] in ".,!?;:…"
        nxt_len = (sum(len(words[j]["w"]) + 1 for j in cur) + len(words[i + 1]["w"])) if i + 1 < len(words) else 0
        too_wide = mode == "phrase" and nxt_len > 24   # serif öbek kadrajdan taşmasın
        if too_wide or len(cur) >= maxw or end_punct or (i + 1 < len(words) and words[i + 1]["start"] - w["end"] > 0.3):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for c in chunks:
        out.append({"text": " ".join(words[i]["w"] for i in c), "start": words[c[0]]["start"],
                    "end": words[c[-1]]["end"], "words": c})
    for a, b in zip(out, out[1:]):  # boşluk bırakma: bir sonraki altyazıya kadar ekranda kalsın
        if b["start"] - a["end"] < 0.4:
            a["end"] = b["start"]
    return out


def build(shot, words_path=None, audio=None):
    style = shot.get("style", "earn")
    scenes = shot["scenes"]
    script_tokens, owner = [], []
    for si, sc in enumerate(scenes):
        toks = sc.get("narration", "").split()
        script_tokens += toks
        owner += [si] * len(toks)
    if not script_tokens:
        sys.exit("shotlist'te hiç narration yok")
    vo = audio or shot.get("voiceover")
    if words_path:
        asr = load_words(words_path)
        words = align(script_tokens, asr)
        vo_dur = ffprobe_duration(vo) if vo and Path(vo).exists() else words[-1]["end"] + 0.3
    else:
        if not vo or not Path(vo).exists():
            sys.exit("--words yok ve seslendirme dosyası bulunamadı; süre tahmin edilemiyor")
        vo_dur = ffprobe_duration(vo)
        words = estimate_times(script_tokens, vo_dur)
    for w, si in zip(words, owner):
        w["scene"] = si
        w["key"] = is_keyword(w["w"], scenes[si].get("keywords", []))

    # Sahne sınırları: sahnenin ilk kelimesinden biraz önce kes (kesme sesten önce gelir)
    pre = 0.08
    starts = []
    for si in range(len(scenes)):
        idx = [i for i, o in enumerate(owner) if o == si]
        if idx:
            starts.append(max(words[idx[0]]["start"] - pre, 0.0))
        else:  # anlatımsız sahne: önceki sahnenin ortasından başlat
            starts.append(None)
    starts[0] = 0.0
    for si in range(len(starts)):
        if starts[si] is None:
            prev = starts[si - 1]
            nxt = next((s for s in starts[si + 1:] if s is not None), vo_dur)
            starts[si] = prev + (nxt - prev) / 2
    outro = shot.get("outro")
    body_end = max(vo_dur, words[-1]["end"] + 0.4)
    tl_scenes = []
    for si, sc in enumerate(scenes):
        s = starts[si]
        e = starts[si + 1] if si + 1 < len(scenes) else body_end
        d = dict(sc)
        d.update(start=round(s, 3), end=round(e, 3), duration=round(e - s, 3))
        tl_scenes.append(d)
    total = body_end
    if outro:
        o = dict(outro)
        o["start"] = round(body_end, 3)
        o["end"] = round(body_end + float(outro.get("duration", 3.0)), 3)
        total = o["end"]
        outro = o
    long_scenes = [s["id"] for s in tl_scenes if s["duration"] > 6.0]
    return {
        "title": shot.get("title", ""),
        "style": style,
        "fps": shot.get("fps", 30),
        "size": shot.get("size", [1080, 1920]),
        "duration": round(total, 3),
        "voiceover": vo,
        "music": shot.get("music"),
        "sfx": shot.get("sfx", {}),
        "fonts": shot.get("fonts", {}),
        "words": words,
        "captions": chunk_captions(words, style, shot.get("caption_chunks")),
        "caption": shot.get("caption") or {},
        "grade": shot.get("grade") or {},
        "scenes": tl_scenes,
        "outro": outro,
        "warnings": ([f"6 saniyeden uzun sahneler (bölmeyi düşün): {', '.join(long_scenes)}"]
                     if long_scenes else []),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shotlist")
    ap.add_argument("-o", "--out", default="timeline.json")
    ap.add_argument("--words")
    ap.add_argument("--audio")
    a = ap.parse_args()
    shot = json.loads(Path(a.shotlist).read_text(encoding="utf-8"))
    base = Path(a.shotlist).resolve().parent
    # Göreli yolları shotlist klasörüne göre çöz
    skill_root = Path(__file__).resolve().parent.parent
    def fix(p):
        if p and str(p).startswith("$SKILL/"):   # skill ile gelen ortak dosyalar (doku, sis, kapanış)
            return str(skill_root / str(p)[len("$SKILL/"):])
        return str((base / p).resolve()) if p and not Path(p).is_absolute() else p
    shot["voiceover"] = fix(shot.get("voiceover"))
    if shot.get("music"):
        shot["music"]["file"] = fix(shot["music"].get("file"))
    shot["sfx"] = {k: fix(v) for k, v in shot.get("sfx", {}).items()}
    for sc in shot["scenes"]:
        if sc.get("image"):
            sc["image"] = fix(sc["image"])
        if sc.get("video"):
            sc["video"] = fix(sc["video"])
        for k in ("image2", "bg", "outline"):
            if sc.get(k):
                sc[k] = fix(sc[k])
    if shot.get("outro") and shot["outro"].get("video"):
        shot["outro"]["video"] = fix(shot["outro"]["video"])
    lk = shot.get("look") or {}
    if lk.get("fog"):
        lk["fog"] = [fix(x) for x in lk["fog"]]
    if lk.get("backdrop"):
        lk["backdrop"] = fix(lk["backdrop"])
    for o in lk.get("overlays", []):
        o["file"] = fix(o["file"])
    if shot.get("outro") and shot["outro"].get("image"):
        shot["outro"]["image"] = fix(shot["outro"]["image"])
    tl = build(shot, a.words, fix(a.audio) if a.audio else None)
    tl["look"] = shot.get("look") or {}
    Path(a.out).write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.out}: {len(tl['scenes'])} sahne, {len(tl['captions'])} altyazı, {tl['duration']:.1f} sn")
    for s in tl["scenes"]:
        print(f"  {s['id']:>5} {s['start']:6.2f}-{s['end']:6.2f} ({s['duration']:.2f}s) "
              f"{s.get('transition', 'cut'):<13} {s.get('narration', '')[:60]}")
    for w in tl["warnings"]:
        print("⚠", w)


if __name__ == "__main__":
    main()
