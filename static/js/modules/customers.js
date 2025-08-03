// Customers Module

let editingCustomerId = null;

// Load and render customers with loading effects
async function loadCustomers() {
  // Show loading overlay
  const overlay = document.getElementById('customerLoadingOverlay');
  const skeleton = document.getElementById('customerSkeleton');
  const table = document.getElementById('customerTable');
  const form = document.getElementById('customerForm');
  
  if (overlay) overlay.classList.remove('hidden');
  if (skeleton) skeleton.classList.remove('hidden');
  if (table) table.classList.add('opacity-0', 'translate-y-4');
  if (form) form.classList.add('opacity-0', 'translate-y-4');
  
  try {
    const resp = await fetch('/api/customers');
    const customers = await resp.json();
    
    // Store customers globally for bill creation
    window.customers = customers;
    
    const tbody = document.getElementById('customerTableBody');
    if (!tbody) return;
      
    // Simulate loading delay for better UX
    await new Promise(resolve => setTimeout(resolve, 800));
    
    tbody.innerHTML = customers.length
        ? customers.map((c, index) => `
          <tr class="customer-item group hover:bg-neutral-800/50 transition-all duration-200 transform hover:scale-[1.01] hover:shadow-sm" style="animation-delay: ${index * 0.1}s;">
            <td class="px-3 py-3">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${c.customer_type === 'Business' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'}">
                ${c.customer_type || 'Individual'}
              </span>
            </td>
            <td class="px-3 py-3">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 bg-indigo-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
                <span class="font-medium text-neutral-200 group-hover:text-white transition-colors duration-200">${c.name || ''}</span>
              </div>
            </td>
            <td class="px-3 py-3">
              <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${c.business_name || ''}</span>
            </td>
            <td class="px-3 py-3">
              <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${c.phone || ''}</span>
            </td>
            <td class="px-3 py-3">
              <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${c.trn || ''}</span>
            </td>
            <td class="px-3 py-3">
              <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${c.city || ''}</span>
            </td>
            <td class="px-3 py-3">
              <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${c.area || ''}</span>
            </td>
            <td class="px-3 py-3 flex gap-2">
              <button class="edit-customer-btn text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 px-3 py-2 rounded transition-all duration-200 transform hover:scale-110 hover:shadow-sm" data-id="${c.customer_id}">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
              <button class="delete-customer-btn text-red-400 hover:text-red-300 hover:bg-red-500/10 px-3 py-2 rounded transition-all duration-200 transform hover:scale-110 hover:shadow-sm" data-id="${c.customer_id}">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
          </td>
        </tr>
      `).join('')
        : `
          <tr>
            <td colspan="8" class="px-6 py-8 text-center">
              <div class="w-16 h-16 mx-auto mb-4 bg-neutral-800/50 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <p class="text-neutral-400 font-medium">No customers found</p>
              <p class="text-neutral-500 text-sm mt-1">Create your first customer above</p>
            </td>
          </tr>
        `;
      
      // Animate in the content
      setTimeout(() => {
        if (form) {
          form.classList.remove('opacity-0', 'translate-y-4');
          form.classList.add('opacity-100', 'translate-y-0');
        }
      }, 200);
      
      setTimeout(() => {
        if (table) {
          table.classList.remove('opacity-0', 'translate-y-4');
          table.classList.add('opacity-100', 'translate-y-0');
        }
      }, 400);
      
    } catch (error) {
      console.error('Error loading customers:', error);
      const tbody = document.getElementById('customerTableBody');
      if (tbody) {
        tbody.innerHTML = `
          <tr>
            <td colspan="8" class="px-6 py-8 text-center">
              <div class="w-16 h-16 mx-auto mb-4 bg-red-500/20 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <p class="text-red-400 font-medium">Failed to load customers</p>
              <p class="text-neutral-500 text-sm mt-1">Please try again later</p>
            </td>
          </tr>
        `;
      }
    } finally {
      // Hide loading overlay and skeleton
      if (overlay) overlay.classList.add('hidden');
      if (skeleton) skeleton.classList.add('hidden');
      
      // Setup event handlers after customers are loaded
      setupCustomerTableHandlers();
      setupCustomerFormHandler();
      setupCustomerTypeHandler();
    }
  }

// Setup customer table event handlers
function setupCustomerTableHandlers() {
  const customerTable = document.getElementById('customerTable');
  
  if (customerTable) {
    // Remove existing event listener if any
    customerTable.removeEventListener('click', customerTableClickHandler);
    customerTable.addEventListener('click', customerTableClickHandler);
  }
}

