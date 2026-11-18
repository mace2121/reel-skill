# Stil rehberi

9 referans videonun `rea-video decompose` + sahne sahne görsel incelemesinden çıkarıldı (ayrıntı: `analiz.md`).
Ortak paydada **ikisi de aynı motor**: AI ile üretilmiş *durağan* görseller After Effects'te hareketlendirilir
(push / pan / parallax), üstüne kinetik yazı ve geçişler bindirilir, altta anlatım + müzik + efektler.
Video modeli neredeyse hiç gerekmez; hız ve çeşitlilik kurgudan gelir.

## Ortak kurallar (iki stil)

- **Format:** 1080x1920, 30 fps (hex 24 fps de olur), 40–75 sn.
- **Tempo:** dakikada 16–30 kesme (ortalama sahne 2–3.5 sn). Sahne içinde de en az bir "olay" olsun
  (başlık girer, polaroid düşer, kelime değişir) — ekran 1.5 sn'den uzun hiç değişmeden durmasın.
- **Kanca ilk 2 sn'de:** şaşırtıcı iddia + güçlü görsel + başlık çarpması.
- **Kelime kelime altyazı:** her kelime ya da 2–3 kelimelik parça konuşma anında görünür; anahtar kelime renkli.
- **Ses:** tek anlatıcı (TTS kabul), altında düşük müzik (−17…−20 dB), her geçişte whoosh, her başlıkta vuruş.
  Kesmeler müzik vuruşuna değil **anlatıma** oturur.
- **Kapanış:** duygusal tek cümle → (earn) CTA kartı.

## earn — karışık medya belgesel

| Öğe | Nasıl |
|---|---|
| Görsel dil | Fotogerçekçi ya da sinematik AI görseller (Halloween, uçak kaçırma, Ay, Buffett) + **masa üstü objeler**: eski gazete kupürü, polaroid, kara tahta, klip-board, dosya, para, harita; arka planda doku (ahşap masa, yeşil kesme matı, grunge siyah kağıt, kırmızı kumaş) |
| Çerçeveler | Tam ekran; **daire maske** içinde görsel (beyaz ince halka, arkada bulanık aynı görsel); **polaroid** (beyaz kart, hafif eğik, altında el yazısı / büyük harf etiket, kırmızı iple panoya iğneli); **bölünmüş** ekran (iki görsel, ortada parlayan eğik çizgi: "yaşayanlar / ölüler", "Avrupa / Osmanlı") |
| Başlık | Kalın sıkışık sans (Anton / Bebas tarzı), TAMAMI BÜYÜK HARF, sarı veya kırmızı, gölgeli; **slam** (büyükten küçülerek çarpar + vuruş sesi) ya da **stamp** (çerçeveli, −6° eğik "2.000 YIL ÖNCE"). Bazen kelime içinde sansür yıldızı ("DE*D") |
| Altyazı | Ekranın %70 yüksekliğinde koyu yarı saydam **hap** içinde beyaz yazı (Poppins SemiBold), 1–3 kelime, anahtar kelime kırmızı |
| Geçiş | Çoğunlukla **blur whip** (dikey kayma + yön bulanıklığı), arada zoom blur, flash, daire açılış, fırça / altıgen maske |
| Renk | Doygun, sıcak-turuncu ↔ soğuk-mavi kontrast, hafif grain, vinyet |
| Kapanış | Ürün / kanal kartı (earn.edits'te eski TV ekranında "Editors Learn Faster" + AEP ikonu + URL). Sen: "TAKİP ET" + slogan |

## hex — vintage arşiv / gravür

| Öğe | Nasıl |
|---|---|
| Görsel dil | **Gravür, çelik baskı, yağlı boya portre, 1800'ler fotoğrafı** görünümlü AI görseller; siyah-beyaz ya da sepya; ameliyathane amfisi, gemi güvertesi, Napolyon portresi, eski market |
| Çerçeveler | Çoğunlukla tam ekran; kesilmiş figür (cut-out) düz arka plan üstünde; portre altında isim etiketi (yeşil / altın şerit); arşiv belgesi (sipariş formu, patent çizimi) masa üstünde |
| Hareket | Yavaş push + **2.5D parallax** (ön figür ve arka plan ayrı hızlarda), hafif dönme |
| Altyazı | Ekran **ortasında tek kelime**, italik serif (Playfair Display Italic), krem rengi, yumuşak belirme; anahtar kelime büyük ve altın rengi ("leather", "room") |
| Başlık | Nadiren; isim / yıl etiketi ("Samuel Walker", "It's 1936.") |
| Geçiş | **Işık sızması** (turuncu-sarı ışık huzmesi soldan sağa), yumuşak fade, film yanığı; periyodik ışık sızmaları sahne içinde de geçer |
| Renk | Sepya tint %60–70, yükseltilmiş siyahlar, grain, güçlü vinyet |
| Kapanış | CTA yok ya da tek satır; günümüze bağlayan son görüntü (modern market, bugünkü bina) |

## Konu → stil seçimi

- earn: suç / gizem (D.B. Cooper), para / yatırım (Buffett), soğuk savaş (Ay'ı bombalama), gelenek kökenleri
  (Cadılar Bayramı), motivasyon (korku), din / Orta Çağ tuhaflıkları (ceset yargılama).
- hex: icat hikâyesi (alışveriş arabası, Colt tabancası), tıp tarihi (anestezi), 18.–19. yüzyıl biyografi.

## Hedef aralıklar (kalite kontrol)

`rea-video decompose build/reel.mp4` çıktısıyla karşılaştır:

| Ölçü | earn | hex |
|---|---|---|
| Süre | 40–48 sn | 45–77 sn |
| Sahne sayısı | 11–24 | 22–24 |
| Kesme / dk | 16–31 | 17–29 |
| Altyazı satırı | konuşmanın tamamı | her kelime |
| Efekt sayısı | 16–25 | 16–19 |
