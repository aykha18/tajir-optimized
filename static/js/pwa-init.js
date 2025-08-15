// PWA Initialization Script
class PWAInitializer {
  constructor() {
    this.pwaManager = null;
    this.syncManager = null;
    this.offlineStorage = null;
    this.mobileNavigation = null;
    this.mobileBilling = null;
    this.isInitialized = false;
  }

  async init() {
    if (this.isInitialized) {
      return;
    }

    try {
      console.log('PWA Initializer: Starting initialization...');

      // Initialize offline storage
      this.offlineStorage = new OfflineStorage();
      await this.offlineStorage.init();

      // Initialize sync manager
      this.syncManager = new SyncManager();
      await this.syncManager.init();

      // Initialize PWA manager
      this.pwaManager = new PWAManager();
      this.pwaManager.setSyncManager(this.syncManager);
      await this.pwaManager.init();

      // Initialize Mobile Navigation (if on mobile)
      if (window.innerWidth <= 768) {
        this.mobileNavigation = new MobileNavigation();
        await this.mobileNavigation.init();
      }
      
      // Initialize Mobile Billing (always available for mobile toggle)
      try {
        this.mobileBilling = new MobileBilling();
        await this.mobileBilling.init();
        console.log('PWA Initializer: Mobile Billing initialized successfully');
      } catch (error) {
        console.error('PWA Initializer: Mobile Billing initialization failed', error);
        this.mobileBilling = null;
      }

      // Set up global PWA object
      window.TajirPWA = {
        pwaManager: this.pwaManager,
        syncManager: this.syncManager,
        offlineStorage: this.offlineStorage,
        mobileNavigation: this.mobileNavigation,
        mobileBilling: this.mobileBilling,
        getStatus: () => this.getStatus(),
        saveOfflineBill: (data) => this.syncManager.saveOfflineBill(data),
        saveOfflineCustomer: (data) => this.syncManager.saveOfflineCustomer(data),
        saveOfflineProduct: (data) => this.syncManager.saveOfflineProduct(data),
        loadOfflineData: () => this.syncManager.loadOfflineData(),
        getPendingSyncCount: () => this.syncManager.getPendingSyncCount(),
        promptInstall: () => this.pwaManager.promptInstall(),
        showNotification: (title, options) => this.pwaManager.showNotification(title, options),
        testMobileBillingSync: () => this.mobileBilling?.testSync()
      };

      // Initialize offline data loading
      await this.loadOfflineData();

      // Set up periodic sync
      this.setupPeriodicSync();

      this.isInitialized = true;
      console.log('PWA Initializer: Initialization completed successfully');

      // Dispatch initialization event
      window.dispatchEvent(new CustomEvent('pwaInitialized', {
        detail: { timestamp: Date.now() }
      }));

    } catch (error) {
      console.error('PWA Initializer: Initialization failed', error);
    }
  }

  async loadOfflineData() {
    try {
      const offlineData = await this.syncManager.loadOfflineData();
      
      // Store offline data in global scope for easy access
      window.offlineData = offlineData;
      
      console.log('PWA Initializer: Offline data loaded', {
        customers: offlineData.customers.length,
        products: offlineData.products.length,
        bills: offlineData.bills.length
      });
    } catch (error) {
      console.error('PWA Initializer: Failed to load offline data', error);
    }
  }

  setupPeriodicSync() {
    // Sync every 5 minutes when online
    setInterval(() => {
      if (navigator.onLine) {
        this.syncManager.syncPendingData();
      }
    }, 5 * 60 * 1000);

    // Register background sync if supported
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      this.syncManager.registerBackgroundSync();
    }
  }

  async getStatus() {
    const pwaStatus = await this.pwaManager.getPWAStatus();
    const syncStatus = await this.syncManager.getSyncStatus();
    
    return {
      ...pwaStatus,
      ...syncStatus,
      isInitialized: this.isInitialized,
      offlineDataCount: {
        customers: window.offlineData?.customers?.length || 0,
        products: window.offlineData?.products?.length || 0,
        bills: window.offlineData?.bills?.length || 0
      }
    };
  }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  // Load PWA modules
  await loadPWAModules();
  
  // Initialize PWA
  const pwaInitializer = new PWAInitializer();
  await pwaInitializer.init();
});

// Load PWA modules dynamically
async function loadPWAModules() {
  const modules = [
    '/static/js/modules/offline-storage.js',
    '/static/js/modules/sync-manager.js',
    '/static/js/modules/pwa-manager.js',
    '/static/js/modules/mobile-navigation.js',
    '/static/js/modules/mobile-billing.js'
  ];

  for (const module of modules) {
    try {
      await loadScript(module);
    } catch (error) {
      console.error(`Failed to load module: ${module}`, error);
    }
  }
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PWAInitializer;
} 