# shotlist.json şeması ve sahne kataloğu

Tam, çalışan örnek: `examples/tahir-elci/shotlist.json` (görseller projeye özeldir; yapı için bak).
Yollar shotlist dosyasına göre görelidir; skill ile gelen ortak dosyalar `$SKILL/assets/...` diye yazılır.

```jsonc
{
  "title": "…", "style": "earn", "fps": 30, "size": [1080, 1920],
  "voiceover": "assets/vo.mp3",
  "music": {"file": "assets/music.mp3", "db": -19},
  "sfx": {"whoosh": "assets/sfx/whoosh.wav", "hit": "…", "pop": "…", "type": "…"},
  "fonts": {"title": "AmedBaslikAnton-Regular"},
  "look": { … },                       // references/marka.md'deki hazır blok
  "scenes": [ { …sahne… } ],
  "outro": {"duration": 3.3, "video": "$SKILL/assets/marka/outro_amed.mp4", "text": []}
}
```

## Nasıl kurulur (bilmen gereken model)
Her sahne kendi kompozisyonunda (`SC sXX`) kurulur ve ana kompozisyona tek bir **3B katman** olarak girer. Sahneler
uzayda istasyonlara dizilir; **geçiş = kameranın (`KAMERA`) bir istasyondan diğerine uçması**. Altyazılar, doku
katmanları ve kapanış ana kompozisyonda 2B'dir. Sahne başlıkları sahnenin içindedir (sahneyle birlikte hareket eder).

## Ortak sahne alanları

