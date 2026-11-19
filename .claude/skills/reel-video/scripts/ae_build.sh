#!/bin/bash
# shotlist.json -> timeline.json -> build.jsx -> After Effects projesi (-> render + ses dengeleme)
#
#   ae_build.sh <proje_klasörü> [--render] [--words assets/words.json]
#
# - macOS + After Effects gerekir (uygulama adı otomatik bulunur; AE_APP ile ezilebilir).
# - Python: REEL_PY ortam değişkeni, yoksa <proje>/../.venv/bin/python, yoksa python3 (Pillow gerekir).
# - AE'de açık duran proje KAYDEDİLMEDEN kapatılır; yalnızca boş bir proje ya da bu klasörün build/reel.aep'i
#   açıksa devam eder, başka bir proje açıksa durur (kullanıcının işi ezilmesin).
set -uo pipefail
PRJ="$(cd "${1:?proje klasörü ver}" && pwd)"; shift
RENDER=0; WORDS="assets/words.json"
while [ $# -gt 0 ]; do case "$1" in --render) RENDER=1;; --words) WORDS="$2"; shift;; esac; shift; done
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${REEL_PY:-}"; [ -z "$PY" ] && [ -x "$PRJ/../.venv/bin/python" ] && PY="$PRJ/../.venv/bin/python"; PY="${PY:-python3}"
AE_DIR="${AE_DIR:-$(ls -d /Applications/Adobe\ After\ Effects* 2>/dev/null | sort | tail -1)}"
AE_APP="${AE_APP:-$(basename "$AE_DIR")}"
[ -d "$AE_DIR" ] || { echo "After Effects bulunamadı"; exit 1; }
cd "$PRJ" || exit 1
mkdir -p build tools
cat > tools/_reset.jsx <<JSX
(function(){ var o=new File("$PRJ/tools/_reset.txt"); o.encoding="UTF-8"; o.open("w");
var p=app.project, f=p.file, ours=f && f.fsName.indexOf("$PRJ")===0;
if (p.numItems>0 && !ours) { o.write("BUSY "+(f?f.fsName:"(kaydedilmemiş proje, "+p.numItems+" öğe)")); o.close(); return; }
try { app.endUndoGroup(); } catch(e){} p.close(CloseOptions.DO_NOT_SAVE_CHANGES); app.newProject(); o.write("ok"); o.close(); })();
JSX
rm -f tools/_reset.txt build/reel.log.txt
osascript -e "tell application \"$AE_APP\" to DoScriptFile \"$PRJ/tools/_reset.jsx\"" >/dev/null 2>&1
for i in $(seq 1 90); do [ -f tools/_reset.txt ] && break; /bin/sleep 1; done
ST="$(cat tools/_reset.txt 2>/dev/null)"
case "$ST" in ok) ;; BUSY*) echo "DURDU: After Effects'te başka bir proje açık: ${ST#BUSY }"; exit 2;; *) echo "DURDU: After Effects yanıt vermedi (Scripting izinleri?)"; exit 2;; esac
rm -f build/reel.aep
WARG=(); [ -f "$WORDS" ] && WARG=(--words "$WORDS")
"$PY" "$HERE/timeline.py" shotlist.json -o timeline.json "${WARG[@]}" || exit 1
"$PY" "$HERE/build_ae_jsx.py" timeline.json -o build/build.jsx --aep build/reel.aep --mp4 build/reel.mp4 | head -1
osascript -e "tell application \"$AE_APP\" to DoScriptFile \"$PRJ/build/build.jsx\"" >/dev/null 2>&1
for i in $(seq 1 200); do [ -f build/reel.log.txt ] && break; /bin/sleep 2; done
echo "--- reel.log.txt"; tr '\r' '\n' < build/reel.log.txt; echo
grep -q "TAMAM" build/reel.log.txt || { echo "DURDU: AE betiği tamamlanmadı (log'a bak)"; exit 3; }
[ "$RENDER" = 1 ] || exit 0
rm -f build/reel_ae.mp4
"$AE_DIR/aerender" -project "$PRJ/build/reel.aep" -comp REEL -output "$PRJ/build/reel_ae.mp4" > build/aerender.log 2>&1 || { echo "aerender hata verdi (build/aerender.log)"; exit 4; }
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 build/reel_ae.mp4)
# AE çıktısında tepe 0 dB'ye vuruyor: sesi -14 LUFS / -1 dBTP'ye dengele, görüntüye dokunma
ffmpeg -y -loglevel error -i build/reel_ae.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1.0:LRA=11" -c:a aac -b:a 256k -ar 48000 -t "$D" -movflags +faststart build/reel.mp4
echo "build/reel.mp4 hazır ($D sn)"
