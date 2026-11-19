# reel-skill

Verdiğin bir konuyu **earn.edits tarzında**, ~30–45 saniyelik dikey (9:16) **Türkçe anlatımlı** bir reel videoya
çeviren Claude Code skill'i (Amed Güncel kanalı için ayarlı). Bitmiş MP4 + After Effects projesi teslim eder.

**v2:** gerçek fotoğraf önce (AI yalnızca gerekirse), fotoğraftan maskelenen katmanlı sahneler (siyah-beyaz + halftone
arka plan, renkli ve konturlu konu, arada başlık), gerçek 3B kamera geçişleri + hareket bulanıklığı, pano / polaroid /
dağınık kelime sahneleri, halftone-toz-gren dokuları, sis, kanal kapanışı. Akış: `.claude/skills/reel-video/SKILL.md`.

```
konu → araştırma → Türkçe senaryo → gerçek fotoğraflar (+ maske, gerekirse AI görsel) → sahne listesi
     → Türkçe seslendirme + müzik + efektler (ElevenLabs / Magnific) → kelime zamanları
     → After Effects projesi (3B kamera) → render → kare kare kontrol → MP4
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
2. Python 3.10+ + `pip install pillow opencv-python-headless faster-whisper`, ffmpeg
3. After Effects 2023+ (macOS'ta betik `osascript` ile, render `aerender` ile çalışır)
4. claude.ai bağlayıcıları: Magnific, ElevenLabs
5. Fontlar: `assets/fonts/` içindekileri sisteme kur; ayrıca Playfair Display Italic
6. Doku ve sis: lisanslı paketlerden üretildiği için repoda yok — `assets/doku/README.md`

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
| `build_ae_jsx.py` | timeline → After Effects ExtendScript (sahne kompozisyonları, 3B kamera, katmanlı sahneler, yazılar, doku, ses, render kuyruğu) |
| `ae_build.sh` | tek komut: timeline → build.jsx → After Effects → aerender → ses dengeleme |
| `frame_sheets.py` | videoyu zaman etiketli kare föylerine çevirir (kontrol ve referans analizi) |
| `layer_prep.py` | fotoğraf + maske → hizalı katmanlar (siyah-beyaz arka plan, renkli konu, kontur) |
| `cutout_prep.py` | arka planı silinmiş figürü 9:16 tuvale oturtur, sticker kenarlığı ekler |
| `words.py` | seslendirmeden kelime zamanları (faster-whisper, yerel) |
| `prep_overlays.sh` | 4K yatay doku / sis kliplerini 1080x1920'ye çevirir |
| `styles.py` | stil ön ayarları · `preview_ffmpeg.py`: eski, düz önizleme (yeni görünümü göstermez) |

Örnekler: `examples/tahir-elci/shotlist.json` (güncel görünüm), `examples/lale/shotlist.json` (ilk sürüm şeması)

```bash
bash .claude/skills/reel-video/scripts/ae_build.sh projeler/<ad> --render
python3 .claude/skills/reel-video/scripts/frame_sheets.py projeler/<ad>/build/reel.mp4 -o projeler/<ad>/build/qc/son
```

## Not
Referans videoların görüntüsü, metni ya da sesi bu repoda yok ve kopyalanmaz; yalnızca yapı, tempo ve stil
taklit edilir. Üretilen içeriğin bilgi doğruluğu ve telif durumu kullanıcının sorumluluğundadır.
