// Main Application JavaScript
// Global log silencer for production
(() => {
  try {
    const hostname = typeof window !== 'undefined' ? window.location.hostname : '';
    const isProd = /railway|tajirtech|tajir\.up\.railway\.app|up\.railway\.app/i.test(hostname);
    if (isProd && typeof console !== 'undefined') {
      const originalError = console.error ? console.error.bind(console) : () => {};
      // Silence noisy logs in production, keep errors
      console.log = () => {};
      console.info = () => {};
      console.debug = () => {};
      console.warn = () => {};
      console.error = originalError;
    }
  } catch (_) {
    // fail safe: do nothing
  }
})();

document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 DOM Content Loaded');
  console.log('📦 Available modules:', {
    loadProductTypes: typeof window.loadProductTypes,
    setupProductTypeFormHandler: typeof window.setupProductTypeFormHandler,
    setupProductTypeListHandlers: typeof window.setupProductTypeListHandlers
  });
  
  // Reset cache clearing flag on page load
  window.isClearingCache = false;
  
  // Safe lucide icon creation with fallback
  try {
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
      lucide.createIcons();
    } else {
      console.warn('Lucide library not available, using fallback icons');
    }
  } catch (lucideError) {
    console.warn('Error creating lucide icons:', lucideError);
  }
  
    // Custom confirmation dialog function - removed to avoid conflicts with expenses.js
  
  // Initialize plan management
  initializePlanManagement();

  // Initialize cache clearing functionality
  initializeCacheClearing();

  // Navigation functionality
  const navBtns = document.querySelectorAll('.nav-btn');
  const pages = document.querySelectorAll('.page');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Check if button is disabled
      if (btn.disabled) {
        return; // Don't process disabled buttons
      }
      
      // Remove active class from all buttons
      navBtns.forEach(b => b.classList.remove('bg-neutral-700', 'ring-2', 'ring-indigo-500/60'));
      // Add active class to clicked button
      btn.classList.add('bg-neutral-700', 'ring-2', 'ring-indigo-500/60');

      // Hide all pages
      pages.forEach(p => p.classList.add('hidden'));

      // Show target page
      const targetPage = document.getElementById(btn.dataset.go);
      if (targetPage) {
        targetPage.classList.remove('hidden');
        // Update page title
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
          const h3 = targetPage.querySelector('h3');
          if (h3) {
            pageTitle.textContent = h3.textContent;
          } else {
            // Fallback: use button text or derive from section ID
            pageTitle.textContent = btn.textContent.trim() || btn.dataset.go.replace('Sec', '').replace(/([A-Z])/g, ' $1').trim();
          }
        }
        
        // Load data for specific sections
        if (btn.dataset.go === 'customerSec') {
          loadCustomers();
        } else if (btn.dataset.go === 'productTypeSec') {
          console.log('🔄 Loading product types section...');
          if (window.loadProductTypes) {
            loadProductTypes();
          } else {
            console.error('❌ loadProductTypes function not found!');
          }
        } else if (btn.dataset.go === 'productSec') {
          loadProducts();
        } else if (btn.dataset.go === 'employeeSec') {
          loadEmployees();
        } else if (btn.dataset.go === 'vatSec') {
          loadVatRates();
        } else if (btn.dataset.go === 'billingSec') {
          initializeBillingSystem();
        } else if (btn.dataset.go === 'dashSec') {
          // Dashboard will be loaded when accessed
          if (window.createRevenueChart) {
            createRevenueChart();
            createRegionsChart();
            createTrendingProductsChart();
            createRepeatedCustomersChart();
            createEmployeeBarChart();
            createEmployeePieChart();
          }
        } else if (btn.dataset.go === 'advancedReportsSec') {
          initializeReports();

        } else if (btn.dataset.go === 'shopSettingsSec') {
          // Ensure the section is visible
          if (targetPage) {
            targetPage.classList.remove('hidden');
          }
          // Check if initializeShopSettings function exists
          if (typeof initializeShopSettings === 'function') {
            initializeShopSettings();
          } else {
            console.error('initializeShopSettings function not found');
          }
        }
      }
    });
  });

  // Cache clearing functionality
  function initializeCacheClearing() {
    const clearCacheBtn = document.getElementById('clearCacheBtn');
    
    if (clearCacheBtn && !clearCacheBtn.hasAttribute('data-cache-initialized')) {
      // Mark as initialized to prevent duplicate event listeners
      clearCacheBtn.setAttribute('data-cache-initialized', 'true');
      
      clearCacheBtn.addEventListener('click', async () => {
        // Show confirmation dialog using custom notification
        const confirmed = await showConfirmDialog('Are you sure you want to clear all app cache? This will remove all stored data and may require you to log in again.');
        
        if (confirmed) {
          try {
            // Set a flag to prevent double refresh
            window.isClearingCache = true;
            
            // Add a small delay to ensure the flag is set before any service worker events
            await new Promise(resolve => setTimeout(resolve, 100));
            
            await clearAllCache();
            
            // Show success notification
            if (window.showSimpleToast) {
              window.showSimpleToast('Cache cleared successfully! The app will refresh in 3 seconds.', 'success');
            } else {
              // Fallback to mobile notification if available
              if (window.TajirPWA && window.TajirPWA.mobileNavigation) {
                window.TajirPWA.mobileNavigation.showMobileNotification('Cache cleared successfully! The app will refresh in 3 seconds.', 'success');
              }
            }
            
            setTimeout(() => {
              // Reset the flag before reloading
              window.isClearingCache = false;
              window.location.reload();
            }, 3000);
          } catch (error) {
            console.error('Error clearing cache:', error);
            
            // Show error notification
            if (window.showSimpleToast) {
              window.showSimpleToast('Error clearing cache. Please try again.', 'error');
            } else {
              // Fallback to mobile notification if available
              if (window.TajirPWA && window.TajirPWA.mobileNavigation) {
                window.TajirPWA.mobileNavigation.showMobileNotification('Error clearing cache. Please try again.', 'error');
              }
            }
            window.isClearingCache = false;
          }
        }
      });
    }
  }

  async function clearAllCache() {

    
    // Clear localStorage
    try {
      localStorage.clear();

    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }

    // Clear sessionStorage
    try {
      sessionStorage.clear();

    } catch (error) {
      console.error('Error clearing sessionStorage:', error);
    }

    // Clear IndexedDB (if OfflineStorage is available)
    try {
      if (window.TajirPWA && window.TajirPWA.offlineStorage) {
        const stores = ['customers', 'products', 'bills', 'pending_sync', 'settings'];
        for (const storeName of stores) {
          await window.TajirPWA.offlineStorage.clearStore(storeName);
        }
  
      }
    } catch (error) {
      console.error('Error clearing IndexedDB:', error);
    }

    // Clear service worker cache
    try {
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        );
  
      }
    } catch (error) {
      console.error('Error clearing service worker cache:', error);
    }

    // Unregister service worker (skip during manual cache clear to prevent double refresh)
    try {
      if ('serviceWorker' in navigator) {
        if (window.isClearingCache) {
  
        } else {
          const registrations = await navigator.serviceWorker.getRegistrations();
          await Promise.all(
            registrations.map(registration => registration.unregister())
          );

        }
      }
    } catch (error) {
      console.error('Error unregistering service worker:', error);
    }


  }

  // Navigation function for Upcoming Features
  window.navigateToUpcomingFeatures = function() {
    // Navigate to upcoming features section
    const upcomingFeaturesSec = document.getElementById('upcomingFeaturesSec');
    if (upcomingFeaturesSec) {
      upcomingFeaturesSec.scrollIntoView({ behavior: 'smooth' });
    } else {
      // If section doesn't exist, show a notification
      if (window.showSimpleToast) {
        window.showSimpleToast('Upcoming Features section not found', 'info');
      }
    }
  };
}); 