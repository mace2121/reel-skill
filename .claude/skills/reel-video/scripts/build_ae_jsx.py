#!/usr/bin/env python3
"""timeline.json -> build.jsx (After Effects ExtendScript)

build.jsx tek seferde şunları yapar: görselleri / sesleri içe aktarır, 1080x1920 ana kompozisyonu kurar,
her sahneye hareket (push / pan / parallax) ve çerçeve (tam / daire / polaroid / bölünmüş) verir,
geçişleri (blur whip, zoom blur, flash, fade, ışık sızması, daire açılış, kayma) ayar katmanlarıyla yapar,
başlıkları ve altyazıları kelime zamanlarına göre yerleştirir, ses efektlerini koyar, stil gradını ekler,
render kuyruğuna H.264 ekler ve projeyi .aep olarak kaydeder.

Kullanım:
  python3 build_ae_jsx.py timeline.json -o build/build.jsx --aep build/reel.aep --mp4 build/reel.mp4 [--render-now]

Çalıştırma (After Effects kapalıyken veya açıkken):
  Windows: "C:\\Program Files\\Adobe\\Adobe After Effects 2025\\Support Files\\AfterFX.exe" -r build\\build.jsx
  macOS:   osascript -e 'tell application "Adobe After Effects 2025" to DoScriptFile "/abs/build/build.jsx"'
Render:
  aerender -project build/reel.aep -comp REEL -output build/reel.mp4
"""
import argparse
import json
from pathlib import Path

from styles import color, resolve

POS_Y = {"top": 0.20, "upper": 0.30, "center": 0.45, "lower": 0.60, "bottom": 0.66}


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def prepare(tl, aep, mp4, render_now, om_template):
    st = resolve(tl.get("style", "earn"), {"fonts": tl.get("fonts") or {}, "caption": tl.get("caption") or {},
                                           "grade": tl.get("grade") or {}})
    W, H = tl["size"]
    cap = st["caption"]
    scenes = []
    for i, sc in enumerate(tl["scenes"]):
        s = dict(sc)
        s.setdefault("transition", st["default_transition"] if i else "cut")
        s.setdefault("move", st["default_move"])
        s.setdefault("frame", "full")
        if s.get("title"):
            t = dict(st["title"])
            t.update(s["title"])
            raw = t.get("text", "")
            t["text"] = raw if t.get("keep_case") else (tr_upper(raw) if tl["style"] == "earn" else raw)
            t["rgb"] = color(st, t.get("color"))
            _pos = t.get("pos", "top")   # ad ya da 0-1 arası sayı
            t["y"] = (_pos if isinstance(_pos, (int, float)) else POS_Y.get(_pos, 0.2)) * H
            longest = max((len(x) for x in t["text"].split("\n")), default=1)
            # Anton harf genişliği ~0.45 * punto; ekran genişliğinin %88'ini geçme
            t["size"] = int(min(t.get("size", st["title"]["size"]), 0.88 * W / max(longest * 0.47, 1)))
            t["font"] = st["fonts"]["title"] if t.get("anim") != "type" else st["fonts"]["caption"]
            if t.get("font_key"):
                t["font"] = st["fonts"].get(t["font_key"], t["font"])
            if t.get("over"):
                t["over"] = t["over"] if t.get("keep_case") else (tr_upper(t["over"]) if tl["style"] == "earn" else t["over"])
            s["title"] = t
        if s.get("marks"):   # fosforlu kalem / alt çizgi / elle çizilmiş elips
            s["marks"] = [dict(m, rgb=color(st, m.get("color", "yellow"))) for m in s["marks"]]
        if s.get("labels"):  # sahne içi küçük etiketler (isim, yıl, açıklama)
            lbs = []
            for lb in s["labels"]:
                lb = dict(lb)
                lb["rgb"] = color(st, lb.get("color", "white"))
                if lb.get("bg"):
                    lb["bg_rgb"] = color(st, lb["bg"])
                lb["font"] = st["fonts"].get(lb.get("font_key", "caption"), st["fonts"]["caption"])
                lbs.append(lb)
            s["labels"] = lbs
        if s.get("transition_color"):
            s["tr_rgb"] = color(st, s["transition_color"])
        if s.get("label"):  # polaroid altı / görsel altı küçük etiket
            s["label"] = tr_upper(s["label"]) if tl["style"] == "earn" else s["label"]
        if s.get("frame") == "scatter":   # kelimeler ekrana dağılır: kelime zamanlarını sahneye taşı
            s["words_t"] = [{"w": w["w"], "start": w["start"], "key": bool(w.get("key"))} for w in tl["words"]
                            if sc["start"] - 0.05 <= w["start"] < sc["end"]]
            s.setdefault("caption", False)
        scenes.append(s)
    mute = [(x["start"], x["end"]) for x in scenes if x.get("caption") is False]
    caps = []
    for c in tl["captions"]:
        if any(a - 0.05 <= c["start"] < b for a, b in mute):
            continue
        words = [tl["words"][i] for i in c["words"]]
        text = c["text"]
        # anahtar kelimelerin karakter aralıkları (vurgu rengi için)
        ranges, pos = [], 0
        for w in words:
            if w.get("key"):
                ranges.append([pos, pos + len(w["w"])])
            pos += len(w["w"]) + 1
        cy = crgb = ckey = None   # sahneye özel altyazı yüksekliği (0-1) ve renkleri (açık zeminli sahneler için)
        for x in scenes:
            if x["start"] - 0.05 <= c["start"] < x["end"]:
                if x.get("caption_y") is not None:
                    cy = x["caption_y"] * H
                if x.get("caption_color"):
                    crgb = color(st, x["caption_color"])
                if x.get("caption_key_color"):
                    ckey = color(st, x["caption_key_color"])
        caps.append({"text": text, "start": c["start"], "end": c["end"], "key": ranges, "y": cy, "rgb": crgb, "key_rgb": ckey})
    out = tl.get("outro")
    if out:
        out = dict(out)
        out["lines"] = [tr_upper(x) if tl["style"] == "earn" else x for x in out.get("text", [])]
    sfx = {k: v for k, v in (tl.get("sfx") or {}).items() if v}
    music = tl.get("music") or {}
    return {
        "title": (tl.get("title") or "REEL")[:60],
        "style": tl["style"],
        "W": W, "H": H, "fps": tl["fps"], "dur": tl["duration"],
        "vo": tl.get("voiceover"),
        "music": music.get("file"), "music_db": music.get("db", st["music_db"]),
        "sfx": sfx, "sfx_map": st["sfx_map"],
        "scenes": scenes,
        "look": tl.get("look") or {},
        "captions": caps,
        "cap": {"mode": cap["mode"], "size": cap["size"], "y": cap["y"] * H, "rgb": color(st, cap["color"]),
                "key_rgb": color(st, cap["key_color"]), "font": st["fonts"]["caption"],
                "pill_rgb": color(st, cap.get("pill", "#1E1E1E")), "pill_opacity": cap.get("pill_opacity", 78)},
        "grade": st["grade"],
        "colors": {k: color(st, k) for k in st["colors"]},
        "fonts": st["fonts"],
        "outro": out,
        "render": {"aep": str(Path(aep).resolve()), "mp4": str(Path(mp4).resolve()),
                   "log": str(Path(aep).resolve().with_suffix(".log.txt")),
                   "render_now": render_now, "om_template": om_template},
    }


