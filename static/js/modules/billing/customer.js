/**
 * Billing Customer Module
 * Handles customer selection, searching, creation, and field population.
 */
(function() {
    'use strict';

    function getCustomerInputs() {
        const customer_name = document.getElementById('billCustomer')?.value || '';
        const customer_phone = window.getCombinedPhoneNumber() || '';
        const country_code = document.getElementById('countryCodeText')?.textContent.trim() || '';
        const customer_city = document.getElementById('billCity')?.value || '';
        const customer_area = document.getElementById('billArea')?.value || '';
        const customer_trn = document.getElementById('billTRN')?.value || '';
        const customer_type = document.getElementById('billCustomerType')?.value || 'Individual';
        const business_name = document.getElementById('billBusinessName')?.value || '';
        const business_address = document.getElementById('billBusinessAddress')?.value || '';
        return {
            customer_name,
            customer_phone,
            country_code,
            customer_city,
            customer_area,
            customer_trn,
            customer_type,
            business_name,
            business_address,
        };
    }

    async function fetchCustomerByMobile(phone) {
        try {
            const response = await fetch(`/api/customers?phone=${encodeURIComponent(phone)}`);
            if (response.ok) {
                const customers = await response.json();
                if (Array.isArray(customers) && customers.length > 0) {
                    return customers[0]; // Return the first matching customer
                }
            }
            return null;
        } catch (error) {
            console.error('Error fetching customer by mobile:', error);
            return null;
        }
    }

    async function populateCustomerFields(customer) {
        const billCustomerElement = document.getElementById('billCustomer');
        const billMobileElement = document.getElementById('billMobile');
        const billCityElement = document.getElementById('billCity');
        const billAreaElement = document.getElementById('billArea');
        const billTRNElement = document.getElementById('billTRN');
        const billCustomerTypeElement = document.getElementById('billCustomerType');
        const billBusinessNameElement = document.getElementById('billBusinessName');
        const billBusinessAddressElement = document.getElementById('billBusinessAddress');

        if (billCustomerElement) billCustomerElement.value = customer.name || '';

        // Handle phone number parsing
        if (billMobileElement) {
            const fullPhone = customer.phone || '';
            const { code, number } = window.parsePhoneNumber ? window.parsePhoneNumber(fullPhone) : { code: '', number: fullPhone };

            // Update UI
            const codeElement = document.getElementById('countryCodeText');
            const flagElement = document.getElementById('countryFlag');

            if (codeElement) codeElement.textContent = code;

            // Find flag
            const country = (window.countryCodes || []).find(c => c.code === code);
            if (flagElement && country) flagElement.textContent = country.flag;

            billMobileElement.value = number;
        }
        if (billCityElement) billCityElement.value = customer.city || '';
        if (billAreaElement) billAreaElement.value = customer.area || '';
        if (billTRNElement) billTRNElement.value = customer.trn || '';
        if (billCustomerTypeElement) billCustomerTypeElement.value = customer.customer_type || 'Individual';
        if (billBusinessNameElement) billBusinessNameElement.value = customer.business_name || '';
        if (billBusinessAddressElement) billBusinessAddressElement.value = customer.business_address || '';

        // Show/hide business fields based on customer type
        const businessFields = document.querySelectorAll('.business-billing-field');
        const trnField = document.querySelector('.trn-billing-field');

        if (customer.customer_type === 'Business') {
            businessFields.forEach(field => field.style.display = 'flex');
            if (trnField) trnField.style.display = 'flex';
            if (billBusinessNameElement) billBusinessNameElement.required = true;
            if (billBusinessAddressElement) billBusinessAddressElement.required = true;
        } else {
            businessFields.forEach(field => field.style.display = 'none');
            if (trnField) trnField.style.display = 'none';
            if (billBusinessNameElement) billBusinessNameElement.required = false;
            if (billBusinessAddressElement) billBusinessAddressElement.required = false;
        }

        // Loyalty: fetch and render loyalty status for this customer
        try {
            if (customer && customer.customer_id) {
                await renderLoyaltySummary(customer.customer_id);
            }
        } catch (e) {
            console.error('Failed to render loyalty summary', e);
        }
    }

    function clearCustomerFields() {
        const billCustomerElement = document.getElementById('billCustomer');
        const billMobileElement = document.getElementById('billMobile');
        const billCityElement = document.getElementById('billCity');
        const billAreaElement = document.getElementById('billArea');
        const billTRNElement = document.getElementById('billTRN');
        const billCustomerTypeElement = document.getElementById('billCustomerType');
        const billBusinessNameElement = document.getElementById('billBusinessName');
        const billBusinessAddressElement = document.getElementById('billBusinessAddress');

        if (billCustomerElement) billCustomerElement.value = '';
        if (billMobileElement) billMobileElement.value = '';
        if (billCityElement) billCityElement.value = '';
        if (billAreaElement) billAreaElement.value = '';
        if (billTRNElement) billTRNElement.value = '';
        if (billCustomerTypeElement) billCustomerTypeElement.value = 'Individual';
        if (billBusinessNameElement) billBusinessNameElement.value = '';
        if (billBusinessAddressElement) billBusinessAddressElement.value = '';

        // Hide business fields for new customer
        const businessFields = document.querySelectorAll('.business-billing-field');
        const trnField = document.querySelector('.trn-billing-field');
        businessFields.forEach(field => field.style.display = 'none');
        if (trnField) trnField.style.display = 'none';
        if (billBusinessNameElement) billBusinessNameElement.required = false;
        if (billBusinessAddressElement) billBusinessAddressElement.required = false;

        // Clear loyalty summary panel
        const loyaltySummaryElement = document.getElementById('loyaltySummary');
        if (loyaltySummaryElement) {
            loyaltySummaryElement.innerHTML = '';
            loyaltySummaryElement.style.display = 'none';
        }
    }

    async function setupMobileCustomerFetch() {
        const billMobileElement = document.getElementById('billMobile');
        if (billMobileElement) {
            // Load country codes first
            if (window.loadCountryCodes) await window.loadCountryCodes();
            // Initialize Country Code Selector
            if (window.setupCountryCodeSelector) window.setupCountryCodeSelector();

            let mobileDropdown = null;
            let debounceTimer = null;

            // Create mobile dropdown
            function createMobileDropdown() {
                if (mobileDropdown) {
                    document.body.removeChild(mobileDropdown);
                }

                mobileDropdown = document.createElement('div');
                mobileDropdown.id = 'mobileDropdown';
                mobileDropdown.className = 'fixed bg-neutral-900 border border-neutral-700 rounded-lg shadow-lg max-h-48 overflow-y-auto z-99999';
                mobileDropdown.style.display = 'none';
                document.body.appendChild(mobileDropdown);

                return mobileDropdown;
            }

            // Show mobile suggestions
            function showMobileSuggestions(customers) {
                if (!mobileDropdown) {
                    mobileDropdown = createMobileDropdown();
                }

                if (customers.length === 0) {
                    mobileDropdown.style.display = 'none';
                    return;
                }

                const rect = billMobileElement.getBoundingClientRect();
                mobileDropdown.style.left = rect.left + 'px';
                mobileDropdown.style.top = (rect.bottom + 5) + 'px';
                mobileDropdown.style.width = rect.width + 'px';
                mobileDropdown.style.display = 'block';

                mobileDropdown.innerHTML = customers.map(customer => `
                  <div class="mobile-suggestion-item px-3 py-2 hover:bg-neutral-800 cursor-pointer border-b border-neutral-700 last:border-b-0" 
                       data-phone="${customer.phone}" 
                       data-customer='${JSON.stringify(customer)}'>
                    <div class="flex items-center justify-between">
                      <div>
                        <div class="text-white font-medium">${customer.name}</div>
                        <div class="text-neutral-400 text-sm">${customer.phone}</div>
                        ${customer.business_name ? `<div class="text-neutral-500 text-xs">${customer.business_name}</div>` : ''}
                      </div>
                      <div class="text-xs text-neutral-500">
                        ${customer.city || ''} ${customer.area ? `- ${customer.area}` : ''}
                      </div>
                    </div>
                  </div>
                `).join('');

                // Add click handlers
                mobileDropdown.querySelectorAll('.mobile-suggestion-item').forEach(item => {
                    item.addEventListener('click', async function () {
                        const customer = JSON.parse(this.dataset.customer);
                        await populateCustomerFields(customer);
                        hideMobileDropdown();
                    });
                });
            }

            // Hide mobile dropdown
            function hideMobileDropdown() {
                if (mobileDropdown) {
                    mobileDropdown.style.display = 'none';
                }
            }

            // Search customers by mobile number
            async function searchCustomersByMobile(query) {
                try {
                    const response = await fetch(`/api/customers?search=${encodeURIComponent(query)}`);
                    if (response.ok) {
                        const customers = await response.json();
                        const filteredCustomers = customers.filter(customer => {
                            if (!customer.phone) return false;
                            return customer.phone.includes(query) || (customer.phone.replace(/^\+\d+/, '')).startsWith(query);
                        });
                        return filteredCustomers.slice(0, 5); // Limit to 5 suggestions
                    }
                    return [];
                } catch (error) {
                    console.error('Error searching customers by mobile:', error);
                    return [];
                }
            }

            // Debounced search function
            function debouncedMobileSearch(query) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(async () => {
                    if (query.length >= 5) {
                        const customers = await searchCustomersByMobile(query);
                        showMobileSuggestions(customers);
                    } else {
                        hideMobileDropdown();
                    }
                }, 300);
            }

            // Input event for real-time autocomplete
            billMobileElement.addEventListener('input', function (e) {
                // Keep only digits and enforce max length 10
                const sanitized = (e.target.value || '').replace(/\D/g, '').slice(0, 15);
                if (e.target.value !== sanitized) {
                    e.target.value = sanitized;
                }
                const phone = sanitized;
                if (phone.length >= 5) {
                    debouncedMobileSearch(phone);
                } else {
                    hideMobileDropdown();
                }
            });

            // Focus event to show suggestions if there's a value
            billMobileElement.addEventListener('focus', function (e) {
                const phone = e.target.value.trim();
                if (phone.length >= 5) {
                    debouncedMobileSearch(phone);
                }
            });

            // Blur event
            billMobileElement.addEventListener('blur', async function (e) {
                setTimeout(() => {
                    hideMobileDropdown();
                }, 200);

                const phone = (e.target.value || '').trim();
                if (!phone) return;

                if (phone.length > 0 && phone.replace(/\D/g, '').length < 5) {
                    if (window.showModernAlert) {
                        window.showModernAlert('Please enter valid mobile number', 'warning', 'Invalid Mobile');
                    }
                    e.target.focus();
                    return;
                }

                const customer = await fetchCustomerByMobile(phone);
                if (customer) {
                    await populateCustomerFields(customer);
                }
            });

            // Handle escape key
            billMobileElement.addEventListener('keydown', function (e) {
                if (e.key === 'Escape') {
                    hideMobileDropdown();
                }
            });

            // Hide dropdown when clicking outside
            document.addEventListener('click', function (e) {
                if (mobileDropdown && !billMobileElement.contains(e.target) && !mobileDropdown.contains(e.target)) {
                    hideMobileDropdown();
                }
            });
        }
    }

    function setupCustomerTypeHandler() {
        const billCustomerTypeElement = document.getElementById('billCustomerType');
        if (billCustomerTypeElement) {
            billCustomerTypeElement.addEventListener('change', function () {
                const customerType = this.value;
                const businessFields = document.querySelectorAll('.business-billing-field');
                const trnField = document.querySelector('.trn-billing-field');
                const billBusinessNameElement = document.getElementById('billBusinessName');
                const billBusinessAddressElement = document.getElementById('billBusinessAddress');

                if (customerType === 'Business') {
                    businessFields.forEach(field => field.style.display = 'flex');
                    if (trnField) trnField.style.display = 'flex';
                    if (billBusinessNameElement) billBusinessNameElement.required = true;
                    if (billBusinessAddressElement) billBusinessAddressElement.required = true;
                } else {
                    businessFields.forEach(field => field.style.display = 'none');
                    if (trnField) trnField.style.display = 'none';
                    if (billBusinessNameElement) billBusinessNameElement.required = false;
                    if (billBusinessAddressElement) billBusinessAddressElement.required = false;
                }
            });
        }
    }

    async function loadRecentCustomers() {
        try {
            const response = await fetch('/api/customers/recent');
            const recentCustomers = await response.json();

            const container = document.getElementById('recentCustomersContainer');
            if (!container) return;

            if (recentCustomers && recentCustomers.length > 0) {
                container.innerHTML = recentCustomers.map(customer => `
                       <button 
                         class="customer-pill"
                         data-customer-id="${customer.customer_id}"
                         data-customer-name="${customer.name}"
                         data-customer-phone="${customer.phone || ''}"
                         data-customer-city="${customer.city || ''}"
                         data-customer-area="${customer.area || ''}"
                         data-customer-trn="${customer.trn || ''}"
                         data-customer-type="${customer.customer_type || 'Individual'}"
                         data-business-name="${customer.business_name || ''}"
                         data-business-address="${customer.business_address || ''}"
                       >
                         <svg data-lucide="user" class="w-1 h-1"></svg>
                         <span>${customer.name}</span>
                         ${customer.phone ? `<span class="text-neutral-300">(${customer.phone})</span>` : ''}
                       </button>
                     `).join('');

                container.querySelectorAll('.customer-pill').forEach(btn => {
                    btn.addEventListener('click', async function () {
                        const customerData = {
                            customer_id: this.getAttribute('data-customer-id'),
                            name: this.getAttribute('data-customer-name'),
                            phone: this.getAttribute('data-customer-phone'),
                            city: this.getAttribute('data-customer-city'),
                            area: this.getAttribute('data-customer-area'),
                            trn: this.getAttribute('data-customer-trn'),
                            customer_type: this.getAttribute('data-customer-type'),
                            business_name: this.getAttribute('data-business-name'),
                            business_address: this.getAttribute('data-business-address')
                        };

                        await populateCustomerFields(customerData);
                    });

                    btn.addEventListener('mouseenter', function () {
                        showCustomerTooltip(this);
                    });

                    btn.addEventListener('mouseleave', function () {
                        hideCustomerTooltip();
                    });
                });

                try {
                    if (typeof lucide !== 'undefined' && lucide.createIcons) {
                        lucide.createIcons();
                    }
                } catch (lucideError) {
                    console.warn('Error creating lucide icons:', lucideError);
                }
            } else {
                container.innerHTML = '<p class="text-neutral-500 text-sm">No recent customers found</p>';
            }
        } catch (error) {
            console.error('Error loading recent customers:', error);
            const container = document.getElementById('recentCustomersContainer');
            if (container) {
                container.innerHTML = '<p class="text-neutral-500 text-sm">Failed to load recent customers</p>';
            }
        }
    }

    function initializeMobileRecentCustomers() {
        const mobileBtn = document.getElementById('mobileRecentCustomersBtn');
        const mobileDropdown = document.getElementById('mobileRecentCustomersDropdown');

        if (mobileBtn && mobileDropdown) {
            mobileBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                const isVisible = !mobileDropdown.classList.contains('hidden');

                if (isVisible) {
                    hideMobileRecentCustomersDropdown();
                } else {
                    showMobileRecentCustomersDropdown();
                }
            });

            document.addEventListener('click', function (e) {
                if (!mobileBtn.contains(e.target) && !mobileDropdown.contains(e.target)) {
                    hideMobileRecentCustomersDropdown();
                }
            });
        }
    }

    function showMobileRecentCustomersDropdown() {
        const dropdown = document.getElementById('mobileRecentCustomersDropdown');
        if (dropdown) {
            dropdown.classList.remove('hidden');
            loadMobileRecentCustomers();
        }
    }

    function hideMobileRecentCustomersDropdown() {
        const dropdown = document.getElementById('mobileRecentCustomersDropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
        }
    }

    async function loadMobileRecentCustomers() {
        try {
            const response = await fetch('/api/customers/recent');
            const recentCustomers = await response.json();

            const container = document.getElementById('mobileRecentCustomersList');
            if (!container) return;

            if (recentCustomers && recentCustomers.length > 0) {
                container.innerHTML = recentCustomers.map(customer => `
                  <button 
                    class="mobile-customer-item"
                    data-customer-id="${customer.customer_id}"
                    data-customer-name="${customer.name}"
                    data-customer-phone="${customer.phone || ''}"
                    data-customer-city="${customer.city || ''}"
                    data-customer-area="${customer.area || ''}"
                    data-customer-trn="${customer.trn || ''}"
                    data-customer-type="${customer.customer_type || 'Individual'}"
                    data-business-name="${customer.business_name || ''}"
                    data-business-address="${customer.business_address || ''}"
                  >
                    <div class="flex items-center justify-between w-full">
                      <div class="flex items-center space-x-2">
                        <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                        </svg>
                        <span class="text-sm text-white font-medium">${customer.name}</span>
                      </div>
                      ${customer.phone ? `<span class="text-xs text-neutral-400">${customer.phone}</span>` : ''}
                    </div>
                  </button>
                `).join('');

                container.querySelectorAll('.mobile-customer-item').forEach(btn => {
                    btn.addEventListener('click', async function () {
                        const customerData = {
                            customer_id: this.getAttribute('data-customer-id'),
                            name: this.getAttribute('data-customer-name'),
                            phone: this.getAttribute('data-customer-phone'),
                            city: this.getAttribute('data-customer-city'),
                            area: this.getAttribute('data-customer-area'),
                            trn: this.getAttribute('data-customer-trn'),
                            customer_type: this.getAttribute('data-customer-type'),
                            business_name: this.getAttribute('data-business-name'),
                            business_address: this.getAttribute('data-business-address')
                        };

                        await populateCustomerFields(customerData);
                        hideMobileRecentCustomersDropdown();

                        if (window.showSimpleToast) {
                            window.showSimpleToast(`Customer "${customerData.name}" selected`, 'success');
                        }
                    });
                });
            } else {
                container.innerHTML = '<div class="p-3 text-center"><p class="text-neutral-500 text-sm">No recent customers found</p></div>';
            }
        } catch (error) {
            console.error('Error loading mobile recent customers:', error);
            const container = document.getElementById('mobileRecentCustomersList');
            if (container) {
                container.innerHTML = '<div class="p-3 text-center"><p class="text-neutral-500 text-sm">Failed to load recent customers</p></div>';
            }
        }
    }

    function showCustomerTooltip(element) {
        hideCustomerTooltip();

        const customerData = {
            name: element.getAttribute('data-customer-name'),
            phone: element.getAttribute('data-customer-phone'),
            city: element.getAttribute('data-customer-city'),
            area: element.getAttribute('data-customer-area'),
            trn: element.getAttribute('data-customer-trn'),
            customer_type: element.getAttribute('data-customer-type'),
            business_name: element.getAttribute('data-business-name'),
            business_address: element.getAttribute('data-business-address')
        };

        let tooltipContent = `
            <div class="customer-tooltip-content">
              <div class="tooltip-header">
                <strong>${customerData.name}</strong>
              </div>
              <div class="tooltip-body">
          `;

        if (customerData.phone) {
            tooltipContent += `<div class="tooltip-row"><span class="tooltip-label">Phone:</span> <span class="tooltip-value">${customerData.phone}</span></div>`;
        }
        if (customerData.city) {
            tooltipContent += `<div class="tooltip-row"><span class="tooltip-label">City:</span> <span class="tooltip-value">${customerData.city}</span></div>`;
        }
        if (customerData.area) {
            tooltipContent += `<div class="tooltip-row"><span class="tooltip-label">Area:</span> <span class="tooltip-value">${customerData.area}</span></div>`;
        }
        if (customerData.customer_type === 'Business') {
            if (customerData.business_name) {
                tooltipContent += `<div class="tooltip-row"><span class="tooltip-label">Business:</span> <span class="tooltip-value">${customerData.business_name}</span></div>`;
            }
            if (customerData.business_address) {
                tooltipContent += `<div class="tooltip-row"><span class="tooltip-label">Address:</span> <span class="tooltip-value">${customerData.business_address}</span></div>`;
            }
            if (customerData.trn) {
                tooltipContent += `<div class="tooltip-row"><span class="tooltip-label">TRN:</span> <span class="tooltip-value">${customerData.trn}</span></div>`;
            }
        }
        if (customerData.customer_type) {
            tooltipContent += `<div class="tooltip-row"><span class="tooltip-label">Type:</span> <span class="tooltip-value">${customerData.customer_type}</span></div>`;
        }

        tooltipContent += `
              </div>
            </div>
          `;

        const tooltip = document.createElement('div');
        tooltip.className = 'customer-tooltip';
        tooltip.innerHTML = tooltipContent;
        tooltip.id = 'customerTooltip';

        const rect = element.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const tooltipWidth = 300;
        const padding = 20;

        tooltip.style.position = 'fixed';
        tooltip.style.zIndex = '10000';

        let leftPosition = rect.left + rect.width + 10;
        let isPositionedLeft = false;

        if (leftPosition + tooltipWidth + padding > viewportWidth) {
            leftPosition = rect.left - tooltipWidth - 10;
            isPositionedLeft = true;
        }

        if (leftPosition < padding) {
            leftPosition = padding;
            isPositionedLeft = false;
        }

        if (isPositionedLeft) {
            tooltip.classList.add('tooltip-left');
        } else {
            tooltip.classList.add('tooltip-right');
        }

        tooltip.style.left = leftPosition + 'px';
        tooltip.style.top = rect.top + 'px';

        document.body.appendChild(tooltip);
    }

    function hideCustomerTooltip() {
        const tooltip = document.getElementById('customerTooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    function setupCustomerQuickSearch() {
        const customerInput = document.getElementById('billCustomer');
        if (!customerInput) return;

        let searchTimeout;
        let dropdown;

        function createCustomerDropdown() {
            dropdown = document.createElement('div');
            dropdown.className = 'customer-suggestion';
            dropdown.style.cssText = 'position: fixed; z-index: 99999 !important; background: #1f2937; border: 1px solid #374151; border-radius: 8px; max-height: 240px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);';
            dropdown.style.display = 'none';
            document.body.appendChild(dropdown);

            dropdown.addEventListener('click', function (e) {
                e.stopPropagation();
            });
        }

        function showCustomerSuggestions(customers) {
            if (!dropdown) createCustomerDropdown();

            const inputRect = customerInput.getBoundingClientRect();
            dropdown.style.left = inputRect.left + 'px';
            dropdown.style.top = (inputRect.bottom + 4) + 'px';
            dropdown.style.width = inputRect.width + 'px';
            dropdown.style.minWidth = '200px';

            dropdown.innerHTML = customers.map(customer => `
              <div class="customer-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" 
                   data-customer-id="${customer.customer_id}"
                   data-customer-name="${customer.name}"
                   data-customer-phone="${customer.phone || ''}"
                   data-customer-email="${customer.email || ''}"
                   data-customer-address="${customer.address || ''}"
                   data-customer-city="${customer.city || ''}"
                   data-customer-area="${customer.area || ''}"
                   data-customer-trn="${customer.trn || ''}"
                   data-customer-type="${customer.customer_type || 'Individual'}"
                   data-business-name="${customer.business_name || ''}"
                   data-business-address="${customer.business_address || ''}">
                <div class="flex items-center justify-between">
                  <span class="text-neutral-200">${customer.name}</span>
                  <span class="text-xs text-neutral-400">${customer.phone || ''}</span>
                </div>
              </div>
            `).join('');

            const options = dropdown.querySelectorAll('.customer-option');
            options.forEach(option => {
                option.addEventListener('click', async function (e) {
                    e.preventDefault();
                    e.stopPropagation();

                    const customerData = {
                        customer_id: this.getAttribute('data-customer-id'),
                        name: this.getAttribute('data-customer-name'),
                        phone: this.getAttribute('data-customer-phone'),
                        email: this.getAttribute('data-customer-email'),
                        address: this.getAttribute('data-customer-address'),
                        city: this.getAttribute('data-customer-city'),
                        area: this.getAttribute('data-customer-area'),
                        trn: this.getAttribute('data-customer-trn'),
                        customer_type: this.getAttribute('data-customer-type'),
                        business_name: this.getAttribute('data-business-name'),
                        business_address: this.getAttribute('data-business-address')
                    };

                    await populateCustomerFields(customerData);
                    hideCustomerDropdown();
                    customerInput.value = customerData.name;
                });
            });

            dropdown.style.display = 'block';
        }

        function hideCustomerDropdown() {
            if (dropdown) {
                dropdown.style.transition = 'all 0.2s ease';
                dropdown.style.opacity = '0';
                dropdown.style.transform = 'translateY(-10px)';

                setTimeout(() => {
                    dropdown.style.display = 'none';
                    if (dropdown.parentNode) {
                        dropdown.parentNode.removeChild(dropdown);
                    }
                    dropdown = null;
                }, 200);
            }
        }

        async function searchCustomers(query) {
            if (!query.trim()) {
                hideCustomerDropdown();
                return;
            }

            try {
                const response = await fetch(`/api/customers?search=${encodeURIComponent(query)}`);

                if (!response.ok) {
                    console.error('Customer search failed:', response.status, response.statusText);
                    hideCustomerDropdown();
                    return;
                }

                const customers = await response.json();

                if (customers && customers.length > 0) {
                    showCustomerSuggestions(customers);
                } else {
                    hideCustomerDropdown();
                }
            } catch (error) {
                console.error('Error searching customers:', error);
                hideCustomerDropdown();
            }
        }

        function debouncedSearch(query) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => searchCustomers(query), 300);
        }

        customerInput.addEventListener('input', function () {
            debouncedSearch(this.value);
        });

        customerInput.addEventListener('focus', function () {
            if (this.value.trim()) {
                debouncedSearch(this.value);
            }
        });

        document.addEventListener('click', function (e) {
            if (e.target.closest('.customer-option')) {
                return;
            }
            if (customerInput.contains(e.target)) {
                return;
            }
            if (!customerInput.contains(e.target) && (!dropdown || !dropdown.contains(e.target))) {
                hideCustomerDropdown();
            }
        });
    }

    function setupCityAreaAutocomplete() {
        const cityInput = document.getElementById('billCity');
        const areaInput = document.getElementById('billArea');

        if (!cityInput || !areaInput) {
            console.warn('City/Area autocomplete elements not found');
            return;
        }

        let cityDebounceTimer = null;
        let areaDebounceTimer = null;
        let cityDropdown = null;
        let areaDropdown = null;

        function createCityDropdown() {
            if (cityDropdown) {
                cityDropdown.remove();
            }
            cityDropdown = document.createElement('div');
            cityDropdown.className = 'city-suggestion';
            cityDropdown.style.cssText = 'position: fixed; z-index: 99999 !important; background: #1f2937; border: 1px solid #374151; border-radius: 8px; max-height: 240px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);';
            cityDropdown.style.display = 'none';
            document.body.appendChild(cityDropdown);

            cityDropdown.addEventListener('click', function (e) {
                e.stopPropagation();
            });
        }

        function createAreaDropdown() {
            if (areaDropdown) {
                areaDropdown.remove();
            }
            areaDropdown = document.createElement('div');
            areaDropdown.className = 'area-suggestion';
            areaDropdown.style.cssText = 'position: fixed; z-index: 99999 !important; background: #1f2937; border: 1px solid #374151; border-radius: 8px; max-height: 240px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);';
            areaDropdown.style.display = 'none';
            document.body.appendChild(areaDropdown);

            areaDropdown.addEventListener('click', function (e) {
                e.stopPropagation();
            });
        }

        cityInput.addEventListener('input', function () {
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

                    if (filteredCities.length > 0) {
                        showCitySuggestions(filteredCities);
                    } else {
                        hideCityDropdown();
                    }
                } catch (error) {
                    console.error('Error loading cities:', error);
                }
            }, 300);
        });

        function showCitySuggestions(cities) {
            if (!cityDropdown) createCityDropdown();

            const inputRect = cityInput.getBoundingClientRect();
            cityDropdown.style.left = inputRect.left + 'px';
            cityDropdown.style.top = (inputRect.bottom + 4) + 'px';
            cityDropdown.style.width = inputRect.width + 'px';
            cityDropdown.style.minWidth = '200px';

            cityDropdown.innerHTML = cities.map(city => `
            <div class="city-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" data-city="${city}">
              ${city}
            </div>
          `).join('');

            const options = cityDropdown.querySelectorAll('.city-option');
            options.forEach(option => {
                option.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();

                    const selectedCity = this.getAttribute('data-city');
                    cityInput.value = selectedCity;
                    hideCityDropdown();

                    areaInput.value = '';
                    updateAreaDropdownForCity(selectedCity);
                });
            });

            cityDropdown.style.display = 'block';
        }

        function hideCityDropdown() {
            if (cityDropdown) {
                cityDropdown.style.transition = 'all 0.2s ease';
                cityDropdown.style.opacity = '0';
                cityDropdown.style.transform = 'translateY(-10px)';

                setTimeout(() => {
                    cityDropdown.style.display = 'none';
                    if (cityDropdown.parentNode) {
                        cityDropdown.parentNode.removeChild(cityDropdown);
                    }
                    cityDropdown = null;
                }, 200);
            }
        }

        areaInput.addEventListener('input', function () {
            clearTimeout(areaDebounceTimer);
            const query = this.value.trim();

            if (query.length < 2) {
                hideAreaDropdown();
                return;
            }

            areaDebounceTimer = setTimeout(async () => {
                try {
                    const cityValue = cityInput.value.trim();
                    const url = cityValue ? `/api/areas?city=${encodeURIComponent(cityValue)}` : '/api/areas';
                    const response = await fetch(url);
                    const areas = await response.json();
                    const filteredAreas = areas.filter(area =>
                        area.toLowerCase().includes(query.toLowerCase())
                    );

                    if (filteredAreas.length > 0) {
                        showAreaSuggestions(filteredAreas);
                    } else {
                        hideAreaDropdown();
                    }
                } catch (error) {
                    console.error('Error loading areas:', error);
                }
            }, 300);
        });

        function showAreaSuggestions(areas) {
            if (!areaDropdown) createAreaDropdown();

            const inputRect = areaInput.getBoundingClientRect();
            areaDropdown.style.left = inputRect.left + 'px';
            areaDropdown.style.top = (inputRect.bottom + 4) + 'px';
            areaDropdown.style.width = inputRect.width + 'px';
            areaDropdown.style.minWidth = '200px';

            areaDropdown.innerHTML = areas.map(area => `
            <div class="area-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" data-area="${area}">
              ${area}
            </div>
          `).join('');

            const options = areaDropdown.querySelectorAll('.area-option');
            options.forEach(option => {
                option.addEventListener('click', function (e) {
                    e.preventDefault();
                    e.stopPropagation();

                    const selectedArea = this.getAttribute('data-area');
                    areaInput.value = selectedArea;
                    hideAreaDropdown();

                    if (!cityInput.value.trim()) {
                        findCityForArea(selectedArea);
                    }
                });
            });

            areaDropdown.style.display = 'block';
        }

        function hideAreaDropdown() {
            if (areaDropdown) {
                areaDropdown.style.transition = 'all 0.2s ease';
                areaDropdown.style.opacity = '0';
                areaDropdown.style.transform = 'translateY(-10px)';

                setTimeout(() => {
                    areaDropdown.style.display = 'none';
                    if (areaDropdown.parentNode) {
                        areaDropdown.parentNode.removeChild(areaDropdown);
                    }
                    areaDropdown = null;
                }, 200);
            }
        }

        document.addEventListener('click', function (e) {
            if (e.target.closest('.city-option') || e.target.closest('.area-option')) {
                return;
            }
            if (cityInput.contains(e.target) || areaInput.contains(e.target)) {
                return;
            }
            if (!cityInput.contains(e.target) && (!cityDropdown || !cityDropdown.contains(e.target))) {
                hideCityDropdown();
            }
            if (!areaInput.contains(e.target) && (!areaDropdown || !areaDropdown.contains(e.target))) {
                hideAreaDropdown();
            }
        });

        async function updateAreaDropdownForCity(city) {
            try {
                const response = await fetch(`/api/areas?city=${encodeURIComponent(city)}`);
                const areas = await response.json();

                if (areas.length > 0) {
                    showAreaSuggestions(areas);
                } else {
                    if (!areaDropdown) createAreaDropdown();

                    const inputRect = areaInput.getBoundingClientRect();
                    areaDropdown.style.left = inputRect.left + 'px';
                    areaDropdown.style.top = (inputRect.bottom + 4) + 'px';
                    areaDropdown.style.width = inputRect.width + 'px';
                    areaDropdown.style.minWidth = '200px';

                    areaDropdown.innerHTML = '<div class="px-4 py-2 text-neutral-400 text-sm">No areas found for this city</div>';
                    areaDropdown.style.display = 'block';

                    setTimeout(() => {
                        hideAreaDropdown();
                    }, 2000);
                }
            } catch (error) {
                console.error('Error updating areas for city:', error);
            }
        }

        async function findCityForArea(area) {
            try {
                const response = await fetch(`/api/cities?area=${encodeURIComponent(area)}`);
                const cities = await response.json();

                if (cities.length > 0) {
                    cityInput.value = cities[0];
                }
            } catch (error) {
                console.error('Error finding city for area:', error);
            }
        }
    }

    async function renderLoyaltySummary(customerId) {
        try {
            const summary = document.getElementById('loyaltySummary');
            const tierBadge = document.getElementById('loyaltyTierBadge');
            const pointsText = document.getElementById('loyaltyPointsText');
            const enrollBtn = document.getElementById('loyaltyEnrollBtn');
            const note = document.getElementById('loyaltyNote');
            if (!summary || !tierBadge || !pointsText || !enrollBtn || !note) return;

            const resp = await fetch(`/api/loyalty/customers/${customerId}`);

            if (resp.ok) {
                const data = await resp.json();
                if (data && data.success) {
                    const lp = data.loyalty_profile || {};
                    summary.classList.remove('hidden');
                    tierBadge.textContent = lp.tier_level || 'Bronze';
                    pointsText.textContent = `Points: ${lp.available_points ?? 0}`;
                    enrollBtn.classList.add('hidden');
                    note.textContent = `Lifetime: ${lp.total_points ?? 0} • Purchases: ${lp.total_purchases ?? 0}`;
                } else {
                    showNotEnrolledState();
                }
            } else if (resp.status === 404) {
                showNotEnrolledState();
            } else {
                console.error('Loyalty API error:', resp.status, resp.statusText);
                showNotEnrolledState();
            }

            function showNotEnrolledState() {
                summary.classList.remove('hidden');
                tierBadge.textContent = 'Not enrolled';
                pointsText.textContent = 'Points: 0';
                enrollBtn.classList.remove('hidden');
                note.textContent = 'Enroll this customer to start earning points.';
                enrollBtn.onclick = async () => {
                    try {
                        const res = await fetch(`/api/loyalty/customers/${customerId}/enroll`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
                        const j = await res.json();
                        if (j && j.success) {
                            if (window.showSimpleToast) window.showSimpleToast('Customer enrolled in loyalty', 'success');
                            await renderLoyaltySummary(customerId);
                        } else {
                            if (window.showModernAlert) window.showModernAlert(j.error || 'Failed to enroll', 'error');
                        }
                    } catch (e) {
                        console.error('Enroll failed', e);
                    }
                };
            }
        } catch (e) {
            console.error('Loyalty summary error', e);
            const summary = document.getElementById('loyaltySummary');
            const tierBadge = document.getElementById('loyaltyTierBadge');
            const pointsText = document.getElementById('loyaltyPointsText');
            const enrollBtn = document.getElementById('loyaltyEnrollBtn');
            const note = document.getElementById('loyaltyNote');

            if (summary && tierBadge && pointsText && enrollBtn && note) {
                summary.classList.remove('hidden');
                tierBadge.textContent = 'Not enrolled';
                pointsText.textContent = 'Points: 0';
                enrollBtn.classList.remove('hidden');
                note.textContent = 'Enroll this customer to start earning points.';
            }
        }
    }

    // Expose functions globally
    window.BillingCustomer = {
        getInputs: getCustomerInputs,
        fetchByMobile: fetchCustomerByMobile,
        populate: populateCustomerFields,
        clear: clearCustomerFields,
        setupMobileFetch: setupMobileCustomerFetch,
        setupTypeHandler: setupCustomerTypeHandler,
        loadRecent: loadRecentCustomers,
        initMobileRecent: initializeMobileRecentCustomers,
        setupQuickSearch: setupCustomerQuickSearch,
        setupCityArea: setupCityAreaAutocomplete,
        renderLoyalty: renderLoyaltySummary
    };

    // Backward compatibility aliases
    window.getCustomerInputs = getCustomerInputs;
    window.fetchCustomerByMobile = fetchCustomerByMobile;
    window.populateCustomerFields = populateCustomerFields;
    window.clearCustomerFields = clearCustomerFields;
    window.setupMobileCustomerFetch = setupMobileCustomerFetch;
    window.setupCustomerTypeHandler = setupCustomerTypeHandler;
    window.loadRecentCustomers = loadRecentCustomers;
    window.initializeMobileRecentCustomers = initializeMobileRecentCustomers;
    window.showMobileRecentCustomersDropdown = showMobileRecentCustomersDropdown;
    window.hideMobileRecentCustomersDropdown = hideMobileRecentCustomersDropdown;
    window.loadMobileRecentCustomers = loadMobileRecentCustomers;
    window.showCustomerTooltip = showCustomerTooltip;
    window.hideCustomerTooltip = hideCustomerTooltip;
    window.setupCustomerQuickSearch = setupCustomerQuickSearch;
    window.setupCityAreaAutocomplete = setupCityAreaAutocomplete;
    window.renderLoyaltySummary = renderLoyaltySummary;

})();
