$logDir = "C:\Users\Dan\AppData\Local\Temp\opencode\finance_bot"
$logFile = Join-Path $logDir "bot_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$python = "C:\Users\Dan\AppData\Local\Temp\opencode\.venv\Scripts\python.exe"
$script = "C:\Users\Dan\AppData\Local\Temp\opencode\finance_bot\bot.py"

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $python
$psi.Arguments = $script
$psi.WorkingDirectory = $logDir
$psi.UseShellExecute = $true
$psi.CreateNoWindow = $true

$p = [System.Diagnostics.Process]::Start($psi)
Write-Output "Started bot PID $($p.Id)"
