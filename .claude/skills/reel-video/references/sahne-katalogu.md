# shotlist.json şeması ve sahne kataloğu

Tam örnek: `examples/lale/shotlist.json`. Yollar shotlist dosyasına göre görelidir.

```jsonc
{
  "title": "Lale Çılgınlığı",
  "style": "earn",                 // earn | hex
  "fps": 30, "size": [1080, 1920],
  "voiceover": "assets/vo.mp3",
  "music": {"file": "assets/music.mp3", "db": -19},
  "sfx": {"whoosh": "assets/sfx/whoosh.wav", "hit": "...", "pop": "...", "type": "..."},
  "fonts": {"title": "Anton-Regular"},   // isteğe bağlı: stilin fontlarını ez (PostScript adı)
  "scenes": [ { ...sahne... } ],
  "outro": {"duration": 3.0, "image": "assets/img/outro.png", "text": ["Takip et", "Her gün bir tarih sırrı"]}
}
```

## Sahne alanları

| Alan | Değerler | Not |
|---|---|---|
| `id` | `s01`… | dosya adlarıyla aynı tut |
| `narration` | metin | bu sahnede okunan kelimeler; tüm sahneler birleşince senaryo |
| `image` | yol | 9:16 görsel (zorunlu, `video` yoksa) |
| `video` | yol | isteğe bağlı kısa klip; sahneden uzun olmalı |
| `prompt` | metin | görsel üretim prompt'u (yeniden üretim için sakla) |
| `frame` | `full` · `circle` · `polaroid` · `split` | `split` için `image2` gerekir; `circle`/`polaroid` için isteğe bağlı `bg` (yoksa görselin bulanık kopyası) |
| `label` | metin | polaroid altındaki yazı |
| `tilt` | derece | polaroid eğimi (varsayılan −4) |
| `move` | `push_in` · `pull_out` · `pan_left` · `pan_right` · `pan_up` · `pan_down` · `parallax` · `static` | varsayılan: earn push_in, hex parallax |
| `transition` | `cut` · `blur_whip` · `zoom_blur` · `flash` · `fade` · `light_leak` · `circle_reveal` · `slide_up` | sahneye **giriş** geçişi; ilk sahne her zaman cut |
| `title` | `{text, anim, color, pos, size, delay, until, rotate, keep_case}` | `anim`: `slam` · `stamp` · `pop` · `type` · `fade`; `pos`: `top` · `upper` · `center` · `lower` · `bottom`; renk: `yellow` · `red` · `white` · `orange` · `blue` · `cream` · `gold` ya da `#hex`; earn'de otomatik BÜYÜK HARF (Türkçe İ/I doğru) |
| `keywords` | liste | altyazıda vurgulanacak kelime kökleri ("çök" → "çöktü") |
| `sfx` | `["hit"]` ya da `[{"name": "pop", "at": 0.4}]` | otomatik efektlere ek |

Otomatik efektler: geçişte `whoosh` (hex: `whoosh_soft`), slam/stamp başlıkta `hit`, polaroid/daire girişinde
`pop` (hex: `paper`), type başlıkta `type` (hex: `typewriter`).

## Tempo kuralları
- Sahne 1.5–4 sn (timeline 6 sn üstünü uyarır). Kanca sahnesi 1.5–2.5 sn.
- Aynı geçiş arka arkaya en fazla 3 kez; her 4–5 sahnede bir farklı tür.
- Aynı `move` arka arkaya 2'den fazla olmasın (push_in → pan_left → pull_out …).
- earn: 11–16 sahnede ≥3 başlık, ≥2 polaroid/daire, ≥1 split ya da stamp. Başlık metni anlatımı tekrar etmez,
  **özetler** ("Kimse almadı", "%90", "1637"). Başlık ile o anki altyazı aynı kelimeyse başlığı kaldır.
- hex: başlık yalnızca isim / yıl ("Samuel Walker", "1846"), `pos: upper` ya da `lower`; altyazı ortada kalır.
- Kapanış sahnesi en az 3 sn, hareket yavaş (push_in), geçiş `fade` ya da `light_leak`.

## Sahne tipleri (prompt + alan kalıpları)

| Tip | Alanlar | Prompt fikri |
|---|---|---|
| Kanca görseli | full, push_in, title slam | tek güçlü nesne / sahne, dramatik ışık |
| Yıl / yer kartı | polaroid + label, title stamp "1637" | dönem şehri / mekânı |
| Kanıt objesi | polaroid ya da full, pan | gazete kupürü, belge, mühür, harita masa üstünde (top-down, ahşap / kesme matı) |
| Kişi | full parallax ya da circle | portre / cut-out figür |
| Karşılaştırma | split | iki karşıt görsel (önce/sonra, Doğu/Batı, yaşayan/ölü) |
| Rakam vurgusu | full + title stamp büyük | rakamla ilişkili sahne (çöküş, kalabalık, para) |
| Duygusal kapanış | full, slow push, light_leak | minimal, karanlık, tek nesne |
