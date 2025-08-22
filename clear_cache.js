// Clear Cache Script - Run this in browser console
console.log('🧹 Clearing all caches...');

// Clear all caches
async function clearAllCaches() {
    try {
        // Clear service worker caches
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            console.log('Found caches:', cacheNames);
            
            for (const cacheName of cacheNames) {
                await caches.delete(cacheName);
                console.log('✅ Deleted cache:', cacheName);
            }
        }
        
        // Unregister all service workers
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            console.log('Found service workers:', registrations.length);
            
            for (const registration of registrations) {
                await registration.unregister();
                console.log('✅ Unregistered service worker');
            }
        }
        
        // Clear localStorage and sessionStorage
        localStorage.clear();
        sessionStorage.clear();
        console.log('✅ Cleared localStorage and sessionStorage');
        
        // Clear IndexedDB
        if ('indexedDB' in window) {
            const databases = await indexedDB.databases();
            for (const db of databases) {
                indexedDB.deleteDatabase(db.name);
                console.log('✅ Deleted IndexedDB:', db.name);
            }
        }
        
        console.log('🎉 All caches cleared! Reloading page...');
        
        // Force reload the page
        setTimeout(() => {
            window.location.reload(true);
        }, 1000);
        
    } catch (error) {
        console.error('❌ Error clearing caches:', error);
    }
}

// Run the cache clearing
clearAllCaches();
