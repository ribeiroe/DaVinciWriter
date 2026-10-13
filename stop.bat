@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "TARGET=%ROOT_DIR%scripts\windows\stop-webui.bat"

if not exist "%TARGET%" (
    echo Could not find "%TARGET%".
    echo.
    pause
    exit /b 1
)

call "%TARGET%"
exit /b %ERRORLEVEL%
