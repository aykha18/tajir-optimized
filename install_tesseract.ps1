# Tesseract OCR Installation Script for Windows
Write-Host "Tesseract OCR Installation Helper" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if Tesseract is already installed
Write-Host "Checking if Tesseract is already installed..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>$null
    if ($tesseractVersion) {
        Write-Host "SUCCESS: Tesseract is already installed!" -ForegroundColor Green
        Write-Host "Version: $tesseractVersion" -ForegroundColor Cyan
        exit 0
    }
} catch {
    Write-Host "ERROR: Tesseract not found in PATH" -ForegroundColor Red
}

Write-Host "`nTesseract OCR Installation Instructions:" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

Write-Host "1. Download Tesseract OCR for Windows:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
Write-Host "   - Download the latest 64-bit version" -ForegroundColor Cyan
Write-Host "   - Example: tesseract-ocr-w64-setup-5.3.1.20230401.exe" -ForegroundColor Cyan

Write-Host "`n2. Install Tesseract:" -ForegroundColor White
Write-Host "   - Run the installer as Administrator" -ForegroundColor Cyan
Write-Host "   - Install to: C:\Program Files\Tesseract-OCR\" -ForegroundColor Cyan
Write-Host "   - IMPORTANT: Check 'Add to PATH' during installation" -ForegroundColor Green
Write-Host "   - Install additional language data (recommended)" -ForegroundColor Cyan

Write-Host "`n3. After Installation:" -ForegroundColor White
Write-Host "   - Restart your terminal/PowerShell" -ForegroundColor Cyan
Write-Host "   - Run: tesseract --version" -ForegroundColor Cyan
Write-Host "   - Test OCR: python test_ocr.py" -ForegroundColor Cyan

Write-Host "`nChecking common installation paths..." -ForegroundColor Yellow

# Check common installation paths
$commonPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
)

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        Write-Host "SUCCESS: Found Tesseract at: $path" -ForegroundColor Green
        
        # Try to add to PATH temporarily
        $env:PATH = $env:PATH + ";" + (Split-Path $path)
        Write-Host "Added to PATH temporarily. Testing..." -ForegroundColor Yellow
        
        try {
            $version = & $path --version 2>$null
            if ($version) {
                Write-Host "SUCCESS: Tesseract is working! Version: $version" -ForegroundColor Green
                Write-Host "`nTo make this permanent, add to your system PATH:" -ForegroundColor Yellow
                Write-Host "   $(Split-Path $path)" -ForegroundColor Cyan
                exit 0
            }
        } catch {
            Write-Host "ERROR: Tesseract found but not working properly" -ForegroundColor Red
        }
    }
}

Write-Host "ERROR: Tesseract not found in common locations" -ForegroundColor Red

Write-Host "`nManual Installation Steps:" -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow

Write-Host "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
Write-Host "2. Run installer as Administrator" -ForegroundColor Cyan
Write-Host "3. Install to: C:\Program Files\Tesseract-OCR\" -ForegroundColor Cyan
Write-Host "4. Check 'Add to PATH' option" -ForegroundColor Green
Write-Host "5. Restart terminal and test" -ForegroundColor Cyan

Write-Host "`nAfter installation, run this script again to verify!" -ForegroundColor Green

# Wait for user input
Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
