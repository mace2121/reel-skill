# After Effects: proje üretimi, after-effects-mcp, render

## Neden ExtendScript + MCP birlikte
[after-effects-mcp](https://github.com/Dakkshin/after-effects-mcp) kompozisyon, metin / şekil / düz renk katmanı,
keyframe, expression, maske, kamera, null oluşturabilir ve katman bilgisi okuyabilir; ama **görsel / ses içe
aktaramaz ve render alamaz** (izinli script listesinde yok). Bu yüzden:

1. Projenin tamamı `build_ae_jsx.py` ile tek bir `build.jsx` olarak üretilir (içe aktarma, sahneler, geçişler,
   yazılar, sesler, render kuyruğu, .aep kaydı).
2. `build.jsx` AE'nin komut satırı ile çalıştırılır.
3. after-effects-mcp **kontrol ve ince ayar** içindir: katmanları listele, zamanlama / konum / ölçek düzelt,
   keyframe ve expression ekle.
4. Render `aerender` ile alınır.

## build.jsx üret ve çalıştır
AE yolları: repo kökündeki `ae-yollari.json` (kurulum scriptinin yazdığı `afterfx` / `aerender`) varsa onu kullan.

```bash
python3 $S/build_ae_jsx.py timeline.json -o build/build.jsx --aep build/reel.aep --mp4 build/reel.mp4
```
Windows (PowerShell / Git Bash; sürüm klasörünü kendi kurulumuna göre değiştir):
```bash
"/c/Program Files/Adobe/Adobe After Effects 2025/Support Files/AfterFX.exe" -r "C:\\tam\\yol\\build\\build.jsx"
```
macOS:
```bash
osascript -e 'tell application "Adobe After Effects 2025" to DoScriptFile "/tam/yol/build/build.jsx"'
```
- AE açık değilse açılır, betik çalışır, proje kaydedilir. İlk çalıştırmada AE "betik dosya yazabilsin mi"
  diye sorabilir: Settings → Scripting & Expressions → **Allow Scripts to Write Files and Access Network** açık olmalı.
- Betik bitince `build/reel.log.txt` yazar. Oku:
  - `EKSİK DOSYA` → yol yanlış / dosya yok.
  - `FONT YOK, yerine … kullanıldı` → fontu kur (aşağıda) ve betiği yeniden çalıştır.
  - `HATA (satır N)` → `build.jsx`'in o satırına bak; çoğu zaman eski AE sürümünde olmayan bir özellik.
  - `TAMAM: … katman` → başarılı.
- Betiği tekrar çalıştırmak **yeni bir REEL kompozisyonu** ekler; temiz başlamak için AE'de yeni proje aç
  (File → New) ya da `.aep`'yi sil.

## Render
```bash
"/c/Program Files/Adobe/Adobe After Effects 2025/Support Files/aerender.exe" -project "C:\\…\\build\\reel.aep" -comp REEL -output "C:\\…\\build\\reel.mp4"
```
- AE 2023 ve sonrası H.264'ü doğrudan render kuyruğundan verir; betik "H.264 - Match Render Settings - 15 Mbps"
  şablonunu dener. Şablon bulunamazsa log'da yazar; o zaman AE çıktısı .mov / .avi olabilir →
  `ffmpeg -i reel.mov -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -movflags +faststart reel.mp4`.
- Alternatif: `--render-now` ile betik sonunda AE içinde render (AE arayüzü render bitene kadar kilitli kalır).

## after-effects-mcp ile ince ayar
Kurulum ve panel: `kurulum.md`. AE'de **Window → mcp-bridge-auto.jsx** paneli açık ve "Auto-run commands"
işaretli olmalı. Komutlar sıraya girer; sonucu `get-results` ile al.

| İş | Araç |
|---|---|
| Proje / kompozisyon listesi | `run-script` → `getProjectInfo`, `listCompositions` |
| Katman bilgisi | `getLayerInfo` (compName: "REEL") |
| Konum / ölçek / opaklık / zaman | `setLayerProperties` (layerName ör. "TITLE s06", "CAP 12") |
| Keyframe ekle | `setLayerKeyframe` (property: Position / Scale / Opacity / Rotation) |
| Expression | `setLayerExpression` (ör. hafif sallanma: `wiggle(2,6)`) |
| Bulanıklık efekti | `apply-effect` / `apply-effect-template` (`gaussian-blur`, `directional-blur`) |
| Ek metin / şekil | `createTextLayer` / `createShapeLayer` (run-script üzerinden) |

Katman adları: sahne görseli = `s01`; daire / polaroid grubu = `s01_grp`; başlık = `TITLE s01`; altyazı =
`CAP 0…`; hap = `CAP pill N`; geçiş ayar katmanı = `TR whip s02` vb.; `GRADE`, `VIGNETTE`, `VO`, `MUSIC`, `SFX …`.

**Önemli:** MCP ile yapılan değişiklikler `.aep`'de kalır ama `build.jsx` yeniden üretilirse kaybolur. Kalıcı
değişiklik = shotlist / timeline'ı düzelt + yeniden üret. MCP'yi son rötuşlar için kullan ve sonra
`File → Save` (ya da kullanıcıya kaydetmesini söyle) ve yeniden render al.

## Fontlar
Google Fonts'tan indir ve sisteme kur (AE yeniden başlatılmalı):
- earn: **Anton**, **Poppins** (SemiBold), **Playfair Display** (Italic)
- hex: **Playfair Display** (Italic, Bold Italic)
Hepsi Türkçe karakterleri (ğ ş ı İ ç ö ü) destekler. Farklı font istersen shotlist'te `"fonts": {"title": "PostScriptAdı"}`.

## Sorun giderme
| Belirti | Çözüm |
|---|---|
| Betik hiçbir şey yapmadı, log yok | Scripting izinleri kapalı; ya da yol boşluk içeriyor ve tırnaklanmadı |
| Türkçe karakterler bozuk | build.jsx UTF-8 BOM ile yazılır; dosyayı başka bir editörle kaydedip BOM'u silmeyin |
| Track matte çalışmıyor | AE 2023 öncesi: matte katmanı hedefin hemen üstünde olmalı (betik böyle kurar); katman sırasını elle değiştirmeyin |
| Altyazı hapı metinden kaymış | Hap boyutu/konumu expression ile metne bağlı; metin katmanının anchor expression'ını silmeyin |
| Render çok yavaş | Motion blur'u kapat (comp ayarı), `Directional Blur` uzunluğunu azalt |
