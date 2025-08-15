const CACHE_NAME = 'tajir-pos-v1.0.2';
const STATIC_CACHE = 'tajir-static-v1.0.2';
const DYNAMIC_CACHE = 'tajir-dynamic-v1.0.2';

const STATIC_ASSETS = [
  '/',
  '/app',
  '/static/css/main.css',
  '/static/css/animations.css',
  '/static/js/app.js',
  '/static/js/modules/billing-system.js',
  '/static/js/modules/customers.js',
  '/static/js/modules/products.js',
  '/static/js/modules/employees.js',
  '/static/js/modules/reports.js',
  '/static/js/modules/dashboard.js',
  '/static/js/modules/shop-settings.js',
  '/static/js/modules/vat.js',
  '/static/js/modules/plan-management.js',
  '/static/js/modules/product-types.js',
  '/static/js/modules/offline-storage.js',
  '/static/js/modules/sync-manager.js',
  '/static/js/modules/pwa-manager.js',
  '/static/js/pwa-init.js',
  '/static/manifest.json',
  '/static/icons/icon-72.png',
  '/static/icons/icon-96.png',
  '/static/icons/icon-128.png',
  '/static/icons/icon-144.png',
  '/static/icons/icon-152.png',
  '/static/icons/icon-192.png',
  '/static/icons/icon-384.png',
  '/static/icons/icon-512.png'
];

// Install event - cache static assets
self.addEventListener('install', event => {
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {

        // Cache files individually to handle failures gracefully
        const cachePromises = STATIC_ASSETS.map(url => {
          return cache.add(url).catch(error => {
            console.warn('Service Worker: Failed to cache', url, error);
            // Don't fail the entire installation if one file fails
            return Promise.resolve();
          });
        });
        return Promise.all(cachePromises);
      })
      .then(() => {
        
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
  
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // API calls - network first, cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Clone the response before using it
          const responseClone = response.clone();
          
          // Cache successful API responses
          if (response.ok) {
            caches.open(DYNAMIC_CACHE)
              .then(cache => cache.put(request, responseClone));
          }
          
          return response;
        })
        .catch(() => {
  
          return caches.match(request);
        })
    );
    return;
  }
  
  // Static assets - cache first, network fallback
  event.respondWith(
    caches.match(request)
      .then(response => {
        if (response) {
  
          return response;
        }
        

        return fetch(request)
          .then(response => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone the response before caching
            const responseToCache = response.clone();
            caches.open(DYNAMIC_CACHE)
              .then(cache => cache.put(request, responseToCache));
            
            return response;
          });
      })
  );
});

// Background sync for offline data
self.addEventListener('sync', event => {
  
  
  if (event.tag === 'sync-pending-data') {
    event.waitUntil(syncPendingData());
  }
});

// Push notification handling
self.addEventListener('push', event => {
  
  
  // Check if we have permission to show notifications
  if (Notification.permission !== 'granted') {
    
    return;
  }
  
  const options = {
    body: event.data ? event.data.text() : 'New notification from Tajir POS',
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View',
        icon: '/static/icons/icon-192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/icon-192.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Tajir POS', options)
      .catch(error => {
        console.error('Service Worker: Failed to show notification', error);
      })
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/app')
    );
  }
});

// Helper function to sync pending data
async function syncPendingData() {
  try {
    // This will be implemented with IndexedDB integration

    
    // Get all clients
    const clients = await self.clients.matchAll();
    
    // Notify clients about sync
    clients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETED',
        timestamp: Date.now()
      });
    });
  } catch (error) {
    console.error('Service Worker: Sync failed', error);
  }
}

// Message handling from main thread
self.addEventListener('message', event => {
  
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      version: CACHE_NAME,
      timestamp: Date.now()
    });
  }
}); 