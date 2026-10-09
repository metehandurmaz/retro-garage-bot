# Registers a Windows scheduled task that runs the bot three times a day (one Short per run).
# Each run first pulls the latest code from GitHub (scripts\run.ps1 -> scripts\update.ps1).
#   powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1
param(
    [string[]]$Times = @("10:00", "15:00", "20:00"),
    [string]$TaskName = "RetroGarageBot"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Run scripts\setup.ps1 first." }

$runner = Join-Path $root "scripts\run.ps1"
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`"" -WorkingDirectory $root
$triggers = $Times | ForEach-Object { New-ScheduledTaskTrigger -Daily -At $_ }
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers -Settings $settings -Principal $principal -Force | Out-Null
Write-Host "Task '$TaskName' runs daily at $($Times -join ', '). Logs: $root\logs\bot.log"
