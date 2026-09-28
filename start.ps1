#Requires -Version 5.1
<#
.SYNOPSIS
  Launch classroom-mcp REST API (port 11105).
.DESCRIPTION
  Clears port zombies, starts uvicorn/Starlette backend with the repo root as
  working directory, waits for TCP readiness (not a fixed sleep), then opens
  the browser unless -NoBrowser is given.
#>
param(
  [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$Port = 11105

# 1. Clear port zombies before bind.
$holders = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
foreach ($h in $holders) {
  try { Stop-Process -Id $h.OwningProcess -Force -ErrorAction Stop } catch { }
}
Start-Sleep -Seconds 1

# 2. Start backend with explicit working directory.
$proc = Start-Process -FilePath "uv" `
  -ArgumentList "run", "python", "-m", "classroom_mcp.api" `
  -WorkingDirectory $RepoRoot -PassThru -WindowStyle Minimized
Write-Host "classroom-mcp backend starting (PID $($proc.Id)) on port $Port..."

# 3. TCP readiness poll (30 x 2 s), not a fixed sleep.
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Seconds 2
  try {
    $tcp = New-Object Net.Sockets.TcpClient
    $iar = $tcp.BeginConnect("127.0.0.1", $Port, $null, $null)
    if ($iar.AsyncWaitHandle.WaitOne(1000)) {
      $tcp.EndConnect($iar)
      $ready = $true
      $tcp.Close()
      break
    }
    $tcp.Close()
  } catch { }
}
if (-not $ready) {
  Write-Host "[ERROR] Backend did not bind port $Port in 60 s." -ForegroundColor Red
  exit 1
}
Write-Host "Backend ready on http://127.0.0.1:$Port" -ForegroundColor Green

# 4. Browser auto-open after 200.
if (-not $NoBrowser) {
  Start-Process "http://127.0.0.1:$Port"
}
