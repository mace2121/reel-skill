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
