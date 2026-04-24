$ErrorActionPreference = 'Stop'

$projectRoot = $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$script = Join-Path $projectRoot 'password_checker\main.py'

& $python $script @args