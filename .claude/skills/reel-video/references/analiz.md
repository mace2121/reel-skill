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

## Kare kare inceleme: hex_creatives "anestezi" (1.468 kare, 49 sn) ve "Colt" (1.843 kare, 77 sn)

| Gözlem | Anestezi | Colt |
|---|---|---|
| Görsel | Siyah-beyaz gravür / eski fotoğraf görünümü; tek renk vurgu (kırmızı kan, sarı sıvı) | Sıcak turuncu-sepya yağlı boya; mavi deniz, yeşil şerit gibi sınırlı renk |
| Kamera | Kesilmiş figürlerle yavaş 3B parallax; aynı sahnenin yakın / uzak yeniden kadrajı; odak kaydırma | Aynı; nesneler (dümen, top) sahne içinde döner |
| Işık | Çapraz pencere ışığı huzmesi, kadrajı yıkayan beyaz geçiş, kenarda bulanık ön plan gölgeleri | Sürekli kayan dikey sıcak ışık bantları, film yanığı |
| Yazı | Sahnenin içinde küçük serif öbek, kelime kelime; anahtar kelime büyük italik; hap yok | Aynı + koyu yeşil şerit üstünde isim / yıl etiketi |
| Ara sahne | Beyaz ışık içinde yıl ("On October 16th, 1846") | Eski kağıt + silik tabanca çizimleri + daire içinde cümle; ahşap masada belge |
| Vurgu | Sarı çizgiyle izlenen hortum | Sarı çizgiyle izlenen ufuk / süvari hattı |
| Tempo | 24 sahne, ağır anlatım | 22 sahne, ağır anlatım |
| Kapanış | Bugünkü bina ("still stands today") | Belge (sipariş formu) |

## Yedi videonun kare kare incelemesi (19.11.2026: 2 hex_creatives + 5 earn.edits; toplam ≈ 8.400 kare, her 2.–3. kare föyle bakıldı)

### v1 hex_creatives 1778744949 "bilek saati / Santos-Dumont" (1927 kare, 64 sn) 
- Açılış: krem zemin, renkli moda gravürü figürleri kesilmiş, sıra halinde yana kayar; büyük serif "What if" figürlerin ARKASINDA, küçük devam cümlesi altında.
- Altyazı = TEK KELİME / 2-3 kelime, hep aynı noktada (ekran ortası), küçük serif; açık zeminde siyah, koyuda beyaz; kelimeler birikir sonra sıfırlanır ("He" → "He lands," → "gets" → "gets in"). Anahtar ifade SARI FOSFORLU KUTU içinde italik ("feminine", "better way", "It's a woman's thing").
- Elle çizilmiş sarı elips ayrıntıyı işaretler (bilek) + büyük sarı italik yıl "1904" hane hane yazılır.
- Geçişler: alttan yükselen beyaz perde (wipe up), beyaza yıkama, odak bulanıklığıyla aynı sahnenin yakın kadrajına geçiş, dikey itme (bina → menü belgesi aşağıdan girer, belge yukarı kayar).
- Boş kart sahneleri: açık gri/krem kağıt + yalnızca kelimeler (nefes, 1-1,5 sn), bazen kenardan kesilmiş nesne girer (kadeh tokuşturan eller).
- Gerçek arşiv filmi (siyah-beyaz sokak) + küçük sarı etiket "PARIS" + büyük beyaz italik "1901"; önden geçen koyu siluetler.
- Portre açılışı: kare çerçeve boş belirir, portre içinden aşağıdan yükselir (maske), isim çerçevenin altına harf harf yazılır.
- Aynı kesilmiş figür art arda farklı arka planların önünde (restoran → malikâne → kırmızı halı), kamera uzaklaşır.
- Renkli figür + siyah-beyaz mekân (iki adam masada).
- Kesilmiş uçak bulutların önünde süzülür, yakın plan yeniden kadraj; aynı sahne videoda 3 kez geri döner (leitmotif).
- Sonda hızlı ürün/belge montajı (0,3-1 sn kesmeler), altyazı ürünün üstünde koyu kutu içinde; kapanışta açılış sahnesine dönüş (halka yapı).
- Halftone yok, ışık huzmesi yok; hafif vinyet + kağıt dokusu.

