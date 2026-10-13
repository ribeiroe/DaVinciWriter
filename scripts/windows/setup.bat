@echo off
setlocal enabledelayedexpansion

echo.
echo  ============================================
echo   DaVinci Writer -- First-Time Setup
echo  ============================================
echo.

REM Work from the repository root (this script lives in scripts\windows\)
cd /d "%~dp0..\.."

REM ── 1. Check Python ─────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found.
    echo.
    echo   Please install Python 3.10 or later from:
    echo   https://www.python.org/downloads/
    echo.
    echo   IMPORTANT: During installation, tick the box that says
    echo              "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% detected.

REM ── 2. Create virtual environment ───────────────────────────────────────
if not exist ".venv" (
    echo [..] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

REM ── 3. Install dependencies ─────────────────────────────────────────────
echo [..] Installing dependencies (this may take a minute)...
call .venv\Scripts\activate.bat
python -m pip install --disable-pip-version-check -r web\requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    echo [HINT] Check your internet connection and rerun start.bat.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

REM ── 4. API key setup ────────────────────────────────────────────────────
if not exist ".env" (
    echo.
    echo  ============================================
    echo   API Key Required
    echo  ============================================
    echo.
    echo   DaVinci Writer uses the Anthropic Claude API.
    echo   You need a free API key to generate papers.
    echo.
    echo   Get your key at:  https://console.anthropic.com/
    echo.
    set /p APIKEY="  Paste your API key here (sk-ant-...): "
    if "!APIKEY!"=="" (
        echo.
        echo [WARN] No key entered. Copying .env.example instead.
        copy .env.example .env >nul
    ) else (
        echo ANTHROPIC_API_KEY=!APIKEY!> .env
        echo [OK] API key saved to .env
        if not "!APIKEY:~0,7!"=="sk-ant-" (
            echo.
            echo [WARN] Key doesn't start with "sk-ant-" -- double-check it's correct.
            echo        Edit .env if needed before running the app.
        )
    )
) else (
    echo [OK] .env already configured.
)

REM ── Done ─────────────────────────────────────────────────────────────────
echo.
echo  ============================================
echo   Setup complete^^!
echo  ============================================
echo.
echo   Start the app:   scripts\windows\run-webui.bat
echo   Stop the app:    scripts\windows\stop-webui.bat
echo.
echo   Opening DaVinci Writer now...
start "" "scripts\windows\run-webui.bat"
