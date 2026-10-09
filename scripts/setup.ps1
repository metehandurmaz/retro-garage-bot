# Run once on the Windows server from the project folder:
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python not found. Install Python 3.12+ from https://www.python.org/downloads/ and tick 'Add python.exe to PATH'."
}

if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

$ffmpeg = Join-Path $root "tools\ffmpeg\bin\ffmpeg.exe"
if (-not (Test-Path $ffmpeg)) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $zip = Join-Path $env:TEMP "ffmpeg-release-essentials.zip"
    Invoke-WebRequest "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $zip
    $extract = Join-Path $env:TEMP "ffmpeg-extract"
    if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
    Expand-Archive $zip -DestinationPath $extract
    $inner = Get-ChildItem $extract -Directory | Select-Object -First 1
    New-Item -ItemType Directory -Force -Path (Join-Path $root "tools") | Out-Null
    Move-Item $inner.FullName (Join-Path $root "tools\ffmpeg")
}

if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
New-Item -ItemType Directory -Force -Path "secrets", "music" | Out-Null

Write-Host "Setup done. Fill .env, put client_secret.json in secrets\ and bed.mp3 in music\."
