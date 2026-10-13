@echo off
REM DaVinci Writer Stop Script
REM Shows progress in terminal until app stops

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  DaVinci Writer - Stopping
echo ========================================
echo.

set "RUNNING_PIDS="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":8501 .*LISTENING"') do (
    set "RUNNING_PIDS=!RUNNING_PIDS! %%p"
)

REM Step 1: Check if app is running
echo [1/3] Checking if application is running...
if not defined RUNNING_PIDS (
    echo [1/3] Application is not running ✓
    echo.
    echo ========================================
    echo  Already stopped
    echo ========================================
    echo.
    exit /b 0
)
echo [1/3] Application found running on port 8501 ✓
echo.

REM Step 2: Stop application gracefully
echo [2/3] Stopping application...
for %%p in (!RUNNING_PIDS!) do (
    taskkill /PID %%p /F >nul 2>&1
)
echo [2/3] Stop signal sent ✓
echo.

REM Step 3: Verify it stopped
echo [3/3] Verifying application stopped...
set /a WAIT_COUNT=0

:wait_stopped
set /a WAIT_COUNT+=1
netstat -ano | findstr /R /C:":8501 .*LISTENING" >nul
if errorlevel 1 (
    echo [3/3] Port 8501 is now free ✓
    echo.
    echo ========================================
    echo  Application stopped successfully^^!
    echo ========================================
    echo.
    exit /b 0
) else if !WAIT_COUNT! GEQ 5 (
    echo [3/3] WARNING: Port still in use
    echo.
    echo ========================================
    echo  Attempted to stop but port may still be in use
    echo ========================================
    echo.
    exit /b 1
) else (
    timeout /t 1 /nobreak >nul
    goto wait_stopped
)