// Setup customer form submission handler
function setupCustomerFormHandler() {
  const customerForm = document.getElementById('customerForm');
  
  if (customerForm) {
    // Remove existing event listener if any
    customerForm.removeEventListener('submit', handleCustomerFormSubmit);
    customerForm.addEventListener('submit', handleCustomerFormSubmit);
  }
}

// Setup customer type change handler
function setupCustomerTypeHandler() {
  const customerType = document.getElementById('customerType');
  
  if (customerType) {
    customerType.addEventListener('change', handleCustomerTypeChange);
  }
}

// Handle customer type change
function handleCustomerTypeChange() {
  const customerType = document.getElementById('customerType');
  const businessFields = document.querySelectorAll('.business-field');
  const trnField = document.querySelector('.trn-field');
  
  if (customerType.value === 'Business') {
    businessFields.forEach(field => field.style.display = 'block');
    if (trnField) trnField.style.display = 'block';
  } else {
    businessFields.forEach(field => field.style.display = 'none');
    if (trnField) trnField.style.display = 'none';
  }
}

// Handle customer form submission
async function handleCustomerFormSubmit(e) {
  e.preventDefault();
  
  const customerData = {
    customer_type: document.getElementById('customerType').value,
    name: document.getElementById('customerName').value,
    phone: document.getElementById('customerPhone').value,
    city: document.getElementById('customerCity').value,
    area: document.getElementById('customerArea').value,
    address: document.getElementById('customerAddress').value,
    email: document.getElementById('customerEmail').value
  };
  
  // Add business fields if customer type is Business
  if (customerData.customer_type === 'Business') {
    customerData.business_name = document.getElementById('customerBusinessName').value;
    customerData.business_address = document.getElementById('customerBusinessAddress').value;
    customerData.trn = document.getElementById('customerTRN').value;
  }
  
  if (!customerData.name || !customerData.phone) {
    alert('Name and phone are required');
    return;
  }
  
  // Basic phone number validation
  if (customerData.phone && !/^\d{10,11}$/.test(customerData.phone.replace(/\s/g, ''))) {
    alert('Please enter a valid phone number (10-11 digits)');
    return;
  }
  
  try {
    const url = editingCustomerId ? `/api/customers/${editingCustomerId}` : '/api/customers';
    const method = editingCustomerId ? 'PUT' : 'POST';
    
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(customerData)
    });
    
    if (response.ok) {
      // Reset form
      resetCustomerForm();
      
      // Reload customers
      await loadCustomers();
      
      // Show success message
      if (window.showToast) {
        window.showToast('Customer saved successfully!', 'success');
      }
    } else {
      const errorData = await response.json();
      console.error('Server response:', response.status, errorData);
      
      // Show specific error message for duplicate phone
      if (errorData.error && errorData.error.includes('Phone number')) {
        if (window.showToast) {
          window.showToast(errorData.error, 'error');
        } else {
          alert(errorData.error);
        }
      } else {
        throw new Error(`Failed to save customer: ${response.status} - ${JSON.stringify(errorData)}`);
      }
    }
  } catch (error) {
    console.error('Error saving customer:', error);
    if (window.showToast) {
      window.showToast('Failed to save customer. Please try again.', 'error');
    }
  }
}

// Customer table click handler function
async function customerTableClickHandler(e) {
  const editBtn = e.target.closest('.edit-customer-btn');
  const deleteBtn = e.target.closest('.delete-customer-btn');
  
  if (editBtn) {
    const id = editBtn.getAttribute('data-id');
    editCustomer(id);
  }
  if (deleteBtn) {
    const id = deleteBtn.getAttribute('data-id');
    const confirmed = await showConfirmDialog(
      'Are you sure you want to delete this customer? This action cannot be undone.',
      'Delete Customer',
      'delete'
    );
    if (confirmed) {
      fetch(`/api/customers/${id}`, { method: 'DELETE' })
        .then(() => loadCustomers());
    }
  }
}

// Edit customer function
async function editCustomer(id) {
  try {
    const response = await fetch(`/api/customers/${id}`);
    const customer = await response.json();
    
    if (customer) {
      document.getElementById('customerType').value = customer.customer_type || 'Individual';
      document.getElementById('customerName').value = customer.name || '';
      document.getElementById('customerPhone').value = customer.phone || '';
      document.getElementById('customerCity').value = customer.city || '';
      document.getElementById('customerArea').value = customer.area || '';
      document.getElementById('customerAddress').value = customer.address || '';
      document.getElementById('customerEmail').value = customer.email || '';
      
      // Set business fields if customer type is Business
      if (customer.customer_type === 'Business') {
        document.getElementById('customerBusinessName').value = customer.business_name || '';
        document.getElementById('customerBusinessAddress').value = customer.business_address || '';
        document.getElementById('customerTRN').value = customer.trn || '';
      }
      
      editingCustomerId = id;
      
      // Trigger customer type change to show/hide business fields
      handleCustomerTypeChange();
    }
  } catch (error) {
    console.error('Error editing customer:', error);
  }
}

