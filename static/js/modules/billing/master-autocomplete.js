;(function () {
  const ns = {};

  // State
  let employees = [];
  let masterDropdown;
  let masterInput;
  let masterInputMobile;

  ns.init = function () {
    masterInput = document.getElementById('masterName');
    masterInputMobile = document.getElementById('masterNameMobile');

    if (!masterInput && !masterInputMobile) {
      return;
    }

    // Initialize the system
    initializeBillingSystem();

    // Event listeners for desktop
    if (masterInput) {
      masterInput.addEventListener('input', function () {
        const query = this.value;
        const filteredEmployees = filterEmployees(query);

        if (filteredEmployees.length > 0) {
          renderDropdownOptions(filteredEmployees);
          showDropdown(this);
        } else {
          hideDropdown();
        }
      });

      masterInput.addEventListener('focus', function () {
        if (this.value.trim()) {
          const filteredEmployees = filterEmployees(this.value);
          if (filteredEmployees.length > 0) {
            renderDropdownOptions(filteredEmployees);
            showDropdown(this);
          }
        }
      });
    }

    // Event listeners for mobile
    if (masterInputMobile) {
      masterInputMobile.addEventListener('input', function () {
        const query = this.value;
        const filteredEmployees = filterEmployees(query);

        if (filteredEmployees.length > 0) {
          renderDropdownOptions(filteredEmployees);
          showDropdown(this);
        } else {
          hideDropdown();
        }
      });

      masterInputMobile.addEventListener('focus', function () {
        if (this.value.trim()) {
          const filteredEmployees = filterEmployees(this.value);
          if (filteredEmployees.length > 0) {
            renderDropdownOptions(filteredEmployees);
            showDropdown(this);
          }
        }
      });
    }

    // Global click listener to hide dropdown
    document.addEventListener('click', function (e) {
      // Don't hide if clicking on a master option
      if (e.target.closest('.master-option')) {
        return;
      }

      // Don't hide if clicking on either input
      if ((masterInput && masterInput.contains(e.target)) ||
        (masterInputMobile && masterInputMobile.contains(e.target))) {
        return;
      }

      // Hide only if clicking outside both inputs and dropdown
      if ((!masterInput || !masterInput.contains(e.target)) &&
        (!masterInputMobile || !masterInputMobile.contains(e.target)) &&
        (!masterDropdown || !masterDropdown.contains(e.target))) {
        hideDropdown();
      }
    });
  };

  // Create dropdown container
  function createMasterDropdown() {
    masterDropdown = document.createElement('div');
    masterDropdown.className = 'master-suggestion';
    masterDropdown.style.cssText = 'position: fixed; z-index: 99999 !important; background: #1f2937; border: 1px solid #374151; border-radius: 8px; max-height: 240px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);';
    masterDropdown.style.display = 'none';
    document.body.appendChild(masterDropdown);

    // Prevent dropdown from hiding when clicking inside it
    masterDropdown.addEventListener('click', function (e) {
      e.stopPropagation();
    });
  }

  // Load employees
  async function loadEmployees() {
    try {
      const response = await fetch('/api/employees');
      employees = await response.json();

      // Make employees available globally for debugging
      window.allEmployees = employees;

      // Set default owner if available
      ns.setDefaultOwner();
    } catch (error) {
      console.error('✓ Error loading employees:', error);
    }
  }

  // Set default owner
  ns.setDefaultOwner = function () {
    // First, check if there's a default employee configured in shop settings
    // Assuming billingConfig is available globally or imported
    // We should check if window.billingConfig exists
    const billingConfig = window.billingConfig || {};

    if (billingConfig && billingConfig.default_employee_id) {
      const defaultEmployee = employees.find(emp =>
        (emp.employee_id || emp.id) == billingConfig.default_employee_id
      );
      if (defaultEmployee) {
        // Set the default employee from shop settings
        setMasterValue(defaultEmployee);
        return;
      }
    }

    // Fallback to owner or first employee if no shop settings default
    const owner = employees.find(emp => emp.position === 'Owner');
    if (owner) {
      setMasterValue(owner);
    } else {
      // If no owner found, set the first available employee as default
      if (employees.length > 0) {
        const firstEmployee = employees[0];
        setMasterValue(firstEmployee);
        console.log('Billing System: Set first employee as default:', firstEmployee.name);
      }
    }
  };

  // Helper to set master value
  function setMasterValue(employee) {
    if (masterInput) {
      masterInput.value = employee.name;
      masterInput.setAttribute('data-selected-master', JSON.stringify({
        master_id: employee.employee_id || employee.id,
        master_name: employee.name
      }));
    }

    if (masterInputMobile) {
      masterInputMobile.value = employee.name;
      masterInputMobile.setAttribute('data-selected-master', JSON.stringify({
        master_id: employee.employee_id || employee.id,
        master_name: employee.name
      }));
    }

    // Set global selected master ID
    window.selectedMasterId = employee.employee_id || employee.id;
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
      option.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const masterId = this.getAttribute('data-master-id');
        const masterName = this.getAttribute('data-master-name');

        window.selectedMasterId = masterId;

        // Update both inputs if they exist
        if (masterInput) {
          masterInput.value = masterName;
          masterInput.setAttribute('data-selected-master', JSON.stringify({
            master_id: masterId,
            master_name: masterName
          }));
        }

        if (masterInputMobile) {
          masterInputMobile.value = masterName;
          masterInputMobile.setAttribute('data-selected-master', JSON.stringify({
            master_id: masterId,
            master_name: masterName
          }));
        }

        hideDropdown();
      });
    });
  }

  // Show dropdown
  function showDropdown(activeInput) {
    if (!masterDropdown) createMasterDropdown();
    if (!masterDropdown || !masterDropdown.style) return;

    // Calculate position relative to input
    const inputRect = activeInput.getBoundingClientRect();

    masterDropdown.style.left = inputRect.left + 'px';
    masterDropdown.style.top = (inputRect.bottom + 4) + 'px';
    masterDropdown.style.width = inputRect.width + 'px';
    masterDropdown.style.minWidth = '200px'; // Ensure minimum width

    masterDropdown.style.display = 'block';
    masterDropdown.style.opacity = '0';
    masterDropdown.style.transform = 'translateY(-10px)';

    // Animate in
    setTimeout(() => {
      if (masterDropdown && masterDropdown.style) {
        masterDropdown.style.transition = 'all 0.2s ease';
        masterDropdown.style.opacity = '1';
        masterDropdown.style.transform = 'translateY(0)';
      }
    }, 10);
  }

  // Hide dropdown
  function hideDropdown() {
    if (masterDropdown && masterDropdown.style) {
      masterDropdown.style.transition = 'all 0.2s ease';
      masterDropdown.style.opacity = '0';
      masterDropdown.style.transform = 'translateY(-10px)';

      setTimeout(() => {
        if (masterDropdown && masterDropdown.style) {
          masterDropdown.style.display = 'none';
          // Remove from DOM to prevent memory leaks
          if (masterDropdown.parentNode) {
            masterDropdown.parentNode.removeChild(masterDropdown);
          }
          masterDropdown = null;
        }
      }, 200);
    }
  }

  // Load billing configuration first, then employees
  async function initializeBillingSystem() {
    // Load billing configuration first
    // We assume loadBillingConfiguration is global or we need to wait for it.
    // In the original code, it called loadBillingConfiguration() which was likely global.
    if (typeof window.loadBillingConfiguration === 'function') {
        await window.loadBillingConfiguration();
    }
    
    // Then load employees (which will use the billing config)
    await loadEmployees();
  }

  // Make selected master ID available globally
  ns.getSelectedMasterId = function () {
    return window.selectedMasterId;
  };

  // Test function for master dropdown
  ns.testMasterDropdown = function () {
    if (masterInputMobile) {
      masterInputMobile.focus();
      masterInputMobile.value = 'test';
      masterInputMobile.dispatchEvent(new Event('input'));
    }
  };

  // Test function to check master selection status
  ns.testMasterSelection = function () {
    // const masterNameElement = document.getElementById('masterName');
    // const masterNameMobileElement = document.getElementById('masterNameMobile');
  };
  
  // Backward compatibility for global functions
  window.setDefaultOwner = ns.setDefaultOwner;
  window.getSelectedMasterId = ns.getSelectedMasterId;
  window.testMasterDropdown = ns.testMasterDropdown;
  window.testMasterSelection = ns.testMasterSelection;

  window.MasterAutocomplete = ns;
})();
