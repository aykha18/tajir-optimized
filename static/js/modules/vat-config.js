// VAT Configuration Module

// Default VAT settings
let vatSettings = {
  defaultPercent: 5,
  displayOption: 'show' // 'show' or 'hide_zero'
};

// Initialize VAT configuration
function initVatConfig() {
  loadVatSettings();
  setupVatConfigHandlers();
  updateVatDisplay();
}

// Load VAT settings from localStorage
function loadVatSettings() {
  const savedSettings = localStorage.getItem('vatSettings');
  if (savedSettings) {
    try {
      vatSettings = { ...vatSettings, ...JSON.parse(savedSettings) };
    } catch (e) {
      console.warn('Failed to parse saved VAT settings:', e);
    }
  }
  
  // Update input fields with loaded settings
  const defaultVatInput = document.getElementById('defaultVatPercent');
  const displayOptionSelect = document.getElementById('vatDisplayOption');
  
  if (defaultVatInput) defaultVatInput.value = vatSettings.defaultPercent;
  if (displayOptionSelect) displayOptionSelect.value = vatSettings.displayOption;
  
  // Update VAT input fields with default value
  updateVatInputs();
}

// Save VAT settings to localStorage
function saveVatSettings() {
  localStorage.setItem('vatSettings', JSON.stringify(vatSettings));
}

// Setup VAT configuration event handlers
function setupVatConfigHandlers() {
  // Desktop VAT config button
  const vatConfigBtn = document.getElementById('vatConfigBtn');
  if (vatConfigBtn) {
    vatConfigBtn.addEventListener('click', openVatConfigModal);
  }
  
  // Mobile VAT config button
  const vatConfigBtnMobile = document.getElementById('vatConfigBtnMobile');
  if (vatConfigBtnMobile) {
    vatConfigBtnMobile.addEventListener('click', openVatConfigModal);
  }
  
  // Modal close button
  const closeVatConfig = document.getElementById('closeVatConfig');
  if (closeVatConfig) {
    closeVatConfig.addEventListener('click', closeVatConfigModal);
  }
  
  // Cancel button
  const cancelVatConfig = document.getElementById('cancelVatConfig');
  if (cancelVatConfig) {
    cancelVatConfig.addEventListener('click', closeVatConfigModal);
  }
  
  // Save button
  const saveVatConfig = document.getElementById('saveVatConfig');
  if (saveVatConfig) {
    saveVatConfig.addEventListener('click', handleSaveVatConfig);
  }
  
  // Close modal when clicking outside
  const vatConfigModal = document.getElementById('vatConfigModal');
  if (vatConfigModal) {
    vatConfigModal.addEventListener('click', (e) => {
      if (e.target === vatConfigModal) {
        closeVatConfigModal();
      }
    });
  }
}

// Open VAT configuration modal
function openVatConfigModal() {
  const modal = document.getElementById('vatConfigModal');
  if (modal) {
    modal.classList.remove('hidden');
    // Focus on the default VAT input
    const defaultVatInput = document.getElementById('defaultVatPercent');
    if (defaultVatInput) {
      setTimeout(() => defaultVatInput.focus(), 100);
    }
  }
}

// Close VAT configuration modal
function closeVatConfigModal() {
  const modal = document.getElementById('vatConfigModal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

// Handle saving VAT configuration
function handleSaveVatConfig() {
  const defaultVatInput = document.getElementById('defaultVatPercent');
  const displayOptionSelect = document.getElementById('vatDisplayOption');
  
  if (!defaultVatInput || !displayOptionSelect) return;
  
  const newDefaultPercent = parseFloat(defaultVatInput.value) || 0;
  const newDisplayOption = displayOptionSelect.value;
  
  // Validate input
  if (newDefaultPercent < 0 || newDefaultPercent > 100) {
    if (window.showSimpleToast) {
      window.showSimpleToast('VAT percentage must be between 0 and 100', 'error');
    }
    return;
  }
  
  // Update settings
  vatSettings.defaultPercent = newDefaultPercent;
  vatSettings.displayOption = newDisplayOption;
  
  // Save to localStorage
  saveVatSettings();
  
  // Update VAT input fields
  updateVatInputs();
  
  // Update VAT display
  updateVatDisplay();
  
  // Close modal
  closeVatConfigModal();
  
  // Show success message
  if (window.showSimpleToast) {
    window.showSimpleToast('VAT settings saved successfully!', 'success');
  }
}

// Update VAT input fields with default value
function updateVatInputs() {
  const vatInputs = [
    document.getElementById('vatPercent'),
    document.getElementById('vatPercentMobile')
  ];
  
  vatInputs.forEach(input => {
    if (input) {
      input.value = vatSettings.defaultPercent;
    }
  });
}

// Update VAT display based on current settings
function updateVatDisplay() {
  const vatSummaryRow = document.getElementById('vatSummaryRow');
  const vatLabel = document.getElementById('vatLabel');
  
  if (!vatSummaryRow || !vatLabel) return;
  
  // Get current VAT percentage from the active input
  let currentVatPercent = 5; // Default fallback
  const activeVatInput = document.getElementById('vatPercent') || document.getElementById('vatPercentMobile');
  if (activeVatInput) {
    currentVatPercent = parseFloat(activeVatInput.value) || 0;
  }
  
  // Check if we should hide VAT
  const shouldHideVat = vatSettings.displayOption === 'hide_zero' && currentVatPercent === 0;
  
  if (shouldHideVat) {
    vatSummaryRow.style.display = 'none';
  } else {
    vatSummaryRow.style.display = 'flex';
    // Update the label to show current percentage
    vatLabel.textContent = `Tax (${currentVatPercent}%):`;
  }
}

// Function to check if VAT should be displayed (for external use)
function shouldDisplayVat(vatPercent) {
  if (vatSettings.displayOption === 'hide_zero' && vatPercent === 0) {
    return false;
  }
  return true;
}

// Function to get default VAT percentage (for external use)
function getDefaultVatPercent() {
  return vatSettings.defaultPercent;
}

// Function to update VAT display when VAT input changes (for external use)
function onVatInputChange() {
  updateVatDisplay();
}

// Make functions globally available
window.initVatConfig = initVatConfig;
window.shouldDisplayVat = shouldDisplayVat;
window.getDefaultVatPercent = getDefaultVatPercent;
window.onVatInputChange = onVatInputChange;
window.openVatConfigModal = openVatConfigModal;
