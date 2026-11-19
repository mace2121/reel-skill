# Kurulum ve ortam kontrolü

Skill, After Effects'in kurulu olduğu bilgisayarda çalışır (bu Mac: After Effects 2027).

## Kontrol listesi (her çalışmada)
```bash
ls -d /Applications/Adobe\ After\ Effects*            # AE + aerender
ffmpeg -version | head -1
ls ~/Library/Fonts | grep -iE "AmedBaslik|Poppins-SemiBold|Playfair"
```
- Bağlayıcılar: Magnific (görsel, maske, müzik, efekt) ve ElevenLabs (seslendirme) araçları listede mi; bakiyelere bak
  (`magnific_start`, `account_get_usage`).
- AE'de Settings → Scripting & Expressions → **Allow Scripts to Write Files and Access Network** açık olmalı.

## Python ortamı
Sistem Python'unda Pillow yok. Proje klasörünün yanında bir ortam kur (`ae_build.sh` `<proje>/../.venv`'i kendisi bulur):
```bash
python3 -m venv projeler/.venv
projeler/.venv/bin/pip install pillow opencv-python-headless faster-whisper
```
`faster-whisper` ilk kullanımda ~480 MB model indirir.

## Bu makinenin tuhaflıkları
- Homebrew ffmpeg'de **libass ve drawtext yok**: ffmpeg ile altyazı / yazı basılamaz; etiketli föyler PIL ile yapılır
  (`frame_sheets.py`), önizleme altyazısız çıkar.
- `git` bozuk (xcrun hatası): repo indirmek için `curl -sSL https://codeload.github.com/<kullanıcı>/<repo>/tar.gz/HEAD`.
- Oturumun geçici (scratchpad) klasörü oturum sırasında silinebiliyor: kalıcı dosyaları oraya koyma.
- Dosya yolunda boşluk olan klasörler (`Application Support`) ffmpeg filtre argümanlarını bozar.

## Doku ve sis dosyaları
`assets/doku/` lisanslı efekt paketlerinden hazırlandığı için repoda yok. Repodan yeni kurulumda `assets/doku/README.md`
içindeki komutlarla üret; dosyalar eksikse AE log'unda `EKSİK DOSYA` görürsün (video dokusuz ve sissiz çıkar).

## Kaynak
Repo: `github.com/mace2121/reel-skill` (skill `.claude/skills/reel-video/` altında). Kurulum: repoyu indir,
`bash install.sh`. Yerelde bir betiği ya da belgeyi değiştirirsen repoya da gönder; yoksa yeniden kurulum ezer.

## İsteğe bağlı
- [rea-video](https://github.com/JuneYaooo/rea-video): referans videoları sahnelere ayırmak için (kurulu değil).
- Windows'ta after-effects-mcp kurulumu: repodaki `kurulum/ae-mcp-kur.ps1`.
