# Railway Deployment Guide

## Database Migration for Payment Mode Feature

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

### Railway Environment Variables
Make sure these environment variables are set in Railway:
- `FLASK_ENV=production`
- `DATABASE_URL` (Railway will set this automatically)

### Files Included in Deployment
- ✅ `database_schema.sql` - Contains payment_mode column definition
- ✅ `migrate_payment_mode.py` - Migration script for existing databases
- ✅ `app.py` - Backend API with payment_mode functionality
- ✅ `static/js/modules/billing-system.js` - Frontend payment mode logic
- ✅ `templates/print_bill.html` - Updated print template with dynamic labels
- ✅ `requirements.txt` - Python dependencies

### Testing After Deployment
1. Check that the payment mode setting appears in Shop Settings
2. Test both 'advance' and 'full' payment modes
3. Verify print invoices show correct labels
4. Confirm billing form resets after printing
