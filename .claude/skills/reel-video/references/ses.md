# Ses: seslendirme, kelime zamanları, müzik, efektler

## 1. Türkçe seslendirme (ElevenLabs)
1. `creative_list_voices` → Türkçe konuşabilen (çok dilli model) **derin, sakin, anlatıcı** erkek ya da kadın
   ses seç. Kullanıcının kayıtlı / klonlanmış sesi varsa onu kullan. Seçtiğin sesi ve nedenini söyle.
2. `creative_generate_speech`: metin = `script.md` (tamamı, tek parça); model çok dilli (multilingual v2 /
   v3 hangisi şemada varsa); dil Türkçe. Varsayılan iki take gelir; ikisini de dinle (ffmpeg ile süre + istersen
   transkript), daha net ve doğal olanı seç.
3. `creative_get_flow_run_status` ile bitmesini bekle, sonucu indir → `assets/vo.mp3`.
4. Kontrol: özel isim, rakam, vurgu yanlışsa senaryoda yazımı düzelt (ör. "Harlem"), sadece o cümleyi değil
   tamamını yeniden üret (ton tutarlılığı). Tempo hızlıysa noktalama ekle, yavaşsa kısalt.

Hedef: earn 2.4–2.6 kelime/sn, enerjik; hex 2.2–2.4 kelime/sn, ağır ve ciddi.

## 2. Kelime zamanları → `assets/words.json`
Öncelik sırası:
1. ElevenLabs "with-timestamps" çıktısı geldiyse (alignment / characters) olduğu gibi kaydet.
2. `creative_transcribe_audio` (connect_from = vo dosyasının node'u) → kelime + başlangıç/bitiş içeren JSON.
3. Yerelde: `pip install faster-whisper` →
   ```python
   from faster_whisper import WhisperModel
   m = WhisperModel("medium", compute_type="int8")
   segs, _ = m.transcribe("assets/vo.mp3", language="tr", word_timestamps=True)
   import json; json.dump([{"word": w.word, "start": w.start, "end": w.end} for s in segs for w in s.words],
                          open("assets/words.json", "w"), ensure_ascii=False)
   ```
4. Hiçbiri yoksa `--words` vermeden çalıştır: timeline.py harf sayısına göre tahmin eder.
`timeline.py` transkript ile senaryoyu kendisi hizalar; transkriptte küçük hatalar sorun değil.

## 3. Müzik → `assets/music.mp3`
- Magnific `audio_music_generate` ya da ElevenLabs müzik (şemada varsa). Enstrümantal, vokalsiz, video
  süresi + 5 sn.
- earn: "dark cinematic documentary underscore, tense pulsing synth and low strings, steady 90–110 BPM,
  builds slightly, no vocals"; motivasyon / duygusal konuda "emotional piano and strings".
- hex: "slow orchestral historical documentary underscore, solo cello and piano, 70–85 BPM, melancholic,
  vintage, no vocals".
- Seviye shotlist'te `music.db` (earn −19, hex −17); anlatım her zaman net duyulmalı.
- Telifli şarkı kullanma.

## 4. Ses efektleri → `assets/sfx/`
Magnific `audio_sfx_generate` (ya da ElevenLabs ses efekti). Her biri 0.3–1.2 sn, kısa kuyruk:

| Ad | earn prompt | hex karşılığı |
|---|---|---|
| `whoosh` / `whoosh_soft` | fast cinematic whoosh transition | soft airy whoosh, film reel |
| `hit` / `hit_soft` | deep cinematic impact boom with short tail | soft low piano hit / timpani |
| `pop` / `paper` | short snappy pop / photo snap | paper rustle, photo placed on table |
| `type` / `typewriter` | quick digital text tick | old typewriter keystrokes |

Bir kez üret, `projeler/_ortak/sfx/` altında sakla ve sonraki videolarda tekrar kullan (maliyet düşer).
