// Main Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Reset cache clearing flag on page load
  window.isClearingCache = false;
  
  lucide.createIcons();
  
  // Custom confirmation dialog function
  window.showConfirmDialog = function(message) {
    return new Promise((resolve) => {
      // Create modal overlay
      const overlay = document.createElement('div');
      overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
      overlay.id = 'confirmDialogOverlay';
      
      // Create dialog
      const dialog = document.createElement('div');
      dialog.className = 'bg-neutral-800 border border-neutral-700 rounded-lg p-6 max-w-md mx-4 shadow-xl';
      
      // Create content
      dialog.innerHTML = `
        <div class="flex items-start mb-4">
          <div class="flex-shrink-0">
            <svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-lg font-medium text-white">Confirm Action</h3>
            <p class="mt-2 text-sm text-neutral-300">${message}</p>
          </div>
        </div>
        <div class="flex justify-end space-x-3">
          <button id="confirmCancel" class="px-4 py-2 text-sm font-medium text-neutral-300 bg-neutral-700 border border-neutral-600 rounded-md hover:bg-neutral-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Cancel
          </button>
          <button id="confirmOk" class="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
            OK
          </button>
        </div>
      `;
      
      overlay.appendChild(dialog);
      document.body.appendChild(overlay);
      
      // Add event listeners
      const okBtn = document.getElementById('confirmOk');
      const cancelBtn = document.getElementById('confirmCancel');
      
      const cleanup = () => {
        document.body.removeChild(overlay);
      };
      
      okBtn.addEventListener('click', () => {
        cleanup();
        resolve(true);
      });
      
      cancelBtn.addEventListener('click', () => {
        cleanup();
        resolve(false);
      });
      
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          cleanup();
          resolve(false);
        }
      });
      
      // Focus on OK button for keyboard navigation
      okBtn.focus();
      
      // Handle Escape key
      const handleEscape = (e) => {
        if (e.key === 'Escape') {
          cleanup();
          resolve(false);
          document.removeEventListener('keydown', handleEscape);
        }
      };
      document.addEventListener('keydown', handleEscape);
    });
  };
  
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
          loadProductTypes();
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
}); 