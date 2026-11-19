# After Effects: kurulum, render, sorun giderme

Projenin tamamı `build_ae_jsx.py` ile tek bir `build.jsx` (ExtendScript) olarak üretilir: içe aktarma, sahne
kompozisyonları, 3B kamera, başlıklar, altyazılar, doku katmanları, sesler, render kuyruğu, `.aep` kaydı.
`preview_ffmpeg.py` bu görünümü **göstermez** (eski, düz önizleme; ayrıca kurulu ffmpeg'de altyazı desteği yok):
kontrol her zaman AE çıktısından, kare föyleriyle yapılır.

## Tek komut
```bash
bash $S/ae_build.sh projeler/<ad> --render
```
Sırasıyla: AE'deki projeyi kapatır (yalnızca boşsa ya da bu projenin `reel.aep`'iyse; başka proje açıksa **durur**),
`timeline.py` → `build_ae_jsx.py` → `osascript … DoScriptFile` ile betiği AE'de çalıştırır → `reel.log.txt` bekler →
`aerender` → sesi −14 LUFS / −1 dBTP'ye dengeler (`reel_ae.mp4` ham, `reel.mp4` teslim). 30 sn'lik video ≈ 2–3 dk.

Elle:
```bash
python3 $S/timeline.py shotlist.json -o timeline.json --words assets/words.json
python3 $S/build_ae_jsx.py timeline.json -o build/build.jsx --aep build/reel.aep --mp4 build/reel.mp4
osascript -e 'tell application "Adobe After Effects 2027" to DoScriptFile "/tam/yol/build/build.jsx"'
"/Applications/Adobe After Effects 2027/aerender" -project "$PWD/build/reel.aep" -comp REEL -output "$PWD/build/reel_ae.mp4"
```
Windows: `"…\Support Files\AfterFX.exe" -r build\build.jsx` ve `aerender.exe`.

## Log
`build/reel.log.txt`: `TAMAM: N katman …` başarı. `EKSİK DOSYA` (yol yanlış), `FONT YOK` (fontu kur, AE'yi yeniden
başlat), `HATA (satır N)` (`build.jsx`'in o satırına bak). Betik yarıda kalırsa AE'de yarım bir REEL kalır;
`ae_build.sh` her seferinde projeyi kaydetmeden kapatıp temiz başlar.

## Katman adları (elle rötuş için)
Ana kompozisyon `REEL`: `KAMERA`, `SCENE sXX` (3B sahne katmanları), `BACKDROP`, `TR …` (geçiş ayar katmanları),
`GRADE`, `VIGNETTE`, `OVL halftone / dust / scratches / grain`, `CAP n` + `CAP pill n`, `OUTRO`, `VO`, `MUSIC`, `SFX …`.
Sahne kompozisyonu `SC sXX`: `sXX` (ana görsel / konu), `sXX_bg`, `sXX_kontur`, `sXX_grp` (polaroid / daire null'ı),
`sXX_thread`, `sXX_pin`, `TITLE sXX` / `BTITLE sXX` (konunun arkasındaki başlık), `SUB sXX`, `FOG n`, `TAG sXX`, `W sXX n`.
Elle yapılan değişiklikler `.aep`'de kalır ama yeniden üretimde kaybolur: kalıcı değişiklik = shotlist'i düzelt.

## ExtendScript tuzakları (betiği değiştirirken)
- **Geçersiz referans:** bir katmana efekt, bir şekle dolgu / çizgi, bir metne animatör eklemek, daha önce alınmış
  kardeş özellik referanslarını geçersiz kılar ("Object is invalid"). Eklemeden sonra özelliği katmandan yeniden al.
- **3B sıralama:** iki 3B katmanın arasına 2B katman girerse derinlik sıralaması bölünür. Geçiş ayar katmanları ve
  ses katmanları bu yüzden döngüden sonra en üste / en alta taşınır; track matte'li geçiş (iris) 3B düzende kullanılmaz.
- **Kamera süzülmesi:** kamera anahtarları tüm süre boyunca yumuşatılır; bir sahnenin sonunda anahtar yoksa kamera
  sonraki geçişe doğru erkenden kayar. Her sahne sonuna (`b − 0.22`) anahtar konur.
- **Kadraj payı:** kamera sahneye %4,5 yakın durur (kenarlar görünmesin) ve sahne boyunca %3,5 daha yaklaşır; üst
  kenara yakın başlıklar kırpılır (`pos ≥ 0.13`, gerekirse `dolly: 0`).
- **Glow:** `ADBE Glo2` eşiği beklenen birimde değil; renkleri patlatıyor. Kapalı.
- Hareket bulanıklığı için hem kompozisyonda hem **her katmanda** `motionBlur = true` gerekir.
- `build.jsx` UTF-8 BOM ile yazılır; BOM silinirse Türkçe karakterler bozulur.

## Fontlar
`assets/fonts/` içindekileri `~/Library/Fonts`'a kopyala: `AmedBaslikAnton-Regular`, `Anton-Regular`,
`Poppins-SemiBold`; ayrıca Playfair Display Italic kurulu olmalı. Başka font: shotlist'te `"fonts": {"title": "<PostScript adı>"}`.

## Mocha / takip
Yalnızca hareketli video görüntüsü varsa anlamlı (bir yüzeye yazı oturtmak gibi) ve elle yapılır. Durağan
fotoğraflarla kurulan sahnelerde kullanılmaz; "3B" hissi kamera + katman derinliğinden gelir.
