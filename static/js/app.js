// Main Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
  lucide.createIcons();
  
  // Initialize plan management
  initializePlanManagement();

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
        } else if (btn.dataset.go === 'settingsSec') {
          // Settings/Backup functionality is disabled
          // if (window.loadBackupTable) {
          //   loadBackupTable();
          // }
        } else if (btn.dataset.go === 'shopSettingsSec') {
          initializeShopSettings();
        }
      }
    });
  });
}); 