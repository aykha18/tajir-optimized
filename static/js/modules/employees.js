// Employees Module

let editingEmployeeId = null;

// Setup employee mobile autocomplete
function setupEmployeeMobileAutocomplete() {
  const employeeMobileElement = document.getElementById('employeeMobile');
  if (employeeMobileElement) {
    let employeeMobileDropdown = null;
    let debounceTimer = null;

    // Create employee mobile dropdown
    function createEmployeeMobileDropdown() {
      if (employeeMobileDropdown) {
        document.body.removeChild(employeeMobileDropdown);
      }
      
      employeeMobileDropdown = document.createElement('div');
      employeeMobileDropdown.id = 'employeeMobileDropdown';
      employeeMobileDropdown.className = 'fixed bg-neutral-900 border border-neutral-700 rounded-lg shadow-lg max-h-48 overflow-y-auto z-99999';
      employeeMobileDropdown.style.display = 'none';
      document.body.appendChild(employeeMobileDropdown);
      
      return employeeMobileDropdown;
    }

    // Show employee mobile suggestions
    function showEmployeeMobileSuggestions(employees) {
      if (!employeeMobileDropdown) {
        employeeMobileDropdown = createEmployeeMobileDropdown();
      }
      
      if (employees.length === 0) {
        employeeMobileDropdown.style.display = 'none';
        return;
      }

      const rect = employeeMobileElement.getBoundingClientRect();
      employeeMobileDropdown.style.left = rect.left + 'px';
      employeeMobileDropdown.style.top = (rect.bottom + 5) + 'px';
      employeeMobileDropdown.style.width = rect.width + 'px';
      employeeMobileDropdown.style.display = 'block';

      employeeMobileDropdown.innerHTML = employees.map(employee => `
        <div class="employee-mobile-suggestion-item px-3 py-2 hover:bg-neutral-800 cursor-pointer border-b border-neutral-700 last:border-b-0" 
             data-phone="${employee.phone}" 
             data-employee='${JSON.stringify(employee)}'>
          <div class="flex items-center justify-between">
            <div>
              <div class="text-white font-medium">${employee.name}</div>
              <div class="text-neutral-400 text-sm">${employee.phone}</div>
              <div class="text-neutral-500 text-xs">${employee.position || 'Employee'}</div>
            </div>
            <div class="text-xs text-neutral-500">
              ${employee.address || ''}
            </div>
          </div>
        </div>
      `).join('');

      // Add click handlers
      employeeMobileDropdown.querySelectorAll('.employee-mobile-suggestion-item').forEach(item => {
        item.addEventListener('click', function() {
          const employee = JSON.parse(this.dataset.employee);
          populateEmployeeFields(employee);
          employeeMobileElement.value = employee.phone;
          hideEmployeeMobileDropdown();
        });
      });
    }

    // Hide employee mobile dropdown
    function hideEmployeeMobileDropdown() {
      if (employeeMobileDropdown) {
        employeeMobileDropdown.style.display = 'none';
      }
    }

    // Search employees by mobile number
    async function searchEmployeesByMobile(query) {
      try {
        const response = await fetch(`/api/employees?search=${encodeURIComponent(query)}`);
        if (response.ok) {
          const employees = await response.json();
          // Filter employees whose phone number starts with the query
          const filteredEmployees = employees.filter(employee => 
            employee.phone && employee.phone.startsWith(query)
          );
          return filteredEmployees.slice(0, 5); // Limit to 5 suggestions
        }
        return [];
      } catch (error) {
        console.error('Error searching employees by mobile:', error);
        return [];
      }
    }

    // Debounced search function
    function debouncedEmployeeMobileSearch(query) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(async () => {
        if (query.length >= 5) {
          const employees = await searchEmployeesByMobile(query);
          showEmployeeMobileSuggestions(employees);
        } else {
          hideEmployeeMobileDropdown();
        }
      }, 300);
    }

    // Input event for real-time autocomplete
    employeeMobileElement.addEventListener('input', function(e) {
      const phone = e.target.value.trim();
      if (phone.length >= 5) {
        debouncedEmployeeMobileSearch(phone);
      } else {
        hideEmployeeMobileDropdown();
      }
    });

    // Focus event to show suggestions if there's a value
    employeeMobileElement.addEventListener('focus', function(e) {
      const phone = e.target.value.trim();
      if (phone.length >= 5) {
        debouncedEmployeeMobileSearch(phone);
      }
    });

    // Handle escape key
    employeeMobileElement.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        hideEmployeeMobileDropdown();
      }
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (employeeMobileDropdown && !employeeMobileElement.contains(e.target) && !employeeMobileDropdown.contains(e.target)) {
        hideEmployeeMobileDropdown();
      }
    });
  }
}

