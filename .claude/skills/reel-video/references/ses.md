# Ses: seslendirme, kelime zamanları, müzik, efektler

## 1. Seslendirme (ElevenLabs)
- Ses: **Ogün Can – Turkish Documentary Narrator** (`creative_list_voices` ile `languages: ["tr"]` arayıp kimliğini al;
  kimliği ezberden yazma). Model `eleven_v4`. Metin = `script.md`'nin tamamı, tek parça.
- Varsayılan iki deneme gelir (≈ metin uzunluğu × 2 karakter). Kota dar (Starter): üçüncü deneme sığmayabilir.
  Yedek: Magnific `audio_tts`.
- `creative_get_flow_run_status` ile bitmesini bekle, `content_url`'den indir.
- Bu anlatıcı ≈ **2,15 kelime/sn** okuyor (67 kelime = 31 sn). Hedef süreye oturtmak için hızlandır (perde değişmez),
  en fazla ~%15:
  ```bash
  ffmpeg -i vo_a.mp3 -af "atempo=1.135,loudnorm=I=-19:TP=-3:LRA=11" -ar 44100 -b:a 192k assets/vo.mp3
  ```
  Daha fazlası gerekiyorsa senaryoyu kısalt. Seslendirmeyi −19 LUFS'ta bırak; tepe payı efektlere kalsın.
- Sesi dinleyemezsin: dökümü metinle karşılaştır (aşağıda) ve telaffuz / ton kontrolünü kullanıcıya bırak.

## 2. Kelime zamanları
```bash
python3 $S/words.py assets/vo.mp3 -o assets/words.json --prompt "özel isimler, terimler"
```
Yerel ve ücretsiz. Çıktıdaki döküm senaryoyla aynı mı bak (yanlış okunan kelime burada görünür). Whisper rakamları
rakamla yazar ("28 Kasım 2015"): altyazıda da öyle görünsün istiyorsan shotlist'teki `narration`'ı rakama çevir.
`timeline.py` dökümü senaryoyla kendisi hizalar.

## 3. Müzik
Magnific `audio_music_generate` (`elevenlabs-music-generation-v2`, `instrumental: true`, video süresi + 5 sn; 35 sn ≈
700 kredi). earn: "dark cinematic documentary underscore, tense pulsing low synth and somber low strings, ~95 BPM,
restrained, no vocals". Düzey shotlist'te `music.db` (−19). Kapanış klibinin altında da bu müzik devam eder.

## 4. Efektler
Magnific `audio_sfx_generate`, her biri 1 sn (5 kredi): `whoosh` (fast cinematic whoosh), `hit` (deep impact boom),
`pop` (short snappy pop), `type` (quick text ticks). mp3 gelir; `ffmpeg -i x.mp3 x.wav` ile çevir. Bir kez üretip
`projeler/_ortak/sfx/` altında sakla.

## 5. Düzeyler
- Geçiş (whoosh) sesi: `look.transition_db: -16` (kullanıcı varsayılan −10'u yüksek buldu).
- AE çıktısında toplam tepe 0 dB'ye vurur: `ae_build.sh --render` sonunda `loudnorm=I=-14:TP=-1.0` uygular.
