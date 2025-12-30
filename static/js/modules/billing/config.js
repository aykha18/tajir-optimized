// Billing Configuration Module
// Handles loading, applying, and managing billing settings

;(function() {
    // Billing configuration object
    let billingConfig = {
        enable_trial_date: true,
        enable_delivery_date: true,
        enable_advance_payment: true,
        enable_customer_notes: true,
        enable_employee_assignment: true,
        default_delivery_days: 3
    };

    // Helper to get combined phone number (wraps CountryCode)
    function getCombinedPhoneNumber() { 
        return window.CountryCode.getCombinedPhoneNumber(); 
    }
    
    // Helper to load country codes (wraps CountryCode)
    async function loadCountryCodes() { 
        return window.CountryCode.loadCountryCodes(); 
    }

    // Helper to parse phone number into code and local part (wraps CountryCode)
    function parsePhoneNumber(fullNumber) { 
        return window.CountryCode.parsePhoneNumber(fullNumber); 
    }

    // Setup Country Code Selector (wraps CountryCode)
    function setupCountryCodeSelector() { 
        return window.CountryCode.setupPicker(); 
    }

    // Load billing configuration from shop settings
    async function loadBillingConfiguration() {
        try {
            // Loading billing configuration
            const response = await fetch('/api/shop-settings/billing-config');
            const data = await response.json();

            if (data.success) {
                billingConfig = data.config;
                // Update global reference
                window.billingConfig = billingConfig;
                // Billing config loaded successfully
                applyBillingConfiguration();
            } else {
                // No billing config found, using defaults
                applyBillingConfiguration();
            }
        } catch (error) {
            console.error('❌ Billing System: Error loading billing configuration:', error);
            // Use default configuration
            applyBillingConfiguration();
        }
    }

    // Apply billing configuration to show/hide fields
    function applyBillingConfiguration() {
        // Ensure global config is up to date
        window.billingConfig = billingConfig;

        // Trial Date field
        const trialDateField = document.getElementById('trialDate');
        const trialDateContainer = trialDateField?.closest('.form-group') || trialDateField?.parentElement;

        if (trialDateContainer) {
            if (billingConfig.enable_trial_date) {
                trialDateContainer.style.display = '';
                // Set default trial date if field is enabled and no value set
                if (trialDateField && !trialDateField.value) {
                    const today = new Date();
                    const trial = new Date();
                    const defaultDays = billingConfig.default_trial_days || 2; // Use trial days, fallback to 2
                    trial.setDate(today.getDate() + defaultDays);
                    trialDateField.value = trial.toISOString().split('T')[0];
                }
            } else {
                trialDateContainer.style.display = 'none';
            }
        }

        // Delivery Date field
        const deliveryDateField = document.getElementById('deliveryDate');
        const deliveryDateContainer = deliveryDateField?.closest('.form-group') || deliveryDateField?.parentElement;

        if (deliveryDateContainer) {
            if (billingConfig.enable_delivery_date) {
                deliveryDateContainer.style.display = '';
                // Set default delivery date if field is enabled
                if (deliveryDateField && !deliveryDateField.value) {
                    const today = new Date();
                    const delivery = new Date();
                    const defaultDays = billingConfig.default_delivery_days || 3;
                    delivery.setDate(today.getDate() + defaultDays);
                    const newDeliveryDate = delivery.toISOString().split('T')[0];
                    deliveryDateField.value = newDeliveryDate;
                }
            } else {
                deliveryDateContainer.style.display = 'none';
            }
        }

        // Advance Payment field
        const advancePaymentField = document.getElementById('advancePayment');
        const advancePaymentContainer = advancePaymentField?.closest('.form-group') || advancePaymentField?.parentElement;

        if (advancePaymentContainer) {
            if (billingConfig.enable_advance_payment) {
                advancePaymentContainer.style.display = '';
            } else {
                advancePaymentContainer.style.display = 'none';
                // Clear advance payment if disabled
                if (advancePaymentField) {
                    advancePaymentField.value = '';
                    if (window.updateTotals) window.updateTotals();
                }
            }
        }

        // Customer Notes field
        const customerNotesField = document.getElementById('billNotes');
        const customerNotesContainer = customerNotesField?.closest('.form-group') || customerNotesField?.parentElement;

        if (customerNotesContainer) {
            if (billingConfig.enable_customer_notes) {
                customerNotesContainer.style.display = '';
            } else {
                customerNotesContainer.style.display = 'none';
                // Clear customer notes if disabled
                if (customerNotesField) {
                    customerNotesField.value = '';
                }
            }
        }

        // Employee Assignment field
        const employeeField = document.getElementById('masterName');
        const employeeContainer = employeeField?.closest('.form-group') || employeeField?.parentElement;

        if (employeeContainer) {
            if (billingConfig.enable_employee_assignment) {
                employeeContainer.style.display = '';
                // Populate employee dropdown if enabled
                populateEmployeeDropdown();
            } else {
                // Don't hide the field, just clear it and remove datalist
                if (employeeField) {
                    employeeField.value = '';
                    employeeField.removeAttribute('list');
                    employeeField.removeAttribute('data-selected-employee-id');
                }
                // Remove datalist if it exists
                const datalist = document.getElementById('employeeDatalist');
                if (datalist) {
                    datalist.remove();
                }
            }
        }

        // Set basic default dates (bill date and bill number) after configuration is applied
        setBasicDefaultDates();

        // Re-apply default employee if employees are already loaded
        if (window.allEmployees && window.allEmployees.length > 0) {
            // Call the global setDefaultOwner function if it exists
            if (typeof window.setDefaultOwner === 'function') {
                window.setDefaultOwner();
            }
        }
    }

    // Get next bill number from API
    async function getNextBillNumber() {
        try {
            const response = await fetch('/api/next-bill-number');
            const data = await response.json();
            return data.next_number;
        } catch (error) {
            console.error('Error getting next bill number:', error);
            return null;
        }
    }

    // Set basic default dates (bill date and bill number)
    async function setBasicDefaultDates() {
        const today = new Date();

        const billDateElement = document.getElementById('billDate');
        const billNumberElement = document.getElementById('billNumber');

        // Set default bill date to today
        if (billDateElement) {
            billDateElement.value = today.toISOString().slice(0, 10);
        }

        // Set auto-generated bill number
        if (billNumberElement) {
            const nextBillNumber = await getNextBillNumber();
            if (nextBillNumber) {
                billNumberElement.value = nextBillNumber;
            }
        }
    }

    // Populate employee dropdown with available employees
    async function populateEmployeeDropdown() {
        const employeeField = document.getElementById('masterName');
        if (!employeeField) {
            return;
        }

        try {
            const response = await fetch('/api/employees');
            const employees = await response.json();

            // Create or get existing datalist for autocomplete
            let datalist = document.getElementById('employeeDatalist');
            if (!datalist) {
                datalist = document.createElement('datalist');
                datalist.id = 'employeeDatalist';
                document.body.appendChild(datalist);
            }

            // Clear existing options
            datalist.innerHTML = '';

            // Add employee options to datalist
            if (Array.isArray(employees)) {
                employees.forEach(emp => {
                    const option = document.createElement('option');
                    option.value = emp.name || `Employee #${emp.employee_id}`;
                    option.setAttribute('data-employee-id', emp.employee_id || emp.id || '');
                    datalist.appendChild(option);
                });

                // Set the datalist for the input field
                employeeField.setAttribute('list', 'employeeDatalist');

                // Preselect default employee if configured
                if (billingConfig.default_employee_id) {
                    const defaultEmployee = employees.find(emp =>
                        (emp.employee_id || emp.id) == billingConfig.default_employee_id
                    );
                    if (defaultEmployee) {
                        employeeField.value = defaultEmployee.name || `Employee #${defaultEmployee.employee_id}`;
                        employeeField.setAttribute('data-selected-employee-id', defaultEmployee.employee_id || defaultEmployee.id);
                    }
                }
            }
        } catch (error) {
            console.error('Error populating employee dropdown:', error);
        }
    }

    // Set default billing dates (delivery and trial) based on config
    async function setDefaultBillingDates() {
        const today = new Date();
        const defaultDays = billingConfig?.default_delivery_days || 3;
        const deliveryDate = new Date(today.getTime() + defaultDays * 24 * 60 * 60 * 1000); // Configurable days from now

        const deliveryDateElement = document.getElementById('deliveryDate');
        const trialDateElement = document.getElementById('trialDate');

        // Only set delivery date if it's enabled in billing config
        if (deliveryDateElement && billingConfig?.enable_delivery_date) {
            deliveryDateElement.value = deliveryDate.toISOString().slice(0, 10);
        }

        // Only set trial date if it's enabled in billing config
        if (trialDateElement && billingConfig?.enable_trial_date) {
            // Trial date should be the same as delivery date
            trialDateElement.value = deliveryDate.toISOString().slice(0, 10);
        }
    }

    // Initialize payment mode
    async function initializePaymentMode() {
        try {
            const response = await fetch('/api/shop-settings/payment-mode');
            const data = await response.json();

            if (data.success) {
                const paymentMode = data.payment_mode;
                window.paymentMode = paymentMode; // Store globally

                // Hide/show advance payment fields based on mode
                const advanceFields = [
                    document.getElementById('billAdvPaid'),
                    document.getElementById('billAdvPaidMobile'),
                    document.getElementById('totalAdvancePaid')
                ];

                const advanceLabels = [
                    document.querySelector('label[for="billAdvPaid"]'),
                    document.querySelector('label[for="billAdvPaidMobile"]'),
                    document.querySelector('label[for="totalAdvancePaid"]')
                ];

                if (paymentMode === 'full') {
                    // Keep advance payment fields visible but disable them
                    advanceFields.forEach(field => {
                        if (field) {
                            field.style.display = '';
                            field.disabled = true;
                            field.value = '0';
                        }
                    });

                    advanceLabels.forEach(label => {
                        if (label) {
                            label.style.display = '';
                        }
                    });

                    // Keep table header visible
                    const advHeader = document.getElementById('advHeader');
                    if (advHeader) {
                        advHeader.style.display = '';
                    }

                    // Update the "Total Amount Paid" label for full payment mode
                    const totalAmountLabel = document.querySelector('.bill-summary-row:last-child .text-neutral-400');
                    if (totalAmountLabel) {
                        totalAmountLabel.textContent = 'Total Amount Paid:';
                    }

                    // Set all advance payments to 0
                    const bill = window.bill || [];
                    bill.forEach(item => {
                        item.advance_paid = 0;
                    });

                    // Disable total advance input
                    const totalAdvanceInput = document.getElementById('totalAdvancePaid');
                    if (totalAdvanceInput) {
                        totalAdvanceInput.disabled = true;
                        totalAdvanceInput.value = '0';
                    }

                    // Update totals
                    if (window.BillingTotals && window.BillingTotals.updateTotals) {
                        window.BillingTotals.updateTotals();
                    } else if (window.updateTotals) {
                        window.updateTotals();
                    }
                } else {
                    // Show and enable advance payment fields
                    advanceFields.forEach(field => {
                        if (field) {
                            field.style.display = '';
                            field.disabled = false;
                            field.value = '';
                        }
                    });

                    advanceLabels.forEach(label => {
                        if (label) {
                            label.style.display = '';
                        }
                    });

                    // Show table header
                    const advHeader = document.getElementById('advHeader');
                    if (advHeader) {
                        advHeader.style.display = '';
                    }

                    // Enable total advance input
                    const totalAdvanceInput = document.getElementById('totalAdvancePaid');
                    if (totalAdvanceInput) {
                        totalAdvanceInput.disabled = false;
                    }

                    // Update the "Total Amount Paid" label for advance payment mode
                    const totalAmountLabel = document.querySelector('.bill-summary-row:last-child .text-neutral-400');
                    if (totalAmountLabel) {
                        totalAmountLabel.textContent = 'Total Amount Due:';
                    }
                }
            }
        } catch (error) {
            console.error('Error loading payment mode:', error);
            // Default to advance mode if error
            window.paymentMode = 'advance';
        }
    }

    // Smart Defaults Logic
    function setupSmartDefaults() {
        const billDateInput = document.getElementById('billDate');
        const deliveryDateInput = document.getElementById('deliveryDate');

        if (!billDateInput || !deliveryDateInput) {
            return;
        }

        // Set default bill date to today if not set
        if (!billDateInput.value) {
            const today = new Date().toISOString().split('T')[0];
            billDateInput.value = today;
        }

        // Set default delivery date to bill date + configurable days (only if enabled)
        function updateDeliveryDate() {
            if (billDateInput.value && billingConfig?.enable_delivery_date) {
                const billDate = new Date(billDateInput.value);
                const deliveryDate = new Date(billDate);
                const defaultDays = billingConfig?.default_delivery_days || 3;
                deliveryDate.setDate(deliveryDate.getDate() + defaultDays);
                const newDeliveryDate = deliveryDate.toISOString().split('T')[0];
                deliveryDateInput.value = newDeliveryDate;
            }
        }

        // Update delivery date when bill date changes (only if enabled)
        if (billingConfig?.enable_delivery_date) {
            // Remove existing listener if any
            billDateInput.removeEventListener('change', updateDeliveryDate);
            billDateInput.addEventListener('change', updateDeliveryDate);

            // Set initial delivery date if empty
            if (!deliveryDateInput.value) {
                updateDeliveryDate();
            }
        }

        // Set default trial date to delivery date (same as delivery date) - only if enabled
        const trialDateInput = document.getElementById('trialDate');
        if (trialDateInput && billingConfig?.enable_trial_date) {
            function updateTrialDate() {
                if (billDateInput.value) {
                    const billDate = new Date(billDateInput.value);
                    const trialDate = new Date(billDate);
                    const defaultDays = billingConfig?.default_trial_days || 2; // Use trial days, fallback to 2
                    trialDate.setDate(trialDate.getDate() + defaultDays);
                    trialDateInput.value = trialDate.toISOString().split('T')[0];
                }
            }

            // Keep trial date in sync when delivery or bill date changes
            deliveryDateInput.removeEventListener('change', updateTrialDate);
            deliveryDateInput.addEventListener('change', updateTrialDate);
            billDateInput.removeEventListener('change', updateTrialDate);
            billDateInput.addEventListener('change', updateTrialDate);
            
            if (!trialDateInput.value) {
                updateTrialDate();
            }
        }
    }

    // Expose functions globally
    window.billingConfig = billingConfig;
    window.BillingConfig = {
        load: loadBillingConfiguration,
        apply: applyBillingConfiguration,
        setupCountryCode: setupCountryCodeSelector,
        loadCountryCodes: loadCountryCodes,
        getCombinedPhone: getCombinedPhoneNumber,
        parsePhone: parsePhoneNumber,
        getNextBillNumber: getNextBillNumber,
        setBasicDefaultDates: setBasicDefaultDates,
        populateEmployeeDropdown: populateEmployeeDropdown,
        setDefaultBillingDates: setDefaultBillingDates,
        initializePaymentMode: initializePaymentMode,
        setupSmartDefaults: setupSmartDefaults
    };

    // Backward compatibility aliases
    window.loadBillingConfiguration = loadBillingConfiguration;
    window.applyBillingConfiguration = applyBillingConfiguration;
    window.setupCountryCodeSelector = setupCountryCodeSelector;
    window.loadCountryCodes = loadCountryCodes;
    window.getCombinedPhoneNumber = getCombinedPhoneNumber;
    window.parsePhoneNumber = parsePhoneNumber;
    window.getNextBillNumber = getNextBillNumber;
    window.setBasicDefaultDates = setBasicDefaultDates;
    window.populateEmployeeDropdown = populateEmployeeDropdown;
    window.setDefaultBillingDates = setDefaultBillingDates;
    window.initializePaymentMode = initializePaymentMode;
    window.setupSmartDefaults = setupSmartDefaults;

})();
