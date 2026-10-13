$procs = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue |
         Select-Object -ExpandProperty OwningProcess -Unique
if ($procs) {
    $procs | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Write-Host "DaVinci Web UI stopped."
} else {
    Write-Host "DaVinci Web UI is not running."
}
