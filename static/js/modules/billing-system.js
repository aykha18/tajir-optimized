// Billing System Module - v1.0.3
// Entry point for Billing System initialization.
// Most logic has been modularized into:
// - modules/billing/config.js
// - modules/billing/ui.js
// - modules/billing/customer.js
// - modules/billing/items.js
// - modules/billing/totals.js
// - modules/billing/actions.js
// - modules/billing/vat-listeners.js
// - modules/billing/master-autocomplete.js
// - modules/billing/search-reprint.js

// Global variables
window.bill = []; // Primary declaration of 'bill'
var bill = window.bill; // Local alias for compatibility

let currentBillNumber = '';
let selectedMasterId = null;

function initializeBillingSystem() {
  // Initialize billing system components in dependency order

  loadBillingConfiguration(); // Load billing configuration first
  
  // Customer Module Initialization
  if (window.BillingCustomer) {
      if (window.BillingCustomer.setupMobileFetch) window.BillingCustomer.setupMobileFetch();
      if (window.BillingCustomer.setupTypeHandler) window.BillingCustomer.setupTypeHandler();
      if (window.BillingCustomer.loadRecent) window.BillingCustomer.loadRecent();
      if (window.BillingCustomer.initMobileRecent) window.BillingCustomer.initMobileRecent();
      if (window.BillingCustomer.setupCityArea) window.BillingCustomer.setupCityArea();
      if (window.BillingCustomer.setupQuickSearch) window.BillingCustomer.setupQuickSearch();
  }

  // Master Autocomplete Initialization
  if (window.MasterAutocomplete && window.MasterAutocomplete.init) {
    window.MasterAutocomplete.init();
  }

  // Items Module Initialization
  if (window.BillingItems) {
      if (window.BillingItems.setupAddItemHandler) window.BillingItems.setupAddItemHandler();
      if (window.BillingItems.setupProductQuickAdd) window.BillingItems.setupProductQuickAdd();
  }

  // Totals Module Initialization
  if (window.BillingTotals && window.BillingTotals.setupTotalAdvanceDistribution) {
    window.BillingTotals.setupTotalAdvanceDistribution();
  }

  // Search & Reprint Initialization
  if (window.SearchReprint && window.SearchReprint.init) {
    window.SearchReprint.init();
  }

  // Config Module Initialization
  if (window.BillingConfig) {
      if (window.BillingConfig.setupSmartDefaults) window.BillingConfig.setupSmartDefaults();
      if (window.BillingConfig.initializePaymentMode) window.BillingConfig.initializePaymentMode();
  }

  // UI Module Initialization
  if (window.BillingUI && window.BillingUI.setupMobileBillingToggle) {
      window.BillingUI.setupMobileBillingToggle();
  }

  // Actions Module Initialization
  if (window.BillingActions) {
    if (window.BillingActions.initializePrintButton) window.BillingActions.initializePrintButton();
    window.BillingActions.initializeSaveBill();
    window.BillingActions.initializeWhatsApp();
  } else {
    console.warn('BillingActions module not found');
  }

  // VAT Initialization
  if (window.initVatConfig) {
    window.initVatConfig();
  }

  // VAT Listeners Initialization
  if (window.VATListeners && window.VATListeners.setup) {
    window.VATListeners.setup();
  }

  // Expose functions globally for legacy compatibility
  window.initializeBillingSystem = initializeBillingSystem;
  window.bill = bill; 
}


// Loyalty helpers inside module scope


// Loyalty helpers moved to modules/billing/customer.js



// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', async () => {
    try {
      // First, load billing configuration
      await loadBillingConfiguration();

      // Apply configuration to show/hide fields
      applyBillingConfiguration();

      // Then call the original initialization
      initializeBillingSystem();
      // Attach VAT listeners
      try { if (window.VATListeners && window.VATListeners.setup) window.VATListeners.setup(); } catch (e) { }
    } catch (error) {
      console.error('Error in async billing initialization:', error);
      // Fallback to original initialization
      initializeBillingSystem();
      try { if (window.VATListeners && window.VATListeners.setup) window.VATListeners.setup(); } catch (e) { }
    }
  });
} else {
  // DOM is already loaded, run async initialization
  (async () => {
    try {
      // First, load billing configuration
      await loadBillingConfiguration();

      // Apply configuration to show/hide fields
      applyBillingConfiguration();

      // Then call the original initialization
      initializeBillingSystem();
      try { if (window.VATListeners && window.VATListeners.setup) window.VATListeners.setup(); } catch (e) { }
    } catch (error) {
      console.error('Error in async billing initialization:', error);
      // Fallback to original initialization
      initializeBillingSystem();
      try { if (window.VATListeners && window.VATListeners.setup) window.VATListeners.setup(); } catch (e) { }
    }
  })();
}

// VAT Functions - Global Scope - Moved to modules/billing/vat-listeners.js
/* Function recalcAllItemsForCurrentVat moved to module */

/* Function attachVatChangeListeners moved to module (as VATListeners.setup) */

/* Function testVatEventListeners removed (not needed) */

// Make VAT functions globally available
if (window.VATListeners && window.VATListeners.recalcAllItemsForCurrentVat) {
    window.recalcAllItemsForCurrentVat = window.VATListeners.recalcAllItemsForCurrentVat;
}
if (window.VATListeners && window.VATListeners.setup) {
    window.attachVatChangeListeners = window.VATListeners.setup;
}

