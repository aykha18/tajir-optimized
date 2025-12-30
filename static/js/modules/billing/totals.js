;(function () {
  // --- Private Helpers & Constants ---

  // Helper to get DOM references
  let _domRefs;
  function getDomRefs() {
    const valid = _domRefs &&
      _domRefs.saveBillBtn && document.contains(_domRefs.saveBillBtn) &&
      _domRefs.whatsappBtn && document.contains(_domRefs.whatsappBtn) &&
      _domRefs.emailBtn && document.contains(_domRefs.emailBtn) &&
      _domRefs.printBtn && document.contains(_domRefs.printBtn) &&
      _domRefs.subtotalElement && document.contains(_domRefs.subtotalElement) &&
      _domRefs.vatElement && document.contains(_domRefs.vatElement) &&
      _domRefs.totalElement && document.contains(_domRefs.totalElement) &&
      _domRefs.totalAdvanceInput && document.contains(_domRefs.totalAdvanceInput);
    
    if (valid) return _domRefs;
    
    _domRefs = {
      saveBillBtn: document.getElementById('saveBillBtn'),
      whatsappBtn: document.getElementById('whatsappBtn'),
      emailBtn: document.getElementById('emailBtn'),
      printBtn: document.getElementById('printBtn'),
      subtotalElement: document.getElementById('subTotal'),
      vatElement: document.getElementById('vatAmount'),
      totalElement: document.getElementById('amountDue'),
      totalAdvanceInput: document.getElementById('totalAdvancePaid'),
    };
    return _domRefs;
  }

  function setActionButtonsState(enabled) {
    const { saveBillBtn, whatsappBtn, emailBtn, printBtn } = getDomRefs();
    const configs = [
      { el: saveBillBtn, enable: ['bg-yellow-600', 'text-white', 'hover:bg-yellow-500'], disable: ['opacity-50', 'pointer-events-none', 'bg-yellow-600/40', 'text-white/60'] },
      { el: whatsappBtn, enable: ['bg-green-600', 'text-white', 'hover:bg-green-500'], disable: ['opacity-50', 'pointer-events-none', 'bg-green-600/40', 'text-white/60'] },
      { el: emailBtn, enable: ['bg-blue-600', 'text-white', 'hover:bg-blue-500'], disable: ['opacity-50', 'pointer-events-none', 'bg-blue-600/40', 'text-white/60'] },
      { el: printBtn, enable: ['bg-indigo-600', 'text-white', 'hover:bg-indigo-500'], disable: ['opacity-50', 'pointer-events-none', 'bg-indigo-600/40', 'text-white/60'] },
    ];
    
    configs.forEach(({ el, enable, disable }) => {
      if (!el) return;
      el.disabled = !enabled;
      el.setAttribute('aria-disabled', String(!enabled));
      if (enabled) {
        el.classList.remove(...disable);
        el.classList.add(...enable);
      } else {
        el.classList.add(...disable);
        el.classList.remove(...enable);
      }
    });
  }

  function formatAmount(val) {
    const n = typeof val === 'number' ? val : parseFloat(val) || 0;
    return n.toFixed(2);
  }

  function round2(n) {
    const x = typeof n === 'number' ? n : parseFloat(n) || 0;
    return Math.round(x * 100) / 100;
  }

  function getVatConfig() {
    const vatInputEl = document.getElementById('vatPercent') || document.getElementById('vatPercentMobile');
    let currentVatPercent = parseFloat(vatInputEl?.value);
    if (isNaN(currentVatPercent)) {
      currentVatPercent = window.getDefaultVatPercent ? window.getDefaultVatPercent() : 5;
    }
    currentVatPercent = Math.max(0, Math.min(100, currentVatPercent));
    const includeVatInPrice = window.getIncludeVatInPrice ? window.getIncludeVatInPrice() : false;
    console.log('getVatConfig:', { currentVatPercent, includeVatInPrice });
    return { currentVatPercent, includeVatInPrice };
  }

  // --- Core Calculation Logic ---

  function recomputeItemTotals(it, currentVatPercent, includeVatInPrice) {
    console.log('recomputeItemTotals input:', it, currentVatPercent, includeVatInPrice);
    const rate = parseFloat(it.rate) || 0;
    const quantity = parseInt(it.quantity) || 0;
    const discount = parseFloat(it.discount) || 0;
    const subtotalBeforeDiscount = rate * quantity;
    const discountAmount = (subtotalBeforeDiscount * discount) / 100;
    const afterDiscount = subtotalBeforeDiscount - discountAmount;
    
    it.subtotal = round2(subtotalBeforeDiscount);
    it.vat_percent = currentVatPercent;
    
    if (includeVatInPrice) {
      // If price includes VAT, we need to extract the VAT amount
      const impliedVat = (afterDiscount * currentVatPercent) / (100 + currentVatPercent);
      it.vat_amount = round2(impliedVat);
      it.total = round2(afterDiscount);
    } else {
      // If price excludes VAT, we add VAT on top
      it.vat_amount = round2((afterDiscount * currentVatPercent) / 100);
      it.total = round2(afterDiscount + it.vat_amount);
    }
    console.log('recomputeItemTotals output:', it);
    return it;
  }

  function computeTotals(billItems, includeVatInPrice, vatPercent) {
    let subtotal, totalVat, totalBeforeAdvance;
    
    if (includeVatInPrice) {
      const totalWithVat = billItems.reduce((sum, item) => sum + (item.total || 0), 0);
      const impliedVat = billItems.reduce((sum, item) => sum + (item.vat_amount || 0), 0);
      
      totalVat = round2(impliedVat);
      subtotal = round2(totalWithVat - totalVat);
      totalBeforeAdvance = totalWithVat;
    } else {
      subtotal = billItems.reduce((sum, item) => sum + (item.total || 0), 0);
      totalVat = billItems.reduce((sum, item) => sum + (item.vat_amount || 0), 0);
      
      subtotal = round2(subtotal);
      totalVat = round2(totalVat);
      totalBeforeAdvance = round2(subtotal + totalVat);
    }
    
    const totalAdvance = round2(billItems.reduce((sum, item) => sum + (item.advance_paid || 0), 0));
    const amountDue = Math.max(0, round2(totalBeforeAdvance - totalAdvance));
    
    return { subtotal, totalVat, totalAdvance, amountDue, totalBeforeAdvance };
  }

  // --- Rendering & UI Updates ---

  function updateBillTableHeader(includeVatInPrice) {
    const thead = document.getElementById('billTable')?.querySelector('thead tr');
    if (!thead) return;

    // Find the Tax column header (5th column, index 4)
    // Columns: Name, Qty, Rate, Disc, [Tax], Total, Action
    const taxHeader = thead.children[4];
    if (taxHeader) {
      taxHeader.style.display = includeVatInPrice ? 'none' : '';
    }
  }

  function renderBillRow(item, index, includeVatInPrice) {
    const discountCalc = formatAmount(((item.rate || 0) * (item.quantity || 0) * (item.discount || 0) / 100));
    const vatCell = includeVatInPrice ? '' : `<td class="px-3 py-3">${formatAmount(item.vat_amount || 0)}</td>`;
    
    return `
      <tr class="hover:bg-neutral-800/50 transition-colors swipe-action" data-index="${index}">
        <td class="px-3 py-3">${item.product_name || ''}</td>
        <td class="px-3 py-3">
          <input type="number" min="1" value="${item.quantity || 0}" 
                 class="w-16 bg-transparent border-none text-center text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400 rounded px-1"
                 onchange="updateBillItemField(${index}, 'quantity', this.value)"
                 onblur="updateBillItemField(${index}, 'quantity', this.value)">
        </td>
        <td class="px-3 py-3">${formatAmount(item.rate || 0)}</td>
        <td class="px-3 py-3">
          <div class="flex flex-col items-center">
            <input type="number" min="0" max="100" step="0.01" value="${formatAmount(item.discount || 0)}" 
                   class="w-20 bg-transparent border-none text-center text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400 rounded px-1"
                   onchange="updateBillItemField(${index}, 'discount', this.value)"
                   onblur="updateBillItemField(${index}, 'discount', this.value)">
            <span class="text-xs text-gray-400">${discountCalc}</span>
          </div>
        </td>
        ${vatCell}
        <td class="px-3 py-3">${formatAmount(item.total || 0)}</td>
        <td class="px-3 py-3 flex gap-2">
          <button class="text-red-400 hover:text-red-300 hover:bg-red-500/10 px-2 py-1 rounded transition-all duration-200 transform hover:scale-110 hover:shadow-sm mobile-btn" onclick="deleteBillItem(${index})">
            Delete
          </button>
        </td>
      </tr>
    `;
  }

  function renderBillTable() {
    const tbody = document.getElementById('billTable')?.querySelector('tbody');
    if (!tbody) return;

    const { includeVatInPrice } = getVatConfig();
    
    // Access global bill variable
    const billItems = window.bill || [];

    tbody.innerHTML = billItems.map((item, index) => renderBillRow(item, index, includeVatInPrice)).join('');

    // Update table header to show/hide VAT column
    updateBillTableHeader(includeVatInPrice);

    // Reinitialize swipe actions for mobile
    if (window.mobileEnhancements && window.mobileEnhancements.setupSwipeActions) {
      setTimeout(() => {
        window.mobileEnhancements.setupSwipeActions();
      }, 100);
    }
  }

  function updateSummaryDisplay(subtotal, totalVat, amountDue) {
    const { subtotalElement, vatElement, totalElement } = getDomRefs();
    if (subtotalElement) subtotalElement.textContent = `${formatAmount(subtotal || 0)}`;
    if (vatElement) vatElement.textContent = `${formatAmount(totalVat || 0)}`;
    if (totalElement) totalElement.textContent = `${formatAmount(amountDue || 0)}`;
  }

  function updateTotalAdvanceField() {
    const billItems = window.bill || [];
    const totalAdvance = billItems.reduce((sum, item) => sum + (item.advance_paid || 0), 0);
    const totalAdvanceInput = getDomRefs().totalAdvanceInput || document.getElementById('totalAdvancePaid');
    if (totalAdvanceInput) {
      // Avoid overwriting if user is currently typing in it, unless the value is significantly different (e.g. clamping)
      if (document.activeElement === totalAdvanceInput) {
          const currentVal = parseFloat(totalAdvanceInput.value) || 0;
          if (Math.abs(currentVal - totalAdvance) < 0.01) {
              return;
          }
      }
      totalAdvanceInput.value = formatAmount(totalAdvance);
    }
  }

  function updateTotals() {
    const { currentVatPercent, includeVatInPrice } = getVatConfig();
    const billItems = window.bill || [];
    
    console.log('updateTotals:', { billItems, currentVatPercent, includeVatInPrice });

    const totals = computeTotals(billItems, includeVatInPrice, currentVatPercent);
    const subtotal = totals.subtotal;
    const totalVat = totals.totalVat;
    const amountDue = window.paymentMode === 'full' ? 0 : totals.amountDue;
    const displayAdvance = window.paymentMode === 'full' ? totals.totalBeforeAdvance : totals.totalAdvance;

    setActionButtonsState(billItems.length > 0);
    updateSummaryDisplay(subtotal, totalVat, amountDue);
    
    if (window.paymentMode === 'full') {
      const totalAmountLabel = document.querySelector('.bill-summary-row:last-child .text-neutral-400');
      if (totalAmountLabel) {
        totalAmountLabel.textContent = 'Total Amount Paid:';
      }
      const totalElement = getDomRefs().totalElement;
      if (totalElement) {
        totalElement.textContent = `${formatAmount(totals.totalBeforeAdvance || 0)}`;
      }
    }
    updateTotalAdvanceField();
  }

  function updateVatDisplay() {
    const { includeVatInPrice } = getVatConfig();
    updateBillTableHeader(includeVatInPrice);
  }

  function refreshBillingUI() {
    renderBillTable();
    updateTotals();
    updateVatDisplay();
  }

  function refreshBillRow(index) {
    const tbody = document.getElementById('billTable')?.querySelector('tbody');
    if (!tbody) return false;
    
    const row = tbody.querySelector(`tr[data-index="${index}"]`);
    if (!row) return false;
    
    const { includeVatInPrice } = getVatConfig();
    const billItems = window.bill || [];
    const item = billItems[index];
    if (!item) return false;

    const html = renderBillRow(item, index, includeVatInPrice);
    row.outerHTML = html;
    return true;
  }

  // --- Exposed Window Functions (Handlers) ---

  window.onVatInputChange = function () {
    const { currentVatPercent, includeVatInPrice } = getVatConfig();
    const billItems = window.bill || [];
    
    billItems.forEach(it => {
      recomputeItemTotals(it, currentVatPercent, includeVatInPrice);
    });
    
    refreshBillingUI();
    
    if (window.updateVatSummaryLabel) {
      window.updateVatSummaryLabel();
    }
  };

  window.deleteBillItem = async function (index) {
    if (!window.showConfirmDialog) {
        if (!confirm('Are you sure you want to delete this item?')) return;
        // Fallback if dialog not present
    } else {
        const confirmed = await window.showConfirmDialog(
            'Are you sure you want to delete this item? This action cannot be undone.',
            'Delete Item',
            'delete'
        );
        if (!confirmed) return;
    }

    const billItems = window.bill || [];
    billItems.splice(index, 1);
    refreshBillingUI();

    if (window.showSimpleToast) {
      window.showSimpleToast('Item deleted successfully!', 'success');
    }
  };

  window.updateBillItemField = function (index, field, value) {
    const billItems = window.bill || [];
    const item = billItems[index];
    if (!item) return;

    // Convert value
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
      const { includeVatInPrice, currentVatPercent } = getVatConfig();
      const temp = { ...item };
      recomputeItemTotals(temp, currentVatPercent, includeVatInPrice);
      const maxAdvance = temp.total;
      if (parsedValue > maxAdvance) parsedValue = maxAdvance;
    }

    // Update
    item[field] = parsedValue;

    const { currentVatPercent, includeVatInPrice } = getVatConfig();
    recomputeItemTotals(item, currentVatPercent, includeVatInPrice);

    // Optimized refresh: try to refresh just the row if possible, otherwise full UI
    if (!refreshBillRow(index)) {
        refreshBillingUI();
    } else {
        updateTotals();
    }

    // Update total advance field if advance was changed
    if (field === 'advance_paid') {
      updateTotalAdvanceField();
    }

    if (window.showSimpleToast) {
      window.showSimpleToast(`${field.charAt(0).toUpperCase() + field.slice(1)} updated!`, 'success');
    }
  };

  // --- Advance Distribution Logic ---

  function distributeAdvance(totalAdvanceValue) {
    const billItems = window.bill || [];
    if (billItems.length === 0) return;

    let remainingAdvance = parseFloat(totalAdvanceValue) || 0;
    
    // First pass: Reset all advance payments to 0
    billItems.forEach(item => {
      item.advance_paid = 0;
    });

    // Second pass: Distribute advance sequentially
    const { includeVatInPrice, currentVatPercent } = getVatConfig();

    for (let i = 0; i < billItems.length; i++) {
      const item = billItems[i];
      
      // Calculate item total to know max advance allowed for this item
      // We need to ensure item total is up to date
      recomputeItemTotals(item, currentVatPercent, includeVatInPrice);
      
      const maxAdvance = item.total;
      
      if (remainingAdvance <= 0) {
        item.advance_paid = 0;
      } else if (remainingAdvance >= maxAdvance) {
        item.advance_paid = maxAdvance;
        remainingAdvance -= maxAdvance;
      } else {
        item.advance_paid = round2(remainingAdvance);
        remainingAdvance = 0;
      }
    }

    // Update UI
    // We use updateTotals instead of refreshBillingUI to avoid re-rendering the whole table input fields
    // causing loss of focus if user is typing (though here they are typing in total advance field)
    updateTotals();
    
    // However, we need to update the individual row advance fields if they exist?
    // The current table render (renderBillRow) does NOT show advance_paid per row?
    // Let's check renderBillRow.
    // renderBillRow (lines 141-173) does NOT show advance_paid input or value.
    // So we don't need to re-render table.
    // But wait, if payment mode is NOT full, advance fields might be visible?
    // renderBillRow does not seem to handle advance payment inputs.
    // Let's check billing-system.js or the HTML structure.
    // If the table doesn't show advance fields, where are they?
    // Maybe they are separate? Or maybe renderBillRow is missing them?
    
    // Checking billing-system.js:
    // initializePaymentMode (line 509) talks about document.getElementById('billAdvPaid') etc.
    // These seem to be in the "Add Item" form, not the table.
    // But wait, if I have multiple items, can I set advance per item?
    // The bill array has 'advance_paid' per item (line 121 of totals.js sums it up).
    // But where is it edited?
    // updateBillItemField (line 306 totals.js) handles 'advance_paid'.
    // But renderBillRow doesn't seem to render an input for it.
    
    // Maybe I missed something in renderBillRow.
    // Let's look at renderBillRow again.
    // It has: Name, Qty (input), Rate, Disc (input), [Tax], Total, Action.
    // No Advance column.
    
    // So how does one set advance per item?
    // Maybe it's only set when adding the item?
    // 'billAdvPaid' is in the add item form.
    // Once added, can you edit it?
    // If renderBillRow doesn't have it, you can't edit it in the table.
    // So 'distributeAdvance' updating 'item.advance_paid' is fine, but the user won't see it per item in the table.
    // They will only see the total advance paid updated.
    
    // If so, updateTotals() is sufficient.
  }

  function setupTotalAdvanceDistribution() {
    const totalAdvanceInput = document.getElementById('totalAdvancePaid');
    if (!totalAdvanceInput) return;

    totalAdvanceInput.addEventListener('input', function() {
       distributeAdvance(this.value);
    });
  }

  // --- Export to Namespace ---
  
  window.BillingTotals = {
    computeTotals,
    updateTotals,
    renderBillTable,
    refreshBillingUI,
    formatAmount,
    round2,
    recomputeItemTotals,
    setActionButtonsState,
    getVatConfig,
    setupTotalAdvanceDistribution,
    distributeAdvance,
    updateTotalAdvanceField
  };

  // Expose global aliases for backward compatibility if needed
  window.computeTotals = computeTotals;
  window.updateTotals = updateTotals;
  window.renderBillTable = renderBillTable;
  window.refreshBillingUI = refreshBillingUI;
  window.formatAmount = formatAmount;
  window.round2 = round2; // often used elsewhere
  window.getVatConfig = getVatConfig;
  window.recomputeItemTotals = recomputeItemTotals;
  window.updateTotalAdvanceField = updateTotalAdvanceField;

})();
