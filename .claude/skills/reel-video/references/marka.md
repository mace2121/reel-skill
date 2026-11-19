# Amed Güncel: kanal varsayılanları

Kanal: **Amed Güncel** (@amedguncel, "Diyarbakır'ın sesi ve hafızası"). Sormadan uygula; kullanıcı aksini derse onu yap.

| Öğe | Varsayılan | shotlist'te |
|---|---|---|
| Başlık fontu | Amed başlık fontu, PostScript adı `AmedBaslikAnton-Regular` (`assets/fonts/`; `~/Library/Fonts`'ta kurulu olmalı) | `"fonts": {"title": "AmedBaslikAnton-Regular"}` |
| Altyazı fontu | Poppins SemiBold; dağınık kelime / alt satır için Playfair Display Italic | stil varsayılanı |
| Kapanış | "Takip et" kartı **yok**; kanal animasyonu (logo + @amedguncel + "Takip Ediliyor"), 3,3 sn | `"outro": {"duration": 3.3, "video": "$SKILL/assets/marka/outro_amed.mp4", "text": []}` |
| Genel doku | Halftone tüm videonun üstünde (multiply %85) + toz + çizik + gren | `look.overlays` (aşağıda) |
| Sis | Tam ekran ve katmanlı sahnelerde alt kenarda | `look.fog`, sahnede `"fog": 0.5–0.9` |
| Geçiş sesi | Varsayılan yüksek bulundu, yarıya indirildi | `look.transition_db: -16` |
| Parlama (glow) | Kapalı (renkleri patlatıyor) | `look.glow` yazma |
| Zemin | Sahneler arası boşlukta koyu doku | `look.backdrop` |

Hazır `look` bloğu:
```json
"look": {
  "backdrop": "$SKILL/assets/doku/board_bg.jpg",
  "transition_db": -16,
  "fog": ["$SKILL/assets/doku/fog_low.mp4", "$SKILL/assets/doku/smoke_amb.mp4"],
  "overlays": [
    {"name": "halftone",  "file": "$SKILL/assets/doku/halftone.jpg",  "blend": "multiply", "opacity": 85},
    {"name": "dust",      "file": "$SKILL/assets/doku/dust.mp4",      "blend": "screen",   "opacity": 65},
    {"name": "scratches", "file": "$SKILL/assets/doku/scratches.mp4", "blend": "screen",   "opacity": 35},
    {"name": "grain",     "file": "$SKILL/assets/doku/grain.mp4",     "blend": "overlay",  "opacity": 35}
  ]
}
```

## Kullanıcının tekrar tekrar istedikleri
- **Gerçek görüntü:** olay yeri, kişi, mekân internette varsa onu kullan; kendi bulduğu fotoğrafı gönderirse o sahneye koy.
- **Katmanlı sahne:** arka plan siyah-beyaz + halftone, konu kesilip renkli ve konturlu öne çıkar; başlık arka plan ile
  konunun arasında; konu hafif sallanabilir. Tersi de istenir: konu siyah-beyaz ve konturlu önde, arka plan renkli.
- **Ortalama:** konu çerçevenin ortasında ve tam görünür (polaroidde baş kesilmez).
- **Hareket:** 3B kamera geçişleri, hareket bulanıklığı; durağan kare kalmasın.
- **Dil:** Kürt siyasetiyle ilgili konularda örgüt / taraf kötülenmez, çatışma tarafsız dille anlatılır; fail belirsizse
  kimse fail gösterilmez.
- Düzeltmeleri saniyeyle tarif eder ("00:12'deki portre") ve hızlı, parça parça gönderir.

## Efekt paketleri (kullanıcının, `~/Downloads` altında)
`assets/doku/` bu paketlerden hazırlandı; yeni doku gerekirse `scripts/prep_overlays.sh` ile çevir.
- `vhs-retro-vintage-and-scratch-grain-texture-backg-…/(Footage)/03.Others/Texture/` — kağıt, gren, VHS, hasar dokuları
- `Grunge Halftone Overlay Textures/(Footage)/03.Others/` — halftone klipleri, toz, çizik
- `Atmospheric Fog Transitions …/…/FOG/` ve `Cinematic Fog Overlays/(Footage)/Footages/` — zemin sisi, ortam dumanı
- Kanal kapanışı `AmedGuncel_AhmetKaya_BirSesinHikayesi_9x16.mp4` videosunun 53,28. saniyesinden kesildi.
