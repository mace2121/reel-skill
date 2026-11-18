---
name: reel-video
description: Verilen bir konuyu (tarih, gizem, icat, ekonomi, biyografi…) earn.edits / hex_creatives tarzında 40–75 saniyelik dikey (9:16) Türkçe anlatımlı bir reel videoya çevirir ve bitmiş MP4'ü teslim eder. Konu araştırması, Türkçe senaryo, sahne listesi, AI görseller (Magnific / Higgsfield), Türkçe seslendirme + müzik + ses efektleri (ElevenLabs / Magnific), After Effects projesi (ExtendScript + after-effects-mcp) ve render adımlarını kapsar. Kullanıcı "şu konuda video yap", "bunu reel'e çevir", "earn tarzı / hex tarzı video", "tarih videosu üret" dediğinde kullan.
---

# reel-video: konudan bitmiş reel'e

Bu skill, 9 referans videonun (`references/analiz.md`) `rea-video decompose` ile çıkarılmış ortak stilini
yeniden üretir. İki stil ailesi var; ayrıntıları `references/stil-rehberi.md`:

| Stil | Ne zaman | Görünüm |
|---|---|---|
| **earn** (varsayılan) | Gizem, suç, ekonomi / para, modern tarih, "bunu biliyor muydun" | AI görsel + masa üstü objeler (gazete, polaroid, kara tahta, dosya), kalın sarı / kırmızı başlıklar, hap altyazı, blur-whip geçişler, sonda CTA |
| **hex** | 1900 öncesi tarih, icatlar, tıp / bilim tarihi, biyografi | Sepya ya da siyah-beyaz gravür / yağlı boya görünümlü AI görseller, yavaş parallax, ışık sızması, ortada tek kelime italik serif altyazı |

Kullanıcı stili söylemezse konuya göre seç ve bir cümleyle söyle. Video dili her zaman **Türkçe**.

## Çıktı klasörü

Her video kendi klasöründe üretilir (`projeler/<kısa-ad>/`):

```
projeler/<ad>/
  brief.md          konu, stil, süre, kaynaklar
  script.md         Türkçe anlatım metni
  shotlist.json     sahne listesi (şema: references/sahne-katalogu.md, örnek: examples/lale/shotlist.json)
  assets/img/       sahne görselleri (s01.png …)
  assets/vid/       (isteğe bağlı) görselden üretilen kısa videolar
  assets/vo.mp3     seslendirme   assets/words.json  kelime zamanları
  assets/music.mp3  müzik         assets/sfx/*.wav   ses efektleri
  timeline.json     timeline.py çıktısı
  build/            preview.mp4, build.jsx, reel.aep, reel.mp4 (TESLİM)
```

Scriptler: `S=<bu skill klasörü>/scripts` (Python 3.10+, Pillow, ffmpeg gerekir).

## Akış

### 0. Ortam kontrolü
`references/kurulum.md`'deki kontrol listesini çalıştır: ffmpeg, Python + Pillow, After Effects (+ `aerender`),
after-effects-mcp bağlantısı (`get-help` aracı yanıt veriyor mu), Magnific / Higgsfield / ElevenLabs bağlayıcıları.
Eksik olanı kullanıcıya tek satırda söyle, eksikliğe göre yol seç:
- AE yoksa / ulaşılamıyorsa → teslim `preview_ffmpeg.py` ile tam çözünürlükte yapılır (kalite notu düş).
- Görsel bağlayıcısı yoksa → kullanıcıdan görsel iste ya da durup bağlamasını iste.

### 1. Brief
Konu, stil, hedef süre (varsayılan earn 40–48 sn, hex 45–65 sn), CTA (varsayılan: "Takip et" + kanalın
sloganı; kullanıcının markası varsa onu kullan), ses tercihi. Sorulmamış şeyler için varsayılanı kullan,
gerçekten belirsiz olan tek şeyi sor. `brief.md`'ye yaz.

### 2. Araştırma
Web'de ara; en az 3 bağımsız kaynakla doğrula. Senaryoda kullanacağın her rakam, tarih, isim kaynağa dayanmalı;
uyduramazsın. Tartışmalı bilgiyi "iddiaya göre / rivayete göre" diye işaretle. Kaynakları `brief.md`'ye ekle.

### 3. Senaryo — `references/senaryo.md`
Kanca (ilk 2 sn) → bağlam → gerilim / dönüm → kanıt → sonuç → duygusal kapanış → CTA.
Türkçe tempo ≈ **2.4 kelime/sn** → 45 sn ≈ 105 kelime. Rakamları seslendirme için yazıyla yaz
("yüzde doksan", "bin altı yüz otuz yedi"), başlıkta rakam kullan ("%90", "1637"). `script.md`'ye yaz.

### 4. Sahne listesi — `references/sahne-katalogu.md`
Senaryoyu sahnelere böl: her sahne 1.5–4 sn, bir cümle ya da yarım cümle (`narration`). Sahnelerin
narration'ları birleşince senaryonun tamamı olmalı (sıra ve kelimeler aynı). Her sahneye: görsel prompt'u,
çerçeve (`full / circle / polaroid / split`), hareket, geçiş, varsa başlık ve anahtar kelimeler.
Stil kuralları: earn'de her 2–3 sahnede bir kinetik başlık, en az 2 polaroid / daire çerçeve, geçişlerin çoğu
blur_whip; hex'te başlık az, çerçeve çoğunlukla full, geçiş light_leak / fade.

