// Billing Items Module
// Handles product selection, adding items, and item management

;(function() {

  // --- Helper Functions ---

  function showFieldError(input, message) {
    if (!input) return;

    input.classList.add('billing-input-error');

    // Remove existing error message
    const existingError = input.parentNode.querySelector('.billing-error-message');
    if (existingError) {
      existingError.remove();
    }

    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'billing-error-message';
    errorDiv.textContent = message;
    input.parentNode.appendChild(errorDiv);
  }

  function showBillingSuccess(message) {
    // Create success notification
    const successDiv = document.createElement('div');
    successDiv.className = 'billing-success';
    successDiv.innerHTML = `
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>
      <span>${message}</span>
    `;

    // Try to insert after desktop add item button first
    const addItemBtn = document.getElementById('addItemBtn');
    if (addItemBtn && addItemBtn.parentNode) {
      addItemBtn.parentNode.insertBefore(successDiv, addItemBtn.nextSibling);
    } else {
      // If desktop button not found, try mobile button
      const addItemBtnMobile = document.getElementById('addItemBtnMobile');
      if (addItemBtnMobile && addItemBtnMobile.parentNode) {
        addItemBtnMobile.parentNode.insertBefore(successDiv, addItemBtnMobile.nextSibling);
      } else {
        // If neither button found, append to body as fallback
        document.body.appendChild(successDiv);
      }
    }

    // Remove after 3 seconds
    setTimeout(() => {
      if (successDiv.parentNode) {
        successDiv.parentNode.removeChild(successDiv);
      }
    }, 3000);
  }

  function clearBillingForm(formType = 'desktop') {
    let productInput, quantityInput, priceInput, discountInput, advanceInput, vatInput, notesInput;

    if (formType === 'mobile') {
      productInput = document.getElementById('billProductMobile');
      quantityInput = document.getElementById('billQtyMobile');
      priceInput = document.getElementById('billRateMobile');
      discountInput = document.getElementById('billDiscountMobile');
      advanceInput = document.getElementById('billAdvPaidMobile');
      vatInput = document.getElementById('vatPercentMobile');
      notesInput = null;
    } else {
      productInput = document.getElementById('billProduct');
      quantityInput = document.getElementById('billQty');
      priceInput = document.getElementById('billRate');
      discountInput = document.getElementById('billDiscount');
      advanceInput = document.getElementById('billAdvPaid');
      vatInput = document.getElementById('vatPercent');
      notesInput = document.getElementById('itemNotes');
    }

    if (productInput) {
      productInput.value = '';
      productInput.removeAttribute('data-selected-product');
      productInput.classList.remove('billing-input-error');
    }
    if (quantityInput) {
      quantityInput.value = '1';
      quantityInput.classList.remove('billing-input-error');
    }
    if (priceInput) {
      priceInput.value = '0.00';
      priceInput.classList.remove('billing-input-error');
    }
    if (discountInput) {
      discountInput.value = '0';
      discountInput.classList.remove('billing-input-error');
    }
    if (advanceInput) {
      advanceInput.value = '0';
      advanceInput.classList.remove('billing-input-error');
    }
    if (vatInput) {
      // Use default VAT from configuration if available
      const defaultVat = window.getDefaultVatPercent ? window.getDefaultVatPercent() : 5;
      vatInput.value = defaultVat;
      vatInput.classList.remove('billing-input-error');
    }
    if (notesInput) {
      notesInput.value = '';
    }

    // Clear total advance field
    const totalAdvanceInput = document.getElementById('totalAdvancePaid');
    if (totalAdvanceInput) totalAdvanceInput.value = '';

    // Remove any error messages
    const errorMessages = document.querySelectorAll('.billing-error-message');
    errorMessages.forEach(msg => msg.remove());
  }

  // --- Product Quick Add Logic ---

  function setupProductQuickAdd() {
    // Setup desktop product quick add
    const billProductInput = document.getElementById('billProduct');
    const billRateInput = document.getElementById('billRate');

    if (billProductInput) {
      setupProductQuickAddForInput(billProductInput, billRateInput, 'desktop');
    }

    // Setup mobile product quick add
    const billProductInputMobile = document.getElementById('billProductMobile');
    const billRateInputMobile = document.getElementById('billRateMobile');

    if (billProductInputMobile) {
      setupProductQuickAddForInput(billProductInputMobile, billRateInputMobile, 'mobile');
    }
  }

  function setupProductQuickAddForInput(productInput, rateInput, formType) {
    if (!productInput) {
      return;
    }

    let allProducts = [];
    let productDropdown;

    // Create product dropdown with mobile-optimized styling
    function createProductDropdown() {
      productDropdown = document.createElement('div');
      productDropdown.className = 'product-suggestion-mobile';
      productDropdown.style.cssText = 'position: fixed; z-index: 99999 !important; background: #1f2937; border: 1px solid #374151; border-radius: 8px; max-height: 240px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);';
      productDropdown.style.display = 'none';
      document.body.appendChild(productDropdown);

      // Prevent dropdown from hiding when clicking inside it
      productDropdown.addEventListener('click', function (e) {
        e.stopPropagation();
      });

      // Add touch event handling for mobile
      productDropdown.addEventListener('touchstart', function (e) {
        e.stopPropagation();
      });
    }

    // Load all products
    async function loadAllProducts() {
      try {
        const response = await fetch('/api/products');
        allProducts = await response.json();
        window.allProducts = allProducts; // Store globally for validation

      } catch (error) {
        console.error('Error loading products:', error);
        // Show user-friendly error message
        if (window.showModernAlert) {
            window.showModernAlert('Failed to load products. Please check your connection.', 'error', 'Loading Error');
        }
      }
    }

    // Filter products with improved search
    function filterProducts(query) {
      if (!query.trim()) return [];

      const searchTerm = query.toLowerCase();
      return allProducts.filter(product => {
        const productName = product.product_name.toLowerCase();
        const typeName = (product.type_name || '').toLowerCase();

        return productName.includes(searchTerm) ||
          typeName.includes(searchTerm) ||
          productName.split(' ').some(word => word.startsWith(searchTerm));
      }).slice(0, 10); // Limit to 10 results for better performance
    }

    // Render dropdown options with mobile-optimized styling
    function renderDropdownOptions(filteredProducts) {
      if (!productDropdown) createProductDropdown();

      if (filteredProducts.length === 0) {
        productDropdown.innerHTML = `
          <div class="product-option-mobile" style="color: #9ca3af; text-align: center; padding: 16px;">
            <div style="color: #f3f4f6;">No products found</div>
            <div style="font-size: 12px; margin-top: 4px; color: #6b7280;">Try a different search term</div>
          </div>
        `;
        return;
      }

      productDropdown.innerHTML = filteredProducts.map(product => `
        <div class="product-option-mobile" data-product-id="${product.product_id}" data-product-name="${product.product_name}" data-product-price="${product.rate}" data-product-type="${product.type_name || ''}" style="padding: 12px 16px; border-bottom: 1px solid #374151; cursor: pointer; transition: background-color 0.2s; display: flex; justify-content: space-between; align-items: center; color: #f3f4f6;">
          <div style="flex: 1;">
            <div class="product-name" style="font-weight: 500; color: #f9fafb;">${product.product_name}</div>
            <div class="product-details" style="font-size: 12px; color: #9ca3af; margin-top: 2px;">${product.type_name || ''}</div>
          </div>
          <div class="product-price" style="font-weight: 600; color: #10b981;">${product.rate}</div>
        </div>
      `).join('');

      // Add click listeners with improved touch handling
      const options = productDropdown.querySelectorAll('.product-option-mobile');
      options.forEach(option => {
        // Add hover effects
        option.addEventListener('mouseenter', function () {
          this.style.backgroundColor = '#374151';
        });

        option.addEventListener('mouseleave', function () {
          this.style.backgroundColor = 'transparent';
        });

        const handleSelection = function (e) {
          e.preventDefault();
          e.stopPropagation();

          const productData = {
            product_id: this.getAttribute('data-product-id'),
            name: this.getAttribute('data-product-name'),
            price: this.getAttribute('data-product-price'),
            product_type: this.getAttribute('data-product-type')
          };

          // Set the input value
          productInput.value = productData.name;

          // Auto-fill the rate field
          if (rateInput) {
            rateInput.value = productData.price;
            // Trigger change event to update any dependent fields
            rateInput.dispatchEvent(new Event('change', { bubbles: true }));
          }

          // Set data attribute for validation
          productInput.setAttribute('data-selected-product', JSON.stringify(productData));

          // Add visual feedback
          productInput.style.borderColor = '#10b981';
          setTimeout(() => {
            productInput.style.borderColor = '';
          }, 1000);

          hideDropdown();

          // Show success feedback
          if (window.showSimpleToast) {
              window.showSimpleToast(`${productData.name} selected`, 'success');
          }
        };

        // Handle both click and touch events
        option.addEventListener('click', handleSelection);
        option.addEventListener('touchend', handleSelection);
      });
    }

    // Show dropdown with animation
    function showDropdown() {
      if (!productDropdown) createProductDropdown();

      if (!productDropdown || !productDropdown.style) return;

      // Calculate position relative to input
      const inputRect = productInput.getBoundingClientRect();
      productDropdown.style.left = inputRect.left + 'px';
      productDropdown.style.top = (inputRect.bottom + 4) + 'px';
      productDropdown.style.width = inputRect.width + 'px';
      productDropdown.style.minWidth = '200px';

      productDropdown.style.display = 'block';
      productDropdown.style.opacity = '0';
      productDropdown.style.transform = 'translateY(-10px)';

      // Animate in
      setTimeout(() => {
        if (productDropdown && productDropdown.style) {
          productDropdown.style.transition = 'all 0.2s ease';
          productDropdown.style.opacity = '1';
          productDropdown.style.transform = 'translateY(0)';
        }
      }, 10);
    }

    // Hide dropdown with animation
    function hideDropdown() {
      if (productDropdown && productDropdown.style) {
        productDropdown.style.transition = 'all 0.2s ease';
        productDropdown.style.opacity = '0';
        productDropdown.style.transform = 'translateY(-10px)';

        setTimeout(() => {
          if (productDropdown && productDropdown.style) {
            productDropdown.style.display = 'none';
            // Remove from DOM to prevent memory leaks
            if (productDropdown.parentNode) {
              productDropdown.parentNode.removeChild(productDropdown);
            }
            productDropdown = null;
          }
        }, 200);
      }
    }

    // Enhanced input event handling
    productInput.addEventListener('input', function () {
      const query = this.value;
      const filteredProducts = filterProducts(query);

      if (filteredProducts.length > 0) {
        renderDropdownOptions(filteredProducts);
        showDropdown();
      } else {
        hideDropdown();
      }
    });

    // Enhanced focus event handling
    productInput.addEventListener('focus', function () {
      if (this.value.trim()) {
        const filteredProducts = filterProducts(this.value);
        if (filteredProducts.length > 0) {
          renderDropdownOptions(filteredProducts);
          showDropdown();
        }
      }
    });

    // Enhanced blur event handling
    productInput.addEventListener('blur', function () {
      // Delay hiding to allow for option selection
      setTimeout(() => {
        hideDropdown();
      }, 200);
    });

    // Improved click outside handling
    document.addEventListener('click', function (e) {
      // Don't hide if clicking on a product option
      if (e.target.closest('.product-option-mobile')) {
        return;
      }

      // Don't hide if clicking on the input itself
      if (productInput.contains(e.target)) {
        return;
      }

      // Hide only if clicking outside both input and dropdown
      if (!productInput.contains(e.target) && (!productDropdown || !productDropdown.contains(e.target))) {
        hideDropdown();
      }
    });

    // Add keyboard navigation
    productInput.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        const options = productDropdown?.querySelectorAll('.product-option-mobile');
        if (!options || options.length === 0) return;

        const currentIndex = Array.from(options).findIndex(option =>
          option.classList.contains('selected')
        );

        let newIndex;
        if (e.key === 'ArrowDown') {
          newIndex = currentIndex < options.length - 1 ? currentIndex + 1 : 0;
        } else {
          newIndex = currentIndex > 0 ? currentIndex - 1 : options.length - 1;
        }

        // Remove previous selection
        options.forEach(option => option.classList.remove('selected'));

        // Add new selection
        options[newIndex].classList.add('selected');
        options[newIndex].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const selectedOption = productDropdown?.querySelector('.product-option-mobile.selected');
        if (selectedOption) {
          selectedOption.click();
        }
      } else if (e.key === 'Escape') {
        hideDropdown();
      }
    });

    // Load products on initialization
    loadAllProducts();
  }

  // --- Add Item Logic ---

  function setupAddItemHandler() {
    // Setup desktop add item handler
    const addItemBtn = document.getElementById('addItemBtn');
    if (addItemBtn) {
      // Remove existing event listeners by cloning the element
      const newAddItemBtn = addItemBtn.cloneNode(true);
      addItemBtn.parentNode.replaceChild(newAddItemBtn, addItemBtn);

      newAddItemBtn.classList.add('add-item-btn-mobile');
      newAddItemBtn.addEventListener('click', function (e) {
        e.preventDefault();

        handleAddItem('desktop');
      });
    }

    // Setup mobile add item handler
    const addItemBtnMobile = document.getElementById('addItemBtnMobile');
    if (addItemBtnMobile) {
      // Remove existing event listeners by cloning the element
      const newAddItemBtnMobile = addItemBtnMobile.cloneNode(true);
      addItemBtnMobile.parentNode.replaceChild(newAddItemBtnMobile, addItemBtnMobile);

      newAddItemBtnMobile.addEventListener('click', function (e) {
        e.preventDefault();

        handleAddItem('mobile');
      });
    }
  }

  async function handleAddItem(formType) {

    // Get form elements based on form type
    let productInput, quantityInput, priceInput, discountInput, advanceInput, vatInput, notesInput;

    if (formType === 'mobile') {
      productInput = document.getElementById('billProductMobile');
      quantityInput = document.getElementById('billQtyMobile');
      priceInput = document.getElementById('billRateMobile');
      discountInput = document.getElementById('billDiscountMobile');
      advanceInput = document.getElementById('billAdvPaidMobile');
      vatInput = document.getElementById('vatPercentMobile');
      notesInput = document.getElementById('itemNotesMobile');
    } else {
      productInput = document.getElementById('billProduct');
      quantityInput = document.getElementById('billQty');
      priceInput = document.getElementById('billRate');
      discountInput = document.getElementById('billDiscount');
      advanceInput = document.getElementById('billAdvPaid');
      vatInput = document.getElementById('vatPercent');
      notesInput = document.getElementById('itemNotes');
    }

    // Clear previous error states
    [productInput, quantityInput, priceInput].forEach(input => {
      if (input) {
        input.classList.remove('billing-input-error');
        const errorMsg = input.parentNode.querySelector('.billing-error-message');
        if (errorMsg) errorMsg.remove();
      }
    });

    // Validate required fields with better error handling
    let hasErrors = false;

    if (!productInput || !productInput.value.trim()) {
      showFieldError(productInput, 'Please select a product');
      hasErrors = true;
    }

    // Get selected product data
    const selectedProductData = productInput?.getAttribute('data-selected-product');

    if (!selectedProductData && productInput?.value.trim()) {
      // Check if we have a valid product name but no data attribute
      // This might happen if the product was selected but the attribute wasn't set properly
      const productName = productInput.value.trim();
      if (productName) {
        // Try to find the product in our loaded products
        const allProducts = window.allProducts || [];
        const foundProduct = allProducts.find(p => p.name === productName || p.product_name === productName);

        if (foundProduct) {
          // Set the data attribute now
          productInput.setAttribute('data-selected-product', JSON.stringify(foundProduct));

        } else {
          // Add a small delay to allow for any pending DOM updates
          setTimeout(() => {
            const retrySelectedData = productInput.getAttribute('data-selected-product');
            if (!retrySelectedData) {
              showFieldError(productInput, 'Please select a product from the search results');
              hasErrors = true;
            }
          }, 100);
          return;
        }
      } else {
        showFieldError(productInput, 'Please select a product from the search results');
        hasErrors = true;
      }
    }

    let productData;
    try {
      if (selectedProductData) {
          productData = JSON.parse(selectedProductData);
      } else if (productInput?.value.trim() && window.allProducts) {
          // Fallback again if attribute wasn't set but name matches
          const productName = productInput.value.trim();
          productData = window.allProducts.find(p => p.name === productName || p.product_name === productName);
          if (!productData) {
             throw new Error("Product data not found");
          }
      } else {
          throw new Error("No product selected");
      }
    } catch (error) {
      console.error('Error parsing product data:', error);
      showFieldError(productInput, 'Invalid product data. Please select a product again.');
      hasErrors = true;
    }

    if (!quantityInput || !quantityInput.value || quantityInput.value <= 0) {
      showFieldError(quantityInput, 'Please enter a valid quantity');
      hasErrors = true;
    }

    if (!priceInput || !priceInput.value || priceInput.value <= 0) {
      showFieldError(priceInput, 'Please enter a valid price');
      hasErrors = true;
    }

    if (hasErrors) {
      // Show overall error message
      if (window.showModernAlert) {
        window.showModernAlert('Please fix the errors above before adding the item', 'warning', 'Validation Error');
      }
      return;
    }

    // Get values with better parsing
    const productId = productData.product_id;
    const productName = productData.name || productData.product_name;
    const quantity = parseFloat(quantityInput.value) || 0;
    const price = parseFloat(priceInput.value) || 0;
    const discount = parseFloat(discountInput?.value) || 0;
    const advance = parseFloat(advanceInput?.value) || 0;
    const vatPercent = parseFloat(vatInput?.value) || 0;
    
    // Check if this product already exists in the bill
    const existingItemIndex = window.bill.findIndex(item => item.product_id === productId);

    if (existingItemIndex !== -1) {
      // Product already exists, show confirmation dialog
      const existingItem = window.bill[existingItemIndex];
      const newQuantity = existingItem.quantity + quantity;

      let confirmed;
      if (typeof window.showConfirmDialog !== 'function') {
        console.error('showConfirmDialog is not available!');
        // Fallback to simple confirm
        confirmed = confirm(`"${productName}" is already in the bill. Would you like to increase the quantity?`);

      } else {
        confirmed = await window.showConfirmDialog(
          `"${productName}" is already in the bill with quantity ${existingItem.quantity}.<br><br>Would you like to increase the quantity to ${newQuantity} instead of adding a duplicate item?`,
          'Product Already Added',
          'info'
        );
      }

      if (confirmed) {
        // Update existing item with new quantity and recalculate totals
        // Use global getVatConfig
        const { currentVatPercent, includeVatInPrice } = window.getVatConfig ? window.getVatConfig() : { currentVatPercent: 5, includeVatInPrice: false };
        
        const updated = {
          ...existingItem,
          quantity: newQuantity,
          rate: price,
          discount: discount,
          advance_paid: window.paymentMode === 'full' ? 0 : advance
        };
        
        if (window.recomputeItemTotals) {
             window.bill[existingItemIndex] = window.recomputeItemTotals(updated, currentVatPercent, includeVatInPrice);
        }

        if (window.refreshBillingUI) window.refreshBillingUI();

        // Clear form fields
        clearBillingForm(formType);

        // Show success message
        if (window.showSimpleToast) window.showSimpleToast('Quantity updated', 'success');

        // Focus back to product input
        setTimeout(() => {
          if (productInput) {
            productInput.focus();
          }
        }, 500);
      }
      return;
    }

    const { currentVatPercent, includeVatInPrice } = window.getVatConfig ? window.getVatConfig() : { currentVatPercent: 5, includeVatInPrice: false };

    // Get notes value
    const notes = notesInput ? notesInput.value.trim() : '';

    // Add item to bill
    const item = {
      product_id: productId,
      product_name: productName,
      quantity: quantity,
      rate: price, // Changed from 'price' to 'rate' to match backend expectation
      discount: discount,
      advance_paid: window.paymentMode === 'full' ? 0 : advance, // Set to 0 if full payment mode
      notes: notes // Include notes in the item
    };
    
    if (window.recomputeItemTotals) {
        window.bill.push(window.recomputeItemTotals(item, currentVatPercent, includeVatInPrice));
    } else {
        window.bill.push(item); // Fallback
    }

    if (window.refreshBillingUI) window.refreshBillingUI();

    // Clear form fields with better UX
    clearBillingForm(formType);

    // Show success message with better feedback
    showSimpleToast('Item added', 'success');

    // Focus back to product input for quick addition of next item
    setTimeout(() => {
      if (productInput) {
        productInput.focus();
      }
    }, 500);
  }

  // --- Item Management ---

  function editBillItem(index) {
    const bill = window.bill || [];
    const item = bill[index];
    if (!item) {
      return;
    }

    // Desktop form elements
    const billProductElement = document.getElementById('billProduct');
    const billQuantityElement = document.getElementById('billQty');
    const billPriceElement = document.getElementById('billRate');
    const billDiscountElement = document.getElementById('billDiscount');
    const billAdvanceElement = document.getElementById('billAdvPaid');
    const billVatElement = document.getElementById('vatPercent');
    const itemNotesElement = document.getElementById('itemNotes');

    // Mobile form elements
    const billProductMobileElement = document.getElementById('billProductMobile');
    const billQuantityMobileElement = document.getElementById('billQtyMobile');
    const billPriceMobileElement = document.getElementById('billRateMobile');
    const billDiscountMobileElement = document.getElementById('billDiscountMobile');
    const billAdvanceMobileElement = document.getElementById('billAdvPaidMobile');
    const billVatMobileElement = document.getElementById('vatPercentMobile');
    const itemNotesMobileElement = document.getElementById('itemNotesMobile');

    // Populate desktop form elements
    if (billProductElement) {
      billProductElement.value = item.product_name;
      billProductElement.setAttribute('data-selected-product', JSON.stringify({
        product_id: item.product_id,
        name: item.product_name,
        price: item.rate, 
        product_type: 'Unknown'
      }));
    }
    if (billQuantityElement) billQuantityElement.value = item.quantity;
    if (billPriceElement) billPriceElement.value = item.rate;
    if (billDiscountElement) billDiscountElement.value = item.discount || 0;
    if (billAdvanceElement) billAdvanceElement.value = item.advance_paid || 0;
    if (billVatElement) billVatElement.value = item.vat_percent || 5;
    if (itemNotesElement) itemNotesElement.value = item.notes || '';

    // Populate mobile form elements
    if (billProductMobileElement) {
      billProductMobileElement.value = item.product_name;
      billProductMobileElement.setAttribute('data-selected-product', JSON.stringify({
        product_id: item.product_id,
        name: item.product_name,
        price: item.rate, 
        product_type: 'Unknown'
      }));
    }

    if (billQuantityMobileElement) billQuantityMobileElement.value = item.quantity;
    if (billPriceMobileElement) billPriceMobileElement.value = item.rate;
    if (billDiscountMobileElement) billDiscountMobileElement.value = item.discount || 0;
    if (billAdvanceMobileElement) billAdvanceMobileElement.value = item.advance_paid || 0;
    if (billVatMobileElement) billVatMobileElement.value = item.vat_percent || 5;
    if (itemNotesMobileElement) itemNotesMobileElement.value = item.notes || '';

    // Remove from bill array
    bill.splice(index, 1);
    
    // Refresh UI
    if (window.BillingTotals && window.BillingTotals.refreshBillingUI) {
      window.BillingTotals.refreshBillingUI();
    } else if (typeof window.refreshBillingUI === 'function') {
      window.refreshBillingUI();
    }

    // Show success message
    if (window.showSimpleToast) {
      window.showSimpleToast('Item loaded for editing!', 'info');
    }
  }

  async function deleteBillItem(index) {
    const showConfirm = window.showConfirmDialog || window.confirm;
    const confirmed = await showConfirm(
      'Are you sure you want to delete this item? This action cannot be undone.',
      'Delete Item',
      'delete'
    );

    if (confirmed) {
      const bill = window.bill || [];
      bill.splice(index, 1);
      
      // Refresh UI
      if (window.BillingTotals && window.BillingTotals.refreshBillingUI) {
        window.BillingTotals.refreshBillingUI();
      } else if (typeof window.refreshBillingUI === 'function') {
        window.refreshBillingUI();
      }

      // Show success toast
      if (window.showSimpleToast) {
        window.showSimpleToast('Item deleted successfully!', 'success');
      }
    }
  }

  function updateBillItemField(index, field, value) {
    const bill = window.bill || [];
    const item = bill[index];
    if (!item) return;

    // Convert value to appropriate type
    let parsedValue;
    if (field === 'quantity') {
      parsedValue = parseInt(value) || 1;
      if (parsedValue < 1) parsedValue = 1;
    } else {
      parsedValue = parseFloat(value) || 0;
      if (parsedValue < 0) parsedValue = 0;
    }
    if (field === 'discount') {
      if (parsedValue > 100) parsedValue = 100;
    }
    if (field === 'advance_paid') {
      const { includeVatInPrice, currentVatPercent } = (window.BillingTotals && window.BillingTotals.getVatConfig) 
        ? window.BillingTotals.getVatConfig() 
        : (window.getVatConfig ? window.getVatConfig() : { includeVatInPrice: false, currentVatPercent: 5 });

      const temp = { ...item };
      
      if (window.BillingTotals && window.BillingTotals.recomputeItemTotals) {
        window.BillingTotals.recomputeItemTotals(temp, currentVatPercent, includeVatInPrice);
      } else if (window.recomputeItemTotals) {
        window.recomputeItemTotals(temp, currentVatPercent, includeVatInPrice);
      }
      
      const maxAdvance = temp.total;
      if (parsedValue > maxAdvance) parsedValue = maxAdvance;
    }

    // Update the field
    item[field] = parsedValue;

    const { includeVatInPrice, currentVatPercent } = (window.BillingTotals && window.BillingTotals.getVatConfig) 
        ? window.BillingTotals.getVatConfig() 
        : (window.getVatConfig ? window.getVatConfig() : { includeVatInPrice: false, currentVatPercent: 5 });

    if (window.BillingTotals && window.BillingTotals.recomputeItemTotals) {
        window.BillingTotals.recomputeItemTotals(item, currentVatPercent, includeVatInPrice);
    } else if (window.recomputeItemTotals) {
        window.recomputeItemTotals(item, currentVatPercent, includeVatInPrice);
    }

    if (window.BillingTotals && window.BillingTotals.refreshBillingUI) {
      window.BillingTotals.refreshBillingUI();
    } else if (window.refreshBillingUI) {
      window.refreshBillingUI();
    }

    // Update total advance field if advance was changed
    // Assuming updateTotalAdvanceField is available globally or we can reimplement it
    if (field === 'advance_paid') {
        if (typeof window.updateTotalAdvanceField === 'function') {
            window.updateTotalAdvanceField();
        } else if (window.BillingTotals && window.BillingTotals.updateTotalAdvanceField) {
             window.BillingTotals.updateTotalAdvanceField();
        }
    }

    // Show success message
    if (window.showSimpleToast) {
      window.showSimpleToast(`${field.charAt(0).toUpperCase() + field.slice(1)} updated!`, 'success');
    }
  }

  // --- Export to Namespace ---
  window.BillingItems = {
    setupProductQuickAdd,
    setupAddItemHandler,
    handleAddItem,
    clearBillingForm,
    editBillItem,
    deleteBillItem,
    updateBillItemField
  };

  // Global aliases for backward compatibility
  window.setupProductQuickAdd = setupProductQuickAdd;
  window.setupAddItemHandler = setupAddItemHandler;
  window.handleAddItem = handleAddItem;
  window.editBillItem = editBillItem;
  window.deleteBillItem = deleteBillItem;
  window.updateBillItemField = updateBillItemField;


})();