// Function to reset customer form
function resetCustomerForm() {
  const form = document.getElementById('customerForm');
  
  if (form) {
    form.reset();
    
    // Hide business fields
    const businessFields = document.querySelectorAll('.business-field');
    const trnField = document.querySelector('.trn-field');
    
    businessFields.forEach(field => field.style.display = 'none');
    if (trnField) trnField.style.display = 'none';
  }
  
  editingCustomerId = null;
}

// Initialize area autocomplete elements
function initializeAreaAutocomplete() {
  const customerAreaInput = document.getElementById('customerArea');
  
  if (!customerAreaInput) {
    return;
  }

  let areaSuggestions = [];
  let selectedAreaIndex = -1;
  let customerAreaDropdown;

  // Load area suggestions
  async function loadAreaSuggestions() {
    try {
      const response = await fetch('/api/areas');
      areaSuggestions = await response.json();
    } catch (error) {
      console.error('Error loading area suggestions:', error);
    }
  }

  // Setup area event listeners
  function setupAreaEventListeners() {
    customerAreaInput.addEventListener('input', function() {
      const query = this.value.toLowerCase();
      const filteredAreas = areaSuggestions.filter(area => 
        area.toLowerCase().includes(query)
      );
      
      if (filteredAreas.length > 0) {
        showAreaSuggestions(filteredAreas);
      } else {
        hideAreaDropdown();
      }
    });

    customerAreaInput.addEventListener('focus', function() {
      if (this.value.trim()) {
        const query = this.value.toLowerCase();
        const filteredAreas = areaSuggestions.filter(area => 
          area.toLowerCase().includes(query)
        );
        if (filteredAreas.length > 0) {
          showAreaSuggestions(filteredAreas);
        }
      }
    });
  }

  // Filter area suggestions
  function filterAreaSuggestions(query) {
    return areaSuggestions.filter(area => 
      area.toLowerCase().includes(query.toLowerCase())
    );
  }

  // Show area suggestions
  function showAreaSuggestions(areas) {
    if (!customerAreaDropdown) {
      customerAreaDropdown = document.createElement('div');
      customerAreaDropdown.className = 'area-suggestion absolute z-50 w-full bg-neutral-800 border border-neutral-600 rounded-lg shadow-lg max-h-60 overflow-y-auto mt-1';
      customerAreaDropdown.style.display = 'none';
      customerAreaInput.parentNode.style.position = 'relative';
      customerAreaInput.parentNode.appendChild(customerAreaDropdown);
    }

    customerAreaDropdown.innerHTML = areas.map((area, index) => `
      <div class="area-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" 
           data-area="${area}">
        <span class="text-neutral-200">${area}</span>
      </div>
    `).join('');

    customerAreaDropdown.style.display = 'block';
  }

  // Hide area dropdown
  function hideAreaDropdown() {
    if (customerAreaDropdown) {
      customerAreaDropdown.style.display = 'none';
    }
  }

  // Update selected suggestion
  function updateSelectedSuggestion() {
    const options = customerAreaDropdown?.querySelectorAll('.area-option');
    if (!options) return;

    options.forEach((option, index) => {
      if (index === selectedAreaIndex) {
        option.classList.add('bg-neutral-700');
      } else {
        option.classList.remove('bg-neutral-700');
      }
    });
  }

  // Handle area selection
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('area-option')) {
      const selectedArea = e.target.getAttribute('data-area');
      customerAreaInput.value = selectedArea;
      hideAreaDropdown();
    }
  });

  // Hide dropdown when clicking outside
  document.addEventListener('click', function(e) {
    if (!customerAreaInput.contains(e.target) && (!customerAreaDropdown || !customerAreaDropdown.contains(e.target))) {
      hideAreaDropdown();
    }
  });

  // Initialize
  loadAreaSuggestions();
  setupAreaEventListeners();
}

// Initialize area suggestions and autocomplete
async function initializeAreaAutocompleteWithData() {
  initializeAreaAutocomplete();
}



// Make functions globally available
window.loadCustomers = loadCustomers;
window.initializeAreaAutocompleteWithData = initializeAreaAutocompleteWithData;
window.editCustomer = editCustomer;
window.resetCustomerForm = resetCustomerForm;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeAreaAutocompleteWithData);
} else {
  initializeAreaAutocompleteWithData();
} 