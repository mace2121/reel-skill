# Görsel üretim (Magnific / Higgsfield)

Araç adları bağlayıcıya göre `mcp__Magnific__…` / `mcp__Higgsfield__…` biçimindedir; ilk kullanımdan önce şemayı
yükle (ToolSearch `select:<ad>`), parametre adlarını şemadan al — aşağıdaki akış genel kalıptır.

## Hangi araç
- **Magnific** (önerilen): `magnific_start` (plan / klasör bilgisi) → `images_models_list` (uygun model) →
  `images_generate` (prompt, 9:16 oran, adet) → `creations_wait` → `creations_read` ile sonucu gözle kontrol →
  indirme URL'sinden `curl -L -o assets/img/sXX.png`. Fiyat için önce `simulate_cost`.
- **Higgsfield**: `generate_image` (varsayılan model iyi; oran 9:16) ya da `generate_image_batch` (tüm sahneler
  tek seferde) → `jobs_wait` → sonuç URL'sini indir. Fiyat: `estimate_image_cost`.
- Görsel→video gerekiyorsa (en fazla 2–3 kahraman sahne): Higgsfield `generate_video` ya da Magnific
  `video_generate`, 5 sn, kamera hareketi az; `assets/vid/sXX.mp4` → sahnede `"video"`. Önce fiyat + onay.

Tüm sahneleri **toplu** üret (batch), tek tek değil; ilk turda her sahneden 1 adet, beğenilmeyenleri yeniden.

## Stil blokları (her prompt'un sonuna eklenir)

**earn**
```
vertical 9:16 composition, cinematic documentary still, dramatic contrasty lighting, rich saturated colors,
warm orange highlights and cool teal shadows, shallow depth of field, ultra detailed, photorealistic,
subject centered in the middle 60% of the frame, empty space at top for a headline, no text, no letters, no watermark
```
Masa üstü obje sahneleri için başa: `top-down flat lay on a worn dark wooden desk` / `on a green cutting mat` /
`on black grunge paper`.

**hex**
```
vertical 9:16, 19th century steel engraving / antique oil painting style, sepia monochrome, fine crosshatching,
aged paper texture, museum archive look, soft directional window light, subject centered, no text, no letters,
no watermark, no modern objects
```
Fotoğraf dönemi (1900–1950) için: `vintage black and white archival photograph, film grain, 1930s` .

## Prompt kalıbı
`[konu / eylem], [dönem + yer], [kamera: wide / medium / close-up / top-down], [ışık], ` + stil bloğu.
- Her sahnede **tek ana fikir**. Kalabalık sahnede bile odak tek.
- Başlık gelecek sahnelerde üst %25'i sade bırak ("empty sky / dark background at top").
- Polaroid / daire çerçevesine girecek görsel: konu tam ortada, kare kırpmaya dayanıklı.
- Split için iki ayrı görsel (`image`, `image2`), ikisi de aynı ışık / renk.
- Tarihî kişi: "portrait in the style of a 19th century oil painting of a man resembling …" yerine adı ve dönemi
  yaz; gerçek kişiyi aşağılayıcı / yanıltıcı sahnelerde gösterme.
- Telifli karakter, logo, marka ürünü, gerçek gazete adı (NYT vb.) yazdırma; gazete için "old newspaper with
  unreadable headline" iste, başlığı AE'de kendin yaz.

## Kontrol (her görsel)
Read ile aç ve bak:
- [ ] el / yüz / parmak bozukluğu yok
- [ ] anlamsız harf / sahte yazı yok (varsa yeniden üret ya da o bölgeyi kırpılacak şekilde seç)
- [ ] dönem doğru (modern nesne yok)
- [ ] stil diğer sahnelerle tutarlı (renk / doku)
- [ ] 9:16 ve en az 1024 px genişlik
Sorunlu olanı prompt'u düzelterek yeniden üret; `prompt` alanını shotlist'te güncelle.
