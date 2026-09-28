#Requires -Version 5.1
<#
.SYNOPSIS
  Validate manifest.json and pack the MCP bundle (or explain the manual step).
#>
$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot | Split-Path -Parent
Set-Location $RepoRoot

$manifest = Get-Content "manifest.json" -Raw | ConvertFrom-Json
$pyVersion = (Select-String -Path "pyproject.toml" -Pattern '^version = "(.*)"').Matches[0].Groups[1].Value
if ($manifest.version -ne $pyVersion) {
  Write-Host "[FAIL] manifest.json ($($manifest.version)) != pyproject.toml ($pyVersion)" -ForegroundColor Red
  exit 1
}
Write-Host "manifest version $pyVersion OK" -ForegroundColor Green

uv run python -c "import sys,importlib.util as u; sys.path.insert(0,r'src'); s=u.find_spec('classroom_mcp'); print(s.origin); assert s and 'src' in s.origin"
if ($LASTEXITCODE -ne 0) { throw "package import check failed" }
Write-Host "package import OK" -ForegroundColor Green

$mcpb = Get-Command mcpb -ErrorAction SilentlyContinue
if (-not $mcpb) {
  Write-Host "[INFO] No 'mcpb' CLI on PATH. Manual step: open the Anthropic DXT desktop app, validate, then pack dist/classroom-mcp-v$pyVersion.mcpb." -ForegroundColor Yellow
  exit 1
}
New-Item -ItemType Directory -Force -Path "dist" | Out-Null
& mcpb pack . "dist/classroom-mcp-v$pyVersion.mcpb"