### 5. Maliyet onayı
Üretimden önce kullanıcıya listele: görsel sayısı (sahne + yedek), varsa video üretim sayısı, seslendirme karakter
sayısı, müzik ve efekt üretimi. Kullanıcı onaylamadan **ücretli üretim çağrısı yapma**.

### 6. Görseller — `references/gorsel-uretim.md`
Stilin ortak stil bloğu + sahne prompt'u, 9:16. Magnific (`images_generate`) ya da Higgsfield (`generate_image`).
Her sonucu indirip `assets/img/sXX.png` olarak kaydet ve **gözle kontrol et** (Read): bozuk el / yüz,
anlamsız yazı, yanlış dönem, stil kayması varsa yeniden üret. Gerekirse en fazla 2–3 sahne için kısa
görsel→video (`scene.video`); her biri ayrıca onaylı.

### 7. Ses — `references/ses.md`
1. ElevenLabs ile Türkçe seslendirme (`creative_list_voices` → uygun derin anlatıcı sesi → `creative_generate_speech`,
   model çok dilli). Takeler arasında en iyisini seç, `assets/vo.mp3`.
2. Kelime zamanları: `creative_transcribe_audio` (ya da yerelde faster-whisper) → `assets/words.json`.
   Hiçbiri yoksa timeline.py süreyi harf sayısına göre tahmin eder (daha kaba).
3. Müzik: stile uygun enstrümantal (earn: gerilimli / dramatik 85–130 BPM; hex: ağır orkestral / piyano).
4. Efektler: earn → `whoosh, hit, pop, type`; hex → `whoosh_soft, hit_soft, paper, typewriter`.
   `shotlist.json` → `sfx` alanına yolları yaz.

### 8. Zaman çizelgesi
```bash
python3 $S/timeline.py shotlist.json -o timeline.json --words assets/words.json
```
Çıktıdaki sahne sürelerine bak: 6 sn'den uzun sahneyi böl, 1.2 sn'den kısa sahneyi birleştir. Narration'ı
değiştirdiysen seslendirmeyi yeniden üretmen gerektiğini unutma.

### 9. Önizleme (AE'den önce)
```bash
python3 $S/preview_ffmpeg.py timeline.json -o build/preview.mp4 --scale 0.5
rea-video tiles build/preview.mp4 --start 0 --end <süre> --every 1.5 -o build/tiles.jpg   # varsa
```
Kareleri gözle kontrol et (altyazı okunuyor mu, başlık görseli kapatıyor mu, sahne-anlatım uyumu).
Düzelt, tekrar üret. İstersen önizlemeyi kullanıcıya göster.

### 10. After Effects — `references/after-effects.md`
```bash
python3 $S/build_ae_jsx.py timeline.json -o build/build.jsx --aep build/reel.aep --mp4 build/reel.mp4
"<AE klasörü>/Support Files/AfterFX.exe" -r "<tam yol>/build/build.jsx"      # Windows
aerender -project build/reel.aep -comp REEL -output build/reel.mp4
```
`build/reel.log.txt`'yi oku: `EKSİK DOSYA`, `FONT YOK`, `HATA` satırlarını çöz. Canlı düzeltme ve kontrol için
after-effects-mcp araçlarını kullan (`getLayerInfo`, `setLayerProperties`, `setLayerKeyframe`,
`setLayerExpression`); büyük değişikliklerde shotlist'i düzeltip jsx'i yeniden üret (elle yapılan AE
değişiklikleri yeniden üretimde kaybolur — kullanıcıya söyle).

### 11. Kalite kontrol ve teslim
- `build/reel.mp4`'ün süresi, çözünürlüğü (1080x1920), sesi var mı (ffprobe).
- 1.5 sn arayla kare çıkarıp bak; varsa `rea-video decompose build/reel.mp4 -o build/qc --lang en` ile
  tempo karşılaştır (hedef aralıklar `references/stil-rehberi.md` sonunda).
- Teslim: MP4 yolu + .aep yolu + kısa özet (süre, sahne sayısı, kullanılan ses, kaynaklar) +
  kullanıcının elle değiştirebileceği yerler.

## Kurallar
- Ücretli üretimi (görsel, video, ses, müzik) kullanıcı onayı olmadan başlatma; aynı üretimi "tekrar dene" diye
  körlemesine yineleme — her çağrı ücretlidir.
- Gerçek kişilerin yüzlerini aşağılayıcı / yanıltıcı biçimde üretme; tarihî figürler için "portre tarzı"
  yeterli. Telifli karakter, logo, marka görseli üretme.
- Referans videolardaki görüntüleri, metinleri, sesleri kopyalama: yalnızca yapı, tempo ve stil taklit edilir.
- Uydurma bilgi yok; emin olmadığın bilgiyi senaryoya koyma.
- Kullanıcı bir aşamada geri bildirim verirse ilgili dosyayı (script / shotlist) güncelle ve sonraki adımları
  yeniden çalıştır; sıfırdan başlama.
