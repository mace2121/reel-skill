# reel-skill

- Kullanıcı bir konuyu videoya çevirmek istediğinde `.claude/skills/reel-video/SKILL.md`'yi oku ve akışı izle.
- Video dili Türkçe; yanıtlar Türkçe.
- Her video `projeler/<kısa-ad>/` altında üretilir; `projeler/` git'e girmez.
- Ücretli üretim (görsel, video, ses, müzik) öncesi kullanıcıdan onay al.
- Script değişikliğinden sonra örnekle test et:
  `python3 .claude/skills/reel-video/scripts/timeline.py .claude/skills/reel-video/examples/lale/shotlist.json -o /tmp/tl.json`
  (örnek varlıklar repoda yok; timeline için `--audio` ile herhangi bir ses dosyası ver).
