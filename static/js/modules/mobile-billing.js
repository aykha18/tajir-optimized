/**
 * Mobile Billing Module for Tajir POS PWA
 * Provides touch-friendly billing interface optimized for mobile devices
 */

// Prevent multiple declarations
if (typeof window.MobileBilling === 'undefined') {
  window.MobileBilling = class MobileBilling {
  constructor() {
    this.currentBill = {
      items: [],
      customer: null,
      total: 0,
      tax: 0,
      discount: 0,
      finalTotal: 0
    };
    this.isInitialized = false;
    this.mobileNavigation = null;
    // Tracks if the user modified the mobile bill after opening
    this.mobileBillDirty = false;
  }

  async init() {
    try {
  
      
      this.setupMobileBillingInterface();
      this.setupTouchGestures();
      this.setupMobileOptimizations();
      this.loadOfflineProducts();
      
      
      this.isInitialized = true;
      
      // Dispatch initialization event
      window.dispatchEvent(new CustomEvent('mobileBillingInitialized', {
        detail: { timestamp: Date.now() }
      }));
      
    } catch (error) {
      console.error('Mobile Billing: Initialization failed', error);
      throw error; // Re-throw to let caller know about the error
    }
  }

  setupMobileBillingInterface() {
    // Create mobile billing container
    const billingContainer = document.createElement('div');
    billingContainer.id = 'mobile-billing-container';
    billingContainer.className = 'container-mobile';
    billingContainer.innerHTML = `
      <div class="section-mobile">
        <div class="card-mobile">
          <div class="card-mobile-header">
            <h2 class="text-lg font-semibold">Quick Billing</h2>
            <button id="close-mobile-billing" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div class="card-mobile-body">
            <!-- Product Search -->
            <div class="search-mobile">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <input type="text" id="mobile-product-search" placeholder="Search products..." class="input-mobile">
            </div>
            
            <!-- Product Grid -->
            <div id="mobile-product-grid" class="grid grid-cols-2 gap-4 mb-6">
              <!-- Products will be loaded here -->
            </div>
            
            <!-- Current Bill -->
            <div class="card-mobile">
              <div class="card-mobile-header">
                <h3 class="text-md font-semibold">Current Bill</h3>
                <button id="clear-mobile-bill" class="text-red-500 text-sm">Clear</button>
              </div>
              <div class="card-mobile-body">
                <div id="mobile-bill-items" class="list-mobile">
                  <!-- Bill items will be shown here -->
                </div>
                
                <!-- Bill Summary -->
                <div class="bill-summary-mobile">
                  <div class="bill-summary-row-mobile">
                    <span class="bill-summary-label">Subtotal:</span>
                                         <span class="bill-summary-value" id="mobile-subtotal">0.00</span>
                   </div>
                   <div class="bill-summary-row-mobile">
                     <span class="bill-summary-label">Tax (5%):</span>
                     <span class="bill-summary-value" id="mobile-tax-amount">0.00</span>
                   </div>
                   <div class="bill-summary-row-mobile">
                     <span class="bill-summary-label">Discount:</span>
                     <span class="bill-summary-value" id="mobile-discount-amount">0.00</span>
                   </div>
                   <div class="bill-summary-row-mobile">
                     <span class="bill-summary-label">Total:</span>
                     <span class="bill-summary-total" id="mobile-final-total">0.00</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="billing-actions-mobile">
              <button id="mobile-process-bill-btn" class="billing-action-btn primary">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Process Bill
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Add to body but hide initially
    billingContainer.style.display = 'none';
    
    document.body.appendChild(billingContainer);
    
    // Setup event listeners for mobile billing
    this.setupMobileBillingEvents();
  }

  setupEventListeners() {
    // Product search
    const searchInput = document.getElementById('product-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filterProducts(e.target.value);
      });
    }

    // Clear bill button
    const clearBtn = document.getElementById('clear-bill-btn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.clearBill();
      });
    }

    // Process bill button
    const processBtn = document.getElementById('process-bill-btn');
    if (processBtn) {
      processBtn.addEventListener('click', () => {
        this.processBill();
      });
    }
  }

  setupTouchGestures() {
    // Swipe to remove items from bill
    const billItems = document.getElementById('bill-items');
    if (billItems) {
      billItems.addEventListener('touchstart', (e) => {
        const item = e.target.closest('.list-item-mobile');
        if (item) {
          item.dataset.touchStart = e.touches[0].clientX;
        }
      });

      billItems.addEventListener('touchend', (e) => {
        const item = e.target.closest('.list-item-mobile');
        if (item && item.dataset.touchStart) {
          const touchEnd = e.changedTouches[0].clientX;
          const touchStart = parseInt(item.dataset.touchStart);
          const diff = touchStart - touchEnd;

          if (Math.abs(diff) > 50) {
            // Swipe detected - remove item
            this.removeItemFromBill(item.dataset.productId);
          }
        }
      });
    }
  }

  setupMobileBillingEvents() {
    const container = document.getElementById('mobile-billing-container');
    if (!container) return;

    // Close button
    const closeBtn = container.querySelector('#close-mobile-billing');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        this.hideMobileBilling();
      });
    }

    // Product search
    const searchInput = container.querySelector('#mobile-product-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filterMobileProducts(e.target.value);
      });
    }

    // Clear bill button
    const clearBtn = container.querySelector('#clear-mobile-bill');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.clearMobileBill();
      });
    }

    // Process bill button
    const processBtn = container.querySelector('#mobile-process-bill-btn');
    if (processBtn) {
      processBtn.addEventListener('click', () => {
        this.processMobileBill();
      });
    }
  }

  showMobileBilling() {
    const container = document.getElementById('mobile-billing-container');
    if (container) {
      container.style.display = 'block';
      container.classList.add('fade-in-mobile');
      
      // Sync data from main billing system when opening
      this.syncFromMainBilling();
      
      // Load products if not already loaded
      this.loadMobileProducts();
      
      // Focus on search input
      const searchInput = container.querySelector('#mobile-product-search');
      if (searchInput) {
        setTimeout(() => searchInput.focus(), 300);
      }
    }
  }

  hideMobileBilling() {
    const container = document.getElementById('mobile-billing-container');
    if (container) {
      // Sync mobile bill data to main billing system before hiding
      this.syncToMainBilling();
      
      // Clear the mobile bill after syncing
      this.clearMobileBill();
      
      container.classList.add('slide-up-mobile');
      setTimeout(() => {
        container.style.display = 'none';
        container.classList.remove('slide-up-mobile');
      }, 300);
    }
  }

  // Sync mobile bill data to main billing system
  syncToMainBilling() {
    // Avoid duplicating when user didn't change anything
    if (!this.mobileBillDirty || this.currentBill.items.length === 0) {
  
      return;
    }
    
    try {
      
      
      // Get the main billing system's bill array
      const mainBill = window.bill || [];
      
      
      // Convert mobile bill items to main billing format
      const convertedItems = this.currentBill.items.map(item => ({
        product_id: item.product_id,
        product_name: item.product_name,
        quantity: item.quantity,
        price: item.price,
        discount: 0, // Default discount
        advance: 0, // Default advance
        vat_percent: 5, // Default VAT
        vat_amount: item.total * 0.05, // Calculate VAT
        subtotal: item.total, // Before discount
        total: item.total // After discount
      }));
      
      
      
      // Add items to main bill array
      convertedItems.forEach(item => {
        // Check if product already exists in main bill
        const existingIndex = mainBill.findIndex(billItem => 
          billItem.product_id === item.product_id
        );
        
        if (existingIndex !== -1) {
          // Update existing item quantity
          mainBill[existingIndex].quantity += item.quantity;
          mainBill[existingIndex].total = mainBill[existingIndex].quantity * mainBill[existingIndex].price;
          mainBill[existingIndex].vat_amount = mainBill[existingIndex].total * 0.05;

        } else {
          // Add new item
          mainBill.push(item);

        }
      });
      
      
      
      // Update main billing display
      if (typeof window.renderBillTable === 'function') {
        window.renderBillTable();

      }
      if (typeof window.updateTotals === 'function') {
        window.updateTotals();

      }
      
      // Show success notification
      this.showMobileNotification(`${this.currentBill.items.length} items transferred to main billing`, 'success');
      
      // Clear mobile bill after successful sync
      this.clearMobileBill();
      // Reset dirty flag
      this.mobileBillDirty = false;
      
    } catch (error) {
      console.error('Error syncing mobile bill to main billing:', error);
      this.showMobileNotification('Failed to sync bill data', 'error');
    }
  }

  // Sync main billing data to mobile billing
  syncFromMainBilling() {
    try {
      const mainBill = window.bill || [];
      
      if (mainBill.length === 0) {
        // Clear mobile bill if main bill is empty
        this.currentBill.items = [];
        this.updateMobileBillDisplay();
        this.calculateMobileTotals();
        this.mobileBillDirty = false;

        return;
      }
      
      // Convert main bill items to mobile format
      const mobileItems = mainBill.map(item => ({
        product_id: item.product_id,
        product_name: item.product_name,
        price: item.price,
        quantity: item.quantity,
        total: item.total
      }));
      

      
      // Update mobile bill
      this.currentBill.items = mobileItems;
      this.updateMobileBillDisplay();
      this.calculateMobileTotals();
      // Just mirrored from main; not dirty yet
      this.mobileBillDirty = false;
      

      
    } catch (error) {
      console.error('Error syncing from main billing:', error);
    }
  }

  setupMobileOptimizations() {
    // Prevent zoom on input focus
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      input.addEventListener('focus', () => {
        input.style.fontSize = '16px';
      });
    });

    // Add touch feedback to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
      button.addEventListener('touchstart', () => {
        button.style.transform = 'scale(0.95)';
      });
      
      button.addEventListener('touchend', () => {
        button.style.transform = 'scale(1)';
      });
    });
  }

  async loadOfflineProducts() {
    try {
      // Load products from offline storage
      const products = window.offlineData?.products || [];
      this.displayProducts(products);
    } catch (error) {
      console.error('Mobile Billing: Failed to load products', error);
    }
  }

  async loadMobileProducts() {
    try {
      const response = await fetch('/api/products');
      const products = await response.json();
      this.displayMobileProducts(products);
    } catch (error) {
      console.error('Error loading mobile products:', error);
      this.showMobileNotification('Failed to load products', 'error');
    }
  }

  displayProducts(products) {
    const productGrid = document.getElementById('product-grid');
    if (!productGrid) return;

    productGrid.innerHTML = products.map(product => `
      <div class="card-mobile cursor-pointer" data-product-id="${product.product_id}">
        <div class="card-mobile-body text-center">
          <div class="text-lg font-semibold mb-2">${product.product_name}</div>
          <div class="text-sm text-gray-600 mb-2">${product.product_type || 'General'}</div>
          <div class="text-lg font-bold text-blue-600">AED ${product.price}</div>
          <button class="btn-primary-mobile w-full mt-2" onclick="window.TajirPWA.mobileBilling.addToBill(${product.product_id})">
            Add to Bill
          </button>
        </div>
      </div>
    `).join('');
  }

  displayMobileProducts(products) {
    const grid = document.getElementById('mobile-product-grid');
    if (!grid) return;

    grid.innerHTML = products.map(product => `
      <div class="product-card-mobile" data-product-id="${product.product_id}" data-product-name="${product.product_name}" data-product-price="${product.rate}">
        <div class="product-card-content">
          <div class="product-name">${product.product_name}</div>
          <div class="product-type">${product.type_name || ''}</div>
                     <div class="product-price">${product.rate}</div>
        </div>
        <button class="add-to-bill-btn" onclick="window.TajirPWA.mobileBilling.addToMobileBill(${product.product_id})">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
        </button>
      </div>
    `).join('');
  }

  filterProducts(searchTerm) {
    const products = window.offlineData?.products || [];
    const filtered = products.filter(product => 
      product.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.product_type?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    this.displayProducts(filtered);
  }

  filterMobileProducts(searchTerm) {
    const productCards = document.querySelectorAll('.product-card-mobile');
    const searchLower = searchTerm.toLowerCase();

    productCards.forEach(card => {
      const productName = card.getAttribute('data-product-name').toLowerCase();
      const productType = card.querySelector('.product-type').textContent.toLowerCase();
      
      if (productName.includes(searchLower) || productType.includes(searchLower)) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }

  addToBill(productId) {
    const products = window.offlineData?.products || [];
    const product = products.find(p => p.product_id === productId);
    
    if (!product) return;

    // Check if product already in bill
    const existingItem = this.currentBill.items.find(item => item.product_id === productId);
    
    if (existingItem) {
      existingItem.quantity += 1;
      existingItem.total = existingItem.quantity * existingItem.price;
    } else {
      this.currentBill.items.push({
        product_id: product.product_id,
        product_name: product.product_name,
        price: product.price,
        quantity: 1,
        total: product.price
      });
    }

    this.updateBillDisplay();
    this.calculateTotals();
    // Mark as modified
    this.mobileBillDirty = true;
    
    // Show success feedback
    this.showMobileNotification(`${product.product_name} added to bill`, 'success');
  }

  addToMobileBill(productId) {
    const productCard = document.querySelector(`[data-product-id="${productId}"]`);
    if (!productCard) return;

    const productName = productCard.getAttribute('data-product-name');
    const productPrice = parseFloat(productCard.getAttribute('data-product-price'));

    // Check if product already in bill
    const existingItem = this.currentBill.items.find(item => item.product_id === productId);
    
    if (existingItem) {
      existingItem.quantity += 1;
      existingItem.total = existingItem.quantity * existingItem.price;
    } else {
      this.currentBill.items.push({
        product_id: productId,
        product_name: productName,
        price: productPrice,
        quantity: 1,
        total: productPrice
      });
    }

    this.updateMobileBillDisplay();
    this.calculateMobileTotals();
    // Mark as modified
    this.mobileBillDirty = true;
    
    // Show success feedback
    this.showMobileNotification(`${productName} added to bill`, 'success');
    
    // Add visual feedback to the product card
    productCard.classList.add('added-to-bill');
    setTimeout(() => {
      productCard.classList.remove('added-to-bill');
    }, 1000);
  }

  removeItemFromBill(productId) {
    this.currentBill.items = this.currentBill.items.filter(item => item.product_id !== productId);
    this.updateBillDisplay();
    this.calculateTotals();
  }

  updateBillDisplay() {
    const billItems = document.getElementById('bill-items');
    if (!billItems) return;

    if (this.currentBill.items.length === 0) {
      billItems.innerHTML = '<div class="text-center text-gray-500 py-8">No items in bill</div>';
      return;
    }

    billItems.innerHTML = this.currentBill.items.map(item => `
      <div class="list-item-mobile" data-product-id="${item.product_id}">
        <div class="flex-1">
          <div class="font-semibold">${item.product_name}</div>
          <div class="text-sm text-gray-600">${item.price} x ${item.quantity}</div>
        </div>
        <div class="text-right">
          <div class="font-bold">${item.total.toFixed(2)}</div>
          <button class="text-red-500 text-sm" onclick="window.TajirPWA.mobileBilling.removeItemFromBill(${item.product_id})">
            Remove
          </button>
        </div>
      </div>
    `).join('');
  }

  updateMobileBillDisplay() {
    const billItems = document.getElementById('mobile-bill-items');
    if (!billItems) return;

    if (this.currentBill.items.length === 0) {
      billItems.innerHTML = '<div class="text-center text-gray-500 py-8">No items in bill</div>';
      return;
    }

    billItems.innerHTML = this.currentBill.items.map(item => `
      <div class="list-item-mobile" data-product-id="${item.product_id}">
        <div class="flex-1">
          <div class="font-semibold">${item.product_name}</div>
          <div class="text-sm text-gray-600">${item.price} x ${item.quantity}</div>
        </div>
        <div class="text-right">
          <div class="font-bold">${item.total.toFixed(2)}</div>
          <button class="remove-item-btn-mobile" onclick="window.TajirPWA.mobileBilling.removeFromMobileBill(${item.product_id})">
            Remove
          </button>
        </div>
      </div>
    `).join('');
  }

  removeFromMobileBill(productId) {
    this.currentBill.items = this.currentBill.items.filter(item => item.product_id !== productId);
    this.updateMobileBillDisplay();
    this.calculateMobileTotals();
    this.mobileBillDirty = true;
    this.showMobileNotification('Item removed from bill', 'info');
  }

  calculateTotals() {
    const subtotal = this.currentBill.items.reduce((sum, item) => sum + item.total, 0);
    const tax = subtotal * 0.05; // 5% tax
    const discount = this.currentBill.discount || 0;
    const finalTotal = subtotal + tax - discount;

    this.currentBill.subtotal = subtotal;
    this.currentBill.tax = tax;
    this.currentBill.finalTotal = finalTotal;

    // Update display
    document.getElementById('subtotal').textContent = `${subtotal.toFixed(2)}`;
    document.getElementById('tax-amount').textContent = `${tax.toFixed(2)}`;
    document.getElementById('discount-amount').textContent = `${discount.toFixed(2)}`;
    document.getElementById('final-total').textContent = `${finalTotal.toFixed(2)}`;
  }

  calculateMobileTotals() {
    const subtotal = this.currentBill.items.reduce((sum, item) => sum + item.total, 0);
    const tax = subtotal * 0.05; // 5% tax
    const discount = this.currentBill.discount || 0;
    const finalTotal = subtotal + tax - discount;

    this.currentBill.subtotal = subtotal;
    this.currentBill.tax = tax;
    this.currentBill.finalTotal = finalTotal;

    // Update display
    document.getElementById('mobile-subtotal').textContent = `${subtotal.toFixed(2)}`;
    document.getElementById('mobile-tax-amount').textContent = `${tax.toFixed(2)}`;
    document.getElementById('mobile-discount-amount').textContent = `${discount.toFixed(2)}`;
    document.getElementById('mobile-final-total').textContent = `${finalTotal.toFixed(2)}`;
  }

  clearBill() {
    this.currentBill = {
      items: [],
      customer: null,
      total: 0,
      tax: 0,
      discount: 0,
      finalTotal: 0
    };
    this.updateBillDisplay();
    this.calculateTotals();
    this.showMobileNotification('Bill cleared', 'info');
  }

  clearMobileBill() {
    this.currentBill = {
      items: [],
      customer: null,
      total: 0,
      tax: 0,
      discount: 0,
      finalTotal: 0
    };
    this.updateMobileBillDisplay();
    this.calculateMobileTotals();
    this.mobileBillDirty = false;
    // Removed notification to prevent "Bill Cleared" message
  }

  async processBill() {
    if (this.currentBill.items.length === 0) {
      this.showMobileNotification('Please add items to the bill first', 'error');
      return;
    }

    try {
      // Save bill to offline storage
      const billData = {
        bill_id: Date.now(),
        items: this.currentBill.items,
        subtotal: this.currentBill.subtotal,
        tax: this.currentBill.tax,
        discount: this.currentBill.discount,
        final_total: this.currentBill.finalTotal,
        created_at: new Date().toISOString(),
        status: 'pending'
      };

      // Save to offline storage
      if (window.TajirPWA && window.TajirPWA.saveOfflineBill) {
        await window.TajirPWA.saveOfflineBill(billData);
      }

      // Show success message
      this.showMobileNotification('Bill processed successfully!', 'success');
      
      // Clear bill
      this.clearBill();
      
      // Print receipt (if printer available)
      this.printReceipt(billData);
      
    } catch (error) {
      console.error('Mobile Billing: Failed to process bill', error);
      this.showMobileNotification('Failed to process bill', 'error');
    }
  }

  async processMobileBill() {
    if (this.currentBill.items.length === 0) {
      this.showMobileNotification('Please add items to the bill first', 'error');
      return;
    }

    try {
      // Save bill to offline storage
      const billData = {
        bill_id: Date.now(), // Add the required bill_id for IndexedDB
        items: this.currentBill.items,
        subtotal: this.currentBill.subtotal,
        tax: this.currentBill.tax,
        total: this.currentBill.finalTotal,
        timestamp: Date.now(),
        status: 'pending'
      };

      // Save to offline storage
      if (window.TajirPWA && window.TajirPWA.offlineStorage) {
        await window.TajirPWA.offlineStorage.saveData('bills', billData);
      }

      // Show success message
      this.showMobileNotification('Bill processed successfully! Items transferred to main billing.', 'success');
      
      // Hide mobile billing interface first (this will sync data)
      this.hideMobileBilling();
      
    } catch (error) {
      console.error('Error processing mobile bill:', error);
      this.showMobileNotification('Failed to process bill', 'error');
    }
  }

  printReceipt(billData) {
    // Check if printer is available
    if ('printer' in navigator) {
      const receiptContent = this.generateReceiptHTML(billData);
      
      navigator.printer.print(receiptContent).then(() => {
        this.showMobileNotification('Receipt printed successfully', 'success');
      }).catch(error => {
        console.error('Print failed:', error);
        this.showMobileNotification('Print failed', 'error');
      });
    } else {
      // Fallback: show receipt in modal
      this.showReceiptModal(billData);
    }
  }

  generateReceiptHTML(billData) {
    return `
      <div style="font-family: monospace; max-width: 300px; margin: 0 auto;">
        <h2 style="text-align: center;">Tajir POS</h2>
        <hr>
        <div style="text-align: center;">Receipt</div>
        <div style="text-align: center;">${new Date().toLocaleString()}</div>
        <hr>
        ${billData.items.map(item => `
                     <div style="display: flex; justify-content: space-between; margin: 4px 0;">
             <span>${item.product_name}</span>
             <span>${item.total.toFixed(2)}</span>
           </div>
           <div style="font-size: 12px; color: #666;">
             ${item.quantity} x ${item.price}
           </div>
        `).join('')}
        <hr>
                 <div style="display: flex; justify-content: space-between;">
           <span>Subtotal:</span>
           <span>${billData.subtotal.toFixed(2)}</span>
         </div>
         <div style="display: flex; justify-content: space-between;">
           <span>Tax (5%):</span>
           <span>${billData.tax.toFixed(2)}</span>
         </div>
         <div style="display: flex; justify-content: space-between;">
           <span>Discount:</span>
           <span>${billData.discount.toFixed(2)}</span>
         </div>
        <hr>
                 <div style="display: flex; justify-content: space-between; font-weight: bold;">
           <span>Total:</span>
           <span>${billData.final_total.toFixed(2)}</span>
         </div>
        <hr>
        <div style="text-align: center; font-size: 12px;">
          Thank you for your business!
        </div>
      </div>
    `;
  }

  showReceiptModal(billData) {
    const receiptHTML = this.generateReceiptHTML(billData);
    
    if (window.TajirPWA && window.TajirPWA.mobileNavigation) {
      window.TajirPWA.mobileNavigation.showMobileModal(receiptHTML, {
        title: 'Receipt',
        confirmText: 'Print',
        showCancel: true
      });
    }
  }

  showMobileNotification(message, type = 'info') {
    if (window.TajirPWA && window.TajirPWA.mobileNavigation) {
      window.TajirPWA.mobileNavigation.showMobileNotification(message, type);
    } else {
      // Create a simple custom notification if mobile navigation is not available
      const notification = document.createElement('div');
      notification.className = `mobile-notification ${type}`;
      
      // Create icon based on type
      let icon = '';
      switch (type) {
        case 'success':
          icon = '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
          break;
        case 'error':
          icon = '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
          break;
        case 'warning':
          icon = '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>';
          break;
        default:
          icon = '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-5 h-5"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>';
      }
      
      notification.innerHTML = `
        ${icon}
        <span class="message">${message}</span>
      `;

      document.body.appendChild(notification);

      // Show notification
      setTimeout(() => {
        notification.classList.add('show');
      }, 100);

      // Hide and remove after 3 seconds
      setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
          if (notification.parentElement) {
            notification.remove();
          }
        }, 300);
      }, 3000);
    }
  }

  // Method to get current bill data for external access
  getCurrentBill() {
    return this.currentBill;
  }

  // Method to set bill data from external source
  setCurrentBill(billData) {
    this.currentBill = billData;
    this.updateMobileBillDisplay();
    this.calculateMobileTotals();
  }

  // Method to manually trigger sync for testing
  testSync() {
    // Sync test completed
  }

  // Get bill total
  getBillTotal() {
    return this.currentBill.finalTotal;
  }

  // Check if bill has items
  hasItems() {
    return this.currentBill.items.length > 0;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = window.MobileBilling;
}
} // Close the if (typeof window.MobileBilling === 'undefined') block 