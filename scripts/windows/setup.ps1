#Requires -Version 5.1
$ErrorActionPreference = "Stop"
# Work from the repository root (this script lives in scripts\windows\)
Set-Location (Resolve-Path (Join-Path $PSScriptRoot "..\.."))

function Write-Step($msg)  { Write-Host "[..] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Fail($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host " ============================================" -ForegroundColor Cyan
Write-Host "  DaVinci Writer -- First-Time Setup"          -ForegroundColor Cyan
Write-Host " ============================================" -ForegroundColor Cyan
Write-Host ""

# -- 1. Check Python ----------------------------------------------------------
try {
    $pyver = (python --version 2>&1).ToString().Trim()
    if ($LASTEXITCODE -ne 0) { throw "python not found" }
    Write-Ok "$pyver detected."
} catch {
    Write-Fail "Python was not found."
    Write-Host ""
    Write-Host "  Please install Python 3.10 or later from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  IMPORTANT: During installation, tick 'Add Python to PATH'." -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# -- 2. Virtual environment ---------------------------------------------------
if (-not (Test-Path ".venv")) {
    Write-Step "Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Could not create virtual environment."
        Read-Host "`nPress Enter to exit"
        exit 1
    }
    Write-Ok "Virtual environment created."
} else {
    Write-Ok "Virtual environment already exists."
}

# -- 3. Install dependencies --------------------------------------------------
Write-Step "Installing dependencies (this may take a minute)..."
& ".venv\Scripts\pip.exe" install -q -r "web\requirements.txt"
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Dependency installation failed."
    Read-Host "`nPress Enter to exit"
    exit 1
}
Write-Ok "Dependencies installed."

# -- 4. API key setup ---------------------------------------------------------
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host " ============================================" -ForegroundColor Cyan
    Write-Host "  API Key Required"                            -ForegroundColor Cyan
    Write-Host " ============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  DaVinci Writer uses the Anthropic Claude API."
    Write-Host "  You need an API key to generate papers."
    Write-Host ""
    Write-Host "  Get your key at:  https://console.anthropic.com/" -ForegroundColor Yellow
    Write-Host ""
    $apikey = Read-Host "  Paste your API key (sk-ant-...)"
    if ([string]::IsNullOrWhiteSpace($apikey)) {
        Write-Warn "No key entered. Copying .env.example -- edit .env before running."
        Copy-Item ".env.example" ".env"
    } else {
        "ANTHROPIC_API_KEY=$apikey" | Set-Content ".env" -Encoding Ascii
        Write-Ok "API key saved to .env"
        if (-not $apikey.StartsWith('sk-ant-')) {
            Write-Warn "Key doesn't start with 'sk-ant-' -- double-check it's correct. Edit .env if needed."
        }
    }
} else {
    Write-Ok ".env already configured."
}

# -- Done ----------------------------------------------------------------------
Write-Host ""
Write-Host " ============================================" -ForegroundColor Green
Write-Host "  Setup complete!"                             -ForegroundColor Green
Write-Host " ============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Start the app:  .\scripts\windows\run-webui.ps1"
Write-Host "  Stop the app:   .\scripts\windows\stop-webui.ps1"
Write-Host ""

$launch = Read-Host "Launch DaVinci Writer now? [Y/n]"
if ($launch -ne 'n' -and $launch -ne 'N') {
    & "$PSScriptRoot\run-webui.ps1"
}
