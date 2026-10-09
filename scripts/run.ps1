# Scheduled task entry point: update the code, then upload one Short.
# An update failure (GitHub down, no network) must not stop the upload with the code already on disk.
$root = Split-Path -Parent $PSScriptRoot
$logs = Join-Path $root "logs"
New-Item -ItemType Directory $logs -Force | Out-Null
$updateLog = Join-Path $logs "update.log"

try {
    & (Join-Path $PSScriptRoot "update.ps1") *>> $updateLog
} catch {
    "$(Get-Date -Format s) update failed: $_" | Add-Content $updateLog
}

Set-Location $root
& (Join-Path $root ".venv\Scripts\python.exe") -m src.main
exit $LASTEXITCODE
