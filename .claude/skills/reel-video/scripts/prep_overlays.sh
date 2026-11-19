#!/bin/bash
# 4K yatay doku / sis kliplerini 1080x1920 dikey, hafif dosyalara çevirir (skill'in assets/doku klasörü için).
#   prep_overlays.sh <kaynak.mp4|mov> <çıktı.mp4> [döndür|zemin-sisi|doldur]
#   döndür     : gren, toz, çizik, halftone gibi yönsüz dokular (90° çevir, 1080x1920)
#   zemin-sisi : alt kenarda duran sis (yatay kareyi alta yerleştirir, üstü siyah)
#   doldur     : ortam dumanı (yüksekliğe sığdır, ortadan kırp)
set -euo pipefail
IN="$1"; OUT="$2"; MODE="${3:-döndür}"
case "$MODE" in
  döndür)     VF="transpose=1,scale=1080:1920";;
  zemin-sisi) VF="scale=2560:1440,crop=1080:1440:740:0,pad=1080:1920:0:480:black";;
  doldur)     VF="scale=3414:1920,crop=1080:1920";;
  *) echo "bilinmeyen kip: $MODE"; exit 1;;
esac
ffmpeg -y -loglevel error -i "$IN" -t 12 -an -vf "$VF" -r 30 -c:v libx264 -crf 22 -preset fast -pix_fmt yuv420p "$OUT"
echo "$OUT"
