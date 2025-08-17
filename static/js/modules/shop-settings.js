// Shop Settings Module

function initializeShopSettings() {
  console.log('Initializing shop settings...');
  const shopSettingsForm = document.getElementById('shopSettingsForm');
  const shopSettingsLoadingOverlay = document.getElementById('shopSettingsLoadingOverlay');
  const shopSettingsDisplay = document.getElementById('shopSettingsDisplay');
  const shopSettingsContent = document.getElementById('shopSettingsContent');
  const shopSettingsSection = document.getElementById('shopSettingsSec');
  const isMobile = window.innerWidth <= 1024;

  // Ensure the shop settings section is visible
  if (shopSettingsSection) {
    shopSettingsSection.classList.remove('hidden');
    console.log('Shop settings section made visible');
  } else {
    console.error('Shop settings section not found');
  }

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
      payment_mode: shopSettingsForm?.querySelector('input[name="paymentMode"]:checked')?.value || 'advance'
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

  // Load settings when the section is accessed
  loadShopSettings();
  initializeAutocomplete();
  initializeChangePassword();
}

// Make functions globally available
window.initializeShopSettings = initializeShopSettings; 