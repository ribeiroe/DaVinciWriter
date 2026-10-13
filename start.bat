@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "TARGET=%ROOT_DIR%scripts\windows\run-webui.bat"

if not exist "%TARGET%" (
    echo Could not find "%TARGET%".
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Could not find scripts/windows/run-webui.bat.','DaVinci Writer') | Out-Null"
    exit /b 1
)

start "DaVinci Startup" cmd /c ""%TARGET%""

exit /b 0