JS = r"""
// ---- reel-video build.jsx (otomatik üretildi; elle düzenlemek yerine shotlist'i değiştirip yeniden üretin) ----
(function () {
var LOG = [];
function log(m) { LOG.push(m); }
function flushLog() {
  try { var f = new File(D.render.log); f.encoding = "UTF-8"; f.open("w"); f.write(LOG.join("\n")); f.close(); } catch (e) {}
}
try {
app.beginUndoGroup("reel-video build");
if (!app.project) app.newProject();
var proj = app.project;
var W = D.W, H = D.H, FPS = D.fps, DUR = D.dur;
var folder = proj.items.addFolder("reel_assets");
var cache = {};
function imp(p) {
  if (!p) return null;
  if (cache[p]) return cache[p];
  var f = new File(p);
  if (!f.exists) { log("EKSİK DOSYA: " + p); return null; }
  try {
    var it = proj.importFile(new ImportOptions(f));
    it.parentFolder = folder; cache[p] = it; return it;
  } catch (e) { log("İÇE AKTARILAMADI: " + p + " -> " + e); return null; }
}
var comp = proj.items.addComp("REEL", W, H, 1, DUR, FPS);
comp.bgColor = [0, 0, 0];
comp.motionBlur = true;
try { comp.shutterAngle = 200; } catch (e) {}
var MAIN = comp;
var scFolder = proj.items.addFolder("reel_scenes");
var TAIL = 0.4, LEAD = 0.3, prevSL = null;
var TRDB = (D.look && D.look.transition_db !== undefined) ? D.look.transition_db : -10;   // geçiş (whoosh) sesi düzeyi
// gerçek 3B kamera: sahneler uzayda istasyonlara dizilir, kamera aralarında uçar
var CAM = MAIN.layers.addCamera("KAMERA", [W / 2, H / 2]);
try { CAM.autoOrient = AutoOrientType.NO_AUTO_ORIENT; } catch (e) { log("kamera yönlendirme: " + e); }
var Z0 = CAM.property("ADBE Camera Options Group").property("ADBE Camera Zoom").value;
var KCAM = 0.955;   // kamera hafif yakın durur: sahne kenarları kadraja girmesin
var camP = P(CAM, "ADBE Position"), camRX = P(CAM, "ADBE Rotate X"), camRY = P(CAM, "ADBE Rotate Y"), camRZ = P(CAM, "ADBE Rotate Z");
var ST = { x: W / 2, y: H / 2, z: 0, r: 0 }, TRL = [], BACK = null, lastK = KCAM;
function camAt(st, k) { return [st.x, st.y, st.z - Z0 * (k || KCAM)]; }
if (D.look && D.look.backdrop) {   // sahneler arası boşlukta görünen koyu dokulu zemin (2B, en altta)
  var bki = imp(D.look.backdrop);
  if (bki) { BACK = MAIN.layers.add(bki); BACK.name = "BACKDROP"; span(BACK, 0, DUR); var bks = cover(bki, W, H) * 1.05; P(BACK, "ADBE Scale").setValue([bks, bks]); }
}

function T(l) { return l.property("ADBE Transform Group"); }
function P(l, n) { return T(l).property(n); }
function fx(l, match) { try { return l.property("ADBE Effect Parade").addProperty(match); } catch (e) { log("efekt yok: " + match); return null; } }
function fp(eff, match, idx) { if (!eff) return null; var p = null; try { p = eff.property(match); } catch (e) {} if (!p && idx) { try { p = eff.property(idx); } catch (e2) {} } return p; }
function key(prop, t, v) { if (prop) { try { prop.setValueAtTime(t, v); } catch (e) { var pn = "?"; try { pn = prop.name; } catch (e2) {} log("key hatası " + pn + ": " + e); } } }
function easeAll(prop, inf) {
  if (!prop) return;
  inf = inf || 70;
  for (var k = 1; k <= prop.numKeys; k++) {
    for (var n = 1; n <= 3; n++) {
      try {
        var a = [], b = [];
        for (var j = 0; j < n; j++) { a.push(new KeyframeEase(0, inf)); b.push(new KeyframeEase(0, inf)); }
        prop.setTemporalEaseAtKey(k, a, b); break;
      } catch (e) {}
    }
  }
}
function span(l, a, b) { l.inPoint = Math.max(0, a); l.outPoint = Math.min(DUR, b); }
function adj(name, a, b) {
  var s = comp.layers.addSolid([1, 1, 1], name, W, H, 1);
  s.adjustmentLayer = true; span(s, a, b); return s;
}
function solid(rgb, name, a, b) { var s = comp.layers.addSolid(rgb, name, W, H, 1); span(s, a, b); return s; }
function cover(it, w, h) { return Math.max(w / it.width, h / it.height) * 100; }
function setMatte(layer, matte) {
  try { layer.setTrackMatte(matte, TrackMatteType.ALPHA); }
  catch (e) { try { layer.trackMatteType = TrackMatteType.ALPHA; } catch (e2) { log("track matte kurulamadı"); } }
}
function addText(str, o) {
  var L = comp.layers.addText(str);
  var tp = L.property("ADBE Text Properties").property("ADBE Text Document");
  var d = tp.value;
  try { d.resetCharStyle(); } catch (e) {}
  d.fontSize = o.size; d.fillColor = o.rgb; d.applyFill = true;
  try { d.font = o.font; } catch (e) { log("font atanamadı: " + o.font); }
  if (o.stroke) { d.applyStroke = true; d.strokeColor = o.stroke; d.strokeWidth = o.strokeW || 6; d.strokeOverFill = false; }
  else { d.applyStroke = false; }
  d.justification = ParagraphJustification.CENTER_JUSTIFY;
  if (o.tracking !== undefined) d.tracking = o.tracking;
  if (o.leading) { try { d.autoLeading = false; d.leading = o.leading; } catch (e) {} }
  tp.setValue(d);
  try { if (tp.value.font !== o.font) log("FONT YOK, yerine " + tp.value.font + " kullanıldı (istenen " + o.font + ")"); } catch (e) {}
  // anchor'ı metnin görsel merkezine al
  P(L, "ADBE Anchor Point").expression = "var r=sourceRectAtTime(time,false);[r.left+r.width/2,r.top+r.height/2]";
  P(L, "ADBE Position").setValue([o.x, o.y]);
  return L;
}
function colorRange(L, a, b, rgb) {
  try {
    var anim = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
    anim.property("ADBE Text Animator Properties").addProperty("ADBE Text Fill Color").setValue(rgb);
    var sel = anim.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    sel.property("ADBE Text Range Advanced").property("ADBE Text Range Units").setValue(2);
    sel.property("ADBE Text Index Start").setValue(a);
    sel.property("ADBE Text Index End").setValue(b);
  } catch (e) { log("renk aralığı kurulamadı: " + e); }
}
function typeOn(L, a, d) {
  try {
    var anim = L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
    anim.property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity").setValue(0);
    var sel = anim.property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    var st = sel.property("ADBE Text Percent Start");
    key(st, a, 0); key(st, a + d, 100);
  } catch (e) { log("type-on kurulamadı: " + e); }
}
function shapeRect(name, w, h, rgb, round, strokeRgb, strokeW) {
  var L = comp.layers.addShape(); L.name = name;
  var g = L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
  var c = g.property("ADBE Vectors Group");
  var r = c.addProperty("ADBE Vector Shape - Rect");
  r.property("ADBE Vector Rect Size").setValue([w, h]);
  r.property("ADBE Vector Rect Roundness").setValue(round || 0);
  if (rgb) { c.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(rgb); }
  if (strokeRgb) {
    var s = c.addProperty("ADBE Vector Graphic - Stroke");
    s.property("ADBE Vector Stroke Color").setValue(strokeRgb);
    s.property("ADBE Vector Stroke Width").setValue(strokeW || 4);
  }
  P(L, "ADBE Position").setValue([W / 2, H / 2]);
  // dolgu / çizgi eklemek önceki referansı geçersiz kılar: şekli yeniden al
  try { r = L.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Shape - Rect"); } catch (e) {}
  return { layer: L, rect: r };
}
function shapeEllipse(name, d, rgb, strokeRgb, strokeW) {
  var L = comp.layers.addShape(); L.name = name;
  var g = L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
  var c = g.property("ADBE Vectors Group");
  var e = c.addProperty("ADBE Vector Shape - Ellipse");
  e.property("ADBE Vector Ellipse Size").setValue([d, d]);
  if (rgb) { c.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(rgb); }
  if (strokeRgb) {
    var s = c.addProperty("ADBE Vector Graphic - Stroke");
    s.property("ADBE Vector Stroke Color").setValue(strokeRgb);
    s.property("ADBE Vector Stroke Width").setValue(strokeW || 4);
  }
  P(L, "ADBE Position").setValue([W / 2, H / 2]);
  try { e = L.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Shape - Ellipse"); } catch (e3) {}
  return { layer: L, ellipse: e };
}
function lastAnim(L) { var g = L.property("ADBE Text Properties").property("ADBE Text Animators"); return g.property(g.numProperties); }
// kelime kelime, bulanıklıktan netleşerek gelen yazı
function wordsOn(L, a, d) {
  try {
    L.property("ADBE Text Properties").property("ADBE Text Animators").addProperty("ADBE Text Animator");
    lastAnim(L).property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity").setValue(0);
    try { lastAnim(L).property("ADBE Text Animator Properties").addProperty("ADBE Text Blur").setValue([45, 45]); } catch (e) {}
    lastAnim(L).property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    try { lastAnim(L).property("ADBE Text Selectors").property(1).property("ADBE Text Range Advanced").property("ADBE Text Range Type2").setValue(3); } catch (e) { log("kelime bazlı seçici: " + e); }
    var st = lastAnim(L).property("ADBE Text Selectors").property(1).property("ADBE Text Percent Start");
    key(st, a, 0); key(st, a + d, 100);
  } catch (e) { log("words-on kurulamadı: " + e); }
}
// sis: paketlerden hazırlanan klipler, ekran (screen) karışımıyla
function addFog(a, b, amt) {
  var files = (D.look && D.look.fog) ? D.look.fog : [];
  for (var f = 0; f < files.length; f++) {
    var fi = imp(files[f]); if (!fi) continue;
    var FL = comp.layers.add(fi); FL.name = "FOG " + f;
    var offs = (a * 0.37 + f * 2.3) % Math.max(0.5, fi.duration - (b - a) - 0.5);
    FL.startTime = a - offs; span(FL, a, b);
    FL.blendingMode = BlendingMode.SCREEN;
    P(FL, "ADBE Scale").setValue([cover(fi, W, H) * (f % 2 ? -1 : 1), cover(fi, W, H)]);
    P(FL, "ADBE Opacity").setValue(Math.min(100, amt * 100 * (f ? 0.6 : 1)));
  }
}
var sfxCount = 0;
function sfx(name, t, db) {
  var p = D.sfx[name]; if (!p) return;
  var it = imp(p); if (!it) return;
  var L = comp.layers.add(it); L.startTime = Math.max(0, t); L.name = "SFX " + name;
  try { L.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([db || -6, db || -6]); } catch (e) {}
  sfxCount++;
}

// ---- hareket: base ölçek s0, hareket tipi, süre [a,b]
function applyMove(L, move, s0, a, b, cx, cy) {
  var sc = P(L, "ADBE Scale"), ps = P(L, "ADBE Position"), rt = P(L, "ADBE Rotate Z");
  var dx = W * 0.06, dy = H * 0.04;
  cx = cx || W / 2; cy = cy || H / 2;
  if (move === "push_in") { key(sc, a, [s0, s0]); key(sc, b, [s0 * 1.14, s0 * 1.14]); }
  else if (move === "pull_out") { key(sc, a, [s0 * 1.16, s0 * 1.16]); key(sc, b, [s0 * 1.02, s0 * 1.02]); }
  else if (move === "pan_left") { sc.setValue([s0 * 1.15, s0 * 1.15]); key(ps, a, [cx + dx, cy]); key(ps, b, [cx - dx, cy]); }
  else if (move === "pan_right") { sc.setValue([s0 * 1.15, s0 * 1.15]); key(ps, a, [cx - dx, cy]); key(ps, b, [cx + dx, cy]); }
  else if (move === "pan_up") { sc.setValue([s0 * 1.15, s0 * 1.15]); key(ps, a, [cx, cy + dy]); key(ps, b, [cx, cy - dy]); }
  else if (move === "pan_down") { sc.setValue([s0 * 1.15, s0 * 1.15]); key(ps, a, [cx, cy - dy]); key(ps, b, [cx, cy + dy]); }
  else if (move === "parallax") {
    key(sc, a, [s0 * 1.06, s0 * 1.06]); key(sc, b, [s0 * 1.17, s0 * 1.17]);
    key(ps, a, [cx - dx * 0.4, cy + dy * 0.3]); key(ps, b, [cx + dx * 0.4, cy - dy * 0.3]);
    key(rt, a, -0.8); key(rt, b, 0.8);
  }
  else { sc.setValue([s0 * 1.02, s0 * 1.02]); }
  easeAll(sc, 33); easeAll(ps, 33); easeAll(rt, 33);
}
function popIn(L, t, from) {
  var sc = P(L, "ADBE Scale"), op = P(L, "ADBE Opacity");
  key(sc, t, [from, from]); key(sc, t + 0.16, [106, 106]); key(sc, t + 0.26, [100, 100]);
  key(op, t, 0); key(op, t + 0.08, 100);
  easeAll(sc, 60);
}
function blurredCopy(it, a, b) {
  var L = comp.layers.add(it); span(L, a, b);
  var s0 = cover(it, W, H) * 1.1; P(L, "ADBE Scale").setValue([s0, s0]);
  var g = fx(L, "ADBE Gaussian Blur 2"); var p = fp(g, "ADBE Gaussian Blur 2-0001", 1); if (p) p.setValue(45);
  var br = fx(L, "ADBE Brightness & Contrast 2"); var bp = fp(br, "ADBE Brightness & Contrast 2-0001", 1); if (bp) bp.setValue(-45);
  return L;
}

// ---- sahneler (alttan üste: her yeni katman en üste eklenir, gelen sahne gidenin üstünde kalır)
var OVL = 0.3; // fade / leak / daire geçişlerinde üst üste binme
for (var i = 0; i < D.scenes.length; i++) {
  var sc = D.scenes[i];
  var a = sc.start, b = sc.end;
  var tr = sc.transition || "cut";
  var aIn = a;
  var a0 = i > 0 ? a - LEAD : a;
  var SCOMP = proj.items.addComp("SC " + sc.id, W, H, 1, DUR, FPS); SCOMP.parentFolder = scFolder;
  SCOMP.bgColor = [0, 0, 0]; SCOMP.motionBlur = true; try { SCOMP.shutterAngle = 200; } catch (e) {}
  comp = SCOMP;
  var it = imp(sc.video || sc.image);
  var L, cxy = [W / 2, H / 2];
  if (!it) {
    L = solid([0.25, 0.22, 0.2], "EKSİK " + sc.id, aIn, b);
    span(addText(sc.id + " görsel eksik", { size: 60, rgb: [1, 1, 1], font: D.fonts.caption, x: W / 2, y: H / 2 }), aIn, b);
    comp = MAIN; var SLm = MAIN.layers.add(SCOMP); SLm.name = "SCENE " + sc.id; span(SLm, a, b + TAIL); prevSL = SLm;
    continue;
  }
  var frame = sc.frame || "full";
  if (frame === "full") {
    L = comp.layers.add(it); L.name = sc.id;
    if (sc.video) L.startTime = aIn;
    span(L, a0, b + TAIL);
    if (sc.video && it.duration < b - aIn) log("UYARI: " + sc.id + " videosu sahneden kısa (" + it.duration.toFixed(2) + " sn < " + (b - aIn).toFixed(2) + " sn)");
    applyMove(L, sc.move, cover(it, W, H), aIn, b);
  } else if (frame === "circle" || frame === "polaroid") {
    var bgIt = sc.bg ? imp(sc.bg) : null;
    if (bgIt) { var BG = comp.layers.add(bgIt); span(BG, a0, b + TAIL); applyMove(BG, "push_in", cover(bgIt, W, H), aIn, b); }
    else { blurredCopy(it, a0, b + TAIL); }
    var NUL = comp.layers.addNull(DUR); NUL.name = sc.id + "_grp"; span(NUL, a0, b + TAIL);
    P(NUL, "ADBE Position").setValue([W / 2, H * 0.46]);
    var cy = H * 0.46;
    if (frame === "circle") {
      var dia = W * 0.78;
      var ring = shapeEllipse(sc.id + "_ring", dia + 46, null, D.colors.white, 3).layer; span(ring, a0, b + TAIL);
      P(ring, "ADBE Position").setValue([W / 2, cy]); P(ring, "ADBE Opacity").setValue(70);
      try {
        var rst = ring.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Graphic - Stroke");
        rst.property("ADBE Vector Stroke Dashes").addProperty("ADBE Vector Stroke Dash 1").setValue(16);
        ring.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Graphic - Stroke").property("ADBE Vector Stroke Dashes").addProperty("ADBE Vector Stroke Gap 1").setValue(13);
      } catch (e) { log("kesik halka: " + e); }
      P(ring, "ADBE Rotate Z").expression = "time*14";
      L = comp.layers.add(it); L.name = sc.id; span(L, a0, b + TAIL);
      P(L, "ADBE Position").setValue([W / 2, cy]);
      var s0 = cover(it, dia, dia);
      applyMove(L, sc.move === "parallax" ? "push_in" : sc.move, s0, aIn, b, W / 2, cy);
      var m = shapeEllipse(sc.id + "_matte", dia, [1, 1, 1]).layer; span(m, a0, b + TAIL);
      P(m, "ADBE Position").setValue([W / 2, cy]);
      setMatte(L, m);
      ring.parent = NUL; m.parent = NUL; L.parent = NUL;
    } else {
      var cw = W * 0.66, ch = cw * 1.18, iw = cw * 0.88, ih = iw;
      var card = shapeRect(sc.id + "_card", cw, ch, [0.97, 0.96, 0.93], 6).layer; span(card, a0, b + TAIL);
      P(card, "ADBE Position").setValue([W / 2, cy]);
      var ds = fx(card, "ADBE Drop Shadow"); var dsd = fp(ds, "ADBE Drop Shadow-0005", 5); if (dsd) dsd.setValue(40); var dso = fp(ds, "ADBE Drop Shadow-0002", 2); if (dso) dso.setValue(140);
      var icy = cy - (ch - ih) / 2 + cw * 0.06;
      L = comp.layers.add(it); L.name = sc.id; span(L, a0, b + TAIL);
      P(L, "ADBE Position").setValue([W / 2, icy]);
      applyMove(L, "push_in", cover(it, iw, ih), aIn, b, W / 2, icy);
      var pm = shapeRect(sc.id + "_matte", iw, ih, [1, 1, 1], 0).layer; span(pm, a0, b + TAIL);
      P(pm, "ADBE Position").setValue([W / 2, icy]);
      setMatte(L, pm);
      card.parent = NUL; pm.parent = NUL; L.parent = NUL;
      if (sc.label) {
        var lab = addText(sc.label, { size: 44, rgb: [0.15, 0.13, 0.12], font: D.fonts.title, x: W / 2, y: cy + ch / 2 - cw * 0.1 });
        span(lab, a0, b + TAIL); lab.parent = NUL;
      }
      if (sc.board) {
        var py = cy - ch / 2 + cw * 0.035;
        var thr = shapeRect(sc.id + "_thread", W * 2.2, 5, [0.82, 0.08, 0.08], 0).layer; span(thr, a0, b + TAIL);
        P(thr, "ADBE Position").setValue([W / 2, py]);
        var pin = shapeEllipse(sc.id + "_pin", 38, [0.9, 0.1, 0.1]).layer; span(pin, a0, b + TAIL);
        P(pin, "ADBE Position").setValue([W / 2, py]);
        var pds = fx(pin, "ADBE Drop Shadow"); var pdd = fp(pds, "ADBE Drop Shadow-0005", 5); if (pdd) pdd.setValue(8);
        pin.parent = NUL;
      }
      key(P(NUL, "ADBE Rotate Z"), aIn, sc.board ? 26 : (sc.tilt !== undefined ? sc.tilt - 4 : -9));
      key(P(NUL, "ADBE Rotate Z"), aIn + 0.4, sc.tilt !== undefined ? sc.tilt : -4);
      easeAll(P(NUL, "ADBE Rotate Z"), 70);
    }
    if (sc.board && frame === "polaroid") {
      var npz = P(NUL, "ADBE Position");
      key(npz, aIn - 0.08, [W / 2 + W * 0.22, H * 1.28]); key(npz, aIn + 0.34, [W / 2, H * 0.46]); easeAll(npz, 85);
    } else { popIn(NUL, aIn, 70); }
    sfx(D.sfx_map.pop, aIn, -8);
  } else if (frame === "cutout" && sc.registered) {
    // hizalı cutout: figür, arka plandaki yerinde durur (aynı boyutta iki görsel); kontur çizilir, figür öne çıkar, istenirse sallanır
    var rbIt = imp(sc.bg);
    var rcs = cover(it, W, H);
    if (rbIt) { var RBG = comp.layers.add(rbIt); RBG.name = sc.id + "_bg"; span(RBG, a0, b + TAIL); P(RBG, "ADBE Scale").setValue([cover(rbIt, W, H), cover(rbIt, W, H)]); }
    var anc = sc.anchor || [0.5, 1.0];
    var rpos = [W / 2 + (anc[0] - 0.5) * it.width * rcs / 100, H / 2 + (anc[1] - 0.5) * it.height * rcs / 100];
    L = comp.layers.add(it); L.name = sc.id; span(L, a0, b + TAIL);
    P(L, "ADBE Anchor Point").setValue([it.width * anc[0], it.height * anc[1]]);
    P(L, "ADBE Position").setValue(rpos);
    var pop = sc.pop || {}; var pAt = a + (pop.at === undefined ? 0.9 : pop.at), pSc = pop.scale || 1.06, pLift = pop.lift || 0;
    var rsc = P(L, "ADBE Scale"); key(rsc, pAt, [rcs, rcs]); key(rsc, pAt + 0.45, [rcs * pSc, rcs * pSc]); key(rsc, b + TAIL, [rcs * (pSc + 0.03), rcs * (pSc + 0.03)]); easeAll(rsc, 75);
    if (pLift) { var rps = P(L, "ADBE Position"); key(rps, pAt, rpos); key(rps, pAt + 0.45, [rpos[0], rpos[1] - H * pLift]); easeAll(rps, 75); }
    if (sc.sway) {
      P(L, "ADBE Rotate Z").expression = "var t0=" + (pAt + 0.2).toFixed(3) + "; time<t0 ? 0 : Math.sin((time-t0)*" + (sc.sway_speed || 2.6) + ")*" + sc.sway + "*Math.min(1,(time-t0)/0.5)";
    }
    var rds = fx(L, "ADBE Drop Shadow"); var rdo = fp(rds, "ADBE Drop Shadow-0002", 2); if (rdo) rdo.setValue(0);
    try { var rdo2 = L.property("ADBE Effect Parade").property(1).property("ADBE Drop Shadow-0002"); key(rdo2, pAt, 0); key(rdo2, pAt + 0.45, 190); } catch (e) {}
    try { L.property("ADBE Effect Parade").property(1).property("ADBE Drop Shadow-0005").setValue(60); L.property("ADBE Effect Parade").property(1).property("ADBE Drop Shadow-0004").setValue(26); } catch (e) {}
    if (sc.outline) {
      var olIt = imp(sc.outline);
      if (olIt) {
        var OLN = comp.layers.add(olIt); OLN.name = sc.id + "_kontur"; span(OLN, a0, b + TAIL);
        P(OLN, "ADBE Anchor Point").setValue([olIt.width * anc[0], olIt.height * anc[1]]);
        P(OLN, "ADBE Position").setValue(rpos); P(OLN, "ADBE Scale").setValue([rcs, rcs]);
        OLN.parent = L;
        var oAt = a + (sc.outline_at === undefined ? 0.35 : sc.outline_at);
        var lw = fx(OLN, "ADBE Linear Wipe"); var lwc = fp(lw, "ADBE Linear Wipe-0001", 1);
        key(lwc, oAt, 100); key(lwc, oAt + 0.5, 0);
        try { OLN.property("ADBE Effect Parade").property(1).property("ADBE Linear Wipe-0002").setValue(sc.outline_angle === undefined ? 180 : sc.outline_angle); } catch (e) {}
        try { OLN.property("ADBE Effect Parade").property(1).property("ADBE Linear Wipe-0003").setValue(40); } catch (e) {}
      }
    }
    sfx(D.sfx_map.pop, pAt, -8);
  } else if (frame === "cutout") {
    // cutout: arka plan + alfa kanallı figür (alt kenara oturur, alttan girer); başlık istenirse figürün arkasında
    var cbIt = sc.bg ? imp(sc.bg) : null;
    if (cbIt) {
      var CBG = comp.layers.add(cbIt); CBG.name = sc.id + "_bg"; span(CBG, a0, b + TAIL);
      applyMove(CBG, "push_in", cover(cbIt, W, H), aIn, b);
      var cbr = fx(CBG, "ADBE Brightness & Contrast 2"); var cbp = fp(cbr, "ADBE Brightness & Contrast 2-0001", 1); if (cbp) cbp.setValue(-28);
      var cgb = fx(CBG, "ADBE Gaussian Blur 2"); var cgp = fp(cgb, "ADBE Gaussian Blur 2-0001", 1); if (cgp) cgp.setValue(4);
    } else { solid([0.09, 0.085, 0.085], sc.id + "_bg", a0, b + TAIL); }
    L = comp.layers.add(it); L.name = sc.id; span(L, a0, b + TAIL);
    var cs0 = cover(it, W, H);
    P(L, "ADBE Anchor Point").setValue([it.width / 2, it.height]);
    var cps = P(L, "ADBE Position"), csc = P(L, "ADBE Scale");
    key(cps, aIn, [W / 2 - W * 0.03, H + H * 0.14]); key(cps, aIn + 0.24, [W / 2, H]); key(cps, b, [W / 2 + W * 0.012, H]);
    key(csc, aIn, [cs0, cs0]); key(csc, b, [cs0 * 1.07, cs0 * 1.07]);
    easeAll(cps, 75); easeAll(csc, 33);
    var cds = fx(L, "ADBE Drop Shadow"); var cdd = fp(cds, "ADBE Drop Shadow-0005", 5); if (cdd) cdd.setValue(50); var cdo = fp(cds, "ADBE Drop Shadow-0002", 2); if (cdo) cdo.setValue(170);
    sfx(D.sfx_map.pop, aIn, -8);
  } else if (frame === "scatter") {
    // koyu dokulu zemin; anlatımın kelimeleri söylendikleri anda ekrana dağılarak belirir
    L = comp.layers.add(it); L.name = sc.id; span(L, a0, b + TAIL);
    applyMove(L, "push_in", cover(it, W, H), a, b + TAIL);
    var slots = sc.slots || [[0.50, 0.37], [0.33, 0.43], [0.64, 0.45], [0.46, 0.51], [0.62, 0.56], [0.36, 0.59], [0.53, 0.64], [0.67, 0.67], [0.40, 0.70]];
    var wl = sc.words_t || [];
    for (var wi = 0; wi < wl.length; wi++) {
      var ww = wl[wi], sl = slots[wi % slots.length];
      var WL = addText(ww.w, { size: sc.word_size || 76, rgb: ww.key ? D.colors.red : [0.96, 0.95, 0.92], font: D.fonts.serif, x: W * sl[0], y: H * sl[1] });
      WL.name = "W " + sc.id + " " + wi; span(WL, ww.start, b + TAIL);
      var wo = P(WL, "ADBE Opacity"); key(wo, ww.start, 0); key(wo, ww.start + 0.2, 100);
      var wsx = P(WL, "ADBE Scale"); key(wsx, ww.start, [86, 86]); key(wsx, b + TAIL, [106, 106]);
      var wb = fx(WL, "ADBE Gaussian Blur 2"); var wbp = fp(wb, "ADBE Gaussian Blur 2-0001", 1); key(wbp, ww.start, 26); key(wbp, ww.start + 0.25, 0);
    }
  } else if (frame === "split") {
    // split: sol yarı sc.image, sağ yarı sc.image2, ortada parlayan çizgi
    var it2 = imp(sc.image2);
    L = comp.layers.add(it); L.name = sc.id + "_A"; span(L, a0, b + TAIL);
    applyMove(L, "pan_right", cover(it, W, H), aIn, b);
    if (it2) {
      var L2 = comp.layers.add(it2); L2.name = sc.id + "_B"; span(L2, a0, b + TAIL);
      applyMove(L2, "pan_left", cover(it2, W, H), aIn, b);
      var half = shapeRect(sc.id + "_half", W * 0.5 + 400, H * 1.4, [1, 1, 1], 0).layer; span(half, a0, b + TAIL);
      P(half, "ADBE Position").setValue([W * 0.75 + 200, H / 2]); P(half, "ADBE Rotate Z").setValue(8);
      setMatte(L2, half);
      var line = shapeRect(sc.id + "_line", 8, H * 1.4, [1, 1, 1], 0).layer; span(line, a0, b + TAIL);
      P(line, "ADBE Position").setValue([W / 2, H / 2]); P(line, "ADBE Rotate Z").setValue(8);
      var gl = fx(line, "ADBE Glo2");
    }
  }

  if (sc.fog) addFog(a0, b + TAIL, sc.fog);
  if (sc.tag) {
    var TG = addText(sc.tag, { size: 30, rgb: [1, 1, 1], font: D.fonts.caption, x: W / 2, y: H * 0.94 });
    TG.name = "TAG " + sc.id; span(TG, a0, b + TAIL); P(TG, "ADBE Opacity").setValue(72);
  }

  // ---- sahne başlığı
  if (sc.title) {
    var t = sc.title, ta = a + (t.delay || 0.08), tb = t.until ? a + t.until : b;
    var stampBox = null;
    var TL = addText(t.text, { size: t.size, rgb: t.rgb, font: t.font, x: W / 2, y: t.y, tracking: t.tracking || 0, leading: t.size * 0.95 });
    // figürün arkasında kalacak başlıklar sonda en üste taşınmasın diye ayrı adlandırılır
    var tBehind = !!(t.behind && frame === "cutout");
    TL.name = (tBehind ? "BTITLE " : "TITLE ") + sc.id; span(TL, ta, tb);
    var sh = fx(TL, "ADBE Drop Shadow");
    var sho = fp(sh, "ADBE Drop Shadow-0002", 2); if (sho) sho.setValue(160);
    var shs = fp(sh, "ADBE Drop Shadow-0005", 5); if (shs) shs.setValue(18);
    if (t.rotate) P(TL, "ADBE Rotate Z").setValue(t.rotate);
    if (t.anim === "slam" || t.anim === "stamp") {
      var tsc = P(TL, "ADBE Scale"), top = P(TL, "ADBE Opacity");
      key(tsc, ta, [260, 260]); key(tsc, ta + 0.16, [96, 96]); key(tsc, ta + 0.24, [100, 100]);
      key(top, ta, 0); key(top, ta + 0.06, 100); easeAll(tsc, 85);
      var tbl = fx(TL, "ADBE Motion Blur"); var tbll = fp(tbl, "ADBE Motion Blur-0002", 2);
      key(tbll, ta, 80); key(tbll, ta + 0.16, 0);
      sfx(t.anim === "stamp" ? D.sfx_map.stamp : D.sfx_map.slam, ta, -6);
      if (t.anim === "stamp") {
        if (!t.rotate) P(TL, "ADBE Rotate Z").setValue(-6);
        var box = shapeRect((tBehind ? "BSTAMP box " : "STAMP box ") + sc.id, 100, 100, null, 0, t.rgb, 7); span(box.layer, ta, tb);
        stampBox = box.layer;
        box.rect.property("ADBE Vector Rect Size").expression = 'var t=thisComp.layer("' + TL.name + '");var r=t.sourceRectAtTime(time,false);[r.width+60,r.height+36]';
        P(box.layer, "ADBE Position").expression = 'thisComp.layer("' + TL.name + '").transform.position';
        P(box.layer, "ADBE Rotate Z").expression = 'thisComp.layer("' + TL.name + '").transform.rotation';
        P(box.layer, "ADBE Scale").expression = 'thisComp.layer("' + TL.name + '").transform.scale';
        P(box.layer, "ADBE Opacity").expression = 'thisComp.layer("' + TL.name + '").transform.opacity';
      }
    } else if (t.anim === "pop") {
      popIn(TL, ta, 0); sfx(D.sfx_map.pop, ta, -8);
    } else if (t.anim === "words") {
      wordsOn(TL, ta, t.words_dur || Math.min(0.9, (tb - ta) * 0.5)); sfx(D.sfx_map.type, ta, -12);
    } else if (t.anim === "type") {
      typeOn(TL, ta, Math.min(0.9, (tb - ta) * 0.6)); sfx(D.sfx_map.type, ta, -10);
    } else {
      var fo2 = P(TL, "ADBE Opacity"); key(fo2, ta, 0); key(fo2, ta + 0.3, 100);
      var fs2 = P(TL, "ADBE Scale"); key(fs2, ta, [94, 94]); key(fs2, tb, [104, 104]);
    }
    if (t.ribbon) {
      var rbc = t.ribbon_rgb || [0.12, 0.30, 0.27];
      var rbb = shapeRect("RIBBON " + sc.id, 100, 100, rbc, 0); span(rbb.layer, ta, tb);
      rbb.rect.property("ADBE Vector Rect Size").expression = 'var t=thisComp.layer("' + TL.name + '");var r=t.sourceRectAtTime(time,false);[r.width+70,r.height+34]';
      P(rbb.layer, "ADBE Position").expression = 'thisComp.layer("' + TL.name + '").transform.position';
      P(rbb.layer, "ADBE Rotate Z").setValue(-1.5);
      var rbo = P(rbb.layer, "ADBE Opacity"); key(rbo, ta, 0); key(rbo, ta + 0.25, 92); key(rbo, Math.max(ta + 0.3, tb - 0.1), 92); key(rbo, tb, 0);
      rbb.layer.moveAfter(TL);
    }
    if (D.look && D.look.title_glow) { try { fx(TL, "ADBE Glo2"); } catch (e) {} }
    var SB = null;
    if (t.sub) {
      var sbs = t.sub_size || 52;
      SB = addText(t.sub, { size: sbs, rgb: [1, 1, 1], font: D.fonts[t.sub_font || "caption"] || D.fonts.caption, x: W / 2, y: t.y + t.size * 0.52 + sbs * 0.85 });
      SB.name = "SUB " + sc.id; span(SB, ta, tb);
      var sbh = fx(SB, "ADBE Drop Shadow"); var sbo = fp(sbh, "ADBE Drop Shadow-0002", 2); if (sbo) sbo.setValue(170);
      wordsOn(SB, ta + 0.3, Math.min(0.8, (tb - ta) * 0.4));
      var sbf = P(SB, "ADBE Opacity"); key(sbf, tb - 0.1, 100); key(sbf, tb, 0);
    }
    var OV = null;
    if (t.over) {   // büyük başlığın üstünde küçük beyaz satır (earn: "HE DEMANDED" / "$200,000")
      var ovs = t.over_size || Math.round(t.size * 0.42);
      OV = addText(t.over, { size: ovs, rgb: [1, 1, 1], font: t.font, x: W / 2, y: t.y - t.size * 0.52 - ovs * 0.62 });
      OV.name = "OVER " + sc.id; span(OV, Math.max(a, ta - 0.25), tb);
      var ovh = fx(OV, "ADBE Drop Shadow"); var ovo = fp(ovh, "ADBE Drop Shadow-0002", 2); if (ovo) ovo.setValue(170);
      if (t.rotate) P(OV, "ADBE Rotate Z").setValue(t.rotate);
      popIn(OV, Math.max(a, ta - 0.25), 0);
      var ovf = P(OV, "ADBE Opacity"); key(ovf, Math.max(ta + 0.3, tb - 0.1), 100); key(ovf, tb, 0);
    }
    // figürün arkasındaki başlık: metni (ve damga kutusunu) figür katmanının altına taşı
    if (t.behind && frame === "cutout" && L) {
      try { TL.moveAfter(L); if (stampBox) stampBox.moveAfter(L); if (SB) SB.moveAfter(L); if (OV) OV.moveAfter(L); } catch (e) { log("başlık arkaya alınamadı " + sc.id + ": " + e); }
    }
    // çıkış
    var outO = P(TL, "ADBE Opacity"); key(outO, Math.max(ta + 0.3, tb - 0.1), 100); key(outO, tb, 0);
  }

  // ---- işaretler: fosforlu kalem süpürmesi, alt çizgi, elle çizilmiş elips (konumlar 0-1 kesir; x,y = merkez)
  if (sc.marks) {
    for (var mi = 0; mi < sc.marks.length; mi++) {
      var mk0 = sc.marks[mi], ma = a + (mk0.at === undefined ? 0.3 : mk0.at), mb2 = mk0.until ? a + mk0.until : b + TAIL, md = mk0.dur || 0.35;
      var mw = (mk0.w || 0.5) * W, mh = (mk0.h || 0.03) * H, mx = (mk0.x === undefined ? 0.5 : mk0.x) * W, my = (mk0.y === undefined ? 0.5 : mk0.y) * H;
      try {
        if (mk0.type === "ellipse") {
          var me = shapeEllipse("MARK " + sc.id + " " + mi, 100, null, mk0.rgb, mk0.stroke || 7);
          me.ellipse.property("ADBE Vector Ellipse Size").setValue([mw, mh]);
          span(me.layer, ma, mb2); P(me.layer, "ADBE Position").setValue([mx, my]);
          P(me.layer, "ADBE Rotate Z").setValue(mk0.rotate === undefined ? -8 : mk0.rotate);
          me.layer.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").addProperty("ADBE Vector Filter - Trim");
          var mte = me.layer.property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property("ADBE Vector Filter - Trim").property("ADBE Vector Trim End");
          key(mte, ma, 0); key(mte, ma + md, 100);
        } else {
          var isU = mk0.type === "underline"; if (isU && !mk0.h) mh = H * 0.006;
          var mr = shapeRect("MARK " + sc.id + " " + mi, mw, mh, mk0.rgb, 0);
          mr.rect.property("ADBE Vector Rect Position").setValue([mw / 2, 0]);   // soldan sağa büyüsün
          span(mr.layer, ma, mb2); P(mr.layer, "ADBE Position").setValue([mx - mw / 2, my]);
          if (mk0.rotate) P(mr.layer, "ADBE Rotate Z").setValue(mk0.rotate);
          var msc = P(mr.layer, "ADBE Scale"); key(msc, ma, [0, 100]); key(msc, ma + md, [100, 100]);
          if (!isU) {
            mr.layer.blendingMode = mk0.blend === "normal" ? BlendingMode.NORMAL : (mk0.blend === "screen" ? BlendingMode.SCREEN : BlendingMode.MULTIPLY);
            P(mr.layer, "ADBE Opacity").setValue(mk0.opacity || 85);
          }
        }
      } catch (e) { log("işaret kurulamadı " + sc.id + ": " + e); }
    }
  }
  // ---- etiketler: sahne içinde küçük yazılar; bg verilirse renkli kutu içinde (isim / yıl etiketi)
  if (sc.labels) {
    for (var li = 0; li < sc.labels.length; li++) {
      var lb = sc.labels[li], la = a + (lb.at === undefined ? 0.3 : lb.at), lbe = lb.until ? a + lb.until : b + TAIL;
      try {
        var LB = addText(lb.text, { size: lb.size || 44, rgb: lb.rgb, font: lb.font, x: (lb.x === undefined ? 0.5 : lb.x) * W, y: (lb.y === undefined ? 0.5 : lb.y) * H });
        LB.name = "LABEL " + sc.id + " " + li; span(LB, la, lbe);
        if (lb.rotate) P(LB, "ADBE Rotate Z").setValue(lb.rotate);
        if (lb.anim === "type") typeOn(LB, la, lb.dur || 0.5);
        else if (lb.anim === "pop") popIn(LB, la, 0);
        else { var lbo = P(LB, "ADBE Opacity"); key(lbo, la, 0); key(lbo, la + 0.2, 100); }
        if (lb.bg_rgb) {
          var lbx = shapeRect("LABELBOX " + sc.id + " " + li, 100, 100, lb.bg_rgb, lb.round === undefined ? 10 : lb.round); span(lbx.layer, la, lbe);
          lbx.rect.property("ADBE Vector Rect Size").expression = 'var t=thisComp.layer("' + LB.name + '");var r=t.sourceRectAtTime(time,false);[r.width+' + (lb.pad_x || 40) + ',r.height+' + (lb.pad_y || 24) + ']';
          P(lbx.layer, "ADBE Position").expression = 'thisComp.layer("' + LB.name + '").transform.position';
          P(lbx.layer, "ADBE Rotate Z").expression = 'thisComp.layer("' + LB.name + '").transform.rotation';
          popIn(lbx.layer, la, 0);
          lbx.layer.moveAfter(LB);
        } else {
          var lbs = fx(LB, "ADBE Drop Shadow"); var lbso = fp(lbs, "ADBE Drop Shadow-0002", 2); if (lbso) lbso.setValue(170);
        }
      } catch (e) { log("etiket kurulamadı " + sc.id + ": " + e); }
    }
  }

  // ---- sahne, ana kompozisyona tek 3B katman olarak girer; geçişler gerçek bir kameranın sahneler arasında uçmasıyla yapılır
  for (var mbi = 1; mbi <= SCOMP.numLayers; mbi++) {
    try { var mly = SCOMP.layer(mbi); if (!mly.adjustmentLayer && !mly.nullLayer && mly.hasVideo) mly.motionBlur = true; } catch (e) {}
  }
  comp = MAIN;
  var prevST = { x: ST.x, y: ST.y, z: ST.z, r: ST.r };
  var kind = "same";
  if (i > 0) {
    if (tr === "whip_left") { ST.x += W * 1.35; kind = "x"; }
    else if (tr === "whip_right") { ST.x -= W * 1.35; kind = "x"; }
    else if (tr === "whip_up" || tr === "blur_whip" || tr === "slide_up") { ST.y += H * 1.2; kind = "y"; }
    else if (tr === "whip_down") { ST.y -= H * 1.2; kind = "y"; }
    else if (tr === "zoom_through" || tr === "zoom_blur") { ST.z += 2600; kind = "z"; }
    else if (tr === "spin") { ST.x += W * 1.25; ST.y -= H * 0.3; ST.r += 32; kind = "spin"; }
    else if (tr === "orbit") { ST.x += W * 1.1; ST.z += 1400; kind = "orbit"; }
    else { ST.z -= 2; }   // aynı istasyon: yeni sahne bir tık öne
  }
  var t0 = a - 0.22, t1 = a + 0.26;
  var sIn = a;
  if (i > 0 && kind !== "same") sIn = t0 - 0.05;
  else if (i > 0 && (tr === "fade" || tr === "light_leak")) sIn = a - LEAD;
  else if (i > 0 && tr === "wash") sIn = a - 0.14;
  var SL = MAIN.layers.add(SCOMP); SL.name = "SCENE " + sc.id; span(SL, sIn, b + TAIL);
  SL.threeDLayer = true; SL.motionBlur = true;
  P(SL, "ADBE Position").setValue([ST.x, ST.y, ST.z]);
  if (ST.r) P(SL, "ADBE Rotate Z").setValue(ST.r);
  var so = P(SL, "ADBE Opacity");
  if (i === 0) {
    if (sc.intro === "tilt_down") {   // yakın plandan, hafif eğik başlayıp geri çekilen kamera
      key(camP, a, [ST.x, ST.y - H * 0.2, ST.z - Z0 * 0.5]); key(camP, a + 0.85, camAt(ST));
      key(camRX, a, -7); key(camRX, a + 0.85, 0); key(camRZ, a, -5); key(camRZ, a + 0.85, 0);
    } else { key(camP, 0, camAt(ST)); key(camRZ, 0, 0); }
  } else if (kind !== "same") {
    sfx(D.sfx_map.transition, a - 0.14, TRDB);
    var tm = (t0 + t1) / 2;
    key(camP, t0, camAt(prevST, lastK)); key(camP, t1, camAt(ST));
    key(camRZ, t0, prevST.r); key(camRZ, t1, ST.r);
    if (kind === "x" || kind === "orbit") {       // yatay uçuş: kamera gidiş yönüne doğru döner
      var sg = ST.x > prevST.x ? 1 : -1;
      key(camRY, t0, 0); key(camRY, tm, sg * (kind === "orbit" ? 34 : 20)); key(camRY, t1, 0);
    } else if (kind === "y") {                    // dikey uçuş: kamera eğilir
      var sg2 = ST.y > prevST.y ? 1 : -1;
      key(camRX, t0, 0); key(camRX, tm, -sg2 * 15); key(camRX, t1, 0);
      key(camRZ, tm, (prevST.r + ST.r) / 2 + sg2 * 4);
    } else if (kind === "z") {                    // ileri uçuş: önceki sahnenin içinden geçer
      key(camRZ, tm, (prevST.r + ST.r) / 2 + 9);
    }
  } else if (i > 0 && tr !== "cut") {
    sfx(D.sfx_map.transition, a - 0.12, TRDB);
    if (tr === "flash" || tr === "bw_flash") {
      var F = solid([1, 1, 1], "TR flash " + sc.id, a - 0.06, a + 0.16); TRL.push(F);
      F.blendingMode = BlendingMode.ADD;
      var fo = P(F, "ADBE Opacity"); key(fo, a - 0.06, 0); key(fo, a, tr === "bw_flash" ? 70 : 100); key(fo, a + 0.16, 0);
      // kamera sahneye doğru bir "yumruk" atar
      key(camP, a - 0.02, camAt(ST, KCAM * 0.8)); key(camP, a + 0.4, camAt(ST));
      if (tr === "bw_flash") {
        var BW = adj("TR bw " + sc.id, a - 0.1, a + 0.3); TRL.push(BW);
        fx(BW, "ADBE Tint");
        var BZ = adj("TR bwzoom " + sc.id, a - 0.1, a + 0.3); TRL.push(BZ);
        var rb2 = fx(BZ, "ADBE Radial Blur"); var rba2 = fp(rb2, "ADBE Radial Blur-0001", 1); var rbt2 = fp(rb2, "ADBE Radial Blur-0003", 3);
        if (rbt2) { try { rbt2.setValue(2); } catch (e) {} }
        key(rba2, a - 0.1, 0); key(rba2, a, 60); key(rba2, a + 0.3, 0);
      }
    } else if (tr === "wash") {
      // hex: sıcak beyaz ışık kadrajı yıkar, altında sahne değişir
      key(so, a - 0.12, 0); key(so, a + 0.12, 100);
      var WS = solid(D.look && D.look.wash_rgb ? D.look.wash_rgb : [1, 0.96, 0.86], "TR wash " + sc.id, a - 0.5, a + 0.6); TRL.push(WS);
      var wso = P(WS, "ADBE Opacity"); key(wso, a - 0.5, 0); key(wso, a, 88); key(wso, a + 0.6, 0); easeAll(wso, 60);
    } else if (tr === "iris") {
      // renk kadrajı kaplar, sonra bir noktadan daire açılıp yeni sahneyi gösterir
      var IR = solid(sc.tr_rgb || [0.05, 0.04, 0.03], "TR iris " + sc.id, a - 0.2, a + 0.62); TRL.push(IR);
      var iro = P(IR, "ADBE Opacity"); key(iro, a - 0.2, 0); key(iro, a - 0.02, 100);
      var icx = sc.iris_at ? sc.iris_at[0] * W : W / 2, icy2 = sc.iris_at ? sc.iris_at[1] * H : H / 2, ir0 = 8, ik = ir0 * 0.5523;
      var imk = IR.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
      var ish = new Shape();
      ish.vertices = [[icx, icy2 - ir0], [icx + ir0, icy2], [icx, icy2 + ir0], [icx - ir0, icy2]];
      ish.inTangents = [[-ik, 0], [0, -ik], [ik, 0], [0, ik]]; ish.outTangents = [[ik, 0], [0, ik], [-ik, 0], [0, -ik]]; ish.closed = true;
      imk.property("ADBE Mask Shape").setValue(ish); imk.inverted = true;
      var ime = imk.property("ADBE Mask Offset"); key(ime, a, -10); key(ime, a + 0.6, H * 1.25); easeAll(ime, 70);
    } else if (tr === "wipe_up") {
      // düz renkli perde alttan yükselip kadrajı kaplar, yukarı çıkarken yeni sahne görünür
      var WU = solid(sc.tr_rgb || [1, 1, 1], "TR wipe " + sc.id, a - 0.3, a + 0.42); TRL.push(WU);
      P(WU, "ADBE Scale").setValue([110, 104]);
      var wup = P(WU, "ADBE Position"); key(wup, a - 0.3, [W / 2, H * 1.56]); key(wup, a, [W / 2, H / 2]); key(wup, a + 0.42, [W / 2, -H * 0.56]);
    } else if (tr === "fade" || tr === "light_leak") {
      key(so, a - LEAD, 0); key(so, a, 100);
      if (tr === "light_leak") {
        var LK = solid([1, 0.55, 0.15], "TR leak " + sc.id, a - 0.5, a + 0.55); TRL.push(LK);
        LK.blendingMode = BlendingMode.SCREEN;
        var lo = P(LK, "ADBE Opacity"); key(lo, a - 0.5, 0); key(lo, a, 55); key(lo, a + 0.55, 0); easeAll(lo, 50);
      }
    }
  }
  // sahne boyunca kamera yavaşça yaklaşır (durağan kalmasın)
  if (sc.dolly !== 0) {
    var dA = (i === 0 && sc.intro === "tilt_down") ? a + 0.85 : (kind !== "same" ? t1 : a + 0.4);
    var dB = b - 0.22;   // sonraki sahnenin geçiş başlangıcıyla aynı an
    lastK = KCAM;
    if (dB > dA + 0.3) { lastK = KCAM * (sc.dolly || 0.965); key(camP, dB, camAt(ST, lastK)); }
  } else {   // yaklaşma kapalı: kamera sahne sonuna kadar yerinde kalsın (sonraki geçişe doğru süzülmesin)
    lastK = KCAM; key(camP, b - 0.22, camAt(ST, KCAM));
  }
  prevSL = SL;
}
comp = MAIN;
easeAll(camP, 80); easeAll(camRX, 80); easeAll(camRY, 80); easeAll(camRZ, 80);
// 2B geçiş katmanları sahnelerin arasında kalırsa 3B derinlik sıralamasını böler: hepsini sahnelerin üstüne taşı
for (var tq = 0; tq < TRL.length; tq++) { try { TRL[tq].moveToBeginning(); } catch (e) {} }
for (var sq = MAIN.numLayers; sq >= 1; sq--) { try { var sl2 = MAIN.layer(sq); if (sl2.name.indexOf("SFX ") === 0) sl2.moveToEnd(); } catch (e) {} }
if (BACK) { try { BACK.moveToEnd(); } catch (e) {} }

// ---- outro / CTA
if (D.outro) {
  var o = D.outro, oa = o.start, ob = o.end;
  var oit = imp(o.video || o.image);
  if (oit) {
    var OL = comp.layers.add(oit); OL.name = "OUTRO";
    if (o.video) { OL.startTime = oa; span(OL, oa, ob); var ovs = cover(oit, W, H); P(OL, "ADBE Scale").setValue([ovs, ovs]); }   // hazır kapanış klibi
    else { span(OL, oa, ob); applyMove(OL, "push_in", cover(oit, W, H), oa, ob); }
  }
  else { solid(D.colors.black, "OUTRO bg", oa, ob); }
  for (var k = 0; k < o.lines.length; k++) {
    var ol = addText(o.lines[k], { size: k === 0 ? 120 : 64, rgb: k === 0 ? D.colors.yellow : D.colors.white, font: k === 0 ? D.fonts.title : D.fonts.caption, x: W / 2, y: H * (0.40 + k * 0.09) });
    span(ol, oa + 0.15 + k * 0.25, ob); popIn(ol, oa + 0.15 + k * 0.25, 0);
  }
  if (o.lines.length) sfx(D.sfx_map.slam, oa + 0.15, -6);
}

// ---- altyazılar
var CAPS = [];
for (var c = 0; c < D.captions.length; c++) {
  var cp = D.captions[c];
  if (D.cap.mode === "none") break;
  var ca = cp.start, cb = Math.max(cp.end, ca + 0.18);
  var CL = addText(cp.text, { size: D.cap.size, rgb: (cp.rgb || D.cap.rgb), font: D.cap.font, x: W / 2, y: (cp.y || D.cap.y), tracking: D.cap.mode === "word" ? 10 : 0 });
  CL.name = "CAP " + c; span(CL, ca, cb);
  for (var r = 0; r < cp.key.length; r++) colorRange(CL, cp.key[r][0], cp.key[r][1], (cp.key_rgb || D.cap.key_rgb));
  if (D.cap.mode === "phrase") {
    // sahneye gömülü serif öbek: kelimeler konuşma hızında, bulanıktan netleşerek belirir
    wordsOn(CL, ca, Math.max(0.2, (cb - ca) * 0.75));
    var phs = fx(CL, "ADBE Drop Shadow"); var pho = fp(phs, "ADBE Drop Shadow-0002", 2); if (pho) pho.setValue(cp.rgb ? 0 : 190);
    try { CL.property("ADBE Effect Parade").property(1).property("ADBE Drop Shadow-0005").setValue(22); CL.property("ADBE Effect Parade").property(1).property("ADBE Drop Shadow-0004").setValue(6); } catch (e) {}
    var pop2 = P(CL, "ADBE Opacity"); key(pop2, Math.max(ca + 0.1, cb - 0.12), 100); key(pop2, cb, 0);
    var psc = P(CL, "ADBE Scale"); key(psc, ca, [97, 97]); key(psc, cb, [103, 103]);
  } else if (D.cap.mode === "pill") {
    var pill = shapeRect("CAP pill " + c, 100, 60, D.cap.pill_rgb, 14); span(pill.layer, ca, cb);
    pill.rect.property("ADBE Vector Rect Size").expression = 'var t=thisComp.layer("' + CL.name + '");var r=t.sourceRectAtTime(time,false);[r.width+44,r.height+26]';
    P(pill.layer, "ADBE Position").expression = 'thisComp.layer("' + CL.name + '").transform.position';
    P(pill.layer, "ADBE Opacity").setValue(D.cap.pill_opacity);
    pill.layer.moveAfter(CL);
  } else {
    // hex: tek kelime, yumuşak belirme + hafif büyüme; anahtar kelime daha büyük
    var big = cp.key.length > 0;
    var wsc = P(CL, "ADBE Scale"), wop = P(CL, "ADBE Opacity");
    var base = big ? 140 : 100;
    key(wsc, ca, [base * 0.92, base * 0.92]); key(wsc, cb, [base, base]);
    key(wop, ca, 0); key(wop, ca + 0.07, 100);
    var gl2 = fx(CL, "ADBE Drop Shadow"); var g2o = fp(gl2, "ADBE Drop Shadow-0002", 2); if (g2o) g2o.setValue(120); var g2s = fp(gl2, "ADBE Drop Shadow-0005", 5); if (g2s) g2s.setValue(25);
  }
}

// ---- grad / doku (en üstte, altyazıların altında kalması için sonra altyazıları üste taşıyoruz)
var G = D.grade;
var GR = adj("GRADE", 0, DUR);
if (G.tint > 0) {
  var tn = fx(GR, "ADBE Tint");
  var t1 = fp(tn, "ADBE Tint-0001", 1), t2 = fp(tn, "ADBE Tint-0002", 2), t3 = fp(tn, "ADBE Tint-0003", 3);
  if (t1) t1.setValue([0.10, 0.07, 0.04]); if (t2) t2.setValue([1.0, 0.93, 0.80]); if (t3) t3.setValue(G.tint);
}
if (G.noise > 0) { var nz = fx(GR, "ADBE Noise"); var nza = fp(nz, "ADBE Noise-0001", 1); if (nza) nza.setValue(G.noise); }
if (G.vignette > 0) {
  var V = solid([0, 0, 0], "VIGNETTE", 0, DUR);
  var mk = V.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
  var sh2 = new Shape(); var rx = W * 0.62, ry = H * 0.58, kx = rx * 0.5523, ky = ry * 0.5523, cx = W / 2, cy2 = H / 2;
  sh2.vertices = [[cx, cy2 - ry], [cx + rx, cy2], [cx, cy2 + ry], [cx - rx, cy2]];
  sh2.inTangents = [[-kx, 0], [0, -ky], [kx, 0], [0, ky]];
  sh2.outTangents = [[kx, 0], [0, ky], [-kx, 0], [0, -ky]];
  sh2.closed = true;
  mk.property("ADBE Mask Shape").setValue(sh2);
  mk.inverted = true;
  mk.property("ADBE Mask Feather").setValue([W * 0.35, W * 0.35]);
  P(V, "ADBE Opacity").setValue(G.vignette);
}
if (G.light_leak_every > 0) {
  for (var lt = 1.5; lt < DUR - 1; lt += G.light_leak_every) {
    var LL = solid([1, 0.6, 0.2], "LEAK " + lt.toFixed(1), lt, lt + 1.2);
    LL.blendingMode = BlendingMode.SCREEN;
    var rp2 = fx(LL, "ADBE Ramp"); var q5 = fp(rp2, "ADBE Ramp-0005", 5); if (q5) { try { q5.setValue(2); } catch (e) {} }
    var q2 = fp(rp2, "ADBE Ramp-0002", 2); if (q2) q2.setValue([1, 0.7, 0.35]); var q4 = fp(rp2, "ADBE Ramp-0004", 4); if (q4) q4.setValue([0, 0, 0]);
    var q1 = fp(rp2, "ADBE Ramp-0001", 1); key(q1, lt, [W * 1.05, H * 0.1]); key(q1, lt + 1.2, [W * 0.75, H * 0.35]);
    var q3 = fp(rp2, "ADBE Ramp-0003", 3); if (q3) q3.setValue([W * 0.2, H * 0.9]);
    var llo = P(LL, "ADBE Opacity"); key(llo, lt, 0); key(llo, lt + 0.5, 55); key(llo, lt + 1.2, 0); easeAll(llo, 50);
  }
}
if (D.look) {
  if (D.look.glow) {
    var GLW = adj("GLOW", 0, DUR); var ge = fx(GLW, "ADBE Glo2");
    try { ge.property("ADBE Glo2-0002").setValue(D.look.glow.threshold); } catch (e) { log("glow eşiği: " + e); }
    try { GLW.property("ADBE Effect Parade").property(1).property("ADBE Glo2-0003").setValue(D.look.glow.radius); } catch (e) { log("glow yarıçapı: " + e); }
    try { GLW.property("ADBE Effect Parade").property(1).property("ADBE Glo2-0004").setValue(D.look.glow.intensity); } catch (e) { log("glow şiddeti: " + e); }
  }
  var ovs = D.look.overlays || [];
  var BM = { screen: BlendingMode.SCREEN, multiply: BlendingMode.MULTIPLY, overlay: BlendingMode.OVERLAY, add: BlendingMode.ADD, soft_light: BlendingMode.SOFT_LIGHT };
  for (var ok = 0; ok < ovs.length; ok++) {
    var ov = ovs[ok], oi = imp(ov.file); if (!oi) continue;
    var odur = oi.duration > 0 ? oi.duration : DUR;
    for (var ot = 0; ot < DUR; ot += odur) {
      var OV = comp.layers.add(oi); OV.name = "OVL " + (ov.name || ok); OV.startTime = ot; span(OV, ot, Math.min(DUR, ot + odur));
      OV.blendingMode = BM[ov.blend] || BlendingMode.SCREEN;
      var osc = cover(oi, W, H); P(OV, "ADBE Scale").setValue([osc, osc]);
      P(OV, "ADBE Opacity").setValue(ov.opacity === undefined ? 50 : ov.opacity);
    }
  }
}
// altyazı ve başlıkları gradın üstüne taşı (okunaklı kalsın)
// (önce listeye al: taşırken indeksler kayar)
var tops = [], boxes = [];
for (var li = comp.numLayers; li >= 1; li--) {
  var ly = comp.layer(li), nm = ly.name;
  if (nm.indexOf("CAP pill ") === 0 || nm.indexOf("STAMP box ") === 0) boxes.push(ly);
  else if (nm.indexOf("CAP ") === 0 || nm.indexOf("TITLE ") === 0) tops.push(ly);
}
for (var ti = 0; ti < tops.length; ti++) tops[ti].moveToBeginning();
// kutular kendi metinlerinin hemen altında kalsın
for (var bi = 0; bi < boxes.length; bi++) {
  var bx = boxes[bi], bn = bx.name;
  try {
    if (bn.indexOf("CAP pill ") === 0) bx.moveAfter(comp.layer("CAP " + bn.substr(9)));
    else bx.moveAfter(comp.layer("TITLE " + bn.substr(10)));
  } catch (e) { log("kutu sırası: " + e); }
}

// ---- ses
if (D.vo) { var vit = imp(D.vo); if (vit) { var VL = comp.layers.add(vit); VL.name = "VO"; VL.startTime = 0; } }
if (D.music) {
  var mit = imp(D.music);
  if (mit) {
    var ML = comp.layers.add(mit); ML.name = "MUSIC"; ML.startTime = 0; span(ML, 0, DUR);
    var lv = ML.property("ADBE Audio Group").property("ADBE Audio Levels");
    key(lv, 0, [D.music_db, D.music_db]); key(lv, Math.max(0, DUR - 1.2), [D.music_db, D.music_db]); key(lv, DUR, [-60, -60]);
  }
}

// ---- render kuyruğu + kaydet
var rq = proj.renderQueue.items.add(comp);
var om = rq.outputModule(1);
var tpls = [D.render.om_template, "H.264 - Match Render Settings - 15 Mbps", "H.264 - Match Render Settings - 40 Mbps", "H.264"];
var okT = false;
for (var q = 0; q < tpls.length && !okT; q++) { if (!tpls[q]) continue; try { om.applyTemplate(tpls[q]); okT = true; log("çıktı şablonu: " + tpls[q]); } catch (e) {} }
if (!okT) log("H.264 çıktı şablonu bulunamadı; AE varsayılanıyla render alınacak (AE 2023+ önerilir)");
om.file = new File(D.render.mp4);
proj.save(new File(D.render.aep));
log("TAMAM: " + comp.numLayers + " katman, " + sfxCount + " ses efekti, süre " + DUR.toFixed(2) + " sn");
log("aep: " + D.render.aep);
app.endUndoGroup();
if (D.render.render_now) { proj.renderQueue.render(); log("render bitti: " + D.render.mp4); }
} catch (err) {
  log("HATA (satır " + (err.line || "?") + "): " + err.toString());
}
flushLog();
})();
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("timeline")
    ap.add_argument("-o", "--out", default="build/build.jsx")
    ap.add_argument("--aep", default="build/reel.aep")
    ap.add_argument("--mp4", default="build/reel.mp4")
    ap.add_argument("--render-now", action="store_true", help="betik sonunda AE içinde render al (aerender yerine)")
    ap.add_argument("--om-template", default="", help="AE çıktı modülü şablonu adı (boşsa H.264 şablonları denenir)")
    a = ap.parse_args()
    tl = json.loads(Path(a.timeline).read_text(encoding="utf-8"))
    D = prepare(tl, a.aep, a.mp4, a.render_now, a.om_template)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    # ExtendScript dosyayı BOM'lu UTF-8 okursa Türkçe karakterler bozulmaz
    js = "var D = " + json.dumps(D, ensure_ascii=False, indent=0) + ";\n" + JS
    Path(a.out).write_text("\ufeff" + js, encoding="utf-8")
    print(f"{a.out} yazıldı ({len(D['scenes'])} sahne, {len(D['captions'])} altyazı, {D['dur']:.1f} sn)")
    print(f"log: {D['render']['log']}")


if __name__ == "__main__":
    main()
