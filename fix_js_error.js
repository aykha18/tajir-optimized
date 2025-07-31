// Fix for JavaScript addEventListener error
// Add this to the beginning of your JavaScript section

// Safe element getter with null check
function safeGetElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        console.log(`Element with id '${id}' not found`);
        return null;
    }
    return element;
}

// Safe event listener adder
function safeAddEventListener(element, event, handler) {
    if (element && typeof element.addEventListener === 'function') {
        element.addEventListener(event, handler);
        return true;
    }
    console.log('Cannot add event listener: element is null or not an element');
    return false;
}

// Initialize search invoice functionality safely
function initializeSearchInvoiceSafely() {
    const elements = {
        btn: safeGetElement('searchInvoiceBtn'),
        modal: safeGetElement('searchInvoiceModal'),
        close: safeGetElement('closeSearchInvoice'),
        input: safeGetElement('searchInvoiceInput'),
        results: safeGetElement('searchInvoiceResults')
    };
    
    // Check if all required elements exist
    const missingElements = Object.entries(elements)
        .filter(([name, element]) => !element)
        .map(([name]) => name);
    
    if (missingElements.length > 0) {
        console.log('Missing search invoice elements:', missingElements);
        return false;
    }
    
    // Add event listeners safely
    safeAddEventListener(elements.btn, 'click', () => {
        elements.modal.classList.remove('hidden');
        elements.input.value = '';
        elements.results.innerHTML = '';
        elements.input.focus();
    });
    
    safeAddEventListener(elements.close, 'click', () => {
        elements.modal.classList.add('hidden');
    });
    
    safeAddEventListener(elements.input, 'input', async (e) => {
        const q = e.target.value.trim().toLowerCase();
        if (!q) {
            elements.results.innerHTML = '';
            return;
        }
        
        try {
            const resp = await fetch('/api/bills');
            const allBills = await resp.json();
            const results = (allBills || []).filter(bill =>
                (bill.bill_number && bill.bill_number.toLowerCase().includes(q)) ||
                (bill.customer_name && bill.customer_name.toLowerCase().includes(q)) ||
                (bill.customer_phone && bill.customer_phone.toLowerCase().includes(q))
            );
            
            elements.results.innerHTML = results.length
                ? `<table class="min-w-full text-sm">
                    <thead><tr>
                      <th class="px-2 py-1 text-left">Invoice #</th>
                      <th class="px-2 py-1 text-left">Customer</th>
                      <th class="px-2 py-1 text-left">Date</th>
                      <th class="px-2 py-1 text-left">Amount</th>
                      <th class="px-2 py-1 text-left">Status</th>
                      <th></th>
                    </tr></thead>
                    <tbody>
                      ${results.map(bill => `
                        <tr>
                          <td class="px-2 py-1">${bill.bill_number || bill.bill_id}</td>
                          <td class="px-2 py-1">${bill.customer_name || ''}</td>
                          <td class="px-2 py-1">${bill.bill_date || ''}</td>
                          <td class="px-2 py-1">AED ${parseFloat(bill.total_amount).toFixed(2)}</td>
                          <td class="px-2 py-1">${bill.status || (bill.balance_amount > 0 ? 'Pending' : 'Paid')}</td>
                          <td class="px-2 py-1 flex gap-2">
                            <button class="reprint-btn bg-indigo-600 hover:bg-indigo-500 text-white rounded px-3 py-1" data-id="${bill.bill_id}">Reprint</button>
                            ${(bill.status === 'Pending' || (bill.balance_amount && bill.balance_amount > 0)) ? `<button class="mark-paid-btn bg-green-600 hover:bg-green-500 text-white rounded px-3 py-1" data-id="${bill.bill_id}" data-balance="${bill.balance_amount}">Mark as Paid</button>` : ''}
                          </td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>`
                : '<div class="text-neutral-400 text-center py-4">No invoices found.</div>';
        } catch (error) {
            console.error('Error searching invoices:', error);
            elements.results.innerHTML = '<div class="text-red-400 text-center py-4">Error loading invoices</div>';
        }
    });
    
    // Add click handlers for reprint and mark as paid
    safeAddEventListener(elements.results, 'click', function(e) {
        const btn = e.target.closest('.reprint-btn');
        if (btn) {
            const billId = btn.getAttribute('data-id');
            window.open(`/api/bills/${billId}/print`, '_blank');
        }
    });
    
    console.log('Search invoice functionality initialized successfully');
    return true;
}

// Call this function when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search invoice functionality
    initializeSearchInvoiceSafely();
    
    // Initialize other functionality safely
    const shopSettingsForm = safeGetElement('shopSettingsForm');
    if (!shopSettingsForm) {
        console.log('Shop settings form not found, skipping initialization');
    }
}); 