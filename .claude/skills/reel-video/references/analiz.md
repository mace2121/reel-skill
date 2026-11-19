# Referans analizi (rea-video decompose + sahne sahne inceleme)

9 video, 2026-11-18. Araç: [rea-video](https://github.com/JuneYaooo/rea-video) (VLM yok; sahneler görsel olarak
elle incelendi). Araç durağan görsel animasyonlarını sık sık "AI video" / "3D render" olarak etiketliyor; görsel
incelemede hepsinin **AI durağan görsel + AE hareketi + motion graphics** olduğu görüldü.

| # | Hesap | Konu | Süre | Sahne | Kesme/dk | Not |
|---|---|---|---|---|---|---|
| 1 | earn.edits | Cadılar Bayramı'nın kökeni | 41.9 | 13 | 18.6 | Kırmızı ay kancası, polaroid panosu + kırmızı ip, daire içinde bölünmüş görüntü (yaşayanlar/ölüler), altıgen geçiş, tek kelime kinetik yazı, eski TV'de CTA |
| 2 | earn.edits | Buffett'ın 381 milyar dolar nakdi | 47.1 | 24 | 30.6 | En hızlı kurgu; kesilmiş Buffett figürü kırmızı-beyaz hipnoz sarmalında, sayaç rakamlar, kara tahta, yeşil kesme matı üzerinde para / avuç, klip-board üzerinde el yazısı "The real question is", sonda bulut + polaroid kamera |
| 3 | earn.edits | Korku / "What if" (motivasyon) | 42.2 | 12 | 17.1 | Ünlü bir tabloyu duvarda farklı ışıklarla tekrar tekrar gösterir; turuncu çerçeveli altyazı, AE logoları |
| 4 | earn.edits | D.B. Cooper uçak kaçırma | 43.5 | 16 | 22.1 | "WANTED" ve gazete kupürü (sarı vurgu kalemi), ahşap masa üstü obje kurgusu, uçak üstten, eski TV'de eşkal, "RANSOM MONEY" başlığı |
| 5 | earn.edits | Project A119 (Ay'ı bombalama) | 40.7 | 11 | 16.2 | "DESTROYING THE MOON" kırmızı başlık, kırmızı tonlu 1950'ler bilim insanı, NYT gazetesi masada, siyah ekranda italik "But" |
| 6 | earn.edits | Ölü Papa'nın yargılanması (897) | 39.4 | 16 | 24.4 | Sinematik Orta Çağ sahneleri, sarı "PUT ON TRIAL" fırça yazı, mavi gridli zeminde gravür kartı "897 AD", kırmızı kumaş üstünde tarih kitabı sayfası |
| 7 | hex_creatives | Alışveriş arabasının mucidi | 61.1 | 22 | 21.6 | Siyah-beyaz 1930'lar market fotoğrafları, kesilmiş figür + siyah boşluk, italik serif tek kelime, patent çizimi, sonda günümüz market görüntüleri |
| 8 | hex_creatives | Colt tabancası / Samuel Walker | 76.8 | 22 | 17.2 | Sepya yağlı boya / gravür, güçlü ışık sızmaları, gemi güvertesi tekrar eden set, yeşil isim şeridi, "Purchase Order 1,000 revolvers" belge |
| 9 | hex_creatives | Anestezinin keşfi (1846) | 48.9 | 24 | 29.4 | Siyah-beyaz gravür ameliyathane, diyagonal ışık huzmesi geçişleri, büyük italik anahtar kelime ("leather", "room"), sonda bugünkü bina |

## Ortak kalıplar

1. **Anlatı:** kanca (şaşırtıcı iddia) → "Yıl …" bağlam → kural / inanış → dönüm ("Ama…", "Ve bir gün…") →
   kanıt / sonuç → bugüne bağlama → duygusal tek cümle → (earn) CTA.
2. **Görsel kaynak:** neredeyse tamamı AI durağan görsel; hareket AE'de. Video modeli gerekmiyor.
3. **Yazı:** konuşma ile senkron kelime / ifade; anahtar kelime renkli; bölüm başlarında büyük kinetik başlık.
4. **Ses:** TTS'e benzer anlatıcı, alçak müzik (83–150 BPM), video başına 16–25 efekt; efektlerin çoğu
   yazı girişine ve kesmelere denk.
5. **Geçiş çeşitliliği:** her 2–4 sn yeni bir geçiş türü; aynı geçiş arka arkaya en fazla 2–3 kez.

## Kare kare inceleme: earn.edits "Halloween" (1.259 kare, 41,9 sn)
`frame_sheets.py <kare klasörü> -o ref/s --every 4` ile föylenip tamamı incelendi. Görülen teknikler:

| Zaman | Teknik |
|---|---|
| 0–1 sn | Kamera aydan kapıya hareket bulanıklığıyla iner; yarasalar, sis, kesilmiş nesne (şeker) ayrı katman |
| 0,8–3 sn | Başlık çarparak girer; alt satır kelime kelime, bulanıktan netleşerek |
| 2 sn, 16,5 sn | Geçişte kısa siyah-beyaz + radyal bulanıklık; başlık sahne değişse de ekranda kalır |
| 3,3 sn | Daire büyüyerek açılan geçiş |
| 5 sn | Dev kırmızı harfler kadrajdan geçer, sahne renkten siyah-beyaza döner, kırmızı parlayan başlık |
| 7–10,5 sn | Koyu dokulu kağıt alttan kayar; damga başlık; iğneli polaroidler, kırmızı ip boyunca yana kayan kamera |
| 10,6 sn | Polaroidin içinden daire açılarak tam ekrana geçiş |
| 14–16 sn | Kesik çizgili halka içinde bölünmüş daire, arkada sis ve kıvılcım, el yazısı çok satırlı yazı |
| 17–19 sn | 3B derinlikli başlık; kesilmiş figürler yandan bulanık girer; altıgen desenli geçiş |
| 22–26 sn | Koyu dokulu zemin, hareketli vektör yarasalar, ortada tek kelime altyazı |
| 27–31 sn | Sisli koridor; kesilmiş nesne dönerek uçar; kamera kapının içinden geçerek sonraki sahneye |
| 33–36 sn | Kırmızı parlama → çizikli koyu zemin, dağınık italik kelimeler |
| 36,6 sn– | Beyaz daire açılır, kanal kapanışı |

Her karede: halftone / gren dokusu, yumuşak odak, vinyet, sis; hiçbir kare 1,5 sn'den uzun hareketsiz kalmıyor.
Bizde karşılığı olmayanlar (istenirse eklenebilir): altıgen geçiş, sahneler arası kalıcı başlık, hareketli vektör
nesneler, renk → siyah-beyaz sahne içi dönüş.