// Populate employee fields
function populateEmployeeFields(employee) {
  const employeeNameElement = document.getElementById('employeeName');
  const employeeMobileElement = document.getElementById('employeeMobile');
  const employeeRoleElement = document.getElementById('employeeRole');
  
  if (employeeNameElement) employeeNameElement.value = employee.name || '';
  if (employeeMobileElement) employeeMobileElement.value = employee.phone || '';
  if (employeeRoleElement) employeeRoleElement.value = employee.position || '';
}

// Load and render employees with loading effects
async function loadEmployees() {
  // Show loading overlay
  const overlay = document.getElementById('employeeLoadingOverlay');
  const skeleton = document.getElementById('employeeSkeleton');
  const table = document.getElementById('employeeTable');
  const form = document.getElementById('employeeForm');
  
  if (overlay) overlay.classList.remove('hidden');
  if (skeleton) skeleton.classList.remove('hidden');
  if (table) table.classList.add('opacity-0', 'translate-y-4');
  if (form) form.classList.add('opacity-0', 'translate-y-4');
  
  try {
    const resp = await fetch('/api/employees');
    const employees = await resp.json();
    const tbody = document.getElementById('employeeTableBody');
    if (!tbody) return;
    
    // Simulate loading delay for better UX
    await new Promise(resolve => setTimeout(resolve, 800));
    
    tbody.innerHTML = employees.length
      ? employees.map((e, index) => `
        <tr class="employee-item group hover:bg-neutral-800/50 transition-all duration-200 transform hover:scale-[1.01] hover:shadow-sm" style="animation-delay: ${index * 0.1}s;">
          <td class="px-3 py-3">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 bg-indigo-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
              <span class="font-medium text-neutral-200 group-hover:text-white transition-colors duration-200">${e.name || ''}</span>
            </div>
          </td>
          <td class="px-3 py-3">
            <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${e.phone || ''}</span>
          </td>
          <td class="px-3 py-3">
            <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${e.position || ''}</span>
          </td>
          <td class="px-3 py-3">
            <span class="text-neutral-200 group-hover:text-white transition-colors duration-200">${e.address || ''}</span>
          </td>
          <td class="px-3 py-3 flex gap-2">
            <button class="edit-employee-btn text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 px-3 py-2 rounded transition-all duration-200 transform hover:scale-110 hover:shadow-sm" data-id="${e.employee_id}">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
              </svg>
            </button>
            <button class="delete-employee-btn text-red-400 hover:text-red-300 hover:bg-red-500/10 px-3 py-2 rounded transition-all duration-200 transform hover:scale-110 hover:shadow-sm" data-id="${e.employee_id}">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </td>
        </tr>
      `).join('')
      : `
        <tr>
          <td colspan="5" class="px-6 py-8 text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-neutral-800/50 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
            </div>
            <p class="text-neutral-400 font-medium">No employees found</p>
            <p class="text-neutral-500 text-sm mt-1">Create your first employee above</p>
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
    console.error('Error loading employees:', error);
    const tbody = document.getElementById('employeeTableBody');
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="px-6 py-8 text-center">
            <div class="w-16 h-16 mx-auto mb-4 bg-red-500/20 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
            <p class="text-red-400 font-medium">Failed to load employees</p>
            <p class="text-neutral-500 text-sm mt-1">Please try again later</p>
          </td>
        </tr>
      `;
    }
  } finally {
    // Hide loading elements
    if (overlay) overlay.classList.add('hidden');
    if (skeleton) skeleton.classList.add('hidden');
    
    // Setup event handlers after employees are loaded
    setupEmployeeTableHandlers();
    setupEmployeeFormHandler();
  }
}

// Setup employee table event handlers
function setupEmployeeTableHandlers() {
  const employeeTable = document.getElementById('employeeTable');
  
  if (employeeTable) {
    // Remove existing event listener if any
    employeeTable.removeEventListener('click', employeeTableClickHandler);
    employeeTable.addEventListener('click', employeeTableClickHandler);
  }
}

