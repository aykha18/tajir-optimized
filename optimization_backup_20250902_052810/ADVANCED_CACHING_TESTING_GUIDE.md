# Advanced Caching Features Testing Guide

## Overview
This guide will help you test all the advanced caching features implemented in Step 10, including the CacheManager, tag-based invalidation, cache warming, and performance monitoring.

## Prerequisites
- Ensure your Flask app is running (`python app.py`)
- Redis server should be running
- PostgreSQL database should be accessible

## 1. Test Cache Statistics Endpoint

### Check Current Cache Performance
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/stats" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
  "cache_performance": {
    "hits": 0,
    "misses": 0,
    "hit_rate": 0.0,
    "invalidations": 0,
    "warmups": 0
  },
  "cache_size": {
    "memory_usage": "...",
    "total_keys": 0
  },
  "redis_status": "connected"
}
```

## 2. Test Cache Warming

### Warm Cache for All Data Types
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/warm" -Method POST -ContentType "application/json" -Body '{"cache_type": "all", "user_id": 1}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
  "message": "Cache warming completed",
  "warmed_caches": ["products", "dashboard", "customers"],
  "user_id": 1
}
```

### Warm Specific Cache Type
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/warm" -Method POST -ContentType "application/json" -Body '{"cache_type": "products", "user_id": 1}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 3. Test Cached Endpoints

### Test Products Aggregated (Should Use Cache)
```powershell
# First call - should cache miss
Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content

# Second call - should cache hit
Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test Dashboard Aggregated (Should Use Cache)
```powershell
# First call - should cache miss
Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/aggregated?user_id=1" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content

# Second call - should cache hit
Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/aggregated?user_id=1" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Test Customers Paginated (Should Use Cache)
```powershell
# First call - should cache miss
Invoke-WebRequest -Uri "http://localhost:5000/api/customers/paginated?user_id=1&page=1&per_page=10" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content

# Second call - should cache hit
Invoke-WebRequest -Uri "http://localhost:5000/api/customers/paginated?user_id=1&page=1&per_page=10" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 4. Check Cache Performance After Testing

### Monitor Cache Hit Rate
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/stats" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Changes:**
- `hits` should increase
- `misses` should show initial requests
- `hit_rate` should improve

## 5. Test Cache Invalidation

### Test Pattern-Based Invalidation
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/clear" -Method POST -ContentType "application/json" -Body '{"cache_type": "products", "user_id": 1}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
  "message": "Cache cleared successfully",
  "cleared_patterns": ["products:*", "catalog:*"],
  "user_id": 1
}
```

### Test Tag-Based Invalidation
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/clear" -Method POST -ContentType "application/json" -Body '{"cache_type": "dashboard", "user_id": 1}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 6. Test Cache Optimization

### Trigger Automatic Optimization
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/optimize" -Method POST -ContentType "application/json" -Body '{"user_id": 1}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
{
  "message": "Cache optimization completed",
  "actions_taken": ["cache_warming", "memory_cleanup"],
  "user_id": 1
}
```

## 7. Test Resource Monitoring

### Check Application Health
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

### Check Resource Usage
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

## 8. Test CRUD Operations with Cache Invalidation

### Add a Product (Should Invalidate Product Cache)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/products" -Method POST -ContentType "application/json" -Body '{"name": "Test Product", "price": 99.99, "user_id": 1}' -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Check Cache After Product Addition
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/cache/stats" -Method GET -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Changes:**
- `invalidations` should increase
- Product cache should be cleared

## 9. Performance Testing

### Test Response Times
```powershell
# Test uncached response time
$start = Get-Date
Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing | Out-Null
$uncached = (Get-Date) - $start

# Test cached response time
$start = Get-Date
Invoke-WebRequest -Uri "http://localhost:5000/api/products/aggregated?user_id=1" -Method GET -UseBasicParsing | Out-Null
$cached = (Get-Date) - $start

Write-Host "Uncached: $($uncached.TotalMilliseconds)ms"
Write-Host "Cached: $($cached.TotalMilliseconds)ms"
Write-Host "Improvement: $([math]::Round((($uncached - $cached) / $uncached) * 100, 2))%"
```

## 10. Browser Testing

### Test Frontend Integration
1. Open your browser and navigate to the products page
2. Open Developer Tools (F12) → Console
3. Refresh the page multiple times
4. Check console logs for cache-related messages
5. Monitor network tab for API calls

### Expected Behavior:
- First load: API call to `/api/products/aggregated`
- Subsequent loads: Should use cached data (faster response)
- After cache invalidation: Fresh API call

## 11. Redis CLI Testing (Optional)

### Connect to Redis
```bash
redis-cli
```

### Check Redis Keys
```redis
KEYS *
```

### Check Memory Usage
```redis
INFO memory
```

### Check Key Count
```redis
DBSIZE
```

## 12. Troubleshooting

### Common Issues:

1. **Redis Connection Failed:**
   - Ensure Redis server is running
   - Check Redis configuration in `app.py`

2. **Cache Not Working:**
   - Check browser console for errors
   - Verify Redis connection in `/api/monitor/health`
   - Check cache statistics in `/api/cache/stats`

3. **Performance Not Improving:**
   - Ensure you're testing the same endpoint multiple times
   - Check cache hit rate in statistics
   - Verify TTL settings in cache configuration

## 13. Expected Results

After testing, you should see:
- ✅ Cache hit rates improving with repeated requests
- ✅ Faster response times for cached data
- ✅ Automatic cache invalidation after CRUD operations
- ✅ Successful cache warming and optimization
- ✅ Resource monitoring showing connection pool usage
- ✅ Health checks confirming all services are running

## 14. Next Steps

Once you've verified all caching features are working:
1. Monitor performance in production
2. Adjust TTL values based on data freshness requirements
3. Configure cache warming schedules if needed
4. Set up alerts for cache performance metrics

---

**Note:** All endpoints should return proper JSON responses. If you encounter any errors, check the Flask console for detailed error messages and ensure all dependencies are properly configured.
