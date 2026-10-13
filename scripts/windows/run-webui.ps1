$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

& "$root\scripts\windows\run-webui.bat"
