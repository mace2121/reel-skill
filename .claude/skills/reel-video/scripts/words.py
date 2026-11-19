#!/usr/bin/env python3
"""Seslendirmeden kelime zamanları (yerel, ücretsiz): faster-whisper.

  words.py assets/vo.mp3 -o assets/words.json [--model small] [--prompt "özel isimler, terimler"]

Ses ffmpeg ile çözülüp numpy dizisi olarak verilir (faster-whisper'ın PyAV yolu bu ortamda hata veriyor).
"""
import argparse, json, subprocess
import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("-o", "--out", default="assets/words.json")
ap.add_argument("--model", default="small"); ap.add_argument("--lang", default="tr"); ap.add_argument("--prompt", default=None)
a = ap.parse_args()
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
segs, _ = WhisperModel(a.model, compute_type="int8").transcribe(np.frombuffer(raw, np.float32), language=a.lang, word_timestamps=True, initial_prompt=a.prompt)
ws = [{"word": w.word.strip(), "start": round(float(w.start), 3), "end": round(float(w.end), 3)} for s in segs for w in s.words]
json.dump(ws, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
print(len(ws), "kelime:", " ".join(w["word"] for w in ws))