### v2 hex_creatives 1794901275 "alışveriş arabası / Goldman" (734 kare, 61 sn, 12 fps) 
- Tamamen siyah-beyaz arşiv fotoğrafı; sonlara doğru renkli eski film, en sonda bugünün renkli görüntüsü (dönem ilerledikçe görüntü de ilerler).
- Açılış: siyah zemin, fotoğraf "kart" olarak durur; kişi karttan kesilmiş, beyaz konturlu, kartın kenarından taşar; sarı fırça çizgileri kadrajı çaprazlar; kamera içeri dalıp sonraki fotoğrafa geçer (zoom-through).
- Altyazı = küçük italik, 1-3 kelime; (a) konunun üstünde siyah etiket kutusunda, nesneye yapışık hareket eder, (b) sahnenin içine perspektifle gömülü: duvarda sola yaslı 3-4 satır büyük italik ("at the entrance / to show / how to use them"), zeminde yıl ("It's 1936."), gökyüzünde binanın iki yanına bölünmüş kelimeler; anahtar kelime sarı.
- Portre: beyaz çerçeveli kare + sarı isim etiketi, siyah zeminde.
- Belge sahnesi: patent sayfaları masaya tek tek düşer (üst üste, eğik); sonra nesne parça parça kurulur (çubuklar uçar, tekerlekler yuvarlanır, sepetler iner); arkasından gazete ilanı alttan yukarı kayar.
- Boş kart: açık kağıt ya da çok koyu silik mekân + tek cümle ("Nobody wants one.").
- Arşiv filmi kareleri: altyazı küçük koyu kutuda, kişinin göğüs hizasında.
- Çok figürlü "sahne": kesilmiş kişiler koyu boşlukta, her birinin üstünde küçük etiket; kamera yana kayar.
- Halftone / huzme yok; toz zerreleri + hafif gren.

### v3 earn.edits 1793626737 "D.B. Cooper" (1305 kare, 43 sn; son 6 sn reklam) 
- AKAN ALTYAZI YOK: yalnızca 2 satırlık başlıklar (üst satır beyaz küçük, alt satır sarı büyük; harfler karışık sırayla belirir). Alt satır kişinin başının ARKASINDA kalır. Aynı sahnede alt satır yerinde değişir ("$200,000" → "4 PARACHUTES"). Tek satırda iki renk ("NEVER" beyaz + "IDENTIFIED" sarı).
- Açılış ve sahne arası "gökyüzü köprüsü": kamera bulutlara çıkar, bulanıklaşır, yeni sahneye iner. Tarih kartı da gökyüzünde: "NOVEMBER 24" küçük beyaz + "1971" dev sarı; sonra yukarı kayıp çıkar.
- Geçişler: sis / duman beyazlatması, dikey şerit (jaluzi) silme, daire iris, whip bulanıklığı.
- İsim etiketi: kişinin yanında sarı yuvarlak köşeli etiket, isim harf harf yazılır ("Dan Cooper").
- Renk vurgusu: sahnedeki tek nesne yeşil parlar (para), gerisi normal.
- Sarı not kartı: üstten görünen nesnenin (uçak) üstünde sarı kart, siyah kalın yazı 2 satır, kelime kelime.
- Gazete sahnesi: gazete ahşap masaya düşer, kamera yaklaşır, manşetin üstünden sarı fosforlu kalem geçer; ardından üstüne tek satır başlık.
- Kesilmiş nesne (uçak) gökyüzünde yana kayar, başlık uçağın ARKASINDA.
- Kapanış: sarı kareli zemin + derin gölgeli beyaz kalın yazı, 2 satır (büyük + küçük), iki kart art arda ("ONE MAN / ONE DARING ESCAPE", "MYSTERY / REMAINS UNSOLVED").
- 12 sahne / 37 sn → sahne başı ≈ 3 sn; görseller tam kare AI illüstrasyon, halftone bu videoda belirgin değil.

### v4 earn.edits 1794571254 "Kadavra Sinodu" (1182 kare, 39 sn; son 5 sn reklam) 
- Kanca (0-4,5 sn): 3 hızlı sahne, altyazı yok, 2 satır başlık (beyaz + kırmızı / sarı, bulanıktan netleşir, ışıma). Bulutlardan iniş, üstten görünüş, renk çakması (yeşil → turuncu → kahve), dikey whip + RGB ayrışmalı bulanıklık.
- Kancadan sonra hap altyazı başlar: küçük koyu yuvarlak hap, beyaz yazı, 1-2 kelime, alt-orta, sabit.
- Kağıt kart sahnesi: kraft kağıt + ışık huzmeleri + ince kare doku; koyu serif italik tarih "897 AD"; gravür portre kartları (beyaz kenarlı) eğik uçarak gelir, durur, yana kayıp çıkar; kartın altındaki ismin altına KIRMIZI ÇİZGİ çekilir; giriş anında 1 karelik negatif (mavi) çakma.
- Daire iris: karttaki bir noktadan daire açılır, sonraki sahne içinden çıkar. Kapanışta tersi (daire kapanır).
- Alıntı yazısı: daktilo (monospace) font, tırnak içinde, büyük harf, harf harf yazılır, konunun yanında boşlukta ("DRESSED IN PAPAL ROBES."); doruk cümlede neon kırmızı ışıma.
- Seçici renk: sahne siyah-beyaz, yalnızca vurgulanan kişi renkli; sonra tersine döner. Doruk anında tüm sahne KIRMIZIYA boyanır (renk seli), ardından aynı renkten daire büyüyerek sonraki sahneye geçer.
- Aynı geniş tablo 4-5 kez farklı kadrajla kullanılır (yana kayma, yakınlaşma, odak kaydırma).
- Belge: kırmızı dokulu zeminde eski sayfa; satırlar sırayla kırmızı fosforluyla boyanır; sayfa dönerek çıkar.
- Dağınık serif italik kelimeler koyu tozlu zeminde (scatter).
- Final: üstten portre, yavaşça renksizleşir, gözlerin üstünde kırmızı ışıklı kelime; daire kapanır → koyu kartta kırmızı kalın başlık.
- Halftone / film çizgisi dokusu tüm videoda hafif.

