# assets/doku: doku ve sis dosyaları

Bu klasördeki klipler ve görseller **lisanslı efekt paketlerinden** hazırlandığı için herkese açık repoda yer almaz;
repodan kurulumda klasör boş gelir. Skill bu adları bekler:

| Dosya | Ne | Nasıl üretilir |
|---|---|---|
| `halftone.jpg` | tüm videonun üstündeki nokta dokusu (1080x1920, açık zemin + koyu noktalar) | dikey bir halftone dokusunu 1080x1920'ye kırp |
| `fog_low.mp4` | alt kenarda zemin sisi | `prep_overlays.sh "<Atmospheric Fog …>/FOG/01.mov" fog_low.mp4 zemin-sisi` |
| `smoke_amb.mp4` | ortam dumanı | `prep_overlays.sh "<Cinematic Fog Overlays>/Footages/Smoke Overlays 09.mp4" smoke_amb.mp4 doldur` |
| `dust.mp4` | toz | `prep_overlays.sh "<Grunge Halftone …>/03.Others/Dust.mp4" dust.mp4 döndür` |
| `scratches.mp4` | çizik | `prep_overlays.sh "<Grunge Halftone …>/03.Others/Scratches.mp4" scratches.mp4 döndür` |
| `grain.mp4` | gren | `prep_overlays.sh "<vhs-retro …>/Texture/Grain 16.mp4" grain.mp4 döndür` |
| `board_bg.jpg` | pano / zemin dokusu (1620x2880) | `<vhs-retro …>/Texture/Damage Texture.jpg` dikeye çevrilip kırpılır |
| `dark_grunge.jpg` | dağınık kelime sahnesinin zemini | `<vhs-retro …>/Texture/2.jpg` |
| `paper_dark.jpg` | koyu katlanmış kağıt | `<vhs-retro …>/Texture/Crmpped  Paper 2.jpg` |

Paketler kullanıcının `~/Downloads` klasöründe (adları `references/marka.md` içinde). Elinde paket yoksa aynı işi gören
herhangi bir serbest lisanslı doku / sis klibi kullanılabilir; dosya adlarını koruman yeterli.
