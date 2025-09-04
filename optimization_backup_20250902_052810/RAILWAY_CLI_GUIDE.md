# Railway CLI Environment Variables Guide

## Overview
This guide shows you how to set up environment variables for Tajir POS using Railway CLI.

## Prerequisites

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login to Railway
```bash
railway login
```

### 3. Link to Your Project
```bash
railway link
```

## Setting Environment Variables

### Method 1: Using the Python Script
```bash
python setup_railway_env.py
```

### Method 2: Using the Batch Script (Windows)
```bash
setup_railway_env.bat
```

### Method 3: Manual CLI Commands

#### Step 1: Check Current Variables
```bash
railway variables
```

#### Step 2: Set Application Variables
```bash
# Generate a secure secret key first
railway variables --set "SECRET_KEY=your_secure_secret_key_here"
railway variables --set "FLASK_ENV=production"
railway variables --set "DEBUG=False"
```

#### Step 3: Set Security Variables
```bash
railway variables --set "BCRYPT_LOG_ROUNDS=12"
railway variables --set "SESSION_COOKIE_SECURE=True"
railway variables --set "SESSION_COOKIE_HTTPONLY=True"
railway variables --set "PERMANENT_SESSION_LIFETIME=3600"
```

#### Step 4: Set Rate Limiting Variables
```bash
railway variables --set "RATELIMIT_STORAGE_URL=memory://"
railway variables --set "RATELIMIT_DEFAULT=200 per day;50 per hour"
```

#### Step 5: Set Logging Variables
```bash
railway variables --set "LOG_LEVEL=INFO"
railway variables --set "LOG_FILE=logs/tajir_pos.log"
```

## PostgreSQL Variables

**Important**: PostgreSQL variables are automatically set by Railway when you add a PostgreSQL plugin:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

### Adding PostgreSQL Plugin
1. Go to Railway dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Railway will automatically set the PostgreSQL environment variables

## Useful Railway CLI Commands

### View All Variables
```bash
railway variables
```

### View Specific Variable
```bash
railway variables --json | grep VARIABLE_NAME
```

### Delete a Variable
```bash
# Note: Railway CLI doesn't have a direct delete command
# Use the Railway dashboard to delete variables
```

### Deploy Application
```bash
railway up
```

### View Logs
```bash
railway logs
```

### Check Status
```bash
railway status
```

### Open in Browser
```bash
railway open
```

## Complete Setup Example

Here's a complete example of setting up all variables:

```bash
# 1. Login and link (if not done already)
railway login
railway link

# 2. Set all environment variables in one command
railway variables --set "SECRET_KEY=your_very_secure_secret_key_here_12345" \
  --set "FLASK_ENV=production" \
  --set "DEBUG=False" \
  --set "BCRYPT_LOG_ROUNDS=12" \
  --set "SESSION_COOKIE_SECURE=True" \
  --set "SESSION_COOKIE_HTTPONLY=True" \
  --set "PERMANENT_SESSION_LIFETIME=3600" \
  --set "RATELIMIT_STORAGE_URL=memory://" \
  --set "RATELIMIT_DEFAULT=200 per day;50 per hour" \
  --set "LOG_LEVEL=INFO" \
  --set "LOG_FILE=logs/tajir_pos.log"

# 3. Verify all variables are set
railway variables

# 4. Deploy the application
railway up

# 5. Check logs
railway logs
```

## ✅ Current Status (Updated)

Your Railway project now has the following environment variables set:

- ✅ `FLASK_ENV=production`
- ✅ `DEBUG=False`
- ✅ `BCRYPT_LOG_ROUNDS=12`
- ✅ `SESSION_COOKIE_SECURE=True`
- ✅ `SESSION_COOKIE_HTTPONLY=True`
- ✅ `PERMANENT_SESSION_LIFETIME=3600`
- ✅ `RATELIMIT_STORAGE_URL=memory://`
- ✅ `RATELIMIT_DEFAULT=200 per day;50 per hour`
- ✅ `LOG_LEVEL=INFO`
- ✅ `LOG_FILE=logs/tajir_pos.log`
- ✅ `SECRET_KEY` (already set)
- ✅ `DATABASE_PATH=pos_tailor.db` (will be overridden by PostgreSQL)

## Next Steps

1. **Add PostgreSQL Plugin** in Railway dashboard
2. **Deploy Application**: `railway up`
3. **Test Functionality**: Open the application URL
4. **Monitor Logs**: `railway logs`

## Troubleshooting

### Common Issues

#### 1. "Not in a Railway project"
```bash
# Solution: Link to your project
railway link
```

#### 2. "Railway CLI not found"
```bash
# Solution: Install Railway CLI
npm install -g @railway/cli
```

#### 3. "Authentication failed"
```bash
# Solution: Login again
railway login
```

#### 4. Variables not showing up
```bash
# Solution: Check if you're in the right project
railway status
railway variables
```

### Verification Commands

After setting variables, verify everything is correct:

```bash
# Check project status
railway status

# List all variables
railway variables

# Check if PostgreSQL variables are set (after adding PostgreSQL plugin)
railway variables --json | grep POSTGRES
```

## Security Best Practices

1. **Generate Strong Secret Keys**: Use a secure random generator
2. **Never Commit Secrets**: Keep environment variables out of version control
3. **Use Production Values**: Set `FLASK_ENV=production` and `DEBUG=False`
4. **Regular Rotation**: Change secret keys periodically
5. **Monitor Logs**: Check for any security-related issues

## Support

- **Railway Documentation**: https://docs.railway.app/
- **Railway CLI Help**: `railway --help`
- **Variable Commands**: `railway variables --help`
