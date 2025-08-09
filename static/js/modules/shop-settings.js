// Shop Settings Module

function initializeShopSettings() {
  const shopSettingsForm = document.getElementById('shopSettingsForm');
  const shopSettingsLoadingOverlay = document.getElementById('shopSettingsLoadingOverlay');
  const shopSettingsDisplay = document.getElementById('shopSettingsDisplay');
  const shopSettingsContent = document.getElementById('shopSettingsContent');
  const isMobile = window.innerWidth <= 1024;

  // Load shop settings on page load
  function loadShopSettings() {
    if (shopSettingsLoadingOverlay) {
      shopSettingsLoadingOverlay.classList.remove('hidden');
    }
    
    fetch('/api/shop-settings')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.settings) {
          const settings = data.settings;
          
          // Populate form fields
          const shopNameField = document.getElementById('shopName');
          const shopMobileField = document.getElementById('shopMobile');
          const shopCityField = document.getElementById('shopCity');
          const shopAreaField = document.getElementById('shopArea');
          const shopAddressField = document.getElementById('shopAddress');
          const shopTRNField = document.getElementById('shopTRN');
          const useDynamicInvoiceTemplateField = document.getElementById('useDynamicInvoiceTemplate');
          
          if (shopNameField) shopNameField.value = settings.shop_name || '';
          if (shopMobileField) shopMobileField.value = settings.shop_mobile || '';
          if (shopCityField) shopCityField.value = settings.city || '';
          if (shopAreaField) shopAreaField.value = settings.area || '';
          if (shopAddressField) shopAddressField.value = settings.address || '';
          if (shopTRNField) shopTRNField.value = settings.trn || '';
          if (useDynamicInvoiceTemplateField) useDynamicInvoiceTemplateField.checked = settings.use_dynamic_invoice_template || false;
          
          // Show form with animation
          if (shopSettingsForm) {
            shopSettingsForm.classList.remove('opacity-0', 'translate-y-4');
          }
          
          // Update display section
          if (shopSettingsDisplay && shopSettingsContent) {
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
              </div>
            `;
            shopSettingsDisplay.classList.remove('opacity-0', 'translate-y-4');
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
      use_dynamic_invoice_template: shopSettingsForm?.querySelector('#useDynamicInvoiceTemplate')?.checked || false
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
          cityInput.value = e.target.getAttribute('data-city');
          cityDropdown.classList.add('hidden');
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
          const response = await fetch('/api/areas');
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
          areaInput.value = e.target.getAttribute('data-area');
          areaDropdown.classList.add('hidden');
        }
      });

      // Hide dropdown when clicking outside
      document.addEventListener('click', function(e) {
        if (!areaInput.contains(e.target) && !areaDropdown.contains(e.target)) {
          areaDropdown.classList.add('hidden');
        }
      });
    }
  }

  // Initialize when the section is shown
  const shopSettingsBtn = document.querySelector('[data-go="shopSettingsSec"]');
  if (shopSettingsBtn) {
    shopSettingsBtn.addEventListener('click', () => {
      // Load settings when the section is accessed
      setTimeout(() => {
        loadShopSettings();
        initializeAutocomplete();
      }, 100);
    });
  }

  // Also load on initial page load if this section is visible
  if (document.getElementById('shopSettingsSec') && !document.getElementById('shopSettingsSec').classList.contains('hidden')) {
    loadShopSettings();
    initializeAutocomplete();
  }
}

// Make functions globally available
window.initializeShopSettings = initializeShopSettings;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeShopSettings);
} else {
  initializeShopSettings();
} 