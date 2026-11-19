---
name: reel-video
description: Verilen bir konuyu (tarih, gizem, suç, biyografi, ekonomi…) Amed Güncel için earn.edits tarzında ~30–45 saniyelik dikey (9:16) Türkçe anlatımlı bir reel videoya çevirir ve bitmiş MP4'ü teslim eder. Araştırma, senaryo, gerçek fotoğraf bulma + maskeleme, gerekirse AI görsel (Magnific), seslendirme + müzik + efekt (ElevenLabs / Magnific), After Effects'te 3B kameralı kurgu (ExtendScript) ve render adımlarını kapsar. Kullanıcı "şu konuda video yap", "reel yap", "earn tarzı video", "bunu videoya çevir", "X. saniyedeki kareyi değiştir" dediğinde kullan.
---

# reel-video: konudan bitmiş reel'e

Bu skill, earn.edits videolarının kare kare incelenmesiyle (`references/analiz.md`) çıkarılan görünümü üretir ve
kullanıcının kanalı **Amed Güncel**'in tercihlerine göre ayarlıdır (`references/marka.md` — her videoda oku).

Görünümün özeti (ayrıntı `references/stil-rehberi.md`):
- **Gerçek fotoğraf önce**, yapay zekâ yalnızca gerçek görüntü bulunamayan yerde ve ekranda "Temsilî görsel" notuyla.
- **Katmanlı sahneler:** arka plan siyah-beyaz + halftone; konu fotoğraftan maskelenir, renkli ve beyaz konturlu öne
  çıkar; başlık arka plan ile konu arasında kalır. Pano üstünde iğneli polaroid + kırmızı ip, dağınık kelime kapanışı.
- **Gerçek 3B kamera:** sahneler uzayda dizilir, kamera aralarında uçar; her katmanda hareket bulanıklığı.
- **Genel doku:** halftone tüm videonun üstünde; toz, çizik, gren; sahne bazında sis.
- **Yazı:** Amed başlık fontu, kelime kelime gelen başlıklar, hap altyazı; kapanışta kanal animasyonu.

İki stil ailesi var: **earn** (varsayılan; yukarıdaki görünüm; örnek `examples/tahir-elci`) ve **hex** (1900 öncesi
tarih, icat, biyografi: sıcak yağlı boya tablolar + dönemin gerçek belgeleri, kayan ışık huzmeleri, sahneye gömülü
italik yazı, yavaş tempo; örnek `examples/el-cezeri`, ayrıntı `stil-rehberi.md` sonu). Kullanıcı söylemezse konuya
göre seç ve söyle; `stil-rehberi.md` sonundaki **alt tür** tablosundan (olay, dava, ekonomi, sanat, arşiv, gravür)
birini seç. Her videoda şunlar bulunsun: işaretleme öğeleri (`marks` / `labels`), 2–4 yazı kartı (`make_card.py`), en az 3
farklı geçiş (`iris`, `wipe_up` dahil), bir belge ya da gazete sahnesi, dev yıl / sayı yazısı. Kullanıcı yeni referans kareleri verirse önce `frame_sheets.py` ile **tamamını** incele ve
`analiz.md`'ye işle. Video dili her zaman Türkçe.

## Çıktı klasörü

```
projeler/<ad>/
  brief.md          konu, stil, süre, doğrulanan bilgiler, görsel kaynak tablosu
  script.md         anlatım metni
  shotlist.json     sahne listesi (şema: references/sahne-katalogu.md, örnek: examples/tahir-elci/shotlist.json)
  assets/real/      internetten / kullanıcıdan gelen gerçek fotoğraflar + sources.tsv
  assets/img/       hazırlanmış sahne görselleri (kırpımlar, maskeler, _bg / _fg / _ol katmanları)
  assets/vo.mp3, words.json, music.mp3, sfx/*.wav
  timeline.json     timeline.py çıktısı
  build/            build.jsx, reel.aep, reel.mp4 (TESLİM), qc/ (kontrol föyleri)
```
Oturum bir proje klasöründe değilse çalışma klasörü geçicidir: kullanıcıya kalıcı bir klasöre taşımayı öner.
**Yardımcı dosyaları oturumun geçici (scratchpad) klasörüne koyma** — oturum sırasında silinebiliyor.

Betikler: `S=~/.claude/skills/reel-video/scripts`. Ortak dosyalar shotlist'te `$SKILL/assets/...` diye yazılır.

## Akış

### 0. Ortam — `references/kurulum.md`
Python ortamı (Pillow, opencv, faster-whisper), ffmpeg, After Effects + `aerender`, Magnific / ElevenLabs
bağlayıcıları. Eksik olanı tek satırda söyle. AE yoksa dur ve sor: bu görünüm ffmpeg önizlemesiyle üretilemez.

### 1. Brief
Konu, süre (kullanıcı ne dediyse; söylemediyse 30–45 sn), stil. `references/marka.md`'deki varsayılanları
(font, kapanış, doku, dil hassasiyetleri) sormadan uygula. `brief.md`'ye yaz.

### 2. Araştırma
En az 3 bağımsız kaynak; senaryodaki her tarih, rakam ve isim kaynağa dayanır. Tartışmalı ya da yargıya konu olan
olaylarda kimseyi fail ilan etme, tarafları kötüleyen sıfat kullanma; mahkemenin / kaynakların dediğini aktar.
Kaynakları `brief.md`'ye ekle.

