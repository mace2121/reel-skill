# reel-skill

Verdiğin bir konuyu **earn.edits / hex_creatives tarzında**, 40–75 saniyelik dikey (9:16) **Türkçe anlatımlı**
bir reel videoya çeviren Claude Code skill'i. Bitmiş MP4 + After Effects projesi teslim eder.

```
konu → araştırma → Türkçe senaryo → sahne listesi → AI görseller (Magnific / Higgsfield)
     → Türkçe seslendirme + müzik + efektler (ElevenLabs / Magnific)
     → zaman çizelgesi (kelime senkronu) → ffmpeg önizleme → After Effects projesi → render → MP4
```

Stil, 9 referans videonun [rea-video](https://github.com/JuneYaooo/rea-video) ile sahne sahne analizinden
çıkarıldı: `.claude/skills/reel-video/references/analiz.md` ve `stil-rehberi.md`.

| Stil | Görünüm |
|---|---|
| `earn` | AI görsel + masa üstü objeler (gazete, polaroid), kalın sarı/kırmızı başlıklar, hap altyazı, blur-whip geçişler, CTA |
| `hex` | Sepya gravür / yağlı boya görünümlü AI görseller, parallax, ışık sızması, ortada tek kelime italik serif |

## Kurulum
Ayrıntılı: [`kurulum.md`](.claude/skills/reel-video/references/kurulum.md). Kısaca (After Effects'in kurulu
olduğu bilgisayarda):

1. `git clone https://github.com/mace2121/reel-skill.git && cd reel-skill && bash install.sh`
2. Python 3.10+ + `pip install pillow`, ffmpeg
3. After Effects 2023+ ve [after-effects-mcp](https://github.com/Dakkshin/after-effects-mcp) (panel açık)
4. claude.ai bağlayıcıları: Magnific, Higgsfield, ElevenLabs
5. (isteğe bağlı) HyperFrames, faster-whisper, rea-video

## Kullanım
Claude Code'da:

```text
reel-video skill'iyle "Lale Çılgınlığı" konusunda earn tarzı 45 saniyelik video yap
```

Claude önce maliyet listesini (görsel / ses / müzik üretimi) gösterir, onay alır, sonra üretir.
Çıktı: `projeler/<ad>/build/reel.mp4` + `reel.aep`.

## Scriptler (`.claude/skills/reel-video/scripts/`)
| Script | İş |
|---|---|
| `timeline.py` | shotlist + kelime zamanları → sahne sınırları, altyazı parçaları, anahtar kelime vurguları |
| `preview_ffmpeg.py` | timeline → hızlı önizleme MP4 (AE gerekmez; AE yoksa yedek teslim) |
| `build_ae_jsx.py` | timeline → After Effects ExtendScript (içe aktarma, hareket, çerçeveler, geçişler, yazılar, ses, grad, render kuyruğu) |
| `styles.py` | iki stilin renk / font / geçiş / grad ön ayarları |

Örnek: `.claude/skills/reel-video/examples/lale/shotlist.json`

```bash
S=.claude/skills/reel-video/scripts
python3 $S/timeline.py shotlist.json -o timeline.json --words assets/words.json
python3 $S/preview_ffmpeg.py timeline.json -o build/preview.mp4 --scale 0.5
python3 $S/build_ae_jsx.py timeline.json -o build/build.jsx --aep build/reel.aep --mp4 build/reel.mp4
```

## Not
Referans videoların görüntüsü, metni ya da sesi bu repoda yok ve kopyalanmaz; yalnızca yapı, tempo ve stil
taklit edilir. Üretilen içeriğin bilgi doğruluğu ve telif durumu kullanıcının sorumluluğundadır.
