#!/usr/bin/env bash
# reel-video skill'ini ~/.claude/skills altına bağlar. Tekrar çalıştırılabilir.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/.claude/skills/reel-video"
DEST="$HOME/.claude/skills/reel-video"
mkdir -p "$HOME/.claude/skills"
if [ -e "$DEST" ] && [ ! -L "$DEST" ]; then
  echo "⚠ $DEST gerçek bir klasör; silip tekrar çalıştırın." >&2; exit 1
fi
if ln -sfn "$SRC" "$DEST" 2>/dev/null; then
  echo "bağlandı: $DEST -> $SRC"
else
  cp -r "$SRC" "$DEST" && echo "kopyalandı (symlink yapılamadı): $DEST — güncellemede tekrar çalıştırın"
fi
python3 -c "import PIL" 2>/dev/null && echo "pillow ok" || echo "⚠ pip install pillow"
command -v ffmpeg >/dev/null && echo "ffmpeg ok" || echo "⚠ ffmpeg kurulu değil"