### 3. Senaryo — `references/senaryo.md`
Kanca → bağlam → dönüm → kanıt → sonuç → kapanış cümlesi. Seslendirme bu anlatıcıda ≈ **2,15 kelime/sn** çıkıyor:
30 sn'lik video için ≈ 58–62 kelime yaz (27 sn anlatım + 3,3 sn kapanış animasyonu). Rakamları yazıyla yaz;
altyazıda rakam görünsün istiyorsan seslendirmeden **sonra** shotlist'teki `narration`'ı rakama çevir.

### 4. Görseller — `references/gorsel-uretim.md`
1. **Gerçek fotoğraf ara:** Wikimedia Commons (lisanslı) + haber sayfalarının kapak görselleri. Kullanıcının
   gönderdiği fotoğraflar her zaman önceliklidir. Kaynak ve hak durumunu `brief.md` tablosuna yaz.
2. Bulunamayan sahneler için AI görsel (Magnific); gerçek kişi için referans fotoğrafla.
3. **Maskele:** katmanlı sahnelerde konuyu Magnific `images_segment` ile kes, `layer_prep.py` ile
   `_bg / _fg / _ol` katmanlarını üret. Düz zeminli AI figürler için `images_remove_background` + `cutout_prep.py`.
4. Her hazırlanan görseli **gözle kontrol et** (konu ortada mı, baş kesilmiş mi, logo / filigran kalmış mı).

Gösterme: ölüm anı, ceset, kan. Faili belli olmayan olayda ateş eden kişi üretme.

### 5. Sahne listesi — `references/sahne-katalogu.md`
Sahne 1,5–3,5 sn. Çerçeve ve geçişleri çeşitlendir (aynı geçiş art arda en fazla 2 kez). Tipik dağılım (12 sahne):
2–3 hizalı cutout (siyah-beyaz arka plan + renkli konu), 3–4 pano polaroidi, 1–2 düz cutout, 1 kolaj, 1 tam ekran,
1 dağınık kelime kapanışı. Başlık altyazıyı tekrar etmez, özetler. Altyazı bir yüzün üstüne geliyorsa o sahnede
`"caption": false` yap ve başlıkla anlat.

### 6. Maliyet onayı
Ücretli her kalemi (görsel, maske, ses, müzik, efekt) kredisiyle listele; kullanıcı onaylamadan üretme. Onaylanan
bütçenin içinde kalan küçük ek kalemler (maske 35, arka plan silme 3 kredi) için yeniden sorma, sonunda raporla.
ElevenLabs kotası dar: iki denemeden fazlası sığmayabilir; gerekirse seslendirmeyi Magnific `audio_tts` ile yap.

### 7. Ses — `references/ses.md`
Seslendirme (ElevenLabs, "Ogün Can" anlatıcısı) → hedef süreye `atempo` ile oturt → `words.py` ile kelime zamanları
→ müzik + 4 efekt (Magnific). Efektler `projeler/_ortak/` altında saklanıp yeniden kullanılabilir.

### 8. Kur ve render al — `references/after-effects.md`
```bash
bash $S/ae_build.sh projeler/<ad> --render      # timeline -> build.jsx -> AE -> aerender -> ses dengeleme
```
`build/reel.log.txt` içinde `TAMAM` görmeden devam etme; `HATA (satır N)` çıkarsa `build.jsx`'in o satırına bak.

### 9. Kare kare kontrol (zorunlu)
```bash
python3 $S/frame_sheets.py build/reel.mp4 -o build/qc/son --every 6
```
Föylerin **hepsine** bak (sahne geçiş anlarına ve kapanış klibinin ilk karelerine yakından). Sık çıkan kusurlar: başlık kadrajın üstünden taşıyor (kamera yaklaşması), konu başlığın
Türkçe harf işaretlerini kapatıyor, altyazı yüzün üstünde, polaroidde baş kesik, kapanış klibinin başında önceki
videodan kare, taşan uzun altyazı, serif fontta harfe benzeyen rakam, fazla karanlık genel görünüm. Düzelt → yeniden kur → yeniden bak. Sesi dinleyemezsin: bunu teslimde açıkça söyle.

### 10. Teslim ve düzeltme turları
MP4'ü gönder; kısa özet: süre, değişenler, harcanan kredi, hak durumu belirsiz görseller, doğrulayamadıkların.
Kullanıcı düzeltmeleri "X. saniyedeki kare" diye tarif eder ve çoğu zaman yeni fotoğraf gönderir: ilgili sahneyi
`timeline.json`'daki sürelerden bul, yalnızca o sahnenin görselini / alanlarını değiştir, önceki sürümü
`reel_vN.mp4` olarak sakla, yeniden kur. Sıfırdan başlama.

## Kurallar
- Ücretli üretimi onaysız başlatma; aynı üretimi körlemesine yineleme.
- Uydurma bilgi yok. Gerçek ve AI görselleri karıştırırken AI olanı ekranda işaretle.
- Haber sitelerinden alınan fotoğrafların hak sahibi çoğu zaman belirsizdir: kullan, ama teslimde söyle.
- Referans videolardan görüntü, metin, ses kopyalama; yalnızca yapı ve teknik.
- After Effects'te kullanıcının açık projesini asla kapatma / ezme (`ae_build.sh` bunu kontrol eder).
- Mocha / takip gibi araçlar yalnızca hareketli video görüntüsü varsa anlamlıdır; durağan fotoğrafta önerme.
- Betiklerde bir hata bulup düzeltirsen ya da yeni bir sahne tipi eklersen `references/` belgelerini de güncelle.
