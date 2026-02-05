# Purpose: Free a port by finding and killing the process using it
# Usage: .\free-port.ps1 [port] [-Force]
# Example: .\free-port.ps1 3002

param(
    [Parameter(Mandatory = $false)]
    [int]$Port = 3002,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

# Design: Check if port is in use, find process, optionally kill it
# Edge Cases: Port not in use, process not found, permission denied

Write-Host "Checking port $Port..." -ForegroundColor Cyan

try {
    # Find process using the port
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if (-not $connection) {
        Write-Host "Port $Port is not in use." -ForegroundColor Green
        exit 0
    }
    
    $processId = $connection.OwningProcess | Select-Object -Unique
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    
    if (-not $process) {
        Write-Host "Process with PID $processId not found (may have already terminated)." -ForegroundColor Yellow
        exit 0
    }
    
    Write-Host "Port $Port is in use by:" -ForegroundColor Yellow
    Write-Host "  Process Name: $($process.ProcessName)" -ForegroundColor White
    Write-Host "  Process ID: $($process.Id)" -ForegroundColor White
    Write-Host "  Path: $($process.Path)" -ForegroundColor White
    
    if ($Force) {
        Write-Host "`nKilling process $($process.Id)..." -ForegroundColor Red
        Stop-Process -Id $process.Id -Force -ErrorAction Stop
        Write-Host "Process killed successfully. Port $Port is now free." -ForegroundColor Green
    } else {
        Write-Host "`nTo kill this process, run:" -ForegroundColor Cyan
        Write-Host "  .\free-port.ps1 -Port $Port -Force" -ForegroundColor White
        Write-Host "`nOr manually:" -ForegroundColor Cyan
        Write-Host "  Stop-Process -Id $($process.Id) -Force" -ForegroundColor White
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
