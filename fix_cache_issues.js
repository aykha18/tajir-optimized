// Comprehensive Cache Clearing Script
// Run this in browser console to fix all caching issues

console.log('🔧 Starting comprehensive cache fix...');

async function fixAllCacheIssues() {
    try {
        console.log('Step 1: Unregistering all Service Workers...');
        
        // Unregister all service workers
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            console.log(`Found ${registrations.length} service workers to unregister`);
            
            for (const registration of registrations) {
                await registration.unregister();
                console.log('✅ Unregistered service worker');
            }
        }
        
        console.log('Step 2: Clearing all caches...');
        
        // Clear all caches
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            console.log(`Found ${cacheNames.length} caches to clear:`, cacheNames);
            
            for (const cacheName of cacheNames) {
                await caches.delete(cacheName);
                console.log(`✅ Deleted cache: ${cacheName}`);
            }
        }
        
        console.log('Step 3: Clearing storage...');
        
        // Clear localStorage and sessionStorage
        localStorage.clear();
        sessionStorage.clear();
        console.log('✅ Cleared localStorage and sessionStorage');
        
        console.log('Step 4: Clearing IndexedDB...');
        
        // Clear IndexedDB
        if ('indexedDB' in window) {
            try {
                const databases = await indexedDB.databases();
                for (const db of databases) {
                    indexedDB.deleteDatabase(db.name);
                    console.log(`✅ Deleted IndexedDB: ${db.name}`);
                }
            } catch (error) {
                console.log('⚠️ IndexedDB clearing failed (this is normal):', error.message);
            }
        }
        
        console.log('Step 5: Setting cache-busting flag...');
        
        // Set a flag to prevent immediate reload
        window.isClearingCache = true;
        
        console.log('🎉 All caches cleared successfully!');
        console.log('🔄 Reloading page in 2 seconds...');
        
        // Force reload after a delay
        setTimeout(() => {
            window.isClearingCache = false;
            window.location.reload(true);
        }, 2000);
        
    } catch (error) {
        console.error('❌ Error during cache clearing:', error);
        console.log('🔄 Attempting page reload anyway...');
        setTimeout(() => {
            window.location.reload(true);
        }, 1000);
    }
}

// Run the fix
fixAllCacheIssues();
