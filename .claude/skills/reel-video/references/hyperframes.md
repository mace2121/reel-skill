# HyperFrames ile özel sahneler

[HyperFrames](https://github.com/heygen-com/hyperframes): HTML/CSS animasyonunu MP4'e render eden açık kaynak
çatı (Node.js 22+). Bu skill'de **tek tek sahneler** için kullanılır; çıkan klip shotlist'te `"video"` olarak
sahneye konur ve AE onu diğer sahneler gibi yerleştirir.

## Ne zaman
AE betiğinin basit kaldığı, kodla daha iyi olan sahneler:
- **Sayaç**: "$0 → $381 MİLYAR" hızla sayan rakam (Buffett videosundaki gibi)
- **Grafik / çizgi**: piyasa düşüşü, nüfus artışı, %90 çöküş eğrisi
- **Harita**: rota çizgisi (uçağın rotası, Hollanda → Osmanlı), pin düşmesi
- **Zaman çizelgesi**: yıllar arasında kayan şerit
- **Kinetik tipografi bloğu**: "The fear of what waits in the darkness" gibi dağınık kelimelerin tek tek belirmesi

## Nasıl
1. Sahnenin süresini timeline.json'dan al (`end - start`, +0.3 sn pay).
2. HyperFrames skill'iyle 1080x1920, 30 fps, o süre kadar bir kompozisyon yaz:
   - Stil renkleri: earn → arka plan siyah grunge / koyu yeşil grid, yazı Anton sarı `#FFD21F` / kırmızı
     `#E53935`, beyaz; hex → krem `#F3E6C4` / altın `#E8C46A`, Playfair Display Italic, sepya doku.
   - Animasyon anahtar zamanlarını anlatımdaki kelime zamanlarına bağla (timeline.json → `words`, o sahnenin
     kelimeleri `scene` alanıyla bulunur; sahne başına göre çıkar).
3. Render → `assets/vid/sXX.mp4`; shotlist'te o sahneye `"video": "assets/vid/sXX.mp4"`, `"move": "static"`.
4. timeline + build_ae_jsx'i yeniden çalıştır.

AE yoksa, tüm videoyu HyperFrames ile yazmak da mümkündür (timeline.json'daki sahneler, kelimeler ve geçişler
spesifikasyon olarak verilir); ama varsayılan teslim yolu AE'dir.
