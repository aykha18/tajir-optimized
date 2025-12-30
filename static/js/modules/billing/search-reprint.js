;(function () {
  const ns = {};

  ns.init = function () {
    // Search & Reprint Invoice Modal Logic
    const searchInvoiceBtn = document.getElementById('searchInvoiceBtn');
    if (searchInvoiceBtn) {
      searchInvoiceBtn.addEventListener('click', () => {
        const modal = document.getElementById('searchInvoiceModal');
        if (modal) {
          modal.classList.remove('hidden');
          const input = document.getElementById('searchInvoiceInput');
          const results = document.getElementById('searchInvoiceResults');
          if (input) {
            input.value = '';
            input.focus();
          }
          if (results) results.innerHTML = '';
        }
      });
    }

    const closeSearchInvoice = document.getElementById('closeSearchInvoice');
    if (closeSearchInvoice) {
      closeSearchInvoice.addEventListener('click', () => {
        const modal = document.getElementById('searchInvoiceModal');
        if (modal) modal.classList.add('hidden');
      });
    }

    const searchInvoiceInput = document.getElementById('searchInvoiceInput');
    if (searchInvoiceInput) {
      searchInvoiceInput.addEventListener('input', async (e) => {
        const q = e.target.value.trim().toLowerCase();
        const resultsContainer = document.getElementById('searchInvoiceResults');
        
        if (!q) {
          if (resultsContainer) resultsContainer.innerHTML = '';
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

          if (resultsContainer) {
            resultsContainer.innerHTML = results.length
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
                        <td class="px-2 py-1">AED ${window.formatAmount ? window.formatAmount(bill.total_amount) : bill.total_amount}</td>
                        <td class="px-2 py-1">${bill.status || (bill.balance_amount > 0 ? 'Pending' : 'Paid')}</td>
                        <td class="px-2 py-1 flex gap-2">
                          <button class="reprint-btn bg-indigo-600 hover:bg-indigo-500 text-white rounded px-3 py-1" data-id="${bill.bill_id}">Print</button>
                          <button class="whatsapp-btn bg-green-600 hover:bg-green-500 text-white rounded px-3 py-1" data-id="${bill.bill_id}">Send WhatsApp</button>
                          ${(bill.status === 'Pending' || (bill.balance_amount && bill.balance_amount > 0)) ? `<button class="mark-paid-btn bg-green-600 hover:bg-green-500 text-white rounded px-3 py-1" data-id="${bill.bill_id}" data-balance="${bill.balance_amount}">Mark Paid</button>` : ''}
                        </td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>`
              : '<div class="text-neutral-400 text-center py-4">No invoices found matching your search.</div>';
          }
        } catch (error) {
          console.error('Error searching bills:', error);
          if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="text-red-400 text-center py-4">Error searching bills. Please try again.</div>';
          }
        }
      });
    }

    // Combined Reprint, WhatsApp, and Mark as Paid functionality
    const searchInvoiceResults = document.getElementById('searchInvoiceResults');
    if (searchInvoiceResults) {
      searchInvoiceResults.addEventListener('click', async function (e) {
        const reprintBtn = e.target.closest('.reprint-btn');
        const whatsappBtn = e.target.closest('.whatsapp-btn');
        const payBtn = e.target.closest('.mark-paid-btn');

        // Handle Reprint functionality
        if (reprintBtn) {
          const billId = reprintBtn.getAttribute('data-id');
          window.open(`/api/bills/${billId}/print`, '_blank');
          return; // Prevent further processing
        }

        // Handle WhatsApp functionality
        if (whatsappBtn) {
          const billId = whatsappBtn.getAttribute('data-id');
          try {
            // First get the bill details to get customer phone
            const billResponse = await fetch(`/api/bills/${billId}`);
            if (!billResponse.ok) {
              window.showModernAlert('Failed to get bill details', 'error');
              return;
            }

            const billData = await billResponse.json();
            const customerPhone = billData.bill?.customer_phone || '';

            if (!customerPhone) {
              window.showModernAlert('Customer phone number not found for this bill', 'error');
              return;
            }

            // Now call the WhatsApp endpoint with required parameters
            const response = await fetch(`/api/bills/${billId}/whatsapp`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                phone: customerPhone,
                language: 'en' // Default to English
              })
            });

            if (response.ok) {
              const data = await response.json();
              if (data.whatsapp_url) {
                window.open(data.whatsapp_url, '_blank');
              }
            } else {
              const errorData = await response.json();
              window.showModernAlert(errorData.error || 'Failed to generate WhatsApp link', 'error');
            }
          } catch (error) {
            console.error('WhatsApp error:', error);
            window.showModernAlert('Error generating WhatsApp link', 'error');
          }
          return; // Prevent further processing
        }

        // Handle Mark as Paid functionality
        if (payBtn) {
          const billId = payBtn.getAttribute('data-id');
          let balance = parseFloat(payBtn.getAttribute('data-balance'));
          if (!balance || balance <= 0) {
            window.showModernAlert('No balance due.', 'info');
            return;
          }
          // Find bill details from the row
          const row = payBtn.closest('tr');
          const billNum = row.children[0].textContent;
          const customer = row.children[1].textContent;
          const date = row.children[2].textContent;
          const total = parseFloat(row.children[3].textContent.replace('AED', ''));
          const status = row.children[4].textContent;
          // Fetch delivery date from backend (optional, fallback to '-')
          let delivery = '-';
          try {
            const resp = await fetch(`/api/bills/${billId}`);
            const data = await resp.json();
            if (data && data.bill && data.bill.delivery_date) delivery = data.bill.delivery_date;
          } catch { }
          const paid = total - balance;
          
          if (window.showPaymentModal) {
            window.showPaymentModal({
              billNum,
              customer,
              paid,
              due: balance,
              max: balance,
              total,
              delivery,
              status,
              onOk: async (amount) => {
                try {
                  payBtn.disabled = true;
                  payBtn.textContent = 'Processing...';
  
                  // Add timeout to prevent hanging
                  const controller = new AbortController();
                  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
  
                  const resp = await fetch(`/api/bills/${billId}/payment`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount_paid: amount }),
                    signal: controller.signal
                  });
  
                  clearTimeout(timeoutId);
                  const result = await resp.json();
  
                  if (result && result.bill && !result.error) {
                    if (window.showPaymentProgressModal) {
                        window.showPaymentProgressModal(() => {
                            window.showModernAlert('Payment recorded. Bill is now ' + (result.bill.status || 'updated'), 'success');
                            const input = document.getElementById('searchInvoiceInput');
                            if (input) input.dispatchEvent(new Event('input'));
                        });
                    } else {
                        // Fallback if modal helper not available
                        window.showModernAlert('Payment recorded. Bill is now ' + (result.bill.status || 'updated'), 'success');
                        const input = document.getElementById('searchInvoiceInput');
                        if (input) input.dispatchEvent(new Event('input'));
                    }
                  } else {
                    window.showModernAlert(result?.error || 'Failed to update payment', 'error');
                    payBtn.disabled = false;
                    payBtn.textContent = 'Mark as Paid';
                  }
                } catch (error) {
                  console.error('Payment processing error:', error);
                  if (error.name === 'AbortError') {
                    window.showModernAlert('Payment request timed out. Please try again.', 'error');
                  } else {
                    window.showModernAlert('Failed to process payment. Please try again.', 'error');
                  }
                  payBtn.disabled = false;
                  payBtn.textContent = 'Mark as Paid';
                }
              }
            });
          } else {
             console.error("showPaymentModal is not defined");
             window.showModernAlert("Payment feature unavailable: Missing modal component", "error");
          }
        }
      });
    }
  };

  window.SearchReprint = ns;
})();
