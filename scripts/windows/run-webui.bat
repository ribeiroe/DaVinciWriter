@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0..\.."

set "APP_LOG=.davinci.log"
set "REQ_FILE=web\requirements.txt"
set "REQ_HASH_FILE=.venv\requirements.sha256"

echo.
echo  ============================================
echo   DaVinci Writer -- Startup Progress
echo  ============================================
echo.
echo [1/6] Checking Python version...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.10+ was not found on PATH.
    echo Install Python and try again.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [1/6] Python !PYTHON_VERSION! found ✓
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [2/6] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create virtual environment.
        pause
        exit /b 1
    )
    echo [2/6] Virtual environment created ✓
) else (
    echo [2/6] Virtual environment exists ✓
)
echo.

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Could not activate virtual environment.
    pause
    exit /b 1
)

echo [3/6] Checking dependencies...
set "CURRENT_REQ_HASH="
for /f %%h in ('certutil -hashfile "%REQ_FILE%" SHA256 ^| findstr /R "^[0-9A-F][0-9A-F]"') do (
    if not defined CURRENT_REQ_HASH set "CURRENT_REQ_HASH=%%h"
)

set "STORED_REQ_HASH="
if exist "%REQ_HASH_FILE%" set /p STORED_REQ_HASH=<"%REQ_HASH_FILE%"

set "NEEDS_INSTALL=0"
if not exist ".venv\Scripts\streamlit.exe" set "NEEDS_INSTALL=1"
if not defined CURRENT_REQ_HASH set "NEEDS_INSTALL=1"
if /I not "!CURRENT_REQ_HASH!"=="!STORED_REQ_HASH!" set "NEEDS_INSTALL=1"

if "!NEEDS_INSTALL!"=="1" (
    echo [3/6] Installing dependencies...
    if not exist ".venv\Scripts\streamlit.exe" (
        echo [INFO] First run can take 5-15 minutes depending on your internet.
    )
    echo [INFO] Live package progress is shown below:
    python -m pip install --disable-pip-version-check -r "%REQ_FILE%"
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        echo [HINT] Check your internet connection and rerun start.bat.
        pause
        exit /b 1
    )
    if defined CURRENT_REQ_HASH (
        > "%REQ_HASH_FILE%" echo !CURRENT_REQ_HASH!
    )
    echo [3/6] Dependencies installed ✓
) else (
    echo [3/6] Dependencies already up to date ✓
)
echo.

echo [4/6] Checking configuration...
if exist ".env" (
    echo [4/6] Configuration file found ✓
) else (
    echo [4/6] Configuration file not found - using defaults
)
echo.

echo [5/6] Starting application in background...
powershell -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c','.venv\Scripts\activate.bat && streamlit run web/app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false > \"%APP_LOG%\" 2>&1' -WorkingDirectory '%CD%' -WindowStyle Hidden"
echo [5/6] Application process started ✓
echo.

echo [6/6] Waiting for application to be ready on http://localhost:8501...
set /a WAIT_COUNT=0
:wait_ready
set /a WAIT_COUNT+=1
netstat -ano | findstr ":8501" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto app_ready

if %WAIT_COUNT% GEQ 180 goto app_timeout

set /a MOD=WAIT_COUNT%%10
if !MOD! EQU 0 (
    echo    Waiting... !WAIT_COUNT!s elapsed.
)

timeout /t 1 >nul
goto wait_ready

:app_ready
echo [6/6] Application is ready ✓
echo.
echo  ============================================
echo   DaVinci is running^^!
echo   URL: http://localhost:8501
echo   To stop: run stop.bat
echo  ============================================
echo.
start "" "http://localhost:8501"
echo DaVinci is running independently. You can safely close this window.
echo.
pause
exit /b 0

:app_timeout
echo [6/6] WARNING: Startup is taking longer than expected
echo.
echo    Check %APP_LOG% for details
echo    Close this window and run stop.bat then start.bat again
pause
exit /b 1
