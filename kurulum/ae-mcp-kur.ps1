# after-effects-mcp kurulumu (Windows)
# Çalıştır (reel-skill klasöründe, normal PowerShell):
#   powershell -ExecutionPolicy Bypass -File kurulum\ae-mcp-kur.ps1
# Ne yapar: Git/Node kontrolü -> after-effects-mcp'yi %USERPROFILE%\after-effects-mcp'ye klonlar/günceller ->
# npm install + build -> köprü panelini After Effects'e kopyalar (yönetici izni ister) -> Claude Code'a MCP olarak ekler.
$ErrorActionPreference = "Stop"
$Repo  = "https://github.com/Dakkshin/after-effects-mcp.git"
$Hedef = Join-Path $env:USERPROFILE "after-effects-mcp"

function Ok($m)   { Write-Host "  [OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "  [X]  $m" -ForegroundColor Red; exit 1 }
function Need($cmd, $hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { Fail "$cmd bulunamadı. Kur: $hint  (sonra yeni bir PowerShell aç)" }
  Ok "$cmd bulundu"
}

Write-Host "`n1) Gereksinimler" -ForegroundColor Cyan
Need git  "winget install Git.Git"
Need node "winget install OpenJS.NodeJS.LTS"
Need npm  "Node.js ile birlikte gelir"
$nodeMajor = [int]((node -v).TrimStart("v").Split(".")[0])
if ($nodeMajor -lt 18) { Fail "Node.js 18+ gerekli (şu an $(node -v)). winget upgrade OpenJS.NodeJS.LTS" }

Write-Host "`n2) after-effects-mcp indir / güncelle" -ForegroundColor Cyan
if (Test-Path (Join-Path $Hedef ".git")) { git -C $Hedef pull --ff-only; Ok "güncellendi: $Hedef" }
else { git clone $Repo $Hedef; Ok "klonlandı: $Hedef" }

Write-Host "`n3) Bağımlılıklar + derleme" -ForegroundColor Cyan
Push-Location $Hedef
try {
  npm install
  if (-not (Test-Path "build\index.js")) { npm run build }
  if (-not (Test-Path "build\index.js")) { Fail "build\index.js oluşmadı; yukarıdaki npm çıktısına bak" }
  Ok "derlendi: $Hedef\build\index.js"
} finally { Pop-Location }

Write-Host "`n4) Köprü panelini After Effects'e kur" -ForegroundColor Cyan
$aeDirs = Get-ChildItem "C:\Program Files\Adobe" -Directory -Filter "Adobe After Effects*" -ErrorAction SilentlyContinue |
          Where-Object { Test-Path (Join-Path $_.FullName "Support Files\AfterFX.exe") } |
          Sort-Object Name -Descending
if (-not $aeDirs) {
  Warn "After Effects bulunamadı (kurulum bitmemiş olabilir). AE kurulunca bu scripti tekrar çalıştır."
} else {
  $ae  = $aeDirs[0].FullName
  $src = Join-Path $Hedef "build\scripts\mcp-bridge-auto.jsx"
  $dst = Join-Path $ae "Support Files\Scripts\ScriptUI Panels"
  Write-Host "  AE: $ae"
  Write-Host "  Yönetici izni penceresi açılacak (Program Files'a kopyalamak için)..."
  $cmd = "New-Item -ItemType Directory -Force -Path '$dst' | Out-Null; Copy-Item -Path '$src' -Destination '$dst' -Force"
  Start-Process powershell -Verb RunAs -Wait -ArgumentList "-NoProfile", "-Command", $cmd
  if (Test-Path (Join-Path $dst "mcp-bridge-auto.jsx")) { Ok "panel kuruldu: $dst\mcp-bridge-auto.jsx" }
  else { Warn "panel kopyalanamadı. Elle kopyala:`n       $src`n    -> $dst" }

  # reel-skill için AE yollarını kaydet
  $cfg = @{ afterfx = (Join-Path $ae "Support Files\AfterFX.exe"); aerender = (Join-Path $ae "Support Files\aerender.exe") } | ConvertTo-Json
  $cfgPath = Join-Path $PSScriptRoot "..\ae-yollari.json"
  Set-Content -Path $cfgPath -Value $cfg -Encoding UTF8
  Ok "AE yolları kaydedildi: $(Resolve-Path $cfgPath)"
}

Write-Host "`n5) Claude Code'a MCP olarak ekle" -ForegroundColor Cyan
$idx = Join-Path $Hedef "build\index.js"
if (Get-Command claude -ErrorAction SilentlyContinue) {
  try { claude mcp remove AfterEffectsMCP --scope user *> $null } catch {}
  claude mcp add --scope user AfterEffectsMCP -- node "$idx"
  Ok "eklendi (tüm projelerde geçerli). Kontrol: claude mcp list"
} else {
  Warn "claude komutu bulunamadı. Claude Code'u kurduktan sonra şunu çalıştır:"
  Write-Host "    claude mcp add --scope user AfterEffectsMCP -- node `"$idx`""
}

Write-Host "`nSon adımlar (After Effects içinde):" -ForegroundColor Cyan
Write-Host "  a) Edit > Preferences > Scripting & Expressions > 'Allow Scripts to Write Files and Access Network' işaretle"
Write-Host "  b) After Effects'i yeniden başlat"
Write-Host "  c) Window > mcp-bridge-auto.jsx panelini aç, 'Auto-run commands' işaretli olsun"
Write-Host "  d) Claude Code'da: 'After Effects MCP bağlantısını test et' de (get-help / getProjectInfo)`n"
