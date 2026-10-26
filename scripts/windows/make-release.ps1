# DaVinci Writer — Build Release Zip (PowerShell)
# Produces a self-contained folder that anyone can unzip and launch with
# a double-click on "Start DaVinci.command" (macOS) or start.bat (Windows).
#
# Usage:
#   .\scripts\windows\make-release.ps1
#   .\scripts\windows\make-release.ps1 -Version 1.0.2

param(
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"

# Get repo root
$RepoRoot = Split-Path -Parent -Path (Split-Path -Parent -Path $PSScriptRoot)
Set-Location $RepoRoot

Write-Host ""
Write-Host "============================================"
Write-Host "  DaVinci Writer — Build Release Zip"
Write-Host "============================================"
Write-Host ""

# Get version
if ([string]::IsNullOrEmpty($Version)) {
    $Version = Read-Host "Version number (e.g. 1.0.2)"
}

if ([string]::IsNullOrEmpty($Version)) {
    Write-Error "Version cannot be empty."
    exit 1
}

$ZipName = "DaVinci-v${Version}.zip"
$FolderName = "DaVinci-v${Version}"
$TmpPath = Join-Path $env:TEMP $FolderName

if (Test-Path $ZipName) {
    $Overwrite = Read-Host "$ZipName already exists. Overwrite? [y/N]"
    if ($Overwrite -ne "y" -and $Overwrite -ne "Y") {
        exit 0
    }
    Remove-Item $ZipName -Force
}

# Stage into temp folder
Write-Host "[..] Staging files..."
if (Test-Path $TmpPath) {
    Remove-Item $TmpPath -Recurse -Force
}
New-Item -ItemType Directory -Path $TmpPath | Out-Null

# Copy files, excluding certain patterns
$ExcludePatterns = @(
    '.git',
    '.venv',
    'output',
    '__pycache__',
    '*.pyc',
    '.env',
    'DaVinci-v*.zip',
    'web\.sessions',
    '.DS_Store',
    '*.log',
    '.davinci.pid'
)

Write-Host "[..] Copying repository files..."
Get-ChildItem -Path $RepoRoot -Recurse -Force | ForEach-Object {
    $RelativePath = $_.FullName.Substring($RepoRoot.Length + 1)
    $IsExcluded = $false
    
    foreach ($Pattern in $ExcludePatterns) {
        if ($RelativePath -like "*$Pattern*" -or $_.Name -like $Pattern) {
            $IsExcluded = $true
            break
        }
    }
    
    if (-not $IsExcluded) {
        $DestPath = Join-Path $TmpPath $RelativePath
        $DestDir = Split-Path -Parent $DestPath
        
        if ($_.PSIsContainer) {
            if (-not (Test-Path $DestDir)) {
                New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
            }
        } else {
            if (-not (Test-Path $DestDir)) {
                New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
            }
            Copy-Item -Path $_.FullName -Destination $DestPath -Force
        }
    }
}

# Strip personal source files; keep only README.md placeholders
Write-Host "[..] Sanitizing source folders..."
$SourceDirs = @('theses', 'artefacts', 'papers', 'my-papers', 'my-response-letters', 'submitted-papers', 'reviewer-feedback')
foreach ($Dir in $SourceDirs) {
    $DirPath = Join-Path $TmpPath "sources" $Dir
    if (Test-Path $DirPath) {
        Get-ChildItem -Path $DirPath -Recurse -Exclude 'README.md' -Force | 
            Where-Object { $_.Name -ne 'README.md' } | 
            Remove-Item -Recurse -Force
    }
}

# Create required output dirs so the app starts cleanly
Write-Host "[..] Creating output directories..."
$OutputDirs = @(
    (Join-Path $TmpPath "output"),
    (Join-Path $TmpPath "output" "knowledge"),
    (Join-Path $TmpPath "output" "knowledge" "sources")
)
foreach ($Dir in $OutputDirs) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
    }
}

# Create the zip file
Write-Host "[..] Creating zip file: $ZipName"
if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
    Compress-Archive -Path $TmpPath -DestinationPath $ZipName -Force
} else {
    $msg = "PowerShell's Compress-Archive cmdlet is not available. Update PowerShell or install 7-Zip."
    Write-Error $msg
    exit 1
}

# Cleanup
Write-Host "[..] Cleaning up temporary files..."
Remove-Item $TmpPath -Recurse -Force

Write-Host ""
Write-Host "✓ Release package created: $ZipName"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Test the release:"
Write-Host "     - Unzip $ZipName to a test folder"
Write-Host "     - Double-click start.bat or Start DaVinci.command"
Write-Host ""
Write-Host "  2. Publish the release:"
Write-Host "     git add -A"
Write-Host "     git commit -m `"Release v$Version`""
Write-Host "     git tag v$Version"
Write-Host "     git push origin main --tags"
Write-Host ""
