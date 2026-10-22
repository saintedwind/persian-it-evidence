$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Open http://127.0.0.1:8765/demo after the server starts. Stop with Ctrl+C.'
& (Join-Path $PSScriptRoot 'run-demo.ps1')
