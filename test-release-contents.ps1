$TestDir = 'C:\Test-Release-Contents'
if (Test-Path $TestDir) { Remove-Item $TestDir -Recurse -Force }

Write-Host "Extracting release..."
Expand-Archive -Path DaVinci-v1.0.1.zip -DestinationPath $TestDir -ErrorAction Stop

Write-Host ""
Write-Host "Top-level extracted folders:"
Get-ChildItem -Path $TestDir | Select-Object Name | Format-Table

# The zip wraps content in a subfolder
$InnerDir = Get-ChildItem -Path $TestDir -Directory | Select-Object -First 1 -ExpandProperty FullName
Write-Host "Inner folder: $InnerDir"
$WebDir = Join-Path $InnerDir 'web'

Write-Host ""
Write-Host "Web directory contents:"
Get-ChildItem -Path $WebDir -File | Select-Object Name | Format-Table

Write-Host ""
Write-Host "Checking critical files:"
$CriticalFiles = @('app.py', 'davinci_core.py', 'requirements.txt')
foreach ($File in $CriticalFiles) {
    $Path = Join-Path $WebDir $File
    if (Test-Path $Path) {
        $Size = (Get-Item $Path).Length
        Write-Host "[OK] $File - $Size bytes"
    } else {
        Write-Host "[MISSING] $File"
    }
}

Write-Host ""
Write-Host "Cleaning up..."
Remove-Item $TestDir -Recurse -Force
Write-Host "Done"
