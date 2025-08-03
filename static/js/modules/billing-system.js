// Billing System Module

// Global variables
let bill = []; // Primary declaration of 'bill'
let currentBillNumber = '';
let selectedMasterId = null;

function initializeBillingSystem() {


  function showPaymentModal({billNum, customer, paid, due, max, total, delivery, status, onOk}) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';
    
    modal.innerHTML = `
      <div class="bg-neutral-900 border border-neutral-700 rounded-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold mb-4">Payment Details</h3>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-neutral-400">Bill #:</span>
            <span class="font-medium">${billNum}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-neutral-400">Customer:</span>
            <span class="font-medium">${customer}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-neutral-400">Total Amount:</span>
            <span class="font-medium text-green-400">AED ${total}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-neutral-400">Advance Paid:</span>
            <span class="font-medium text-blue-400">AED ${paid}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-neutral-400">Balance Due:</span>
            <span class="font-medium text-red-400">AED ${due}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-neutral-400">Delivery Date:</span>
            <span class="font-medium">${delivery}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-neutral-400">Status:</span>
            <span class="font-medium ${status === 'Completed' ? 'text-green-400' : 'text-yellow-400'}">${status}</span>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button class="flex-1 px-4 py-2 rounded-lg border border-neutral-600 hover:bg-neutral-800 transition-colors cancel-btn">
            Cancel
          </button>
          <button class="flex-1 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition-colors ok-btn">
            OK
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    function cleanup() {
      document.body.removeChild(modal);
    }
    
    function onOkClick() {
      cleanup();
      if (onOk) onOk();
    }
    
    function onCancelClick() {
      cleanup();
    }
    
    modal.querySelector('.ok-btn').addEventListener('click', onOkClick);
    modal.querySelector('.cancel-btn').addEventListener('click', onCancelClick);
    
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        onCancelClick();
      }
    });
  }

  function showPaymentProgressModal(onDone) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';
    
    modal.innerHTML = `
      <div class="bg-neutral-900 border border-neutral-700 rounded-xl p-6 max-w-md w-full mx-4">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 bg-indigo-600/20 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-indigo-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </div>
          <h3 class="text-lg font-semibold mb-2">Processing Payment</h3>
          <p class="text-neutral-400 mb-4">Please wait while we process your payment...</p>
          <div class="w-full bg-neutral-700 rounded-full h-2">
            <div class="bg-indigo-600 h-2 rounded-full animate-pulse" style="width: 60%"></div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    function animateStep() {
      const progressBar = modal.querySelector('.bg-indigo-600');
      let width = 60;
      
      const interval = setInterval(() => {
        width += Math.random() * 10;
        if (width >= 100) {
          width = 100;
          clearInterval(interval);
          setTimeout(() => {
            document.body.removeChild(modal);
            if (onDone) onDone();
          }, 500);
        }
        progressBar.style.width = width + '%';
      }, 200);
    }
    
    setTimeout(animateStep, 1000);
  }

  // Modern Alert System
  function showModernAlert(message, type = 'info', title = null) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';
    
    // Determine colors based on type
    let iconColor, bgColor, borderColor, textColor;
    switch (type) {
      case 'success':
        iconColor = 'text-green-400';
        bgColor = 'bg-green-600/20';
        borderColor = 'border-green-500/30';
        textColor = 'text-green-400';
        break;
      case 'error':
        iconColor = 'text-red-400';
        bgColor = 'bg-red-600/20';
        borderColor = 'border-red-500/30';
        textColor = 'text-red-400';
        break;
      case 'warning':
        iconColor = 'text-yellow-400';
        bgColor = 'bg-yellow-600/20';
        borderColor = 'border-yellow-500/30';
        textColor = 'text-yellow-400';
        break;
      default:
        iconColor = 'text-blue-400';
        bgColor = 'bg-blue-600/20';
        borderColor = 'border-blue-500/30';
        textColor = 'text-blue-400';
    }
    
    // Get appropriate icon
    let iconSvg;
    switch (type) {
      case 'success':
        iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>`;
        break;
      case 'error':
        iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>`;
        break;
      case 'warning':
        iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>`;
        break;
      default:
        iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>`;
    }
    
    modal.innerHTML = `
      <div class="bg-neutral-900 border ${borderColor} rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0">
            <div class="w-10 h-10 ${bgColor} rounded-full flex items-center justify-center">
              ${iconSvg}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            ${title ? `<h3 class="text-lg font-semibold text-white mb-1">${title}</h3>` : ''}
            <p class="text-sm text-neutral-300">${message}</p>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button class="px-4 py-2 bg-neutral-700 hover:bg-neutral-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 focus:ring-offset-neutral-900">
            OK
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-remove after 5 seconds for success/info, 8 seconds for warnings, 10 seconds for errors
    const autoRemoveTime = type === 'success' || type === 'info' ? 5000 : type === 'warning' ? 8000 : 10000;
    const autoRemove = setTimeout(() => {
      if (document.body.contains(modal)) {
        document.body.removeChild(modal);
      }
    }, autoRemoveTime);
    
    // Manual close
    const closeModal = () => {
      clearTimeout(autoRemove);
      if (document.body.contains(modal)) {
        document.body.removeChild(modal);
      }
    };
    
    modal.querySelector('button').addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });
    
    // Keyboard support
    const handleKeydown = (e) => {
      if (e.key === 'Escape' || e.key === 'Enter') {
        closeModal();
        document.removeEventListener('keydown', handleKeydown);
      }
    };
    document.addEventListener('keydown', handleKeydown);
  }

  function togglePrint() {
    const printSection = document.getElementById('printSection');
    if (printSection) {
      printSection.classList.toggle('hidden');
    }
  }

  function renderBillTable() {
    const tbody = document.getElementById('billTable')?.querySelector('tbody');
    if (!tbody) return;
    
    tbody.innerHTML = bill.map((item, index) => `
      <tr class="hover:bg-neutral-800/50 transition-colors swipe-action" data-index="${index}">
        <td class="px-3 py-3">${item.product_name}</td>
        <td class="px-3 py-3">${item.quantity}</td>
        <td class="px-3 py-3">AED ${item.price}</td>
        <td class="px-3 py-3">AED ${item.discount || 0}</td>
        <td class="px-3 py-3">AED ${item.advance || 0}</td>
        <td class="px-3 py-3">AED ${item.vat_amount.toFixed(2)}</td>
        <td class="px-3 py-3">AED ${item.total.toFixed(2)}</td>
        <td class="px-3 py-3 flex gap-2">
          <button class="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 px-2 py-1 rounded transition-all duration-200 transform hover:scale-110 hover:shadow-sm mobile-btn" onclick="editBillItem(${index})">
            Edit
          </button>
          <button class="text-red-400 hover:text-red-300 hover:bg-red-500/10 px-2 py-1 rounded transition-all duration-200 transform hover:scale-110 hover:shadow-sm mobile-btn" onclick="deleteBillItem(${index})">
            Delete
          </button>
        </td>
      </tr>
    `).join('');
  }

  function updateTotals() {
    const subtotal = bill.reduce((sum, item) => sum + item.total, 0); // Total after discount
    const totalAdvance = bill.reduce((sum, item) => sum + (item.advance || 0), 0); // Total advance paid
    const vatRate = 0.05; // 5% VAT
    const vat = subtotal * vatRate;
    const totalBeforeAdvance = subtotal + vat;
    const amountDue = totalBeforeAdvance - totalAdvance; // Deduct advance from total
    
    // Enable/disable action buttons based on bill items
    const whatsappBtn = document.getElementById('whatsappBtn');
    const emailBtn = document.getElementById('emailBtn');
    const printBtn = document.getElementById('printBtn');
    
    if (bill.length > 0) {
      // Enable buttons when items exist
      if (whatsappBtn) {
        whatsappBtn.disabled = false;
        whatsappBtn.classList.remove('opacity-50', 'pointer-events-none', 'bg-green-600/40', 'text-white/60');
        whatsappBtn.classList.add('bg-green-600', 'text-white', 'hover:bg-green-500');
      }
      if (emailBtn) {
        emailBtn.disabled = false;
        emailBtn.classList.remove('opacity-50', 'pointer-events-none', 'bg-blue-600/40', 'text-white/60');
        emailBtn.classList.add('bg-blue-600', 'text-white', 'hover:bg-blue-500');
      }
      if (printBtn) {
        printBtn.disabled = false;
        printBtn.classList.remove('opacity-50', 'pointer-events-none', 'bg-indigo-600/40', 'text-white/60');
        printBtn.classList.add('bg-indigo-600', 'text-white', 'hover:bg-indigo-500');
      }
    } else {
      // Disable buttons when no items
      if (whatsappBtn) {
        whatsappBtn.disabled = true;
        whatsappBtn.classList.add('opacity-50', 'pointer-events-none', 'bg-green-600/40', 'text-white/60');
        whatsappBtn.classList.remove('bg-green-600', 'text-white', 'hover:bg-green-500');
      }
      if (emailBtn) {
        emailBtn.disabled = true;
        emailBtn.classList.add('opacity-50', 'pointer-events-none', 'bg-blue-600/40', 'text-white/60');
        emailBtn.classList.remove('bg-blue-600', 'text-white', 'hover:bg-blue-500');
      }
      if (printBtn) {
        printBtn.disabled = true;
        printBtn.classList.add('opacity-50', 'pointer-events-none', 'bg-indigo-600/40', 'text-white/60');
        printBtn.classList.remove('bg-indigo-600', 'text-white', 'hover:bg-indigo-500');
      }
    }
    
    const subtotalElement = document.getElementById('subTotal');
    const vatElement = document.getElementById('vatAmount');
    const totalElement = document.getElementById('amountDue');
    
         if (subtotalElement) {
       subtotalElement.textContent = `AED ${subtotal.toFixed(2)}`;
     }
     if (vatElement) {
       vatElement.textContent = `AED ${vat.toFixed(2)}`;
     }
     if (totalElement) {
       totalElement.textContent = `AED ${amountDue.toFixed(2)}`;
     }
  }

  async function getNextBillNumber() {
    try {
      const response = await fetch('/api/next-bill-number');
      const data = await response.json();
      return data.bill_number;
    } catch (error) {
      console.error('Error getting next bill number:', error);
      return null;
    }
  }

  async function setDefaultBillingDates() {
    const today = new Date();
    const deliveryDate = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000); // 7 days from now
    
    const billDateElement = document.getElementById('billDate');
    const trialDateElement = document.getElementById('trialDate');
    const billNumberElement = document.getElementById('billNumber');
    
    // Set default dates
    if (billDateElement) {
      billDateElement.value = today.toISOString().slice(0, 10);
    }
    
    if (trialDateElement) {
      trialDateElement.value = deliveryDate.toISOString().slice(0, 10);
    }
    
    // Set auto-generated bill number
    if (billNumberElement) {
      const nextBillNumber = await getNextBillNumber();
      if (nextBillNumber) {
        billNumberElement.value = nextBillNumber;
      }
    }
  }

  // Customer fetching by mobile number
  async function fetchCustomerByMobile(phone) {
    try {
      const response = await fetch(`/api/customers?phone=${encodeURIComponent(phone)}`);
      if (response.ok) {
        const customers = await response.json();
        if (Array.isArray(customers) && customers.length > 0) {
          return customers[0]; // Return the first matching customer
        }
      }
      return null;
    } catch (error) {
      console.error('Error fetching customer by mobile:', error);
      return null;
    }
  }

  function populateCustomerFields(customer) {
    const billCustomerElement = document.getElementById('billCustomer');
    const billCityElement = document.getElementById('billCity');
    const billAreaElement = document.getElementById('billArea');
    const billTRNElement = document.getElementById('billTRN');
    const billCustomerTypeElement = document.getElementById('billCustomerType');
    const billBusinessNameElement = document.getElementById('billBusinessName');
    const billBusinessAddressElement = document.getElementById('billBusinessAddress');
    
    if (billCustomerElement) billCustomerElement.value = customer.name || '';
    if (billCityElement) billCityElement.value = customer.city || '';
    if (billAreaElement) billAreaElement.value = customer.area || '';
    if (billTRNElement) billTRNElement.value = customer.trn || '';
    if (billCustomerTypeElement) billCustomerTypeElement.value = customer.customer_type || 'Individual';
    if (billBusinessNameElement) billBusinessNameElement.value = customer.business_name || '';
    if (billBusinessAddressElement) billBusinessAddressElement.value = customer.business_address || '';
    
    // Show/hide business fields based on customer type
    const businessFields = document.querySelectorAll('.business-billing-field');
    const trnField = document.querySelector('.trn-billing-field');
    
    if (customer.customer_type === 'Business') {
      businessFields.forEach(field => field.style.display = 'flex');
      if (trnField) trnField.style.display = 'flex';
      if (billBusinessNameElement) billBusinessNameElement.required = true;
      if (billBusinessAddressElement) billBusinessAddressElement.required = true;
    } else {
      businessFields.forEach(field => field.style.display = 'none');
      if (trnField) trnField.style.display = 'none';
      if (billBusinessNameElement) billBusinessNameElement.required = false;
      if (billBusinessAddressElement) billBusinessAddressElement.required = false;
    }
  }

  function clearCustomerFields() {
    const billCustomerElement = document.getElementById('billCustomer');
    const billCityElement = document.getElementById('billCity');
    const billAreaElement = document.getElementById('billArea');
    const billTRNElement = document.getElementById('billTRN');
    const billCustomerTypeElement = document.getElementById('billCustomerType');
    const billBusinessNameElement = document.getElementById('billBusinessName');
    const billBusinessAddressElement = document.getElementById('billBusinessAddress');
    
    if (billCustomerElement) billCustomerElement.value = '';
    if (billCityElement) billCityElement.value = '';
    if (billAreaElement) billAreaElement.value = '';
    if (billTRNElement) billTRNElement.value = '';
    if (billCustomerTypeElement) billCustomerTypeElement.value = 'Individual';
    if (billBusinessNameElement) billBusinessNameElement.value = '';
    if (billBusinessAddressElement) billBusinessAddressElement.value = '';
    
    // Hide business fields for new customer
    const businessFields = document.querySelectorAll('.business-billing-field');
    const trnField = document.querySelector('.trn-billing-field');
    businessFields.forEach(field => field.style.display = 'none');
    if (trnField) trnField.style.display = 'none';
    if (billBusinessNameElement) billBusinessNameElement.required = false;
    if (billBusinessAddressElement) billBusinessAddressElement.required = false;
  }

  // Setup mobile input event listener for customer fetching
  function setupMobileCustomerFetch() {
    const billMobileElement = document.getElementById('billMobile');
    if (billMobileElement) {
      billMobileElement.addEventListener('blur', async (e) => {
        const phone = e.target.value.trim();
        if (!phone) return;
        
        const customer = await fetchCustomerByMobile(phone);
        if (customer) {
          populateCustomerFields(customer);
        } else {
          clearCustomerFields();
        }
      });
    }
  }

  // Setup customer type change handler
  function setupCustomerTypeHandler() {
    const billCustomerTypeElement = document.getElementById('billCustomerType');
    if (billCustomerTypeElement) {
      billCustomerTypeElement.addEventListener('change', function() {
        const customerType = this.value;
        const businessFields = document.querySelectorAll('.business-billing-field');
        const trnField = document.querySelector('.trn-billing-field');
        const billBusinessNameElement = document.getElementById('billBusinessName');
        const billBusinessAddressElement = document.getElementById('billBusinessAddress');
        
        if (customerType === 'Business') {
          businessFields.forEach(field => field.style.display = 'flex');
          if (trnField) trnField.style.display = 'flex';
          if (billBusinessNameElement) billBusinessNameElement.required = true;
          if (billBusinessAddressElement) billBusinessAddressElement.required = true;
        } else {
          businessFields.forEach(field => field.style.display = 'none');
          if (trnField) trnField.style.display = 'none';
          if (billBusinessNameElement) billBusinessNameElement.required = false;
          if (billBusinessAddressElement) billBusinessAddressElement.required = false;
        }
      });
    }
  }

  // Recent Customers functionality
  async function loadRecentCustomers() {
    try {
      const response = await fetch('/api/customers/recent');
      const recentCustomers = await response.json();
      
      const container = document.getElementById('recentCustomersContainer');
      if (!container) return;
      
      if (recentCustomers && recentCustomers.length > 0) {
                     container.innerHTML = recentCustomers.map(customer => `
               <button 
                 class="customer-pill"
                 data-customer-id="${customer.customer_id}"
                 data-customer-name="${customer.name}"
                 data-customer-phone="${customer.phone || ''}"
                 data-customer-city="${customer.city || ''}"
                 data-customer-area="${customer.area || ''}"
                 data-customer-trn="${customer.trn || ''}"
                 data-customer-type="${customer.customer_type || 'Individual'}"
                 data-business-name="${customer.business_name || ''}"
                 data-business-address="${customer.business_address || ''}"
               >
                 <svg data-lucide="user" class="w-1 h-1"></svg>
                 <span>${customer.name}</span>
                 ${customer.phone ? `<span class="text-neutral-300">(${customer.phone})</span>` : ''}
               </button>
             `).join('');
        
        // Add event listeners to recent customer buttons
        container.querySelectorAll('.customer-pill').forEach(btn => {
          btn.addEventListener('click', function() {
            const customerData = {
              customer_id: this.getAttribute('data-customer-id'),
              name: this.getAttribute('data-customer-name'),
              phone: this.getAttribute('data-customer-phone'),
              city: this.getAttribute('data-customer-city'),
              area: this.getAttribute('data-customer-area'),
              trn: this.getAttribute('data-customer-trn'),
              customer_type: this.getAttribute('data-customer-type'),
              business_name: this.getAttribute('data-business-name'),
              business_address: this.getAttribute('data-business-address')
            };
            
            populateCustomerFields(customerData);
          });
        });
        
        // Refresh Lucide icons
        lucide.createIcons();
      } else {
        container.innerHTML = '<p class="text-neutral-500 text-sm">No recent customers found</p>';
      }
    } catch (error) {
      console.error('Error loading recent customers:', error);
      const container = document.getElementById('recentCustomersContainer');
      if (container) {
        container.innerHTML = '<p class="text-neutral-500 text-sm">Failed to load recent customers</p>';
      }
    }
  }

  // FEATURE 1: Customer Quick Search with Type-ahead
  function setupCustomerQuickSearch() {
    const customerInput = document.getElementById('customerName');
    if (!customerInput) return;

    let searchTimeout;
    let dropdown;

    // Create dropdown container
    function createCustomerDropdown() {
      dropdown = document.createElement('div');
      dropdown.className = 'customer-suggestion absolute z-50 w-full bg-neutral-800 border border-neutral-600 rounded-lg shadow-lg max-h-60 overflow-y-auto mt-1';
      dropdown.style.display = 'none';
      customerInput.parentNode.style.position = 'relative';
      customerInput.parentNode.appendChild(dropdown);
    }

    // Show customer suggestions
    function showCustomerSuggestions(customers) {
      if (!dropdown) createCustomerDropdown();
      
      dropdown.innerHTML = customers.map(customer => `
        <div class="customer-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" 
             data-customer-id="${customer.customer_id}"
             data-customer-name="${customer.name}"
             data-customer-phone="${customer.phone || ''}"
             data-customer-email="${customer.email || ''}"
             data-customer-address="${customer.address || ''}"
             data-customer-city="${customer.city || ''}"
             data-customer-area="${customer.area || ''}"
             data-customer-trn="${customer.trn || ''}"
             data-customer-type="${customer.customer_type || 'Individual'}"
             data-business-name="${customer.business_name || ''}"
             data-business-address="${customer.business_address || ''}">
          <div class="flex items-center justify-between">
            <span class="text-neutral-200">${customer.name}</span>
            <span class="text-xs text-neutral-400">${customer.phone || ''}</span>
          </div>
        </div>
      `).join('');
      
      dropdown.style.display = 'block';
    }

    // Hide customer dropdown
    function hideCustomerDropdown() {
      if (dropdown) {
        dropdown.style.display = 'none';
      }
    }

    // Search customers
    async function searchCustomers(query) {
      if (!query.trim()) {
        hideCustomerDropdown();
        return;
      }

      try {
        const response = await fetch(`/api/customers/search?q=${encodeURIComponent(query)}`);
        const customers = await response.json();
        
        if (customers.length > 0) {
          showCustomerSuggestions(customers);
        } else {
          hideCustomerDropdown();
        }
      } catch (error) {
        console.error('Error searching customers:', error);
        hideCustomerDropdown();
      }
    }

    // Debounced search
    function debouncedSearch(query) {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => searchCustomers(query), 300);
    }

    // Event listeners
    customerInput.addEventListener('input', function() {
      debouncedSearch(this.value);
    });

    customerInput.addEventListener('focus', function() {
      if (this.value.trim()) {
        debouncedSearch(this.value);
      }
    });

    // Handle customer selection
    document.addEventListener('click', function(e) {
      if (e.target.classList.contains('customer-option')) {
        e.preventDefault();
        e.stopPropagation();
        
        const customerData = {
          customer_id: e.target.getAttribute('data-customer-id'),
          name: e.target.getAttribute('data-customer-name'),
          phone: e.target.getAttribute('data-customer-phone'),
          email: e.target.getAttribute('data-customer-email'),
          address: e.target.getAttribute('data-customer-address'),
          city: e.target.getAttribute('data-customer-city'),
          area: e.target.getAttribute('data-customer-area'),
          trn: e.target.getAttribute('data-customer-trn'),
          customer_type: e.target.getAttribute('data-customer-type'),
          business_name: e.target.getAttribute('data-business-name'),
          business_address: e.target.getAttribute('data-business-address')
        };
        
        populateCustomerFields(customerData);
        hideCustomerDropdown();
        customerInput.value = customerData.name;
      }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!customerInput.contains(e.target) && (!dropdown || !dropdown.contains(e.target))) {
        hideCustomerDropdown();
      }
    });
  }

  // FEATURE 2: Product Quick Add with Search
  function setupProductQuickAdd() {
    const billProductInput = document.getElementById('billProduct');
    const billRateInput = document.getElementById('billRate');
    
    if (!billProductInput) {
      return;
    }

    let allProducts = [];
    let productDropdown;

    // Create product dropdown
    function createProductDropdown() {
      productDropdown = document.createElement('div');
      productDropdown.className = 'product-suggestion';
      productDropdown.style.cssText = 'position: absolute; z-index: 9999; background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; max-height: 240px; overflow-y: auto; margin-top: 4px; min-width: 200px; width: 100%;';
      productDropdown.style.display = 'none';
      billProductInput.parentNode.style.position = 'relative';
      billProductInput.parentNode.appendChild(productDropdown);
      
      // Prevent dropdown from hiding when clicking inside it
      productDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
      });
    }

    // Load all products
    async function loadAllProducts() {
      try {
        const response = await fetch('/api/products');
        allProducts = await response.json();
      } catch (error) {
        console.error('Error loading products:', error);
      }
    }

    // Filter products
    function filterProducts(query) {
      if (!query.trim()) return [];
      
      return allProducts.filter(product =>
        product.product_name.toLowerCase().includes(query.toLowerCase()) ||
        (product.type_name && product.type_name.toLowerCase().includes(query.toLowerCase()))
      );
    }

    // Render dropdown options
    function renderDropdownOptions(filteredProducts) {
      if (!productDropdown) createProductDropdown();
      
      productDropdown.innerHTML = filteredProducts.map(product => `
        <div class="product-option" data-product-id="${product.product_id}" data-product-name="${product.product_name}" data-product-price="${product.rate}" data-product-type="${product.type_name || ''}" style="padding: 12px 16px; cursor: pointer; border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: #f8fafc;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #e5e7eb;">${product.product_name}</span>
            <span style="font-size: 12px; color: #9ca3af;">${product.type_name || ''} - <span style="color: #10b981; font-weight: bold;">AED ${product.rate}</span></span>
          </div>
        </div>
      `).join('');
      
      // Add click listeners directly to each option
      const options = productDropdown.querySelectorAll('.product-option');
      options.forEach(option => {
        option.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          
          const productData = {
            product_id: this.getAttribute('data-product-id'),
            name: this.getAttribute('data-product-name'),
            price: this.getAttribute('data-product-price'),
            product_type: this.getAttribute('data-product-type')
          };
          
          // Set the input value
          billProductInput.value = productData.name;
          
          // Auto-fill the rate field
          if (billRateInput) {
            billRateInput.value = productData.price;
          }
          
          // Set data attribute for validation
          billProductInput.setAttribute('data-selected-product', JSON.stringify(productData));
          
          hideDropdown();
        });
      });
    }

    // Show dropdown
    function showDropdown() {
      if (!productDropdown) createProductDropdown();
      productDropdown.style.display = 'block';
    }

    // Hide dropdown
    function hideDropdown() {
      if (productDropdown) {
        // Small delay to ensure selection is processed first
        setTimeout(() => {
          productDropdown.style.display = 'none';
        }, 10);
      }
    }

    // Event listeners
    billProductInput.addEventListener('input', function() {
      const query = this.value;
      const filteredProducts = filterProducts(query);
      
      if (filteredProducts.length > 0) {
        renderDropdownOptions(filteredProducts);
        showDropdown();
      } else {
        hideDropdown();
      }
    });

    billProductInput.addEventListener('focus', function() {
      if (this.value.trim()) {
        const filteredProducts = filterProducts(this.value);
        if (filteredProducts.length > 0) {
          renderDropdownOptions(filteredProducts);
          showDropdown();
        }
      }
    });

    // Hide dropdown when clicking outside - but NOT when clicking on options
    document.addEventListener('click', function(e) {
      // Don't hide if clicking on a product option
      if (e.target.closest('.product-option')) {
        return;
      }
      
      // Don't hide if clicking on the input itself
      if (billProductInput.contains(e.target)) {
        return;
      }
      
      // Hide only if clicking outside both input and dropdown
      if (!billProductInput.contains(e.target) && (!productDropdown || !productDropdown.contains(e.target))) {
        hideDropdown();
      }
    });

    // Load products on initialization
    loadAllProducts();
  }

  // FEATURE 3: Smart Defaults
  function setupSmartDefaults() {
    const billDateInput = document.getElementById('billDate');
    const deliveryDateInput = document.getElementById('deliveryDate');
    
    if (!billDateInput || !deliveryDateInput) return;

    // Set default bill date to today
    const today = new Date().toISOString().split('T')[0];
    billDateInput.value = today;

    // Set default delivery date to bill date + 3 days
    function updateDeliveryDate() {
      if (billDateInput.value) {
        const billDate = new Date(billDateInput.value);
        const deliveryDate = new Date(billDate);
        deliveryDate.setDate(deliveryDate.getDate() + 3);
        deliveryDateInput.value = deliveryDate.toISOString().split('T')[0];
      }
    }

    // Update delivery date when bill date changes
    billDateInput.addEventListener('change', updateDeliveryDate);
    
    // Set initial delivery date
    updateDeliveryDate();

    // Set default trial date to bill date + 1 day
    const trialDateInput = document.getElementById('trialDate');
    if (trialDateInput) {
      function updateTrialDate() {
        if (billDateInput.value) {
          const billDate = new Date(billDateInput.value);
          const trialDate = new Date(billDate);
          trialDate.setDate(trialDate.getDate() + 1);
          trialDateInput.value = trialDate.toISOString().split('T')[0];
        }
      }
      
      trialDateInput.addEventListener('change', updateTrialDate);
      updateTrialDate();
    }
  }

  // FEATURE 3: Master Autocomplete
  function setupMasterAutocomplete() {
    const masterInput = document.getElementById('masterName');
    
    if (!masterInput) {
      return;
    }

    let employees = [];
    let masterDropdown;

    // Create dropdown container
    function createMasterDropdown() {
      console.log('🔍 Creating master dropdown');
      masterDropdown = document.createElement('div');
      masterDropdown.className = 'master-suggestion';
      masterDropdown.style.cssText = 'position: absolute; z-index: 9999; background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; max-height: 240px; overflow-y: auto; margin-top: 4px; min-width: 200px; width: 100%;';
      masterDropdown.style.display = 'none';
      masterInput.parentNode.style.position = 'relative';
      masterInput.parentNode.appendChild(masterDropdown);
      
      // Prevent dropdown from hiding when clicking inside it
      masterDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
      });
    }

    // Load employees
    async function loadEmployees() {
      try {
        const response = await fetch('/api/employees');
        employees = await response.json();
      } catch (error) {
        console.error('Error loading employees:', error);
      }
    }

    // Filter employees
    function filterEmployees(query) {
      if (!query.trim()) return [];
      
      return employees.filter(employee =>
        employee.name.toLowerCase().includes(query.toLowerCase()) ||
        employee.phone?.toLowerCase().includes(query.toLowerCase())
      );
    }

    // Render dropdown options
    function renderDropdownOptions(filteredEmployees) {
      if (!masterDropdown) createMasterDropdown();
      
      masterDropdown.innerHTML = filteredEmployees.map(employee => `
        <div class="master-option" data-master-id="${employee.employee_id}" data-master-name="${employee.name}" data-master-phone="${employee.phone || ''}" style="padding: 12px 16px; cursor: pointer; border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: #f8fafc;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #e5e7eb;">${employee.name}</span>
            <span style="font-size: 12px; color: #9ca3af;">${employee.phone || ''}</span>
          </div>
        </div>
      `).join('');
      
      // Add click listeners directly to each option
      const options = masterDropdown.querySelectorAll('.master-option');
      options.forEach(option => {
        option.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          
          const masterId = this.getAttribute('data-master-id');
          const masterName = this.getAttribute('data-master-name');
          
          window.selectedMasterId = masterId;
          masterInput.value = masterName;
          
          // Set data attribute for validation
          masterInput.setAttribute('data-selected-master', JSON.stringify({
            master_id: masterId,
            master_name: masterName
          }));
          
          hideDropdown();
        });
      });
    }

    // Show dropdown
    function showDropdown() {
      if (!masterDropdown) createMasterDropdown();
      masterDropdown.style.display = 'block';
    }

    // Hide dropdown
    function hideDropdown() {
      if (masterDropdown) {
        // Small delay to ensure selection is processed first
        setTimeout(() => {
          masterDropdown.style.display = 'none';
        }, 10);
      }
    }

    // Event listeners
    masterInput.addEventListener('input', function() {
      const query = this.value;
      const filteredEmployees = filterEmployees(query);
      
      if (filteredEmployees.length > 0) {
        renderDropdownOptions(filteredEmployees);
        showDropdown();
      } else {
        hideDropdown();
      }
    });

    masterInput.addEventListener('focus', function() {
      if (this.value.trim()) {
        const filteredEmployees = filterEmployees(this.value);
        if (filteredEmployees.length > 0) {
          renderDropdownOptions(filteredEmployees);
          showDropdown();
        }
      }
    });
    
    console.log('✅ Master input event listeners attached');

    // Hide dropdown when clicking outside - but NOT when clicking on options
    document.addEventListener('click', function(e) {
      // Don't hide if clicking on a master option
      if (e.target.closest('.master-option')) {
        return;
      }
      
      // Don't hide if clicking on the input itself
      if (masterInput.contains(e.target)) {
        return;
      }
      
      // Hide only if clicking outside both input and dropdown
      if (!masterInput.contains(e.target) && (!masterDropdown || !masterDropdown.contains(e.target))) {
        hideDropdown();
      }
    });

    // Load employees on initialization
    loadEmployees();
  }

  // Make selected master ID available globally
  window.getSelectedMasterId = function() {
    return window.selectedMasterId;
  };

    // Setup Add Item button functionality
  function setupAddItemHandler() {
    const addItemBtn = document.getElementById('addItemBtn');
    if (addItemBtn) {
      addItemBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Use the same element reference method as setupProductQuickAdd
        const productInput = document.getElementById('billProduct');
        const quantityInput = document.getElementById('billQty');
        const priceInput = document.getElementById('billRate');
        const discountInput = document.getElementById('billDiscount');
        const advanceInput = document.getElementById('billAdvPaid');
        const vatInput = document.getElementById('vatPercent');
        
        // Validate required fields
        if (!productInput || !productInput.value.trim()) {
          showModernAlert('Please select a product', 'warning', 'Product Required');
          return;
        }
        
        // Get selected product data
        const selectedProductData = productInput.getAttribute('data-selected-product');
        
        if (!selectedProductData) {
          showModernAlert('Please select a product from the search results', 'warning', 'Product Required');
          return;
        }
        
        let productData;
        try {
          productData = JSON.parse(selectedProductData);
        } catch (error) {
          console.error('Error parsing product data:', error);
          showModernAlert('Invalid product data. Please select a product again.', 'error', 'Product Error');
          return;
        }
        
        if (!quantityInput || !quantityInput.value || quantityInput.value <= 0) {
          showModernAlert('Please enter a valid quantity', 'warning', 'Quantity Required');
          return;
        }
        
        if (!priceInput || !priceInput.value || priceInput.value <= 0) {
          showModernAlert('Please enter a valid price', 'warning', 'Price Required');
          return;
        }
        
        // Get values
        const productId = productData.product_id;
        const productName = productData.name || productData.product_name;
        const quantity = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const discount = parseFloat(discountInput?.value) || 0;
        const advance = parseFloat(advanceInput?.value) || 0;
        const vatPercent = parseFloat(vatInput?.value) || 5;
        
        // Calculate total
        const subtotal = quantity * price;
        const total = subtotal - discount; // Price - Discount
        const vatAmount = total * (vatPercent / 100); // VAT on final amount
        
        // Add item to bill
        const item = {
          product_id: productId,
          product_name: productName,
          quantity: quantity,
          price: price,
          discount: discount,
          advance: advance,
          vat_percent: vatPercent,
          vat_amount: vatAmount,
          subtotal: subtotal, // Store subtotal (before discount)
          total: total // Store final total (after discount)
        };
        
        bill.push(item);
        
        // Update display
        renderBillTable();
        updateTotals();
        
        // Clear form fields
        if (productInput) {
          productInput.value = '';
          productInput.removeAttribute('data-selected-product');
        }
        if (quantityInput) quantityInput.value = '1';
        if (priceInput) priceInput.value = '0.00';
        if (discountInput) discountInput.value = '0';
        if (advanceInput) advanceInput.value = '0';
        if (vatInput) vatInput.value = '5';
        
        // Show success message
        showModernAlert('Item added to bill successfully', 'success');
      });
    }
  }

  // Setup Search & Reprint functionality
  function setupSearchAndReprint() {
    // Search & Reprint Invoice Modal Logic
    document.getElementById('searchInvoiceBtn')?.addEventListener('click', () => {
      document.getElementById('searchInvoiceModal').classList.remove('hidden');
      document.getElementById('searchInvoiceInput').value = '';
      document.getElementById('searchInvoiceResults').innerHTML = '';
      document.getElementById('searchInvoiceInput').focus();
    });
    
    document.getElementById('closeSearchInvoice')?.addEventListener('click', () => {
      document.getElementById('searchInvoiceModal').classList.add('hidden');
    });
    
    document.getElementById('searchInvoiceInput')?.addEventListener('input', async (e) => {
      const q = e.target.value.trim().toLowerCase();
      if (!q) {
        document.getElementById('searchInvoiceResults').innerHTML = '';
        return;
      }
      const resp = await fetch('/api/bills');
      const allBills = await resp.json();
      const results = (allBills || []).filter(bill =>
        (bill.bill_number && bill.bill_number.toLowerCase().includes(q)) ||
        (bill.customer_name && bill.customer_name.toLowerCase().includes(q)) ||
        (bill.customer_phone && bill.customer_phone.toLowerCase().includes(q))
      );
      document.getElementById('searchInvoiceResults').innerHTML = results.length
        ? `<table class="min-w-full text-sm">
            <thead><tr>
              <th class="px-2 py-1 text-left">Invoice #</th>
              <th class="px-2 py-1 text-left">Customer</th>
              <th class="px-2 py-1 text-left">Date</th>
              <th class="px-2 py-1 text-left">Amount</th>
              <th class="px-2 py-1 text-left">Status</th>
              <th></th>
            </tr></thead>
            <tbody>
              ${results.map(bill => `
                <tr>
                  <td class="px-2 py-1">${bill.bill_number || bill.bill_id}</td>
                  <td class="px-2 py-1">${bill.customer_name || ''}</td>
                  <td class="px-2 py-1">${bill.bill_date || ''}</td>
                  <td class="px-2 py-1">AED ${parseFloat(bill.total_amount).toFixed(2)}</td>
                  <td class="px-2 py-1">${bill.status || (bill.balance_amount > 0 ? 'Pending' : 'Paid')}</td>
                  <td class="px-2 py-1 flex gap-2">
                    <button class="reprint-btn bg-indigo-600 hover:bg-indigo-500 text-white rounded px-3 py-1" data-id="${bill.bill_id}">Reprint</button>
                    ${(bill.status === 'Pending' || (bill.balance_amount && bill.balance_amount > 0)) ? `<button class="mark-paid-btn bg-green-600 hover:bg-green-500 text-white rounded px-3 py-1" data-id="${bill.bill_id}" data-balance="${bill.balance_amount}">Mark as Paid</button>` : ''}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>`
        : '<div class="text-neutral-400 text-center py-4">No invoices found.</div>';
    });
    
    // Combined Reprint and Mark as Paid functionality
    document.getElementById('searchInvoiceResults')?.addEventListener('click', async function(e) {
      const reprintBtn = e.target.closest('.reprint-btn');
      const payBtn = e.target.closest('.mark-paid-btn');
      
      // Handle Reprint functionality
      if (reprintBtn) {
        const billId = reprintBtn.getAttribute('data-id');
        window.open(`/api/bills/${billId}/print`, '_blank');
        return; // Prevent further processing
      }
      
      // Handle Mark as Paid functionality
      if (payBtn) {
        const billId = payBtn.getAttribute('data-id');
        let balance = parseFloat(payBtn.getAttribute('data-balance'));
        if (!balance || balance <= 0) {
          showModernAlert('No balance due.', 'info');
          return;
        }
        // Find bill details from the row
        const row = payBtn.closest('tr');
        const billNum = row.children[0].textContent;
        const customer = row.children[1].textContent;
        const date = row.children[2].textContent;
        const total = parseFloat(row.children[3].textContent.replace('AED',''));
        const status = row.children[4].textContent;
        // Fetch delivery date from backend (optional, fallback to '-')
        let delivery = '-';
        try {
          const resp = await fetch(`/api/bills/${billId}`);
          const data = await resp.json();
          if (data && data.bill && data.bill.delivery_date) delivery = data.bill.delivery_date;
        } catch {}
        const paid = total - balance;
        showPaymentModal({
          billNum,
          customer,
          paid,
          due: balance,
          max: balance,
          total,
          delivery,
          status,
          onOk: async (amount) => {
            payBtn.disabled = true;
            payBtn.textContent = 'Processing...';
            const resp = await fetch(`/api/bills/${billId}/payment`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ amount_paid: amount })
            });
            const result = await resp.json();
            if (result && result.bill && !result.error) {
              showPaymentProgressModal(() => {
                showModernAlert('Payment recorded. Bill is now ' + (result.bill.status || 'updated'), 'success');
                document.getElementById('searchInvoiceInput').dispatchEvent(new Event('input'));
              });
            } else {
              showModernAlert(result?.error || 'Failed to update payment', 'error');
              payBtn.disabled = false;
              payBtn.textContent = 'Mark as Paid';
            }
          }
        });
      }
    });
  }

  // Payment Modal Logic
  function showPaymentModal({billNum, customer, paid, due, max, total, delivery, status, onOk}) {
    console.log('DEBUG: showPaymentModal received - due:', due, 'max:', max, 'total:', total);
    const modal = document.getElementById('paymentModal');
    document.getElementById('payBillNum').textContent = billNum;
    document.getElementById('payCustomer').textContent = customer;
    document.getElementById('payPaid').textContent = `AED ${parseFloat(paid).toFixed(2)}`;
    document.getElementById('payDue').textContent = `AED ${parseFloat(due).toFixed(2)}`;
    document.getElementById('payTotal').textContent = `AED ${parseFloat(total).toFixed(2)}`;
    document.getElementById('payDelivery').textContent = delivery || '-';
    document.getElementById('payStatus').textContent = status || '-';
    const input = document.getElementById('payAmountInput');
    input.value = parseFloat(due).toFixed(2);
    input.max = max;
    console.log('DEBUG: Payment input set - value:', input.value, 'max:', input.max);
    input.focus();
    modal.classList.remove('hidden');
    function cleanup() {
      modal.classList.add('hidden');
      okBtn.removeEventListener('click', onOkClick);
      cancelBtn.removeEventListener('click', onCancelClick);
    }
    function onOkClick() {
      let val = parseFloat(input.value);
      console.log('DEBUG: Payment validation - val:', val, 'max:', max, 'input.value:', input.value);
      if (isNaN(val) || val <= 0 || val > max) {
        console.log('DEBUG: Payment validation failed - isNaN:', isNaN(val), 'val <= 0:', val <= 0, 'val > max:', val > max);
        showModernAlert(`Enter a valid amount (max AED ${parseFloat(max).toFixed(2)})`, 'error');
        input.focus();
        return;
      }
      cleanup();
      onOk(val);
    }
    function onCancelClick() {
      cleanup();
    }
    const okBtn = document.getElementById('payModalOk');
    const cancelBtn = document.getElementById('payModalCancel');
    okBtn.addEventListener('click', onOkClick);
    cancelBtn.addEventListener('click', onCancelClick);
  }

  // Payment Progress Modal Logic
  function showPaymentProgressModal(onDone) {
    const modal = document.getElementById('paymentProgressModal');
    const arc = document.getElementById('progressArc');
    const check = document.getElementById('progressCheck');
    const msg = document.getElementById('progressStepMsg');
    const okBtn = document.getElementById('progressOkBtn');
    modal.classList.remove('hidden');
    arc.style.strokeDashoffset = 226.194;
    check.style.opacity = 0;
    okBtn.classList.add('hidden');
    msg.textContent = 'Updating Total Amount Paid...';
    let step = 0;
    const steps = [
      { text: 'Updating Total Amount Paid...', percent: 0.33 },
      { text: 'Updating Payment...', percent: 0.66 },
      { text: 'Update Status.', percent: 1.0 }
    ];
    function animateStep() {
      if (step < steps.length) {
        msg.textContent = steps[step].text;
        arc.style.strokeDashoffset = 226.194 * (1 - steps[step].percent);
        setTimeout(() => {
          step++;
          animateStep();
        }, 600);
      } else {
        arc.style.strokeDashoffset = 0;
        check.style.opacity = 1;
        msg.textContent = 'Payment Complete!';
        okBtn.classList.remove('hidden');
        okBtn.onclick = () => {
          modal.classList.add('hidden');
          if (onDone) onDone();
        };
      }
    }
    animateStep();
  }

  // Bill table click handler
  document.getElementById('billTable')?.querySelector('tbody')?.addEventListener('click', async function(e) {
    if (e.target.closest('button')) {
      const row = e.target.closest('tr');
      const index = Array.from(row.parentNode.children).indexOf(row);
      
      if (e.target.closest('button').textContent.includes('Edit')) {
        editBillItem(index);
      } else if (e.target.closest('button').textContent.includes('Delete')) {
        deleteBillItem(index);
      }
    }
  });

      // WhatsApp button event listener
  document.getElementById('whatsappBtn')?.addEventListener('click', async function() {
    if (bill.length === 0) {
      showModernAlert('Please add items to the bill before sharing.', 'warning', 'No Items');
      return;
    }
    
    if (!document.getElementById('billDate')?.value) {
      showModernAlert('Please select a Bill Date.', 'warning', 'Bill Date Required');
      return;
    }
    
    // Validate master is selected
    const selectedMasterId = window.getSelectedMasterId ? window.getSelectedMasterId() : null;
    console.log('DEBUG: WhatsApp - selectedMasterId:', selectedMasterId);
    if (!selectedMasterId) {
      showModernAlert('Please select a Master from the dropdown.', 'warning', 'Master Required');
      return;
    }
    
    // Calculate totals
    const subtotal = bill.reduce((sum, item) => sum + item.total, 0);
    const totalAdvance = bill.reduce((sum, item) => sum + (item.advance || 0), 0);
    const vatRate = 0.05; // 5% VAT
    const vat = subtotal * vatRate;
    const totalBeforeAdvance = subtotal + vat;
    const amountDue = totalBeforeAdvance - totalAdvance;
    
    // Gather bill data
    const billData = {
      bill_number: document.getElementById('billNumber')?.value || '',
      customer_name: document.getElementById('billCustomer')?.value || '',
      customer_phone: document.getElementById('billMobile')?.value || '',
      customer_city: document.getElementById('billCity')?.value || '',
      customer_area: document.getElementById('billArea')?.value || '',
      customer_trn: document.getElementById('billTRN')?.value || '',
      customer_type: document.getElementById('billCustomerType')?.value || 'Individual',
      business_name: document.getElementById('billBusinessName')?.value || '',
      business_address: document.getElementById('billBusinessAddress')?.value || '',
      bill_date: document.getElementById('billDate')?.value || '',
      delivery_date: document.getElementById('trialDate')?.value || '',
      master_id: window.getSelectedMasterId ? window.getSelectedMasterId() : null,
      vat_percent: 5,
      subtotal: subtotal,
      vat_amount: vat,
      total_amount: totalBeforeAdvance,
      advance_paid: totalAdvance,
      balance_amount: amountDue
    };

    // Prepare items data separately
    const itemsData = bill.map(item => ({
      product_id: item.product_id,
      product_name: item.product_name,
      quantity: item.quantity,
      rate: item.price,
      discount: item.discount || 0,
      advance_paid: item.advance || 0,
      total_amount: item.total
    }));
    
    try {
      // Save bill to backend
      const response = await fetch('/api/bills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bill: billData, items: itemsData })
      });
      
      if (response.ok) {
        const result = await response.json();
        const billId = result.bill_id || result.id;
        
        if (billId) {
          // Send WhatsApp message
          const whatsappResponse = await fetch(`/api/bills/${billId}/whatsapp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              phone: document.getElementById('billMobile')?.value || '',
              language: 'en'
            })
          });
          
          if (whatsappResponse.ok) {
            const whatsappResult = await whatsappResponse.json();
            if (whatsappResult.whatsapp_link) {
              window.open(whatsappResult.whatsapp_link, '_blank');
            }
            
            // Reset form after successful WhatsApp
            if (window.resetBillingForm) {
              await window.resetBillingForm();
            }
          } else {
            const errorData = await whatsappResponse.json();
            showModernAlert(`Error sending WhatsApp: ${errorData.error || 'Unknown error'}`, 'error', 'WhatsApp Error');
          }
        } else {
          showModernAlert('Error: Could not get bill ID from server response.', 'error', 'Server Error');
        }
      } else {
        const errorData = await response.json();
        showModernAlert(`Error saving bill: ${errorData.error || 'Unknown error'}`, 'error', 'Save Error');
      }
    } catch (error) {
      console.error('Error sending WhatsApp:', error);
      showModernAlert('Error sending WhatsApp. Please try again.', 'error', 'Network Error');
    }
  });

  // Email button event listener
  document.getElementById('emailBtn')?.addEventListener('click', async function() {
    if (bill.length === 0) {
      showModernAlert('Please add items to the bill before sending email.', 'warning', 'No Items');
      return;
    }
    
    if (!document.getElementById('billDate')?.value) {
      showModernAlert('Please select a Bill Date.', 'warning', 'Bill Date Required');
      return;
    }
    
    // Validate master is selected
    const selectedMasterId = window.getSelectedMasterId ? window.getSelectedMasterId() : null;
    if (!selectedMasterId) {
      showModernAlert('Please select a Master from the dropdown.', 'warning', 'Master Required');
      return;
    }
    
    // Calculate totals
    const subtotal = bill.reduce((sum, item) => sum + item.total, 0);
    const totalAdvance = bill.reduce((sum, item) => sum + (item.advance || 0), 0);
    const vatRate = 0.05; // 5% VAT
    const vat = subtotal * vatRate;
    const totalBeforeAdvance = subtotal + vat;
    const amountDue = totalBeforeAdvance - totalAdvance;
    
    // Gather bill data
    const billData = {
      bill_number: document.getElementById('billNumber')?.value || '',
      customer_name: document.getElementById('billCustomer')?.value || '',
      customer_phone: document.getElementById('billMobile')?.value || '',
      customer_city: document.getElementById('billCity')?.value || '',
      customer_area: document.getElementById('billArea')?.value || '',
      customer_trn: document.getElementById('billTRN')?.value || '',
      customer_type: document.getElementById('billCustomerType')?.value || 'Individual',
      business_name: document.getElementById('billBusinessName')?.value || '',
      business_address: document.getElementById('billBusinessAddress')?.value || '',
      bill_date: document.getElementById('billDate')?.value || '',
      delivery_date: document.getElementById('trialDate')?.value || '',
      master_id: window.getSelectedMasterId ? window.getSelectedMasterId() : null,
      vat_percent: 5,
      subtotal: subtotal,
      vat_amount: vat,
      total_amount: totalBeforeAdvance,
      advance_paid: totalAdvance,
      balance_amount: amountDue
    };

    // Prepare items data separately
    const itemsData = bill.map(item => ({
      product_id: item.product_id,
      product_name: item.product_name,
      quantity: item.quantity,
      rate: item.price,
      discount: item.discount || 0,
      advance_paid: item.advance || 0,
      total_amount: item.total
    }));
    
    try {
      // Save bill to backend
      const response = await fetch('/api/bills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bill: billData, items: itemsData })
      });
      
      if (response.ok) {
        const result = await response.json();
        const billId = result.bill_id || result.id;
        
        if (billId) {
          // Send email
          const emailResponse = await fetch(`/api/bills/${billId}/send-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: prompt('Please enter customer email address:') || '',
              language: 'en'
            })
          });
          
                     if (emailResponse.ok) {
             const emailResult = await emailResponse.json();
             showModernAlert('Email sent successfully!', 'success', 'Success');
            
            // Reset form after successful email
            if (window.resetBillingForm) {
              await window.resetBillingForm();
            }
          } else {
            const errorData = await emailResponse.json();
            showModernAlert(`Error sending email: ${errorData.error || 'Unknown error'}`, 'error', 'Email Error');
          }
        } else {
          showModernAlert('Error: Could not get bill ID from server response.', 'error', 'Server Error');
        }
      } else {
        const errorData = await response.json();
        showModernAlert(`Error saving bill: ${errorData.error || 'Unknown error'}`, 'error', 'Save Error');
      }
    } catch (error) {
      console.error('Error sending email:', error);
      showModernAlert('Error sending email. Please try again.', 'error', 'Network Error');
    }
  });

  // Print button event listener
  document.getElementById('printBtn')?.addEventListener('click', async function() {
    if (bill.length === 0) {
      showModernAlert('Please add items to the bill before printing.', 'warning', 'No Items');
      return;
    }
    
    if (!document.getElementById('billDate')?.value) {
      showModernAlert('Please select a Bill Date.', 'warning', 'Bill Date Required');
      return;
    }
    
    // Validate master is selected
    const selectedMasterId = window.getSelectedMasterId ? window.getSelectedMasterId() : null;
    if (!selectedMasterId) {
      showModernAlert('Please select a Master from the dropdown.', 'warning', 'Master Required');
      return;
    }
    
    // Calculate totals
    const subtotal = bill.reduce((sum, item) => sum + item.total, 0);
    const totalAdvance = bill.reduce((sum, item) => sum + (item.advance || 0), 0);
    const vatRate = 0.05; // 5% VAT
    const vat = subtotal * vatRate;
    const totalBeforeAdvance = subtotal + vat;
    const amountDue = totalBeforeAdvance - totalAdvance;
    
    // Gather bill data
    const billData = {
      bill_number: document.getElementById('billNumber')?.value || '',
      customer_name: document.getElementById('billCustomer')?.value || '',
      customer_phone: document.getElementById('billMobile')?.value || '',
      customer_city: document.getElementById('billCity')?.value || '',
      customer_area: document.getElementById('billArea')?.value || '',
      customer_trn: document.getElementById('billTRN')?.value || '',
      customer_type: document.getElementById('billCustomerType')?.value || 'Individual',
      business_name: document.getElementById('billBusinessName')?.value || '',
      business_address: document.getElementById('billBusinessAddress')?.value || '',
      bill_date: document.getElementById('billDate')?.value || '',
      delivery_date: document.getElementById('trialDate')?.value || '',
      master_id: window.getSelectedMasterId ? window.getSelectedMasterId() : null,
      vat_percent: 5,
      subtotal: subtotal,
      vat_amount: vat,
      total_amount: totalBeforeAdvance,
      advance_paid: totalAdvance,
      balance_amount: amountDue
    };

    // Prepare items data separately
    const itemsData = bill.map(item => ({
      product_id: item.product_id,
      product_name: item.product_name,
      quantity: item.quantity,
      rate: item.price,
      discount: item.discount || 0,
      advance_paid: item.advance || 0,
      total_amount: item.total
    }));
    
    try {
      console.log('DEBUG: Attempting to save bill with data:', billData);
      
      // Save bill to backend
      const response = await fetch('/api/bills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bill: billData, items: itemsData })
      });
      
      console.log('DEBUG: Response status:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('DEBUG: Backend response:', result);
        const billId = result.bill_id || result.id;
        
        if (billId) {
          console.log('DEBUG: Bill ID received:', billId);
          // Open print page in new tab
          window.open(`/api/bills/${billId}/print`, '_blank');
          
          // Reset form after successful print
          if (window.resetBillingForm) {
            await window.resetBillingForm();
          }
        } else {
          console.log('DEBUG: No bill ID in response');
          showModernAlert('Error: Could not get bill ID from server response.', 'error', 'Server Error');
        }
      } else {
        const errorData = await response.json();
        console.log('DEBUG: Backend error:', errorData);
        showModernAlert(`Error saving bill: ${errorData.error || 'Unknown error'}`, 'error', 'Save Error');
      }
    } catch (error) {
      console.error('Error printing bill:', error);
      showModernAlert('Error printing bill. Please try again.', 'error', 'Network Error');
    }
  });

  // Initialize billing system
  setDefaultBillingDates(); // This is now async but we don't need to await it
  setupMobileCustomerFetch();
  setupCustomerTypeHandler();
  loadRecentCustomers(); // Load recent customers for quick selection
  setupMasterAutocomplete();
  setupAddItemHandler();
  setupSearchAndReprint();
  setupCustomerQuickSearch();
  setupProductQuickAdd();
  setupSmartDefaults();
  
  console.log('🚀 Billing system initialized successfully!');
  
  // Make functions globally available
  window.initializeBillingSystem = initializeBillingSystem;
  window.showPaymentModal = showPaymentModal;
  window.showPaymentProgressModal = showPaymentProgressModal;
  window.showModernAlert = showModernAlert; // Expose modern alert globally
  window.togglePrint = togglePrint;
  window.renderBillTable = renderBillTable;
  window.updateTotals = updateTotals;
  window.bill = bill; // Expose bill globally
  window.getNextBillNumber = getNextBillNumber; // Expose for manual refresh
  window.setDefaultBillingDates = setDefaultBillingDates; // Expose for manual refresh
  window.fetchCustomerByMobile = fetchCustomerByMobile; // Expose for manual use
  window.populateCustomerFields = populateCustomerFields; // Expose for manual use
  window.clearCustomerFields = clearCustomerFields; // Expose for manual use
  window.setupAddItemHandler = setupAddItemHandler; // Expose for manual use
  
  // Function to reset billing form with fresh defaults
  window.resetBillingForm = async function() {
    // Clear bill items
    bill.length = 0;
    renderBillTable();
    updateTotals();
    
    // Reset form fields
    const form = document.getElementById('billingForm');
    if (form) {
      form.reset();
    }
    
    // Set fresh defaults
    await setDefaultBillingDates();
  };
  
  window.editBillItem = function(index) {
    const item = bill[index];
    if (!item) return;
    
    const billProductElement = document.getElementById('billProduct');
    const billQuantityElement = document.getElementById('billQty');
    const billPriceElement = document.getElementById('billRate');
    const billDiscountElement = document.getElementById('billDiscount');
    const billAdvanceElement = document.getElementById('billAdvPaid');
    const billVatElement = document.getElementById('vatPercent');
    
    if (billProductElement) {
      billProductElement.value = item.product_name;
      billProductElement.setAttribute('data-selected-product', JSON.stringify({
        product_id: item.product_id,
        name: item.product_name,
        price: item.price,
        product_type: 'Unknown'
      }));
    }
    if (billQuantityElement) billQuantityElement.value = item.quantity;
    if (billPriceElement) billPriceElement.value = item.price;
    if (billDiscountElement) billDiscountElement.value = item.discount || 0;
    if (billAdvanceElement) billAdvanceElement.value = item.advance || 0;
    if (billVatElement) billVatElement.value = item.vat_percent || 5;
    
    bill.splice(index, 1);
    renderBillTable();
    updateTotals();
  };
  window.deleteBillItem = function(index) {
    // Show confirmation dialog
    const confirmModal = document.getElementById('confirmModal');
    const confirmModalTitle = document.getElementById('confirmModalTitle');
    const confirmModalMsg = document.getElementById('confirmModalMsg');
    const confirmModalOk = document.getElementById('confirmModalOk');
    const confirmModalCancel = document.getElementById('confirmModalCancel');
    
    if (confirmModal && confirmModalTitle && confirmModalMsg && confirmModalOk && confirmModalCancel) {
      confirmModalTitle.textContent = 'Delete Item';
      confirmModalMsg.textContent = 'Are you sure you want to delete this item? This action cannot be undone.';
      
      // Show modal
      confirmModal.classList.remove('hidden');
      
      // Handle confirmation
      const handleConfirm = () => {
        bill.splice(index, 1);
        renderBillTable();
        updateTotals();
        confirmModal.classList.add('hidden');
        confirmModalOk.removeEventListener('click', handleConfirm);
        confirmModalCancel.removeEventListener('click', handleCancel);
      };
      
      const handleCancel = () => {
        confirmModal.classList.add('hidden');
        confirmModalOk.removeEventListener('click', handleConfirm);
        confirmModalCancel.removeEventListener('click', handleCancel);
      };
      
      confirmModalOk.addEventListener('click', handleConfirm);
      confirmModalCancel.addEventListener('click', handleCancel);
    } else {
      // Fallback to simple alert if modal not available
      if (confirm('Are you sure you want to delete this item?')) {
        bill.splice(index, 1);
        renderBillTable();
        updateTotals();
      }
    }
  };
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeBillingSystem);
} else {
  initializeBillingSystem();
}