# Basic Testing Guide (Without Redis)

## Overview
This guide helps you test the core functionality that works without Redis while you set up the Redis server for advanced caching features.

## 1. Test Health & Resource Monitoring

### Health Check
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/monitor/health" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "..."
}
```

### Resource Monitoring
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/monitor/resources" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
  "uptime": "...",
  "request_count": 0,
  "active_connections": 0,
  "max_connections": 10,
  "database_pool": "available",
  "redis_status": "connected"
}
```

## 2. Test Core Endpoints (Without Caching)

### Products Aggregated
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Dashboard Aggregated
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/aggregated?user_id=1" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Customers Paginated
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/customers/paginated?user_id=1&page=1&per_page=10" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 3. Test Connection Pooling

### Multiple Concurrent Requests
Create a simple test script to test connection pooling:

```powershell
# Test multiple concurrent requests to see connection pooling in action
$jobs = @()
for ($i = 1; $i -le 5; $i++) {
    $jobs += Start-Job -ScriptBlock {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing
        return $response.StatusCode
    }
}

# Wait for all jobs to complete
$jobs | Wait-Job | Receive-Job
$jobs | Remove-Job
```

## 4. Test Performance Monitoring

### Check Request Count
```powershell
# Make a few requests
Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing | Out-Null
Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/aggregated?user_id=1" -Method GET -UseBasicParsing | Out-Null

# Check updated resource monitoring
Invoke-WebRequest -Uri "http://localhost:5000/api/monitor/resources" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Changes:**
- `request_count` should increase
- `active_connections` should show current database connections

## 5. Test Database Operations

### Add a Test Product
```powershell
$productData = @{
    name = "Test Product for Caching"
    price = 99.99
    user_id = 1
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/products" -Method POST -ContentType "application/json" -Body $productData -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Check Products Again
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 6. Browser Testing

### Test Frontend Integration
1. Open your browser and navigate to the products page
2. Open Developer Tools (F12) → Console
3. Refresh the page multiple times
4. Check console logs for any errors
5. Monitor network tab for API calls

### Expected Behavior:
- API calls should work (though without caching)
- No Redis-related errors in console
- Database operations should work normally

## 7. What's Working vs. What Needs Redis

### ✅ Working Without Redis:
- Health checks
- Resource monitoring
- Connection pooling
- Database operations
- Core API endpoints
- Performance monitoring decorator

### ❌ Needs Redis:
- Cache statistics
- Cache warming
- Cache invalidation
- Cache optimization
- Advanced caching features

## 8. Next Steps to Enable Full Caching

### Install Redis:
1. **Windows**: Download from https://github.com/microsoftarchive/redis/releases
2. **WSL**: Use `sudo apt install redis-server`
3. **Docker**: `docker run -d -p 6379:6379 redis:alpine`

### Verify Redis Installation:
```bash
# After installation
redis-cli ping
# Should return: PONG
```

### Test Redis Connection:
```powershell
# After Redis is running, test cache endpoints
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/stats" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 9. Troubleshooting

### Common Issues:

1. **Redis Connection Failed:**
   - Ensure Redis server is running
   - Check if port 6379 is available
   - Verify Redis configuration

2. **Database Connection Issues:**
   - Check PostgreSQL is running
   - Verify `.env` file configuration
   - Check connection pool settings

3. **Performance Issues:**
   - Monitor connection pool usage
   - Check database query performance
   - Verify indexes are applied

## 10. Expected Results (Without Redis)

After testing, you should see:
- ✅ Health checks working
- ✅ Resource monitoring active
- ✅ Connection pooling functional
- ✅ Core endpoints responding
- ✅ Database operations working
- ✅ Performance monitoring active
- ❌ Cache features disabled (until Redis is available)

---

**Note:** The advanced caching features will work once Redis is properly configured. For now, focus on testing the core functionality and connection pooling improvements.
