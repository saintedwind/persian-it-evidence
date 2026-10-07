$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if ($pythonCommand) {
    & $pythonCommand.Source server.py
} elseif (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython server.py
} else {
    Write-Error 'Python 3.11+ is required. Install Python, then run: python server.py'
}
