# Railway Deployment Guide

## Overview

This guide covers deploying the Tajir POS system to Railway, including support for:
- Database migrations for Payment Mode feature
- Tesseract OCR for image text extraction
- All Python dependencies and system requirements

## 🚀 Quick Deployment

### 1. Connect to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link your project
railway link
```

### 2. Deploy
```bash
railway up
```

## 🔧 Tesseract OCR Configuration

### Railway Support
✅ **Yes, Railway supports Tesseract OCR!** 

Railway uses Nixpacks for builds, which allows us to install system packages like Tesseract OCR.

### Configuration Files

#### `nixpacks.toml` (Required for Tesseract)
```toml
[phases.setup]
nixPkgs = ["tesseract", "tesseract-data-eng", "python39", "python39Packages.pip"]

[phases.install]
cmds = [
    "pip install -r requirements.txt"
]

[phases.build]
cmds = [
    "python -c \"import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())\""
]

[start]
cmd = "python app.py"
```

#### Environment Variables
Set these in Railway dashboard:
```bash
FLASK_ENV=production
TESSERACT_ENABLED=true
PORT=5000
```

### Verification
After deployment, check Tesseract installation:
```bash
# Connect to Railway shell
railway shell

# Test Tesseract
tesseract --version
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

## 📊 Database Migration for Payment Mode Feature

### For New Deployments
If this is a fresh deployment, Railway will automatically create the database using `database_schema.sql`, which already includes the `payment_mode` column in the `shop_settings` table.

### For Existing Deployments
If you're updating an existing Railway deployment, you need to run the migration script to add the `payment_mode` column.

#### Option 1: Run Migration Script (Recommended)
1. Deploy your code to Railway
2. Connect to your Railway database via Railway CLI or dashboard
3. Run the migration script:
   ```bash
   python migrate_payment_mode.py
   ```

#### Option 2: Manual SQL Migration
If you prefer to run SQL directly:
```sql
-- Check if column exists
PRAGMA table_info(shop_settings);

-- Add payment_mode column if it doesn't exist
ALTER TABLE shop_settings 
ADD COLUMN payment_mode TEXT DEFAULT 'advance' 
CHECK (payment_mode IN ('advance', 'full'));

-- Update existing records
UPDATE shop_settings 
SET payment_mode = 'advance' 
WHERE payment_mode IS NULL;
```

### Verification
After migration, verify the column was added correctly:
```sql
PRAGMA table_info(shop_settings);
```

You should see the `payment_mode` column with:
- Type: TEXT
- Default: 'advance'
- Constraint: CHECK (payment_mode IN ('advance', 'full'))

## 🧪 Testing After Deployment

### 1. Basic Functionality
- ✅ Check that the application loads
- ✅ Verify database connectivity
- ✅ Test user authentication

### 2. Payment Mode Feature
- ✅ Check that the payment mode setting appears in Shop Settings
- ✅ Test both 'advance' and 'full' payment modes
- ✅ Verify print invoices show correct labels
- ✅ Confirm billing form resets after printing

### 3. Upload Products Feature
- ✅ Test CSV file upload
- ✅ Verify catalog analysis
- ✅ Test product creation

### 4. Scan Products Feature (OCR)
- ✅ Test image upload
- ✅ Verify text extraction
- ✅ Check confidence scoring
- ✅ Test copy to clipboard functionality

## 🔍 Troubleshooting

### Tesseract OCR Issues
```bash
# Check if Tesseract is installed
railway shell
tesseract --version

# Check Python pytesseract
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# Check Tesseract path
python -c "import pytesseract; print(pytesseract.pytesseract.tesseract_cmd)"
```

### Database Issues
```bash
# Check database connection
railway shell
python -c "import sqlite3; conn = sqlite3.connect('pos_tailor.db'); print('Database connected')"
```

### Build Issues
```bash
# Check build logs
railway logs

# Rebuild with fresh cache
railway up --force
```

## 📁 Files Included in Deployment

### Core Application
- ✅ `app.py` - Main Flask application
- ✅ `requirements.txt` - Python dependencies
- ✅ `database_schema.sql` - Database schema
- ✅ `migrate_payment_mode.py` - Migration script

### Configuration
- ✅ `nixpacks.toml` - Railway build configuration (Tesseract OCR)
- ✅ `.gitignore` - Git ignore rules

### Frontend
- ✅ `static/` - All static assets (CSS, JS, images)
- ✅ `templates/` - HTML templates
- ✅ `static/js/modules/` - JavaScript modules

### Features
- ✅ Payment Mode functionality
- ✅ Upload Products (Catalog Scanner)
- ✅ Scan Products (OCR Scanner)
- ✅ All billing and POS features

## 🌐 Environment Variables

### Required
```bash
FLASK_ENV=production
PORT=5000
```

### Optional
```bash
TESSERACT_ENABLED=true
DEBUG=false
```

## 📈 Performance Considerations

### OCR Processing
- Tesseract OCR processing is CPU-intensive
- Consider implementing request queuing for large batches
- Monitor memory usage during OCR operations

### File Uploads
- Railway has file size limits
- Implement client-side file compression
- Consider using external storage for large files

### Database
- SQLite is suitable for small to medium deployments
- Consider PostgreSQL for larger scale deployments
- Implement proper indexing for performance

## 🔒 Security Considerations

### File Uploads
- Validate file types and sizes
- Scan uploaded files for malware
- Implement proper file cleanup

### Authentication
- Use secure session management
- Implement rate limiting
- Regular security updates

### Environment Variables
- Never commit sensitive data to Git
- Use Railway's secure environment variable storage
- Rotate secrets regularly

## 📞 Support

### Railway Support
- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway

### Application Support
- Check logs: `railway logs`
- Connect to shell: `railway shell`
- Monitor metrics in Railway dashboard

---

**Last Updated**: December 2024  
**Version**: 2.0.0  
**Status**: ✅ Complete with Tesseract OCR Support
