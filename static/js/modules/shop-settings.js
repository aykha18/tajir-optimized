// Shop Settings Module

function initializeShopSettings() {
  console.log('Initializing shop settings...');
  const shopSettingsForm = document.getElementById('shopSettingsForm');
  const shopSettingsLoadingOverlay = document.getElementById('shopSettingsLoadingOverlay');
  const shopSettingsDisplay = document.getElementById('shopSettingsDisplay');
  const shopSettingsContent = document.getElementById('shopSettingsContent');
  const shopSettingsSection = document.getElementById('shopSettingsSec');
  const isMobile = window.innerWidth <= 1024;
  const tabShopInfo = document.getElementById('tabShopInfo');
  const tabBillingConfig = document.getElementById('tabBillingConfig');
  const shopInfoTabContent = document.getElementById('shopInfoTabContent');
  const billingConfigTabContent = document.getElementById('billingConfigTabContent');

  // Ensure the shop settings section is visible
  if (shopSettingsSection) {
    shopSettingsSection.classList.remove('hidden');
    console.log('Shop settings section made visible');
  } else {
    console.error('Shop settings section not found');
  }

  // Tabs behavior
  function activateTab(tab) {
    if (!tabShopInfo || !tabBillingConfig || !shopInfoTabContent || !billingConfigTabContent) return;
    if (tab === 'shop') {
      tabShopInfo.classList.add('bg-neutral-700','text-white');
      tabShopInfo.classList.remove('bg-transparent','text-neutral-300');
      tabBillingConfig.classList.remove('bg-neutral-700','text-white');
      tabBillingConfig.classList.add('bg-transparent','text-neutral-300');
      shopInfoTabContent.classList.remove('hidden');
      billingConfigTabContent.classList.add('hidden');
    } else {
      tabBillingConfig.classList.add('bg-neutral-700','text-white');
      tabBillingConfig.classList.remove('bg-transparent','text-neutral-300');
      tabShopInfo.classList.remove('bg-neutral-700','text-white');
      tabShopInfo.classList.add('bg-transparent','text-neutral-300');
      billingConfigTabContent.classList.remove('hidden');
      shopInfoTabContent.classList.add('hidden');
    }
  }

  if (tabShopInfo) {
    tabShopInfo.addEventListener('click', () => activateTab('shop'));
  }
  if (tabBillingConfig) {
    tabBillingConfig.addEventListener('click', () => activateTab('billing'));
  }
  // Default active tab
  activateTab('shop');

  // Load shop settings on page load
  function loadShopSettings() {
    console.log('Loading shop settings...');
    if (shopSettingsLoadingOverlay) {
      shopSettingsLoadingOverlay.classList.remove('hidden');
    }
    
    fetch('/api/shop-settings')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.settings) {
          const settings = data.settings;
          console.log('Shop settings loaded successfully:', settings);
          
          // Populate form fields
          const shopNameField = document.getElementById('shopName');
          const shopMobileField = document.getElementById('shopMobile');
          const shopCityField = document.getElementById('shopCity');
          const shopAreaField = document.getElementById('shopArea');
          const shopAddressField = document.getElementById('shopAddress');
          const shopTRNField = document.getElementById('shopTRN');
          const useDynamicInvoiceTemplateField = document.getElementById('useDynamicInvoiceTemplate');
          const paymentModeAdvanceField = document.getElementById('paymentModeAdvance');
          const paymentModeFullField = document.getElementById('paymentModeFull');
          
          // Configurable billing fields
          const enableTrialDateField = document.getElementById('enableTrialDate');
          const enableDeliveryDateField = document.getElementById('enableDeliveryDate');
          const enableAdvancePaymentField = document.getElementById('enableAdvancePayment');
          const enableCustomerNotesField = document.getElementById('enableCustomerNotes');
          const enableEmployeeAssignmentField = document.getElementById('enableEmployeeAssignment');
          const defaultDeliveryDaysField = document.getElementById('defaultDeliveryDays');
          const defaultTrialDaysField = document.getElementById('defaultTrialDays');
          const defaultEmployeeIdField = document.getElementById('defaultEmployeeId');

          // Populate employees dropdown
          if (defaultEmployeeIdField) {
            fetch('/api/employees')
              .then(res => res.json())
              .then(list => {
                if (Array.isArray(list)) {
                  defaultEmployeeIdField.innerHTML = '<option value="">Select employee</option>';
                  list.forEach(emp => {
                    const opt = document.createElement('option');
                    opt.value = emp.employee_id || emp.id || '';
                    opt.textContent = emp.name || `#${opt.value}`;
                    defaultEmployeeIdField.appendChild(opt);
                  });
                  if (settings.default_employee_id) {
                    defaultEmployeeIdField.value = settings.default_employee_id;
                  }
                }
              })
              .catch(() => {});
          }
          
          if (shopNameField) shopNameField.value = settings.shop_name || '';
          if (shopMobileField) shopMobileField.value = settings.shop_mobile || '';
          if (shopCityField) shopCityField.value = settings.city || '';
          if (shopAreaField) shopAreaField.value = settings.area || '';
          if (shopAddressField) shopAddressField.value = settings.address || '';
          if (shopTRNField) shopTRNField.value = settings.trn || '';
          if (useDynamicInvoiceTemplateField) useDynamicInvoiceTemplateField.checked = settings.use_dynamic_invoice_template || false;
          
          // Set payment mode
          const paymentMode = settings.payment_mode || 'advance';
          if (paymentModeAdvanceField) paymentModeAdvanceField.checked = paymentMode === 'advance';
          if (paymentModeFullField) paymentModeFullField.checked = paymentMode === 'full';
          
                     // Set configurable billing fields
           if (enableTrialDateField) enableTrialDateField.checked = Boolean(settings.enable_trial_date);
           if (enableDeliveryDateField) enableDeliveryDateField.checked = Boolean(settings.enable_delivery_date);
           if (enableAdvancePaymentField) enableAdvancePaymentField.checked = Boolean(settings.enable_advance_payment);
           if (enableCustomerNotesField) enableCustomerNotesField.checked = Boolean(settings.enable_customer_notes);
           if (enableEmployeeAssignmentField) enableEmployeeAssignmentField.checked = Boolean(settings.enable_employee_assignment);
          if (defaultDeliveryDaysField) defaultDeliveryDaysField.value = settings.default_delivery_days || 3;
          if (defaultTrialDaysField) defaultTrialDaysField.value = settings.default_trial_days || 3;
          if (defaultEmployeeIdField) defaultEmployeeIdField.disabled = !(enableEmployeeAssignmentField?.checked ?? true);
          
          // Trigger field state updates after loading settings
          setTimeout(() => {
            const updateFieldStates = () => {
              const enableTrialDate = document.getElementById('enableTrialDate');
              const enableDeliveryDate = document.getElementById('enableDeliveryDate');
              const defaultTrialDays = document.getElementById('defaultTrialDays');
              const defaultDeliveryDays = document.getElementById('defaultDeliveryDays');
              const defaultEmployeeId = document.getElementById('defaultEmployeeId');
              
              if (defaultTrialDays) {
                defaultTrialDays.disabled = !enableTrialDate?.checked;
              }
              if (defaultEmployeeId) {
                const enableEmp = document.getElementById('enableEmployeeAssignment');
                defaultEmployeeId.disabled = !enableEmp?.checked;
              }
              
              if (defaultDeliveryDays) {
                defaultDeliveryDays.disabled = !enableDeliveryDate?.checked;
              }
            };
            
            updateFieldStates();
          }, 100);
          
          // Show form with animation
          if (shopSettingsForm) {
            console.log('Showing shop settings form');
            shopSettingsForm.style.display = 'block';
            shopSettingsForm.style.visibility = 'visible';
          } else {
            console.error('Shop settings form not found');
          }
          
          // Update display section
          if (shopSettingsDisplay && shopSettingsContent) {
            console.log('Updating shop settings display');
            shopSettingsContent.innerHTML = `
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span class="text-neutral-400">Shop Name:</span>
                  <span class="text-white ml-2">${settings.shop_name || 'Not set'}</span>
                </div>
                <div>
                  <span class="text-neutral-400">Mobile:</span>
                  <span class="text-white ml-2">${settings.shop_mobile || 'Not set'}</span>
                </div>
                <div>
                  <span class="text-neutral-400">City:</span>
                  <span class="text-white ml-2">${settings.city || 'Not set'}</span>
                </div>
                <div>
                  <span class="text-neutral-400">Area:</span>
                  <span class="text-white ml-2">${settings.area || 'Not set'}</span>
                </div>
                <div class="md:col-span-2">
                  <span class="text-neutral-400">Address:</span>
                  <span class="text-white ml-2">${settings.address || 'Not set'}</span>
                </div>
                <div>
                  <span class="text-neutral-400">TRN:</span>
                  <span class="text-white ml-2">${settings.trn || 'Not set'}</span>
                </div>
                <div>
                  <span class="text-neutral-400">Dynamic Invoice Template:</span>
                  <span class="text-white ml-2">${settings.use_dynamic_invoice_template ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div>
                  <span class="text-neutral-400">Payment Mode:</span>
                  <span class="text-white ml-2">${settings.payment_mode === 'full' ? 'Full Payment Only' : 'Allow Advance Payments'}</span>
                </div>
              </div>
              
              <!-- Billing Configuration Display -->
              <div class="mt-6 pt-6 border-t border-neutral-700/30">
                <h5 class="text-sm font-semibold text-neutral-300 mb-3">Billing Configuration</h5>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                     <div>
                     <span class="text-neutral-400">Trial Date:</span>
                     <span class="text-white ml-2">${Boolean(settings.enable_trial_date) ? 'Enabled' : 'Disabled'}</span>
                   </div>
                   <div>
                     <span class="text-neutral-400">Delivery Date:</span>
                     <span class="text-white ml-2">${Boolean(settings.enable_delivery_date) ? 'Enabled' : 'Disabled'}</span>
                   </div>
                   <div>
                     <span class="text-neutral-400">Advance Payment:</span>
                     <span class="text-white ml-2">${Boolean(settings.enable_advance_payment) ? 'Enabled' : 'Disabled'}</span>
                   </div>
                   <div>
                     <span class="text-neutral-400">Customer Notes:</span>
                     <span class="text-white ml-2">${Boolean(settings.enable_customer_notes) ? 'Enabled' : 'Disabled'}</span>
                   </div>
                   <div>
                     <span class="text-neutral-400">Employee Assignment:</span>
                     <span class="text-white ml-2">${Boolean(settings.enable_employee_assignment) ? 'Enabled' : 'Disabled'}</span>
                   </div>
                  <div>
                    <span class="text-neutral-400">Default Delivery Days:</span>
                    <span class="text-white ml-2">${settings.default_delivery_days || 3} days</span>
                  </div>
                  <div>
                    <span class="text-neutral-400">Default Trial Days:</span>
                    <span class="text-white ml-2">${settings.default_trial_days || 3} days</span>
                  </div>
                </div>
              </div>
            `;
            shopSettingsDisplay.style.display = 'block';
            shopSettingsDisplay.style.visibility = 'visible';
          } else {
            console.error('Shop settings display not found');
          }
        } else {
          console.error('Failed to load shop settings:', data.error);
        }
      })
      .catch(err => {
        console.error('Error loading shop settings:', err);
      })
      .finally(() => {
        if (shopSettingsLoadingOverlay) {
          shopSettingsLoadingOverlay.classList.add('hidden');
        }
      });
  }

  // Save shop settings
  function saveShopSettings(event) {
    event.preventDefault();
    
    const formData = {
      shop_name: shopSettingsForm?.querySelector('#shopName')?.value || '',
      shop_mobile: (shopSettingsForm?.querySelector('#shopMobile')?.value || '').replace(/\D/g, ''),
      city: shopSettingsForm?.querySelector('#shopCity')?.value || '',
      area: shopSettingsForm?.querySelector('#shopArea')?.value || '',
      address: shopSettingsForm?.querySelector('#shopAddress')?.value || '',
      trn: shopSettingsForm?.querySelector('#shopTRN')?.value || '',
      use_dynamic_invoice_template: shopSettingsForm?.querySelector('#useDynamicInvoiceTemplate')?.checked || false,
      payment_mode: shopSettingsForm?.querySelector('input[name="paymentMode"]:checked')?.value || 'advance',
      // Configurable billing fields
      enable_trial_date: shopSettingsForm?.querySelector('#enableTrialDate')?.checked || false,
      enable_delivery_date: shopSettingsForm?.querySelector('#enableDeliveryDate')?.checked || false,
      enable_advance_payment: shopSettingsForm?.querySelector('#enableAdvancePayment')?.checked || false,
      enable_customer_notes: shopSettingsForm?.querySelector('#enableCustomerNotes')?.checked || false,
      enable_employee_assignment: shopSettingsForm?.querySelector('#enableEmployeeAssignment')?.checked || false,
      default_delivery_days: parseInt(shopSettingsForm?.querySelector('#defaultDeliveryDays')?.value || '3'),
      default_trial_days: parseInt(shopSettingsForm?.querySelector('#defaultTrialDays')?.value || '3'),
      default_employee_id: shopSettingsForm?.querySelector('#defaultEmployeeId')?.value || null
    };

    // Mobile-friendly inline validation
    if (!formData.shop_name) {
      showModernAlert('Shop name is required', 'warning');
      return;
    }
    if (formData.shop_mobile && (formData.shop_mobile.length < 9 || formData.shop_mobile.length > 10)) {
      showModernAlert('Shop mobile must be 9-10 digits', 'warning');
      return;
    }

    fetch('/api/shop-settings', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Show success message
        showModernAlert('Shop settings updated successfully!', 'success');
        // Reload settings to update display
        loadShopSettings();
      } else {
        console.error('Failed to save shop settings:', data.error);
        showModernAlert('Failed to update shop settings. Please try again.', 'error');
      }
    })
    .catch(err => {
      console.error('Error saving shop settings:', err);
      showModernAlert('Error saving shop settings. Please try again.', 'error');
    });
  }

  // Event listeners
  if (shopSettingsForm) {
    // Remove existing event listener to prevent duplicates
    shopSettingsForm.removeEventListener('submit', saveShopSettings);
    shopSettingsForm.addEventListener('submit', saveShopSettings);
  }

  // Initialize autocomplete for City and Area fields
  function initializeAutocomplete() {
    const cityInput = document.getElementById('shopCity');
    const areaInput = document.getElementById('shopArea');
    const cityDropdown = document.getElementById('cityDropdown');
    const areaDropdown = document.getElementById('areaDropdown');

    // City autocomplete
    if (cityInput && cityDropdown) {
      cityInput.addEventListener('input', async function() {
        const query = this.value.trim();
        if (query.length < 2) {
          cityDropdown.classList.add('hidden');
          return;
        }

        try {
          const response = await fetch('/api/cities');
          const cities = await response.json();
          const filteredCities = cities.filter(city => 
            city.toLowerCase().includes(query.toLowerCase())
          );

          if (filteredCities.length > 0) {
            cityDropdown.innerHTML = filteredCities.map(city => `
              <div class="city-option px-3 py-2 hover:bg-neutral-700 cursor-pointer text-sm" data-city="${city}">
                ${city}
              </div>
            `).join('');
            cityDropdown.classList.remove('hidden');
          } else {
            cityDropdown.classList.add('hidden');
          }
        } catch (error) {
          console.error('Error loading cities:', error);
        }
      });

      // Handle city selection
      cityDropdown.addEventListener('click', function(e) {
        if (e.target.classList.contains('city-option')) {
          const selectedCity = e.target.getAttribute('data-city');
          cityInput.value = selectedCity;
          cityDropdown.classList.add('hidden');
          
          // Clear area when city changes
          areaInput.value = '';
        }
      });

      // Hide dropdown when clicking outside
      document.addEventListener('click', function(e) {
        if (!cityInput.contains(e.target) && !cityDropdown.contains(e.target)) {
          cityDropdown.classList.add('hidden');
        }
      });
    }

    // Area autocomplete
    if (areaInput && areaDropdown) {
      areaInput.addEventListener('input', async function() {
        const query = this.value.trim();
        if (query.length < 2) {
          areaDropdown.classList.add('hidden');
          return;
        }

        try {
          const cityValue = cityInput.value.trim();
          const url = cityValue ? `/api/areas?city=${encodeURIComponent(cityValue)}` : '/api/areas';
          const response = await fetch(url);
          const areas = await response.json();
          const filteredAreas = areas.filter(area => 
            area.toLowerCase().includes(query.toLowerCase())
          );

          if (filteredAreas.length > 0) {
            areaDropdown.innerHTML = filteredAreas.map(area => `
              <div class="area-option px-3 py-2 hover:bg-neutral-700 cursor-pointer text-sm" data-area="${area}">
                ${area}
              </div>
            `).join('');
            areaDropdown.classList.remove('hidden');
          } else {
            areaDropdown.classList.add('hidden');
          }
        } catch (error) {
          console.error('Error loading areas:', error);
        }
      });

      // Handle area selection
      areaDropdown.addEventListener('click', function(e) {
        if (e.target.classList.contains('area-option')) {
          const selectedArea = e.target.getAttribute('data-area');
          areaInput.value = selectedArea;
          areaDropdown.classList.add('hidden');
          
          // If no city is selected, try to find the city for this area
          if (!cityInput.value.trim()) {
            findCityForArea(selectedArea);
          }
        }
      });
      
      // Find city for selected area
      async function findCityForArea(area) {
        try {
          const response = await fetch(`/api/cities?area=${encodeURIComponent(area)}`);
          const cities = await response.json();
          
          if (cities.length > 0) {
            cityInput.value = cities[0]; // Use the first city found
          }
        } catch (error) {
          console.error('Error finding city for area:', error);
        }
      }

      // Hide dropdown when clicking outside
      document.addEventListener('click', function(e) {
        if (!areaInput.contains(e.target) && !areaDropdown.contains(e.target)) {
          areaDropdown.classList.add('hidden');
        }
      });
    }
  }

  // Initialize change password functionality
  function initializeChangePassword() {
    const openChangePasswordBtn = document.getElementById('openChangePassword');
    const changePasswordModal = document.getElementById('changePasswordModal');
    const changePasswordForm = document.getElementById('changePasswordForm');
    const cancelChangePasswordBtn = document.getElementById('cancelChangePassword');
    const modalContent = document.getElementById('changePasswordModalContent');

    // Open modal
    if (openChangePasswordBtn) {
      // Remove existing event listener to prevent duplicates
      openChangePasswordBtn.removeEventListener('click', openChangePasswordHandler);
      openChangePasswordBtn.addEventListener('click', openChangePasswordHandler);
    }

    function openChangePasswordHandler() {
      if (changePasswordModal && modalContent) {
        changePasswordModal.classList.remove('hidden');
      }
    }

    // Close modal
    if (cancelChangePasswordBtn) {
      // Remove existing event listener to prevent duplicates
      cancelChangePasswordBtn.removeEventListener('click', closeChangePasswordModal);
      cancelChangePasswordBtn.addEventListener('click', closeChangePasswordModal);
    }

    // Close modal on backdrop click
    if (changePasswordModal) {
      // Remove existing event listener to prevent duplicates
      changePasswordModal.removeEventListener('click', backdropClickHandler);
      changePasswordModal.addEventListener('click', backdropClickHandler);
    }

    function backdropClickHandler(e) {
      if (e.target === changePasswordModal) {
        closeChangePasswordModal();
      }
    }

    // Handle form submission
    if (changePasswordForm) {
      // Remove existing event listener to prevent duplicates
      changePasswordForm.removeEventListener('submit', handleChangePasswordSubmit);
      changePasswordForm.addEventListener('submit', handleChangePasswordSubmit);
    }

    function closeChangePasswordModal() {
      if (changePasswordModal && modalContent) {
        changePasswordModal.classList.add('hidden');
        changePasswordForm.reset();
      }
    }

    async function handleChangePasswordSubmit(e) {
      e.preventDefault();
      
      const currentPassword = document.getElementById('currentPassword').value;
      const newPassword = document.getElementById('newPassword').value;
      const confirmPassword = document.getElementById('confirmPassword').value;

      // Validation
      if (!currentPassword || !newPassword || !confirmPassword) {
        alert('All fields are required');
        return;
      }

      if (newPassword.length < 6) {
        alert('New password must be at least 6 characters long');
        return;
      }

      if (newPassword !== confirmPassword) {
        alert('New passwords do not match');
        return;
      }

      try {
        const response = await fetch('/api/account/password', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword
          })
        });

        const data = await response.json();

        if (data.success) {
          alert('Password changed successfully!');
          closeChangePasswordModal();
        } else {
          alert(data.message || 'Failed to change password');
        }
      } catch (error) {
        console.error('Error changing password:', error);
        alert('Failed to change password. Please try again.');
      }
    }
  }

  // Initialize preset functionality
  function initializePresets() {
    const presetTailor = document.getElementById('presetTailor');
    const presetPerfume = document.getElementById('presetPerfume');
    const presetLaundry = document.getElementById('presetLaundry');
    const presetGeneral = document.getElementById('presetGeneral');

    if (presetTailor) {
      presetTailor.addEventListener('click', () => applyPreset('tailor'));
    }
    if (presetPerfume) {
      presetPerfume.addEventListener('click', () => applyPreset('perfume'));
    }
    if (presetLaundry) {
      presetLaundry.addEventListener('click', () => applyPreset('laundry'));
    }
    if (presetGeneral) {
      presetGeneral.addEventListener('click', () => applyPreset('general'));
    }
  }

  // Initialize conditional field enabling
  function initializeConditionalFields() {
    const enableTrialDate = document.getElementById('enableTrialDate');
    const enableDeliveryDate = document.getElementById('enableDeliveryDate');
    const defaultTrialDays = document.getElementById('defaultTrialDays');
    const defaultDeliveryDays = document.getElementById('defaultDeliveryDays');
    
    // Function to update field states
    function updateFieldStates() {
      if (defaultTrialDays) {
        defaultTrialDays.disabled = !enableTrialDate?.checked;
        if (!enableTrialDate?.checked) {
          defaultTrialDays.value = '';
        } else if (!defaultTrialDays.value) {
          defaultTrialDays.value = '3';
        }
      }
      
      if (defaultDeliveryDays) {
        defaultDeliveryDays.disabled = !enableDeliveryDate?.checked;
        if (!enableDeliveryDate?.checked) {
          defaultDeliveryDays.value = '';
        } else if (!defaultDeliveryDays.value) {
          defaultDeliveryDays.value = '3';
        }
      }
    }
    
    // Add event listeners
    if (enableTrialDate) {
      enableTrialDate.addEventListener('change', updateFieldStates);
    }
    if (enableDeliveryDate) {
      enableDeliveryDate.addEventListener('change', updateFieldStates);
    }
    
    // Initial state update
    updateFieldStates();
  }

  function applyPreset(type) {
    const enableTrialDate = document.getElementById('enableTrialDate');
    const enableDeliveryDate = document.getElementById('enableDeliveryDate');
    const enableAdvancePayment = document.getElementById('enableAdvancePayment');
    const enableCustomerNotes = document.getElementById('enableCustomerNotes');
    const enableEmployeeAssignment = document.getElementById('enableEmployeeAssignment');
    const defaultDeliveryDays = document.getElementById('defaultDeliveryDays');
    const defaultTrialDays = document.getElementById('defaultTrialDays');

    switch (type) {
      case 'tailor':
        // Tailor Shop: All features enabled
        if (enableTrialDate) enableTrialDate.checked = true;
        if (enableDeliveryDate) enableDeliveryDate.checked = true;
        if (enableAdvancePayment) enableAdvancePayment.checked = true;
        if (enableCustomerNotes) enableCustomerNotes.checked = true;
        if (enableEmployeeAssignment) enableEmployeeAssignment.checked = true;
        if (defaultDeliveryDays) defaultDeliveryDays.value = 3;
        if (defaultTrialDays) defaultTrialDays.value = 3;
        showModernAlert('Tailor Shop preset applied! All billing features enabled.', 'success');
        break;

      case 'perfume':
        // Perfume Shop: Disable trial and delivery dates
        if (enableTrialDate) enableTrialDate.checked = false;
        if (enableDeliveryDate) enableDeliveryDate.checked = false;
        if (enableAdvancePayment) enableAdvancePayment.checked = true;
        if (enableCustomerNotes) enableCustomerNotes.checked = true;
        if (enableEmployeeAssignment) enableEmployeeAssignment.checked = false;
        if (defaultDeliveryDays) defaultDeliveryDays.value = 1;
        if (defaultTrialDays) defaultTrialDays.value = 1;
        showModernAlert('Perfume Shop preset applied! Trial and delivery dates disabled.', 'success');
        break;

      case 'laundry':
        // Laundry Shop: Disable trial date, keep delivery date
        if (enableTrialDate) enableTrialDate.checked = false;
        if (enableDeliveryDate) enableDeliveryDate.checked = true;
        if (enableAdvancePayment) enableAdvancePayment.checked = true;
        if (enableCustomerNotes) enableCustomerNotes.checked = true;
        if (enableEmployeeAssignment) enableEmployeeAssignment.checked = false;
        if (defaultDeliveryDays) defaultDeliveryDays.value = 2;
        if (defaultTrialDays) defaultTrialDays.value = 1;
        showModernAlert('Laundry Shop preset applied! Trial date disabled, delivery date enabled.', 'success');
        break;

      case 'general':
        // General Store: Basic features only
        if (enableTrialDate) enableTrialDate.checked = false;
        if (enableDeliveryDate) enableDeliveryDate.checked = false;
        if (enableAdvancePayment) enableAdvancePayment.checked = true;
        if (enableCustomerNotes) enableCustomerNotes.checked = true;
        if (enableEmployeeAssignment) enableEmployeeAssignment.checked = false;
        if (defaultDeliveryDays) defaultDeliveryDays.value = 1;
        if (defaultTrialDays) defaultTrialDays.value = 1;
        showModernAlert('General Store preset applied! Basic billing features only.', 'success');
        break;
    }
    
    // Trigger field state updates after preset changes
    const updateFieldStates = () => {
      const defaultTrialDays = document.getElementById('defaultTrialDays');
      const defaultDeliveryDays = document.getElementById('defaultDeliveryDays');
      
      if (defaultTrialDays) {
        defaultTrialDays.disabled = !enableTrialDate?.checked;
        if (!enableTrialDate?.checked) {
          defaultTrialDays.value = '';
        } else if (!defaultTrialDays.value) {
          defaultTrialDays.value = '3';
        }
      }
      
      if (defaultDeliveryDays) {
        defaultDeliveryDays.disabled = !enableDeliveryDate?.checked;
        if (!enableDeliveryDate?.checked) {
          defaultDeliveryDays.value = '';
        } else if (!defaultDeliveryDays.value) {
          defaultDeliveryDays.value = '3';
        }
      }
    };
    
    updateFieldStates();
  }

  // Load settings when the section is accessed
  loadShopSettings();
  initializeAutocomplete();
  initializeChangePassword();
  initializePresets();
  initializeConditionalFields(); // Call the new function here
}

// Make functions globally available
window.initializeShopSettings = initializeShopSettings; 