### v5 earn.edits 1778756705 "Warren Buffett nakitte" (755 kare, 47 sn; son 6 sn reklam)   [ekonomi / açıklayıcı alt türü]
- Görünüm: kağıt kesme kolaj. Kişi kalın renkli konturla (çıkartma gibi) kesilmiş; arka planda iç içe kağıt halkalar; üstten "masa düzeni" sahneleri (banknotlar, bayrak, kalem, pano); düz renkli dokulu kartlar (kırmızı, mavi, yeşil kareli, koyu gri).
- Altyazı İLK KAREDEN var: küçük beyaz yazı, yarı saydam koyu kutu, 2-4 kelime, alt-orta, hep aynı yerde; başlıklar bunun üstünde ayrı.
- Sayılar: kağıt karo "300" → karo çevrilip "381" (kırmızı karo); "200" → "230" haneler zıplayarak değişir; "80%" kırmızı, sayarak büyür; 1 / 2 / 3 sayım kartları (her biri farklı zemin rengi, 0,3 sn) → "THREE YEARS".
- El yazısı altın rengi vurgu ("billion dollars") harf harf yazılır.
- Dikey kelime sütunu: THEN THE / WHOLE / COUNTRY / OF / GREECE alt alta birikir, önüne harita kartı kayar.
- Aksesuar üstünde yazı: kara tahtaya yazı yazılır ("S&P 500"); panodaki kağıda el yazısı ("The real question is"); sarı kart kayarak gelir, üstünde 3 satır.
- Büyüteç geçişi: yuvarlak mercek kadraja girer, sahneyi büyütüp yakın plana geçirir.
- Kadraja giren eller banknot sürer (stop-motion hissi); avuç içinde kırmızı etiket "WHY".
- Düz mavi kart + serif yazı; yıllar yeşil kutuda vurgulu ("In [1999]" / "And [2007]").
- Portre altın çerçevede, çerçevenin etrafında banknot yelpazesi döner; kişinin başı açılır içinden nesne çıkar (mizahi kolaj).
- Koyu kartta "arıza" fontu (kırmızı / beyaz) kelime kelime; kırmızı kartta sarı kalın 3 satır.
- Tempo çok hızlı: 41 sn'de ≈ 22 sahne (ortalama 1,9 sn).

### v6 earn.edits 1790590458 "Çığlık / Munch" (1266 kare, 42 sn; son 6 sn reklam)   [sanat alt türü; earn ile hex arası]
- Hap altyazı YOK; yazı tamamen sahneye gömülü. Açılış kilidi (lockup) karışık font: küçük serif italik "What if" + büyük kırmızı serif italik "Fear" + küçük düz satır + serif italik "Painting", sola yaslı, kelime kelime.
- Sabit "set": spot ışıklı müze duvarı. Aynı duvar 5-6 sahnede sahne olarak kullanılır: duvarda yıl "1892" (altında kırmızı çizgi) → kişi kesilmiş olarak önünden geçer / durur (sarı yırtık kağıt isim etiketi) → çerçeveli tablo eğik sallanarak gelip yerine oturur → kamera 3B eğilir.
- Açıklama okları (callout): tablonun çevresinde ince çizgili küçük etiketler ("Oil", "Pastel", "Paper"); tablonun bölgelerinin üstünde tek kelimeler ("Fear", "Isolation", "Anxiety") sırayla belirir.
- Tablonun içine dalış (zoom-through) → siyah-beyaz kolaj; üstünden kesilmiş uçaklar uçar; kırmızı yazı.
- Spot kartı: koyu turuncu kareli zemin, hareket eden ışık konisi, içinde tek tek serif italik kelimeler ("And / here's / a / strange / fact").
- Beyaz duvar + 4 tablo ızgarası: ışık parlaması üstlerinden geçer, kamera yana kayar, yanlarına etiket yazılır.
- Nesne üstünde vurgu: tablonun bir bölümü kırmızı ışıkla boyanır, üstünde büyüteç şeridi (yakından yazı).
- Kesim matı (yeşil kareli) üstünde tablo, kadraja fırça tutan el girer; üstte daktilo satırı kelime kelime yazılır, imleç bloğu görünür.
- Mavi spot + bokeh ışık topları; kare çerçeve küçülerek kaybolur → koyu zeminde dağınık kelimeler (scatter), sonra hepsi birlikte dönerek uzaklaşır.
- Tempo: 36 sn'de ≈ 12 sahne ama her sahnede 3-4 alt hareket (kadraj değişimi, nesne girişi).

