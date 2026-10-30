# DaVinci Writer - Build Release Zip (PowerShell)
# Creates a self-contained release folder and zips it

param([string]$Version = "1.1.1")

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent -Path (Split-Path -Parent -Path $PSScriptRoot)
Set-Location $RepoRoot

Write-Host "`n============================================"
Write-Host "  DaVinci Writer - Build Release Zip"
Write-Host "============================================`n"

$ZipName = "DaVinci-v${Version}.zip"
$FolderName = "DaVinci-v${Version}"
$TmpPath = Join-Path $env:TEMP $FolderName

if (Test-Path $ZipName) {
    Remove-Item $ZipName -Force
    Write-Host "[..] Removed existing $ZipName"
}

if (Test-Path $TmpPath) {
    Remove-Item $TmpPath -Recurse -Force
}

Write-Host "[..] Creating temporary staging directory..."
New-Item -ItemType Directory -Path $TmpPath | Out-Null

Write-Host "[..] Copying repository files..."
$ExcludePatterns = @('\.git', '\.venv', '__pycache__', '\.env$', '\.DS_Store', '\.davinci\.')

Get-ChildItem -Path $RepoRoot -Recurse -Force | ForEach-Object {
    $RelPath = $_.FullName.Substring($RepoRoot.Length + 1)
    $Skip = $false
    
    foreach ($Pattern in $ExcludePatterns) {
        if ($RelPath -match $Pattern) { $Skip = $true; break }
    }
    # Exclude zip files and compiled Python
    if (-not $Skip -and ($_.Name -like 'DaVinci-v*.zip' -or $_.Name -like '*.pyc')) { $Skip = $true }
    
    if (-not $Skip -and $RelPath -notmatch '^output\\') {
        $DestPath = Join-Path $TmpPath $RelPath
        if ($_.PSIsContainer) {
            if (-not (Test-Path $DestPath)) {
                New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
            }
        } else {
            $DestDir = Split-Path -Parent $DestPath
            if (-not (Test-Path $DestDir)) {
                New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
            }
            Copy-Item -Path $_.FullName -Destination $DestPath -Force
        }
    }
}

Write-Host "[..] Sanitizing source folders..."
$SourceDirs = @('theses', 'artefacts', 'papers', 'my-papers', 'my-response-letters', 'submitted-papers', 'reviewer-feedback')
foreach ($Dir in $SourceDirs) {
    $Path = Join-Path -Path $TmpPath -ChildPath "sources" | Join-Path -ChildPath $Dir
    if (Test-Path $Path) {
        Get-ChildItem -Path $Path -Recurse -Force | 
            Where-Object { $_.Name -ne 'README.md' } | 
            Remove-Item -Recurse -Force
    }
}

Write-Host "[..] Creating output directories..."
$OutputDirs = @('output', 'output\knowledge', 'output\knowledge\sources')
foreach ($Dir in $OutputDirs) {
    $Path = Join-Path $TmpPath $Dir
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

Write-Host "[..] Creating zip file..."
Compress-Archive -Path $TmpPath -DestinationPath $ZipName -Force

Write-Host "[..] Cleaning up..."
Remove-Item $TmpPath -Recurse -Force

$ZipSize = (Get-Item $ZipName).Length / 1MB
Write-Host "`n[OK] Release created: $ZipName ($([math]::Round($ZipSize, 2)) MB)`n"
Write-Host "Next steps:"
Write-Host "  1. Test: Unzip and run start.bat or Start DaVinci.command"
Write-Host "  2. Publish:"
Write-Host "     git add -A"
Write-Host "     git commit -m 'Release v$Version'"
Write-Host "     git tag v$Version"
Write-Host "     git push origin main --tags"
Write-Host ""