// Setup employee form submission handler
function setupEmployeeFormHandler() {
  const employeeForm = document.getElementById('employeeForm');
  
  if (employeeForm) {
    // Remove existing event listener if any
    employeeForm.removeEventListener('submit', handleEmployeeFormSubmit);
    employeeForm.addEventListener('submit', handleEmployeeFormSubmit);
  }
  
  // Setup employee mobile autocomplete
  setupEmployeeMobileAutocomplete();
}

// Handle employee form submission
async function handleEmployeeFormSubmit(e) {
  e.preventDefault();
  
  const employeeData = {
    name: (document.getElementById('employeeName') || {}).value || '',
    mobile: (document.getElementById('employeeMobile') || {}).value || '',
    address: (document.getElementById('employeeAddress') || {}).value || ''
  };
  // Optional role -> send as position if provided
  const roleEl = document.getElementById('employeeRole');
  if (roleEl && roleEl.value) {
    employeeData.position = roleEl.value;
  }
  
  if (!employeeData.name) {
    alert('Employee name is required');
    return;
  }
  
  // Basic mobile number validation
  if (employeeData.mobile && !/^\d{10,11}$/.test(employeeData.mobile.replace(/\s/g, ''))) {
    alert('Please enter a valid mobile number (10-11 digits)');
    return;
  }
  
  try {
    const url = editingEmployeeId ? `/api/employees/${editingEmployeeId}` : '/api/employees';
    const method = editingEmployeeId ? 'PUT' : 'POST';
    
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(employeeData)
    });
    
    if (response.ok) {
      // Reset form
      resetEmployeeForm();
      
      // Reload employees
      await loadEmployees();
      
      // Show success message
      if (window.showToast) {
        window.showToast('Employee saved successfully!', 'success');
      }
    } else {
      const errorData = await response.json();
      console.error('Server response:', response.status, errorData);
      
      // Show specific error message for duplicate mobile
      if (errorData.error && errorData.error.includes('Mobile number')) {
        if (window.showToast) {
          window.showToast(errorData.error, 'error');
        } else {
          alert(errorData.error);
        }
      } else {
        throw new Error(`Failed to save employee: ${response.status} - ${JSON.stringify(errorData)}`);
      }
    }
  } catch (error) {
    console.error('Error saving employee:', error);
    if (window.showToast) {
      window.showToast('Failed to save employee. Please try again.', 'error');
    }
  }
}

// Employee table click handler function
async function employeeTableClickHandler(e) {
  const editBtn = e.target.closest('.edit-employee-btn');
  const deleteBtn = e.target.closest('.delete-employee-btn');
  
  if (editBtn) {
    const id = editBtn.getAttribute('data-id');
    editEmployee(id);
  }
  if (deleteBtn) {
    const id = deleteBtn.getAttribute('data-id');
    const confirmed = await showConfirmDialog(
      'Are you sure you want to delete this employee? This action cannot be undone.',
      'Delete Employee',
      'delete'
    );
    if (confirmed) {
      fetch(`/api/employees/${id}`, { method: 'DELETE' })
        .then(() => loadEmployees());
    }
  }
}

// Edit employee function
async function editEmployee(id) {
  try {
    const response = await fetch(`/api/employees/${id}`);
    const employee = await response.json();
    
    if (employee) {
      const nameEl = document.getElementById('employeeName');
      const mobileEl = document.getElementById('employeeMobile');
      const addressEl = document.getElementById('employeeAddress');
      if (nameEl) nameEl.value = employee.name || '';
      if (mobileEl) mobileEl.value = employee.phone || '';
      if (addressEl) addressEl.value = employee.address || '';
      const roleEl = document.getElementById('employeeRole');
      if (roleEl) roleEl.value = employee.position || '';
      
      editingEmployeeId = id;
      
      // Update button text to indicate editing mode
      const submitBtn = document.querySelector('#employeeForm button[type="submit"]');
      if (submitBtn) {
        submitBtn.innerHTML = `
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          Update Employee
        `;
      }
    }
  } catch (error) {
    console.error('Error editing employee:', error);
  }
}

// Function to reset employee form
function resetEmployeeForm() {
  const form = document.getElementById('employeeForm');
  
  if (form) {
    form.reset();
  }
  
  editingEmployeeId = null;
  
  // Reset button text
  const submitBtn = document.querySelector('#employeeForm button[type="submit"]');
  if (submitBtn) {
    submitBtn.innerHTML = `
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      Add/Update
    `;
  }
}

// Make functions globally available
window.loadEmployees = loadEmployees;
window.editEmployee = editEmployee;
window.resetEmployeeForm = resetEmployeeForm; 