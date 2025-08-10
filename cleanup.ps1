# Tajir POS Cleanup Script
# Cleans up logs and test artifacts

Write-Host "Starting Tajir POS Cleanup..." -ForegroundColor Green

# Clean up test artifacts
Write-Host "Cleaning test artifacts..." -ForegroundColor Yellow
if (Test-Path "tests\selenium\__pycache__") {
    Remove-Item -Path "tests\selenium\__pycache__" -Recurse -Force
    Write-Host "  Removed __pycache__ directory" -ForegroundColor Green
}

if (Test-Path "tests\selenium\report.html") {
    Remove-Item -Path "tests\selenium\report.html" -Force
    Write-Host "  Removed test report" -ForegroundColor Green
}

# Clean up logs
Write-Host "Cleaning log files..." -ForegroundColor Yellow
if (Test-Path "logs\errors.log") {
    Clear-Content -Path "logs\errors.log"
    Write-Host "  Cleared errors.log" -ForegroundColor Green
}

if (Test-Path "logs\tajir_pos.log") {
    # Only clear if file is larger than 10MB
    $logSize = (Get-Item "logs\tajir_pos.log").Length
    if ($logSize -gt 10MB) {
        Clear-Content -Path "logs\tajir_pos.log"
        Write-Host "  Cleared tajir_pos.log (was $([math]::Round($logSize/1MB, 2))MB)" -ForegroundColor Green
    } else {
        Write-Host "  Skipped tajir_pos.log (size: $([math]::Round($logSize/1MB, 2))MB)" -ForegroundColor Yellow
    }
}

# Clean up any temporary files
Write-Host "Cleaning temporary files..." -ForegroundColor Yellow
$tempFiles = @("*.tmp", "*.temp", "*.log.tmp")
foreach ($pattern in $tempFiles) {
    $files = Get-ChildItem -Path "." -Filter $pattern -Recurse -ErrorAction SilentlyContinue
    if ($files) {
        $files | Remove-Item -Force
        Write-Host "  Removed $($files.Count) temporary files" -ForegroundColor Green
    }
}

Write-Host "Cleanup completed successfully!" -ForegroundColor Green
Write-Host "Tip: Run this script regularly to keep your workspace clean" -ForegroundColor Cyan
