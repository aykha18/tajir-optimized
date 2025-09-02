# Tajir POS Deployment Script
Write-Host "🚀 Starting Tajir POS Deployment..." -ForegroundColor Green

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if requirements are installed
Write-Host "Installing/updating requirements..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install requirements." -ForegroundColor Red
    exit 1
}

# Check for syntax errors
Write-Host "Checking for syntax errors..." -ForegroundColor Yellow
python -m py_compile app.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Syntax errors found in app.py." -ForegroundColor Red
    exit 1
}

# Test import
Write-Host "Testing application import..." -ForegroundColor Yellow
python -c "import app; print('✅ Application imports successfully')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to import application." -ForegroundColor Red
    exit 1
}

# Check environment file
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Please create one with database credentials." -ForegroundColor Yellow
}

# Check PostgreSQL configuration
if (Test-Path "postgresql_config.py") {
    Write-Host "✅ PostgreSQL configuration found" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL configuration not found." -ForegroundColor Yellow
}

Write-Host "`n🎉 Pre-deployment checks completed!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Ensure PostgreSQL is running and accessible" -ForegroundColor White
Write-Host "2. Set up environment variables in Railway dashboard" -ForegroundColor White
Write-Host "3. Deploy using: railway up" -ForegroundColor White
Write-Host "`n🚀 Ready for deployment!" -ForegroundColor Green
