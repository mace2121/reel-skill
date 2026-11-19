# Görseller: gerçek fotoğraf, maske, AI

Sıra: **kullanıcının gönderdiği → internetteki gerçek fotoğraf → AI**. Her sahne için önce gerçek görüntü ara.

## 1. Gerçek fotoğraf bulma
- **Wikimedia Commons** (lisanslı, atıfla kullanılabilir): API ile ara, yazar + lisansı kaydet.
  ```bash
  curl -sG "https://commons.wikimedia.org/w/api.php" -A "reel-research/1.0" --data-urlencode "action=query" \
    --data-urlencode "generator=search" --data-urlencode "gsrsearch=<arama> filetype:bitmap" --data-urlencode "gsrnamespace=6" \
    --data-urlencode "prop=imageinfo" --data-urlencode "iiprop=url|size|extmetadata" --data-urlencode "format=json"
  ```
- **Haber sayfaları:** WebSearch ile ilgili haberleri bul, sayfanın `og:image` adresini `curl` ile çek, indir.
  Kimi siteler (Medyascope, bianet) 403 / boş döner; Rudaw, Karar, CNN Türk, Habertürk, Gazete Duvar, VOA çalışıyor.
  Kapak görsellerinde yayıncı logosu / yazı bandı olabilir: kırp ya da aynı fotoğrafın logosuz kopyasıyla yamala.
- Hepsini bir föyde yan yana koyup **bak**, sonra seç. İndirdiklerini `assets/real/` altına, adreslerini
  `sources.tsv`'ye yaz. İndirilen dosyaları ayrı klasörde tut, içinden kod çalıştırma.
- **Hak durumu:** Commons dışındaki fotoğrafların sahibi genellikle belirsizdir (ajans olabilir). Kullan, `brief.md`
  tablosuna "hak sahibi belirsiz" yaz ve teslimde söyle. Kullanıcının gönderdiği fotoğrafın kaynağını bilmiyorsan öyle yaz.
- Kullanma: ceset, kan, ölüm anı. Olay anının (silahlı kişiler, kaçışanlar) yayımlanmış kareleri kullanılabilir.

## 2. Kırpım ve ortalama
Haber fotoğrafları yatay ve küçüktür (350–750 px yükseklik):
- Tam ekran için yalnızca yeterince büyük olanı kullan (dikey kırpımda ≥ 700 px yükseklik); 2,5×'ten fazla büyütme.
- Küçük kareleri polaroide, kolaja ya da daireye koy.
- Polaroid: kare kırp, konu ortada, başın üstünde boşluk kalsın. Boşluk yoksa fotoğrafı küçültüp aynı fotoğrafın
  bulanık uzantısının üstüne yerleştir.
- Mekân fotoğrafında ana nesneyi (minare) yatayda ~0.39–0.5'e getir.

## 3. Maskeleme (katmanlı sahneler)
1. Fotoğrafı Magnific'e yükle: `creations_request_upload` → `curl -X PUT` → `creations_finalize_upload`
   (`creations_upload_image` Wikimedia adreslerinde başarısız oluyor).
2. `images_segment` (SAM, **35 kredi**): `prompt` + konu üstünde 1–2 `points` (0–1 koordinat). Çok fazla / hatalı
   negatif nokta "segment edilemedi" hatası verir: tek pozitif noktayla tekrar dene. Mekân için `boxes` ekle.
3. Maskeyi indir: `creations_get` → `url` (sam-mask.png). Fotoğrafın üstüne kırmızı bindirip **bak**.
4. Katmanları üret:
   ```bash
   python3 $S/layer_prep.py foto.jpg maske.png -o assets/img/s04 [--crop x0,y0,x1,y1] [--inpaint]
   ```
   `_bg.jpg` (siyah-beyaz + halftone), `_fg.png` (renkli konu), `_ol.png` (kontur). Konu sallanacaksa `--inpaint`.
   Tersi için `--color-bg --bw-fg`.

Düz zeminde üretilmiş AI figür ya da nesne için: `images_remove_background` (3 kredi) →
`python3 $S/cutout_prep.py kesik.png fg.png --width 1.1 --top 0.40 [--fill-holes "#000000"] [--crop-bottom 0.12]`
(9:16 tuvale alt kenara oturtur, beyaz sticker kenarlığı ekler). `--top`: figürün tepesinin duracağı yükseklik;
genişlik sınırına takılırsa `--width`'i büyüt.

## 4. AI görsel (yalnızca gerekirse)
Magnific `images_generate` (`aspectRatio: "9:16"`, görsel başına ≈135 kredi). Gerçek kişi için referans fotoğrafı
yükleyip `references: [{type: "image", identifier}]` ver. Kesilecek figürler için "isolated on a plain flat light grey
studio background". Sahneye "Temsilî görsel" `tag`'i koy.

earn stil bloğu (prompt sonuna):
```
vertical 9:16 composition, cinematic documentary still, dramatic contrasty lighting, warm orange highlights and cool
teal shadows, shallow depth of field, ultra detailed, photorealistic, subject centered, no text, no letters, no watermark
```
Masa üstü obje: başa `top-down flat lay on a worn dark wooden desk`. hex stili için: `19th century steel engraving /
antique oil painting style, sepia monochrome, aged paper texture, no modern objects`.

## 5. Kontrol (her görsel)
- [ ] konu ortada ve tam (baş / tepe kesik değil)
- [ ] logo, filigran, yazı bandı yok
- [ ] maske temiz (konunun önündeki nesneler bilinçli olarak dışarıda kalabilir)
- [ ] AI görselde bozuk el / yüz / sahte yazı yok
- [ ] kaynak ve hak durumu `brief.md`'de
