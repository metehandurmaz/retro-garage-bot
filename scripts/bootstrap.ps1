# One-time switch of an existing server install to self-updating mode. Paste into an admin PowerShell:
#   [Net.ServicePointManager]::SecurityProtocol='Tls12'; iex (irm https://raw.githubusercontent.com/metehandurmaz/retro-garage-bot/main/scripts/bootstrap.ps1)
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$repo = "metehandurmaz/retro-garage-bot"
$root = "C:\retro-garage-bot"
if (-not (Test-Path "$root\.env")) { throw "$root\.env bulunamadi" }

Write-Host "`n--- Eski bot.log (son 25 satir) ---" -ForegroundColor Cyan
Get-Content "$root\logs\bot.log" -Tail 25 -ErrorAction SilentlyContinue

New-Item -ItemType Directory "$root\scripts" -Force | Out-Null
Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/$repo/main/scripts/update.ps1" -OutFile "$root\scripts\update.ps1"
& "$root\scripts\update.ps1"
& "$root\.venv\Scripts\python.exe" -m pip install -q -r "$root\requirements.txt"
& "$root\scripts\install_task.ps1"

Write-Host "`nBot simdi bir video hazirlayip yukluyor (2-5 dakika)..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName "RetroGarageBot"
Start-Sleep -Seconds 10
$deadline = (Get-Date).AddMinutes(15)
while ((Get-ScheduledTask -TaskName "RetroGarageBot").State -eq "Running" -and (Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 10
}
Write-Host "`n--- Yeni bot.log (son 15 satir) ---" -ForegroundColor Cyan
Get-Content "$root\logs\bot.log" -Tail 15
Write-Host "`nKURULUM TAMAM. Bundan sonra her sey otomatik." -ForegroundColor Green
