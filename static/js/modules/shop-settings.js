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
    const settings = {
      shop_name: form.querySelector('[name="shop_name"]').value.trim(),
      shop_mobile: form.querySelector('[name="shop_mobile"]').value.trim(),
      city: form.querySelector('[name="city"]').value.trim(),
      area: form.querySelector('[name="area"]').value.trim(),
      address: form.querySelector('[name="address"]').value.trim(),
      trn: form.querySelector('[name="trn"]').value.trim(),
      default_delivery_days: parseInt(form.querySelector('[name="default_delivery_days"]').value || '0', 10),
      default_trial_days: parseInt(form.querySelector('[name="default_trial_days"]').value || '0', 10),
      enable_trial_date: form.querySelector('[name="enable_trial_date"]').checked,
      enable_delivery_date: form.querySelector('[name="enable_delivery_date"]').checked,
      enable_advance_payment: form.querySelector('[name="enable_advance_payment"]').checked,
      use_dynamic_invoice_template: form.querySelector('[name="use_dynamic_invoice_template"]').checked,
      enable_customer_notes: form.querySelector('[name="enable_customer_notes"]').checked,
      enable_employee_assignment: form.querySelector('[name="enable_employee_assignment"]').checked,
      default_employee_id: form.querySelector('[name="default_employee_id"]').value || null
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

  // Export functions for global access
  window.initializeShopSettings = initializeShopSettings;
  window.initializeChangePassword = initializeChangePassword;
})(); 