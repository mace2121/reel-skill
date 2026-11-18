# Kurulum ve ortam kontrolü

Bu skill, **After Effects'in kurulu olduğu bilgisayarda** çalışan Claude Code içinde uçtan uca çalışır
(after-effects-mcp yerel bir köprüdür; bulut oturumundan AE'ye ulaşılamaz). Bulut oturumunda yalnızca
senaryo, shotlist, görsel/ses üretimi ve ffmpeg önizlemesi yapılabilir.

## 1. Bu repo
```bash
git clone https://github.com/mace2121/reel-skill.git
cd reel-skill
bash install.sh        # skill'i ~/.claude/skills/reel-video olarak bağlar (Windows'ta Git Bash)
```
Repo klasöründe Claude Code açarsan skill `.claude/skills/` altından zaten yüklenir.

## 2. Temel araçlar
- Python 3.10+ ve `pip install pillow`
- ffmpeg (PATH'te): Windows `winget install Gyan.FFmpeg`, macOS `brew install ffmpeg`
- (isteğe bağlı) `pip install faster-whisper` — yerel Türkçe kelime zamanları
- (isteğe bağlı) [rea-video](https://github.com/JuneYaooo/rea-video) — kalite kontrolü ve yeni referans analizi

## 3. After Effects + after-effects-mcp
After Effects 2023 veya sonrası (H.264 render için). Sonra:
```bash
git clone https://github.com/Dakkshin/after-effects-mcp.git
cd after-effects-mcp
npm install
npm run build
npm run install-bridge
```
AE → Settings → Scripting & Expressions → **Allow Scripts to Write Files and Access Network** ✔.
AE → **Window → mcp-bridge-auto.jsx** paneli açık, "Auto-run commands" ✔.

Claude Code'a ekle (yolu kendi klasörünle değiştir):
```bash
claude mcp add AfterEffectsMCP -- node "C:\\Users\\<sen>\\after-effects-mcp\\build\\index.js"
```

## 4. Üretim bağlayıcıları
claude.ai → Settings → Connectors: **Magnific**, **Higgsfield**, **ElevenLabs** bağlı olmalı (Claude Code aynı
hesapla giriş yaptıysa bağlayıcılar gelir). Hangisinin bağlı olduğunu `/mcp` ile gör.

## 5. HyperFrames (isteğe bağlı)
Sayaç, harita, grafik gibi kodla daha iyi olan sahneler için — `hyperframes.md`.
```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

## Kontrol listesi (skill her çalışmada)
```bash
python3 -c "import PIL; print('pillow ok')"
ffmpeg -version | head -1
```
- AE: AfterFX.exe ve aerender.exe yolu var mı (Windows: `C:\Program Files\Adobe\Adobe After Effects 20XX\Support Files\`)
- MCP: `get-help` aracı yanıt veriyor mu; `run-script` → `getProjectInfo` sonucu `get-results` ile geliyor mu
- Bağlayıcılar: Magnific / Higgsfield / ElevenLabs araçları listede mi
