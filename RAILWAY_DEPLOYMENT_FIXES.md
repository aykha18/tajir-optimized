# Railway Deployment Fixes

This guide helps you apply the database fixes to your Railway deployment to resolve setup wizard and shop settings issues.

## 🚀 Quick Deployment

### Option 1: Run the Comprehensive Fix Script

```bash
# Deploy all fixes at once
python deploy_railway_fixes.py
```

This script will:
- ✅ Fix all database sequences
- ✅ Create missing shop settings for users
- ✅ Verify database constraints
- ✅ Provide a complete status report

### Option 2: Run Individual Fix Scripts

```bash
# Fix sequences only
python fix_railway_sequences.py

# Fix missing shop settings only
python fix_railway_shop_settings.py
```

## 🔧 What These Scripts Fix

### 1. Database Sequence Issues
- **Problem**: Setup wizard fails with "duplicate key value violates unique constraint"
- **Solution**: Aligns all database sequences with actual data
- **Tables Fixed**: users, shop_settings, employees, user_plans, vat_rates, bills, bill_items, customers, products, product_types

### 2. Missing Shop Settings
- **Problem**: Users get 404 error when accessing shop settings
- **Solution**: Creates default shop settings for users who don't have them
- **Default Values**: AED currency, Asia/Dubai timezone, dynamic invoice template enabled

### 3. Database Constraints
- **Problem**: Global unique constraints prevent multiple users from sharing contact info
- **Solution**: Verifies constraints are properly configured for multi-tenant system

## 📋 Prerequisites

1. **Railway CLI Installed**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Logged into Railway**:
   ```bash
   railway login
   ```

3. **Connected to Your Project**:
   ```bash
   railway link
   ```

## 🚀 Deployment Steps

### Step 1: Deploy the Fix Scripts

```bash
# Upload the fix scripts to Railway
railway run python deploy_railway_fixes.py
```

### Step 2: Verify the Fix

After running the script, you should see:
```
🎉 Railway deployment fixes completed successfully!

📋 Summary:
  ✅ Fixed X database sequences
  ✅ Created Y missing shop settings
  ✅ Verified database constraints
  ✅ All users now have shop settings

🚀 Your Railway deployment is now ready!
```

### Step 3: Test the Application

1. **Test Setup Wizard**: Try creating a new shop account
2. **Test Shop Settings**: Login and access shop settings
3. **Test Multi-Currency**: Verify currency and timezone settings work

## 🔍 Troubleshooting

### If the script fails:

1. **Check Database Connection**:
   ```bash
   railway run python -c "import os; print('DATABASE_URL:', os.getenv('DATABASE_URL')[:20] + '...')"
   ```

2. **Check Database Tables**:
   ```bash
   railway run python -c "
   import psycopg2, os
   conn = psycopg2.connect(os.getenv('DATABASE_URL'))
   cursor = conn.cursor()
   cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\'')
   print('Tables:', [row[0] for row in cursor.fetchall()])
   conn.close()
   "
   ```

3. **Manual Database Access**:
   ```bash
   railway run psql $DATABASE_URL
   ```

### Common Issues:

- **Permission Denied**: Make sure your Railway project has database access
- **Table Not Found**: The database might not be fully migrated
- **Connection Timeout**: Check your Railway database status

## 📊 Expected Results

After successful deployment:

- ✅ **Setup Wizard**: Works without sequence conflicts
- ✅ **Shop Settings**: All users can access their settings
- ✅ **Multi-Currency**: Default AED currency and Asia/Dubai timezone
- ✅ **No 404 Errors**: All API endpoints work correctly

## 🔄 Reverting Changes

If you need to revert the changes:

```bash
# Connect to database
railway run psql $DATABASE_URL

# Remove created shop settings (if needed)
DELETE FROM shop_settings WHERE user_id IN (
    SELECT user_id FROM users WHERE shop_code LIKE 'TEST%'
);

# Reset sequences (if needed)
SELECT setval('shop_settings_setting_id_seq', 1, false);
```

## 📞 Support

If you encounter issues:

1. Check the Railway logs: `railway logs`
2. Verify database status in Railway dashboard
3. Run the verification commands above
4. Contact support with the error messages

---

**Note**: These fixes are safe to run multiple times. The scripts check for existing data before making changes.
