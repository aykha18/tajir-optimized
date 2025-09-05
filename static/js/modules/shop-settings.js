// Shop Settings Module
(function() {
  'use strict';

  // Initialize shop settings when DOM is ready
function initializeShopSettings() {
  const shopSettingsForm = document.getElementById('shopSettingsForm');
    if (!shopSettingsForm) {
      return;
    }

    // Load initial shop settings
        loadShopSettings();
    
    // Populate employees dropdown if present
    populateEmployeesDropdown();
    
    // Bind form submission
    shopSettingsForm.addEventListener('submit', handleShopSettingsSubmit);
    
    // Bind explicit save button
    const saveBtn = document.getElementById('saveShopSettingsBtn');
    if (saveBtn && !saveBtn.hasAttribute('data-bound')) {
      saveBtn.setAttribute('data-bound', 'true');
      saveBtn.addEventListener('click', (e) => {
        e.preventDefault();
        // Trigger same handler using the form element
        try {
          handleShopSettingsSubmit({ preventDefault: () => {}, target: shopSettingsForm });
        } catch (err) {
          // Silent error handling
        }
      });
    }
    
    // Bind logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn && !logoutBtn.hasAttribute('data-bound')) {
      logoutBtn.setAttribute('data-bound', 'true');
      logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Setup city and area autocomplete
    setupShopCityAreaAutocomplete();
  }

  // Load shop settings from server
  async function loadShopSettings() {
    try {
      const response = await fetch('/api/shop-settings');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const payload = await response.json();
      
      if (payload.success && payload.settings) {
        populateShopSettingsForm(payload.settings);
        // Note: shopSettingsDisplay is commented out in HTML, so we don't show it
      } else {
        await loadBillingConfigDefaults();
          }
        } catch (error) {
      if (window.showModernAlert) {
        window.showModernAlert('Failed to load shop settings', 'error');
      }
      // Try loading defaults even on error
      try { await loadBillingConfigDefaults(); } catch (_) {}
    }
  }

  // Load only billing configuration defaults when full settings unavailable
  async function loadBillingConfigDefaults() {
    try {
      const resp = await fetch('/api/shop-settings/billing-config');
      if (!resp.ok) return;
      const json = await resp.json();
      if (!json.success || !json.config) return;
      const cfg = json.config;
      const form = document.getElementById('shopSettingsForm');
      if (!form) return;
      const setChecked = (name, val) => {
        const el = form.querySelector(`[name="${name}"]`);
        if (el && el.type === 'checkbox') el.checked = Boolean(val);
      };
      const setNumber = (name, val) => {
        const el = form.querySelector(`[name="${name}"]`);
        if (el && el.type === 'number') el.value = (val ?? '').toString();
      };
      setChecked('enable_trial_date', cfg.enable_trial_date);
      setChecked('enable_delivery_date', cfg.enable_delivery_date);
      setChecked('enable_advance_payment', cfg.enable_advance_payment);
      setNumber('default_delivery_days', cfg.default_delivery_days);
    } catch (e) {
      // Silent error handling
    }
  }

  // Populate form with current settings
  function populateShopSettingsForm(settings) {
    // Set form values
    const form = document.getElementById('shopSettingsForm');
    if (!form) {
      return;
    }

    const findEl = (name) => (form ? form.querySelector(`[name="${name}"]`) : null) || document.querySelector(`[name="${name}"]`);
    const setValue = (name, value) => {
      const input = findEl(name);
      if (!input) return;
      if (input.type === 'checkbox') {
        input.checked = Boolean(value);
      } else if (input.type === 'number') {
        input.value = value ?? '';
      } else {
        input.value = value ?? '';
      }
    };

    setValue('shop_name', settings.shop_name);
    setValue('shop_mobile', settings.shop_mobile);
    setValue('city', settings.city);
    setValue('area', settings.area);
    setValue('address', settings.address);
    setValue('trn', settings.trn);
    setValue('default_delivery_days', settings.default_delivery_days);
    setValue('default_trial_days', settings.default_trial_days);
    setValue('enable_trial_date', settings.enable_trial_date);
    setValue('enable_delivery_date', settings.enable_delivery_date);
    setValue('enable_advance_payment', settings.enable_advance_payment);
    setValue('use_dynamic_invoice_template', settings.use_dynamic_invoice_template);
    setValue('enable_customer_notes', settings.enable_customer_notes);
    setValue('enable_employee_assignment', settings.enable_employee_assignment);
    
    // Currency and timezone settings
    setValue('currency_code', settings.currency_code || 'AED');
    setValue('timezone', settings.timezone || 'Asia/Dubai');

    // Preserve selected default employee if provided
    try {
      const select = document.getElementById('defaultEmployeeId');
      if (select) {
        const selectedId = settings.default_employee_id;
        if (selectedId != null) {
          if (select.options.length > 1) {
            select.value = String(selectedId);
          } else {
            select.setAttribute('data-selected', String(selectedId));
          }
        }
      }
    } catch (_) {}
    }

    // Handle form submission
  async function handleShopSettingsSubmit(e) {
      e.preventDefault();
      
    const form = e.target;
    
    // Helper function to safely get form field values
    const getFieldValue = (name, defaultValue = '') => {
      const field = form.querySelector(`[name="${name}"]`);
      return field ? field.value.trim() : defaultValue;
    };
    
    const getFieldChecked = (name, defaultValue = false) => {
      const field = form.querySelector(`[name="${name}"]`);
      return field ? field.checked : defaultValue;
    };
    
    const getFieldNumber = (name, defaultValue = 0) => {
      const field = form.querySelector(`[name="${name}"]`);
      return field ? parseInt(field.value || defaultValue, 10) : defaultValue;
    };
    
    const settings = {
      shop_name: getFieldValue('shop_name'),
      shop_mobile: getFieldValue('shop_mobile'),
      city: getFieldValue('city'),
      area: getFieldValue('area'),
      address: getFieldValue('address'),
      trn: getFieldValue('trn'),
      default_delivery_days: getFieldNumber('default_delivery_days', 0),
      default_trial_days: getFieldNumber('default_trial_days', 0),
      enable_trial_date: getFieldChecked('enable_trial_date'),
      enable_delivery_date: getFieldChecked('enable_delivery_date'),
      enable_advance_payment: getFieldChecked('enable_advance_payment'),
      use_dynamic_invoice_template: getFieldChecked('use_dynamic_invoice_template'),
      enable_customer_notes: getFieldChecked('enable_customer_notes'),
      enable_employee_assignment: getFieldChecked('enable_employee_assignment'),
      default_employee_id: getFieldValue('default_employee_id') || null,
      currency_code: getFieldValue('currency_code', 'AED'),
      timezone: getFieldValue('timezone', 'Asia/Dubai')
    };
    
    try {
      const response = await fetch('/api/shop-settings', {
          method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      
      const result = await response.json();
      
      if (response.ok && result.success) {
        if (window.showModernAlert) {
          window.showModernAlert('Shop settings updated successfully', 'success');
        }
        // Reload settings to show updated values
        loadShopSettings();
        } else {
        throw new Error(result.message || 'Failed to update settings');
        }
      } catch (error) {
      if (window.showModernAlert) {
        window.showModernAlert(error.message || 'Failed to update settings', 'error');
      }
    }
  }

  // Initialize change password functionality
  function initializeChangePassword() {
    const openChangePasswordBtn = document.getElementById('openChangePassword');
    if (!openChangePasswordBtn) {
      return;
    }

    // Remove any existing event listeners
    if (openChangePasswordBtn) {
      openChangePasswordBtn.removeEventListener('click', openChangePasswordHandler);
      openChangePasswordBtn.addEventListener('click', openChangePasswordHandler);
    }
  }

  // Handle change password button click
  function openChangePasswordHandler() {
    const changePasswordModal = document.getElementById('changePasswordModal');
    
    if (changePasswordModal) {
      changePasswordModal.classList.remove('hidden');
      
      // Add event listeners for modal controls
      setupChangePasswordModal();
    }
  }

  // Setup change password modal event listeners
  function setupChangePasswordModal() {
    const changePasswordModal = document.getElementById('changePasswordModal');
    const cancelBtn = document.getElementById('cancelChangePassword');
    const changePasswordForm = document.getElementById('changePasswordForm');
    
    if (!changePasswordModal) return;
    
    // Cancel button functionality
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => {
        changePasswordModal.classList.add('hidden');
        // Clear form fields
        if (changePasswordForm) {
          changePasswordForm.reset();
        }
      });
    }
    
    // Close modal when clicking outside
    changePasswordModal.addEventListener('click', (e) => {
      if (e.target === changePasswordModal) {
        changePasswordModal.classList.add('hidden');
        if (changePasswordForm) {
          changePasswordForm.reset();
        }
      }
    });
    
    // Handle form submission
    if (changePasswordForm) {
      changePasswordForm.addEventListener('submit', handleChangePasswordSubmit);
    }
  }

  // Handle change password form submission
  async function handleChangePasswordSubmit(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Basic validation
    if (!currentPassword || !newPassword || !confirmPassword) {
      if (window.showModernAlert) {
        window.showModernAlert('Please fill in all fields', 'error');
      }
      return;
    }
    
    if (newPassword !== confirmPassword) {
      if (window.showModernAlert) {
        window.showModernAlert('New passwords do not match', 'error');
      }
      return;
    }
    
    if (newPassword.length < 6) {
      if (window.showModernAlert) {
        window.showModernAlert('New password must be at least 6 characters', 'error');
      }
      return;
    }
    
    try {
      const response = await fetch('/api/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });
      
      const result = await response.json();
      
      if (response.ok && result.success) {
        if (window.showModernAlert) {
          window.showModernAlert('Password changed successfully', 'success');
        }
        // Close modal and reset form
        const changePasswordModal = document.getElementById('changePasswordModal');
        if (changePasswordModal) {
          changePasswordModal.classList.add('hidden');
        }
        const changePasswordForm = document.getElementById('changePasswordForm');
        if (changePasswordForm) {
          changePasswordForm.reset();
        }
      } else {
        throw new Error(result.message || 'Failed to change password');
      }
    } catch (error) {
      if (window.showModernAlert) {
        window.showModernAlert(error.message || 'Failed to change password', 'error');
      }
    }
  }

  async function populateEmployeesDropdown() {
    try {
      const select = document.getElementById('defaultEmployeeId');
      if (!select) return;
      // Avoid duplicate loads
      if (select.getAttribute('data-loaded') === 'true') return;
      const resp = await fetch('/api/employees');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const list = await resp.json();
      // Clear existing options except placeholder
      select.innerHTML = '<option value="">Select employee</option>';
      list.forEach(emp => {
        const opt = document.createElement('option');
        opt.value = emp.employee_id || emp.id || emp.emp_id || '';
        opt.textContent = emp.name || emp.employee_name || `${emp.first_name || ''} ${emp.last_name || ''}`.trim();
        select.appendChild(opt);
      });
      select.setAttribute('data-loaded', 'true');
    } catch (err) {
      // Silent error handling
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initializeShopSettings();
      initializeChangePassword();
    });
  } else {
    initializeShopSettings();
    initializeChangePassword();
  }

  // Handle logout
  async function handleLogout() {
    try {
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result = await response.json();
      
      if (response.ok && result.success) {
        if (window.showModernAlert) {
          window.showModernAlert('Logout successful', 'success');
        }
        // Redirect to login page after a short delay
        setTimeout(() => {
          window.location.href = '/login';
        }, 1000);
      } else {
        throw new Error(result.message || 'Logout failed');
      }
    } catch (error) {
      if (window.showModernAlert) {
        window.showModernAlert(error.message || 'Logout failed', 'error');
      }
    }
  }

  // FEATURE: City and Area Autocomplete for Shop Settings
  function setupShopCityAreaAutocomplete() {
    const cityInput = document.getElementById('shopCity');
    const areaInput = document.getElementById('shopArea');
    
    if (!cityInput || !areaInput) {
      console.warn('Shop City/Area autocomplete elements not found');
      return;
    }
    
    let cityDebounceTimer = null;
    let areaDebounceTimer = null;
    let cityDropdown = null;
    let areaDropdown = null;
    
    // Create city dropdown container
    function createCityDropdown() {
      if (cityDropdown) return;
      
      cityDropdown = document.createElement('div');
      cityDropdown.className = 'absolute z-50 w-full bg-neutral-800 border border-neutral-600 rounded-lg shadow-lg max-h-48 overflow-y-auto';
      cityDropdown.style.display = 'none';
      
      // Position relative to city input
      const cityContainer = cityInput.parentElement;
      cityContainer.style.position = 'relative';
      cityContainer.appendChild(cityDropdown);
      
      cityDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
      });
    }
    
    // Create area dropdown container
    function createAreaDropdown() {
      if (areaDropdown) return;
      
      areaDropdown = document.createElement('div');
      areaDropdown.className = 'absolute z-50 w-full bg-neutral-800 border border-neutral-600 rounded-lg shadow-lg max-h-48 overflow-y-auto';
      areaDropdown.style.display = 'none';
      
      // Position relative to area input
      const areaContainer = areaInput.parentElement;
      areaContainer.style.position = 'relative';
      areaContainer.appendChild(areaDropdown);
      
      areaDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
      });
    }
    
    // City autocomplete
    cityInput.addEventListener('input', function() {
      clearTimeout(cityDebounceTimer);
      const query = this.value.trim();
      
      if (query.length < 2) {
        hideCityDropdown();
        return;
      }
      
      cityDebounceTimer = setTimeout(async () => {
        try {
          const response = await fetch('/api/cities');
          const cities = await response.json();
          const filteredCities = cities.filter(city => 
            city.toLowerCase().includes(query.toLowerCase())
          );
          
          if (filteredCities && filteredCities.length > 0) {
            showCityDropdown(filteredCities);
          } else {
            hideCityDropdown();
          }
        } catch (error) {
          console.error('Error fetching cities:', error);
          hideCityDropdown();
        }
      }, 300);
    });
    
    // Area autocomplete
    areaInput.addEventListener('input', function() {
      clearTimeout(areaDebounceTimer);
      const query = this.value.trim();
      
      if (query.length < 2) {
        hideAreaDropdown();
        return;
      }
      
      areaDebounceTimer = setTimeout(async () => {
        try {
          const response = await fetch('/api/areas');
          const areas = await response.json();
          const filteredAreas = areas.filter(area => 
            area.toLowerCase().includes(query.toLowerCase())
          );
          
          if (filteredAreas && filteredAreas.length > 0) {
            showAreaDropdown(filteredAreas);
          } else {
            hideAreaDropdown();
          }
        } catch (error) {
          console.error('Error fetching areas:', error);
          hideAreaDropdown();
        }
      }, 300);
    });
    
    function showCityDropdown(cities) {
      createCityDropdown();
      
      cityDropdown.innerHTML = '';
      cities.forEach(city => {
        const item = document.createElement('div');
        item.className = 'px-3 py-2 hover:bg-neutral-700 cursor-pointer text-sm text-neutral-200 border-b border-neutral-700 last:border-b-0';
        item.textContent = city;
        item.addEventListener('click', () => {
          cityInput.value = city;
          hideCityDropdown();
          cityInput.focus();
        });
        cityDropdown.appendChild(item);
      });
      
      cityDropdown.style.display = 'block';
    }
    
    function showAreaDropdown(areas) {
      createAreaDropdown();
      
      areaDropdown.innerHTML = '';
      areas.forEach(area => {
        const item = document.createElement('div');
        item.className = 'px-3 py-2 hover:bg-neutral-700 cursor-pointer text-sm text-neutral-200 border-b border-neutral-700 last:border-b-0';
        item.textContent = area;
        item.addEventListener('click', () => {
          areaInput.value = area;
          hideAreaDropdown();
          areaInput.focus();
        });
        areaDropdown.appendChild(item);
      });
      
      areaDropdown.style.display = 'block';
    }
    
    function hideCityDropdown() {
      if (cityDropdown) {
        cityDropdown.style.display = 'none';
      }
    }
    
    function hideAreaDropdown() {
      if (areaDropdown) {
        areaDropdown.style.display = 'none';
      }
    }
    
    // Hide dropdowns when clicking outside
    document.addEventListener('click', function(e) {
      if (!cityInput.contains(e.target) && !cityDropdown?.contains(e.target)) {
        hideCityDropdown();
      }
      if (!areaInput.contains(e.target) && !areaDropdown?.contains(e.target)) {
        hideAreaDropdown();
      }
    });
    
    // Hide dropdowns on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        hideCityDropdown();
        hideAreaDropdown();
      }
    });
  }

  // Export functions for global access
  window.initializeShopSettings = initializeShopSettings; 
  window.initializeChangePassword = initializeChangePassword;
  window.setupShopCityAreaAutocomplete = setupShopCityAreaAutocomplete;
})(); 