| Alan | Değer | Not |
|---|---|---|
| `id` | `s01`… | |
| `narration` | metin | bu sahnede okunan kelimeler; hepsi birleşince senaryo |
| `image` | yol | ana görsel (cutout'ta alfa kanallı konu) |
| `frame` | `full` · `cutout` · `polaroid` · `circle` · `split` · `scatter` | aşağıda |
| `transition` | aşağıdaki liste | sahneye **giriş**; ilk sahne `cut` |
| `title` | nesne | aşağıda |
| `keywords` | liste | altyazıda kırmızı vurgulanacak kelime kökleri |
| `caption` | `false` | bu sahnede altyazıyı kapat (yüz üstüne geliyorsa) |
| `fog` | 0–1 | sis yoğunluğu (`look.fog` kliplerinden) |
| `tag` | metin | altta küçük not: "Temsilî görsel", "Arka plan: …" |
| `dolly` | sayı | kamera yaklaşması: varsayılan 0.965; `0` kapatır (üstte başlık varsa kapat); 0.93 güçlü |
| `intro` | `tilt_down` | yalnızca ilk sahne: yakın plandan geri çekilerek açılış |
| `sfx` | `["hit"]` | ek ses efekti |
| `source` | metin | görselin kaynağı (yalnızca kayıt için) |

## Çerçeveler

**`full`** — tam ekran görsel. `move`: `push_in` · `pull_out` · `pan_left/right/up/down` · `parallax` · `static`.
Düşük çözünürlüklü haber fotoğrafını tam ekran kullanma; polaroid, kolaj ya da cutout yap.

**`cutout` (düz)** — arka plan (`bg`) + alfa kanallı figür (`image`, `cutout_prep.py` çıktısı). Figür alttan girer,
sahne boyunca hafif büyür. `title.behind: true` ile başlık figürün arkasında. Örnek: delil torbası, siluetler, portre.

**`cutout` + `"registered": true` (hizalı, katmanlı)** — kanalın imza sahnesi. Konu, arka plandaki yerinde durur;
`image` ve `bg` **aynı piksel boyutunda** (`layer_prep.py` çıktıları).
| Alan | Not |
|---|---|
| `outline` | yalnızca kontur halkası PNG; `outline_at` (sn) anında silinerek çizilir, `outline_angle` yön |
| `pop` | `{at, scale, lift}`: konu öne çıkar (varsayılan at 0.9, scale 1.06) |
| `anchor` | `[x, y]` 0–1: büyüme / sallanma merkezi (insan: `[0.5, 1.0]`; minare: tabanı) |
| `sway`, `sway_speed` | derece cinsinden sağa sola salınım; arka planda konunun kopyası `--inpaint` ile doldurulmalı |
Kullanımlar: açılışta kişi renkli / kalabalık siyah-beyaz; mekân (minare) renkli + başlık arkasında + sallanma.

**`polaroid`** — beyaz kart, `label` (alt yazı), `tilt`. `"board": true` + `bg` (koyu doku) → iğne + kırmızı ip, kart
alttan dönerek gelir. Art arda pano sahnelerini `whip_left` / `whip_up` ile bağla: ip boyunca kayma hissi verir.
Görsel kare olmalı ve konu ortada; kart kenarlardan ~%7 kırpar, baş üst kenara yapışmasın. Başlık `pos: 0.17`.

**`circle`** — daire maske + kesik çizgili dönen halka; `bg` verilmezse görselin bulanık kopyası.

**`split`** — `image` + `image2`, ortada parlayan eğik çizgi.

**`scatter`** — koyu dokulu zemin (`image`); anlatımın kelimeleri söylendikleri anda Playfair italikle dağınık belirir.
`slots` (`[[x, y], …]` 0–1), `word_size`. Altyazı kendiliğinden kapanır. Kapanış cümlesi için.

**Kolaj** — ayrı bir çerçeve değil: iki düşük çözünürlüklü gerçek kareyi PIL ile koyu zeminde eğik fotoğraf kartları
olarak birleştir, `full` ile kullan (örnek: "olay anı" sahnesi).

## Başlık (`title`)
| Alan | Değer |
|---|---|
| `text` | earn'de otomatik BÜYÜK HARF (Türkçe İ/I doğru); `keep_case` ile kapat |
| `anim` | `slam` (büyükten çarpar) · `stamp` (çerçeveli, eğik) · `words` (kelime kelime, bulanıktan net) · `pop` · `type` · `fade` |
| `color` | `yellow` · `red` · `white` · `orange` · `blue` · `cream` ya da `#hex` |
| `pos` | `top` (0.20) · `upper` (0.30) · `center` (0.45) · `lower` (0.60) · `bottom` (0.66) ya da 0–1 sayı |
| `behind` | cutout'ta başlığı konu ile arka plan arasına al |
| `sub`, `sub_font`, `sub_size` | alt satır (kelime kelime gelir; `sub_font: "serif"` = Playfair italik) |
| `delay`, `until`, `size`, `words_dur`, `rotate` | zamanlama / boyut |

Yerleşim kuralları: başlık 0.13'ün üstüne çıkmasın (kamera payı kırpar); `behind` başlıkta konu en fazla bir harfi
kapatsın ve Ç / Ş / İ / Ğ işaretlerini örtmesin; yüz üstüne başlık koyma (`lower` kullan).

## Geçişler
| Geçiş | Kamera |
|---|---|
| `whip_left` / `whip_right` | sonraki sahne yanda; kamera gidiş yönüne dönerek uçar |
| `whip_up` / `whip_down` | sonraki sahne altta / üstte; kamera eğilerek uçar |
| `zoom_through` | sonraki sahne derinde; kamera öncekinin içinden geçer |
| `orbit` | yan + derin, geniş dönüş |
| `spin` | çapraz + 32° yatış |
| `bw_flash` | aynı istasyon: siyah-beyaz parlama + radyal bulanıklık, kamera "yumruk" atar |
| `flash` · `fade` · `light_leak` · `cut` | aynı istasyon |

`blur_whip` ve `slide_up` = `whip_up`; `zoom_blur` = `zoom_through`. `iris` / `circle_reveal` 3B düzende yok.

## `look`
`backdrop` (zemin dokusu), `fog` (klip listesi), `overlays` (`file`, `blend`: screen / multiply / overlay / add /
soft_light, `opacity`), `transition_db` (geçiş sesi; kanal varsayılanı −16), `glow` (kullanma), `title_glow`.

## `outro`
`{"duration", "video", "text": []}` hazır kapanış klibi; ya da `{"duration", "image", "text": ["…", "…"]}` yazılı kart.

## Otomatik ses efektleri
Geçişte `whoosh`, slam / stamp başlıkta `hit`, polaroid / daire / cutout girişinde `pop`, `words` / `type` başlıkta `type`.

## hex stili alanları
Çalışan örnek: `examples/el-cezeri/shotlist.json`.
- Kök: `"style": "hex"`, `"caption_chunks": "phrase"` (2–4 kelimelik, en çok ~24 karakterlik öbekler),
  `"caption": {"mode": "phrase", "size": 74, "y": 0.5, "color": "white", "key_color": "gold"}`,
  `"grade": {…}` (stil gradını ezer), `"fonts": {"title": "PlayfairDisplay-Italic", "caption": "PlayfairDisplay-Italic"}`.
- Sahne: `caption_y` (0–1; yazıyı konunun üstündeki boş alana al: tablolar için 0.15–0.22),
  `caption_color` / `caption_key_color` (`#hex`; açık zeminli sahnede koyu yazı, gölgesiz).
- Başlık: `ribbon: true` (+ `ribbon_rgb`) isim şeridi.
- Geçiş: `wash` (sıcak beyaz ışık yıkaması; rengi `look.wash_rgb`). Kısa sahneye (< 1,5 sn) `wash` koyma: yıkama
  sahnenin yarısını yer, `fade` kullan.
- Ses efekti adları: `whoosh_soft`, `hit_soft`, `paper`, `typewriter`.
- Belge sayfası: sayfayı PIL ile krem kenarlık + gölge + 2° eğimle saydam 1296x2304 tuvale yerleştir, `cutout` ile koyu
  masa zemininin önüne koy; sayfayı tuvalin ortasının biraz altına al (`cy ≈ 0.56`) ki üstte altyazıya yer kalsın.

## İşaretler, etiketler ve yeni geçişler
Referans videoların hepsinde olan "işaretleme" öğeleri. Konumlar 0–1 arası kesirdir (`x`, `y` = merkez; `w`, `h` = boyut),
`at` = sahne başından saniye. Görsel hareket ediyorsa işaret kayar: işaretli sahnede `"move": "none"` kullan.

```json
"marks": [
  {"type": "highlight", "x": 0.5, "y": 0.42, "w": 0.5, "h": 0.035, "at": 0.5, "color": "#F2D21B"},
  {"type": "underline", "x": 0.5, "y": 0.80, "w": 0.4, "at": 0.9, "color": "#C0392B"},
  {"type": "ellipse",   "x": 0.5, "y": 0.50, "w": 0.7, "h": 0.09, "at": 0.5, "color": "yellow"}
],
"labels": [
  {"text": "Dan Cooper", "x": 0.62, "y": 0.44, "at": 0.6, "bg": "yellow", "color": "#111111", "anim": "type"},
  {"text": "Yağlı boya", "x": 0.2, "y": 0.3, "at": 1.2, "size": 38}
]
```
- `highlight`: fosforlu kalem, soldan sağa süpürür (gazete manşeti, belge satırı). Varsayılan karışım `multiply` (açık zemin
  için); koyu zeminde `"blend": "screen"` ya da `"normal"` + `opacity`. Ardışık satırlar için birkaç tane, `at` 0,4 sn arayla.
- `underline`: ismin / yılın altına ince çizgi. `ellipse`: elle çizilmiş gibi çizilen halka (ayrıntıyı işaretle); `rotate`, `stroke`.
- `labels`: `bg` verilirse renkli kutu içinde (isim, yıl, yer etiketi), verilmezse gölgeli düz yazı (açıklama etiketi).
  `anim`: `type` (harf harf) | `pop` | yok (belirme). `font_key`: `caption` | `title` | `serif`. `until` ile erken kapat.
- Başlıkta `"over": "..."`: büyük başlığın üstünde küçük beyaz satır (earn: üstte "ÜÇ POLİS", altta sarı "BERAAT").
- Geçiş `iris`: renk kadrajı kaplar, sonra bir noktadan daire açılır. `transition_color` (ad ya da `#hex`), `iris_at: [x, y]`
  (dairenin açıldığı nokta; sahnedeki Ay, yüz, belge mührü gibi bir nesnenin üstü). Doruk anı ve belgeye geçiş için.
- Geçiş `wipe_up`: düz renkli perde alttan yükselip yukarı çıkar (`transition_color`, varsayılan beyaz). hex'te krem / beyaz.
- Yalnız başlıklı earn videosu (akan altyazı yok): kökte `"caption": {"mode": "none"}`; her sahneye 2 satır başlık (`over` + `text`).
- Yazı kartı sahnesi: `scripts/make_card.py` ile zemin üret (düz renk + gren; `--grid`, `--dust`, `--spot x,y`), sahnede
  `"move": "none"`, `"caption": false` + başlık, ya da `frame: "scatter"`. Her videoda 2–4 kart: yıl, soru, doruk cümlesi, kapanış.

Henüz olmayanlar (referanslarda var; istenirse elle ya da ileride): gökyüzü / bulut köprüsü geçişi, büyüteç geçişi, renk seli
(sahnenin tek renge boyanması), seçici renk için hazır alan (şimdilik `registered` kesimle yapılıyor), sayarak büyüyen sayı /
karo sayı, sahneye uçan 3B kıvrık gazete, anahtar kelimenin arkasında fosforlu kutu (altyazı içinde), nesneye yapışık altyazı.