### v7 earn.edits 1794149862 "Ay'ı vurma planı / Project A119" (1223 kare, 41 sn; son 5 sn reklam) 
- Hap altyazı YOK; yalnızca başlıklar. Açılış başlığı eğik (≈ -12°), kırmızı + beyaz 2 satır + minik 3. satır, ışık çizgileriyle çarparak gelir; sahne 1 karelik kırmızı çakma ile vurgulanır.
- Sürekli kamera: sahneler arası kesme yerine dikey kaydırma (Ay → roket rampası → izleyenler), odak kaydırma, ön planda bulanık siluetler.
- Tarih etiketi: kırmızı yuvarlak köşeli kutu + beyaz kalın "1950s", dönerek gelir, sahnedeki ekranın üstüne oturur.
- Seçici renk: sahne siyah-beyaz, yalnızca bilim insanının önlüğü / gazete renkli.
- Gazete sayfası sahnenin İÇİNE uçarak gelir (kıvrık, 3B), durur, çıkar; ayrı sahnede ahşap masaya düşen gazete + yavaş yaklaşma.
- Uzay sahnesi: füze izi Dünya'dan Ay'a çizgi halinde ilerler (çizgi animasyonu), Ay beyaz patlar (parlama) → geçiş.
- Daire iris: sahnedeki Ay'dan daire büyür → Ay yüzeyi dokulu kart + 3 satır başlık (küçük beyaz / büyük kırmızı / orta beyaz); sonra yüzey 3B yatarak ufuk olur, üstüne kırmızı kart içinde nesne iner.
- Dağınık serif italik kelimeler koyu yıldızlı zeminde ("But / the / Strangest / Part?").
- Final: düşük açıdan kalabalık + arkada dev Ay, üstte turuncu ışıklı tabela kartı içinde 3 satır yazı.
- Başlıklarda derin gölge + hafif 3B kalınlık; tüm videoda toz zerresi + hafif gren, halftone belirgin değil.

### Ortak sonuçlar (7 video + önceki 3)
1. Altyazı üç ayrı biçimde: (a) hap / kutu altyazı sabit yerde (v4 kancadan sonra, v5 baştan), (b) hiç altyazı yok, yalnız başlık (v3, v6, v7), (c) hex: tek kelime / kısa öbek sahne içinde (v1 sabit nokta + sarı fosforlu kutu; v2 nesneye yapışık siyah etiket ya da duvara gömülü çok satır).
2. İşaretleme öğeleri her videoda var: fosforlu kalem süpürmesi (gazete / belge / anahtar kelime), isim altı çizgisi, elle çizilmiş elips, sarı / kırmızı etiket kutusu (isim, yıl, yer), açıklama etiketleri.
3. Boş "kart" sahneleri: düz renkli dokulu zemin (kareli, kağıt, yıldızlı, spot ışıklı) + yalnızca yazı; her videoda 2-4 kez, nefes ve vurgu için.
4. Geçiş çeşitliliği: gökyüzü / bulut köprüsü, sis beyazlatması, daire iris (bir nesneden açılır), beyaz perde yukarı, dikey itme, büyüteç, renk seli + aynı renkten daire, odak kaydırma, 1 karelik renk çakması.
5. Seçici renk (konu renkli, gerisi siyah-beyaz) ve tek nesnede renkli ışıma.
6. Sahne içi alt hareket: aynı görsel 2-4 farklı kadrajla, nesneler / kartlar / eller kadraja girip çıkar; "set" olarak kullanılan sabit mekân.
7. Belge / gazete: masaya düşer ya da sahneye uçar, kamera yaklaşır, üstü boyanır.
8. Sayı ve tarih: dev sarı / kırmızı yıl, karo sayılar, sayarak büyüyen yüzde.
9. Halka yapı: açılış sahnesi sonda geri döner (v1); leitmotif sahne 3 kez.
