# Pulls the latest code from GitHub into this folder.
# Local state (.env, secrets, data, music, logs, tools, .venv) is never in the repo, so it is never touched.
param(
    [string]$Repo = "metehandurmaz/retro-garage-bot",
    [string]$Branch = "main"
)
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$root = Split-Path -Parent $PSScriptRoot

$tmp = Join-Path $env:TEMP "retro-garage-update"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory $tmp | Out-Null
$zip = Join-Path $tmp "code.zip"
Invoke-WebRequest -UseBasicParsing "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $zip
Expand-Archive $zip -DestinationPath $tmp -Force
$code = Get-ChildItem $tmp -Directory | Select-Object -First 1

$requirements = Join-Path $root "requirements.txt"
$before = if (Test-Path $requirements) { (Get-FileHash $requirements).Hash } else { "" }

foreach ($item in "src", "scripts", "assets", "requirements.txt", "README.md", ".env.example") {
    $from = Join-Path $code.FullName $item
    if (Test-Path $from) { Copy-Item $from $root -Recurse -Force }
}

if ((Get-FileHash $requirements).Hash -ne $before) {
    & (Join-Path $root ".venv\Scripts\python.exe") -m pip install -q -r $requirements
}
Remove-Item $tmp -Recurse -Force
Write-Output "$(Get-Date -Format s) updated from $Repo@$Branch"
