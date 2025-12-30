;(function () {
  
  // Helper to access globals safely
  const getGlobals = () => ({
    bill: window.bill || [],
    BillingTotals: window.BillingTotals,
    BillingCustomer: window.BillingCustomer,
    BillingConfig: window.BillingConfig,
    showSimpleToast: window.BillingUI?.showSimpleToast || window.showSimpleToast,
    getVatConfig: window.BillingTotals?.getVatConfig || window.getVatConfig,
    recomputeItemTotals: window.BillingTotals?.recomputeItemTotals || window.recomputeItemTotals,
    computeTotals: window.BillingTotals?.computeTotals || window.computeTotals,
    formatAmount: window.BillingTotals?.formatAmount || window.formatAmount,
    getCustomerInputs: window.BillingCustomer?.getCustomerInputs || window.getCustomerInputs,
    getCombinedPhoneNumber: window.BillingConfig?.getCombinedPhone || window.getCombinedPhoneNumber,
    resetBillingForm: window.resetBillingForm
  });

  // Function to prepare bill data for saving
  async function prepareBillData() {
    const { 
      bill, 
      showSimpleToast, 
      getVatConfig, 
      recomputeItemTotals, 
      computeTotals, 
      getCustomerInputs 
    } = getGlobals();

    // Check if bill has items
    if (bill.length === 0) {
      if (showSimpleToast) {
        showSimpleToast('Please add items to the bill first', 'warning');
      }
      return null;
    }

    // Validate required fields
    const customerMobile = document.getElementById('billMobile')?.value?.trim();

    if (!customerMobile) {
      if (showSimpleToast) {
        showSimpleToast('Please enter customer mobile number in the Mobile field', 'warning');
      }
      // Focus on the mobile field to help user
      const mobileField = document.getElementById('billMobile');
      if (mobileField) {
        mobileField.focus();
        mobileField.style.borderColor = '#ef4444'; // Red border to highlight
        setTimeout(() => {
          mobileField.style.borderColor = ''; // Reset after 3 seconds
        }, 3000);
      }
      return null;
    }

    // Generate bill number if not exists
    const billNumberInput = document.getElementById('billNumber');
    if (billNumberInput && !billNumberInput.value.trim()) {
      const timestamp = Date.now();
      billNumberInput.value = `BILL-${timestamp}`;
    }

    // Collect bill data
    const masterNameElement = document.getElementById('masterName');
    const masterNameMobileElement = document.getElementById('masterNameMobile');
    let masterId = null;

    // Try to get master_id from the data-selected-master attribute (check both desktop and mobile)
    let selectedMasterElement = masterNameElement;
    if (!selectedMasterElement || !selectedMasterElement.getAttribute('data-selected-master')) {
      selectedMasterElement = masterNameMobileElement;
    }

    if (selectedMasterElement && selectedMasterElement.getAttribute('data-selected-master')) {
      try {
        const selectedMaster = JSON.parse(selectedMasterElement.getAttribute('data-selected-master'));
        masterId = selectedMaster.master_id;
      } catch (e) {
        console.warn('Failed to parse selected master data:', e);
      }
    } else {
      // Try to use global selectedMasterId as fallback
      if (window.selectedMasterId) {
        masterId = window.selectedMasterId;
      }
    }

    // Ensure items use the current VAT percent
    const { currentVatPercent, includeVatInPrice } = getVatConfig();
    bill.forEach((it) => {
      recomputeItemTotals(it, currentVatPercent, includeVatInPrice);
    });

    const totalsForSave = computeTotals(bill, includeVatInPrice, currentVatPercent);
    const subtotalNet = totalsForSave.subtotal;
    const totalVat = totalsForSave.totalVat;
    const totalAdvance = totalsForSave.totalAdvance;
    const amountDue = totalsForSave.amountDue;
    const totalBeforeAdvance = totalsForSave.totalBeforeAdvance;
    const subtotalForRequest = includeVatInPrice ? totalBeforeAdvance : subtotalNet;
    const shouldShowVat = window.shouldDisplayVat ? window.shouldDisplayVat(totalVat > 0 ? 1 : 0) : true;


    const cust = getCustomerInputs();
    const billData = {
      bill: {
        bill_number: document.getElementById('billNumber')?.value || '',
        customer_name: cust.customer_name,
        customer_phone: cust.customer_phone,
        country_code: cust.country_code,
        customer_city: cust.customer_city,
        customer_area: cust.customer_area,
        customer_trn: cust.customer_trn,
        customer_type: cust.customer_type,
        business_name: cust.business_name,
        business_address: cust.business_address,
        bill_date: document.getElementById('billDate')?.value || '',
        delivery_date: document.getElementById('deliveryDate')?.value || '',
        trial_date: document.getElementById('trialDate')?.value || '',
        master_id: masterId,
        master_name: document.getElementById('masterName')?.value || '',
        notes: document.getElementById('billNotes')?.value || '',
        subtotal: subtotalForRequest,
        discount: 0, // No discount field in current UI
        vat_amount: totalVat,
        vat_percent: currentVatPercent,
        should_show_vat: shouldShowVat,
        total_amount: totalBeforeAdvance,
        advance_paid: window.paymentMode === 'full' ? totalBeforeAdvance : totalAdvance,
        balance_amount: window.paymentMode === 'full' ? 0 : amountDue
      },
      items: bill
    };

    return billData;
  }

  async function handleSaveBillClick() {
    const { bill, showSimpleToast } = getGlobals();

    // Check if there are items in the bill
    if (bill.length === 0) {
      if (showSimpleToast) {
        showSimpleToast('Please add items to the bill first', 'warning');
      }
      return;
    }

    try {
      // Create the bill data
      const billData = await prepareBillData();
      if (!billData) {
        if (showSimpleToast) {
          showSimpleToast('Failed to prepare bill data', 'error');
        }
        return;
      }

      // Save the bill
      const saveResponse = await fetch('/api/bills', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(billData)
      });

      if (!saveResponse.ok) {
        throw new Error('Failed to save bill');
      }

      const saveResult = await saveResponse.json();

      if (saveResult.error) {
        if (showSimpleToast) {
          showSimpleToast(saveResult.error, 'error');
        }
        return;
      }

      if (saveResult.bill_id) {
        // Store the current bill ID
        window.currentBillId = saveResult.bill_id;

        // Update bill number field with the actual bill number from response
        if (saveResult.bill_number) {
          const billNumberElement = document.getElementById('billNumber');
          if (billNumberElement) {
            billNumberElement.value = saveResult.bill_number;
          }
        }

        // Show success message
        if (showSimpleToast) {
          showSimpleToast('Bill saved successfully!', 'success');
        }

        // Update button text to show saved status
        const saveBillBtn = document.getElementById('saveBillBtn');
        if (saveBillBtn) {
          saveBillBtn.innerHTML = '<svg data-lucide="check" class="w-4 h-4"></svg> Saved';
          saveBillBtn.classList.remove('bg-yellow-600', 'hover:bg-yellow-500');
          saveBillBtn.classList.add('bg-green-600', 'hover:bg-green-500');

          // Reset button after 3 seconds
          setTimeout(() => {
            saveBillBtn.innerHTML = '<svg data-lucide="save" class="w-4 h-4"></svg> Save Invoice';
            saveBillBtn.classList.remove('bg-green-600', 'hover:bg-green-500');
            saveBillBtn.classList.add('bg-yellow-600', 'hover:bg-yellow-500');
          }, 3000);
        }

      } else {
        if (showSimpleToast) {
          showSimpleToast('Failed to save bill', 'error');
        }
      }

    } catch (error) {
      console.error('Error saving bill:', error);
      if (showSimpleToast) {
        showSimpleToast('Failed to save bill. Please try again.', 'error');
      }
    }
  }

  async function handleWhatsAppClick() {
    const { 
      bill, 
      showSimpleToast, 
      getCombinedPhoneNumber, 
      formatAmount, 
      resetBillingForm 
    } = getGlobals();

    try {
      // Check if there are items in the bill
      if (bill.length === 0) {
        if (showSimpleToast) {
          showSimpleToast('Please add items to the bill first', 'warning');
        }
        return;
      }

      // Check if customer mobile is provided
      const customerMobile = document.getElementById('billMobile')?.value?.trim();
      if (!customerMobile) {
        if (showSimpleToast) {
          showSimpleToast('Please enter customer mobile number to send WhatsApp', 'warning');
        }
        // Focus on the mobile field
        const mobileField = document.getElementById('billMobile');
        if (mobileField) {
          mobileField.focus();
          mobileField.style.borderColor = '#ef4444';
          setTimeout(() => {
            mobileField.style.borderColor = '';
          }, 3000);
        }
        return;
      }

      let billId = window.currentBillId; // Check if bill is already saved
      let billData = null;

      // If bill is not saved, ask user if they want to save it first
      if (!billId) {
        const shouldSave = confirm('Would you like to save this bill before sending WhatsApp? This will create a permanent record.');
        if (shouldSave) {
          // Save the bill first
          billData = await prepareBillData();
          if (!billData) {
            if (showSimpleToast) {
              showSimpleToast('Failed to prepare bill data', 'error');
            }
            return;
          }

          const saveResponse = await fetch('/api/bills', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(billData)
          });

          if (!saveResponse.ok) {
            throw new Error('Failed to save bill');
          }

          const saveResult = await saveResponse.json();

          if (saveResult.error) {
            if (showSimpleToast) {
              showSimpleToast(saveResult.error, 'error');
            }
            return;
          }

          if (saveResult.bill_id) {
            billId = saveResult.bill_id;
            window.currentBillId = billId;

            // Update save button to show saved status
            const saveBillBtn = document.getElementById('saveBillBtn');
            if (saveBillBtn) {
              saveBillBtn.innerHTML = '<svg data-lucide="check" class="w-4 h-4"></svg> Saved';
              saveBillBtn.classList.remove('bg-yellow-600', 'hover:bg-yellow-500');
              saveBillBtn.classList.add('bg-green-600', 'hover:bg-green-500');
            }
          } else {
            if (showSimpleToast) {
              showSimpleToast('Failed to save bill', 'error');
            }
            return;
          }
        } else {
          // Use draft bill data for WhatsApp
          billData = await prepareBillData();
          if (!billData) {
            if (showSimpleToast) {
              showSimpleToast('Failed to prepare bill data', 'error');
            }
            return;
          }
        }
      }

      // If we have a saved bill, use the API endpoint
      if (billId) {
        const customerPhone = getCombinedPhoneNumber() || '';

        if (!customerPhone) {
          if (showSimpleToast) {
            showSimpleToast('Please enter customer mobile number to send WhatsApp', 'warning');
          }
          return;
        }

        // Use the existing WhatsApp API endpoint
        const whatsappResponse = await fetch(`/api/bills/${billId}/whatsapp`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            phone: customerPhone,
            language: 'en'
          })
        });

        if (!whatsappResponse.ok) {
          const errorData = await whatsappResponse.json();
          throw new Error(errorData.error || 'Failed to generate WhatsApp link');
        }

        const whatsappResult = await whatsappResponse.json();

        if (whatsappResult.success && whatsappResult.whatsapp_url) {
          window.open(whatsappResult.whatsapp_url, '_blank');

          // Also open printable invoice in new tab using existing endpoint
          const printUrl = `${window.location.origin}/api/bills/${billId}/print`;
          window.open(printUrl, '_blank');

          if (showSimpleToast) {
            showSimpleToast('WhatsApp opened with bill details!', 'success');
          }

          // Reset the billing form after successful WhatsApp send
          if (resetBillingForm) await resetBillingForm();
        } else {
          throw new Error('Failed to generate WhatsApp link');
        }
      } else {
        // Use draft bill data to create WhatsApp message
        const customerName = billData.bill.customer_name || 'Customer';
        const customerPhone = billData.bill.customer_phone || '';
        const totalAmount = formatAmount(billData.bill.total_amount || '0');
        const billNumber = billData.bill.bill_number || 'Draft';
        const billDate = billData.bill.bill_date || '';
        const subtotal = formatAmount(billData.bill.subtotal || '0');
        const vatAmount = formatAmount(billData.bill.vat_amount || '0');
        const advancePaid = formatAmount(billData.bill.advance_paid || '0');
        const balanceAmount = formatAmount(billData.bill.balance_amount || '0');

        // Create detailed bill message
        let message = `*🧾 TAJIR POS - DRAFT BILL*\n\n`;
        message += `*Customer Details:*\n`;
        message += `• Name: ${customerName}\n`;
        if (customerPhone) message += `• Phone: ${customerPhone}\n\n`;

        message += `*Bill Details:*\n`;
        message += `• Bill #: ${billNumber} (Draft)\n`;
        message += `• Date: ${billDate}\n\n`;

        // Add items details
        if (billData.items && billData.items.length > 0) {
          message += `*Items:*\n`;
          billData.items.forEach((item, index) => {
            message += `${index + 1}. ${item.product_name} - Qty: ${item.quantity} - Rate: ${formatAmount(item.rate)} - Total: ${formatAmount(item.total)}\n`;
          });
          message += `\n`;
        }

        message += `*Bill Summary:*\n`;
        message += `• Subtotal: ${subtotal}\n`;
        message += `• VAT: ${vatAmount}\n`;
        message += `• Advance Paid: ${advancePaid}\n`;
        message += `• Balance Amount: ${balanceAmount}\n`;
        message += `*Total Amount: ${totalAmount}*\n\n`;
        message += `*Note: This is a draft bill. Please save it in the POS system for permanent record.*`;

        // Encode the message for WhatsApp
        const encodedMessage = encodeURIComponent(message);

        // Construct WhatsApp URL
        let whatsappUrl;
        if (customerPhone) {
          // Trust the customerPhone as it comes from the backend or combined input
          const cleanPhone = customerPhone.replace(/\D/g, '');
          whatsappUrl = `https://wa.me/${cleanPhone}?text=${encodedMessage}`;
        } else {
          whatsappUrl = `https://wa.me/?text=${encodedMessage}`;
        }

        window.open(whatsappUrl, '_blank');

        if (showSimpleToast) {
          showSimpleToast('WhatsApp opened with draft bill details!', 'success');
        }

        if (resetBillingForm) await resetBillingForm();
      }
      
    } catch (error) {
      console.error('Error handling WhatsApp:', error);
      if (showSimpleToast) {
        showSimpleToast('Failed to send WhatsApp. Please try again.', 'error');
      }
    }
  }

  // Handle Print Button Click
  async function handlePrintClick() {
    const { 
      bill, 
      showSimpleToast, 
      resetBillingForm 
    } = getGlobals();

    // Re-acquire showModernAlert as it might not be in getGlobals initial destructure if added later
    const alertFn = window.BillingUI?.showModernAlert || window.showModernAlert || ((msg) => alert(msg));

    if (bill.length === 0) {
      alertFn('Please add items to the bill first', 'warning', 'No Items');
      return;
    }

    // Require customer mobile
    const billMobileInput = document.getElementById('billMobile');
    const customerMobile = billMobileInput?.value?.trim() || '';
    if (!customerMobile) {
      alertFn('Please enter customer mobile number', 'warning', 'Mobile Required');
      if (billMobileInput) billMobileInput.focus();
      return;
    }

    // Check if bill is already saved
    let billId = window.currentBillId;

    // If bill is not saved, save it first
    if (!billId) {
      // Generate bill number if not exists
      const billNumberInput = document.getElementById('billNumber');
      if (billNumberInput && !billNumberInput.value.trim()) {
        const timestamp = Date.now();
        billNumberInput.value = `BILL-${timestamp}`;
      }

      // Collect bill data
      const billData = await prepareBillData();
      if (!billData) {
        alertFn('Failed to prepare bill data', 'error', 'Save Failed');
        return;
      }

      try {
        // Save bill first
        const saveResponse = await fetch('/api/bills', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(billData)
        });

        const saveResult = await saveResponse.json();

        if (saveResult.error) {
          alertFn(saveResult.error, 'error', 'Save Failed');
          return;
        }

        if (saveResult.bill_id) {
          // Store the current bill ID
          window.currentBillId = saveResult.bill_id;
          billId = saveResult.bill_id;

          // Update bill number field with the actual bill number from response
          if (saveResult.bill_number) {
            const billNumberElement = document.getElementById('billNumber');
            if (billNumberElement) {
              billNumberElement.value = saveResult.bill_number;
            }
          }

          // Show success message
          if (showSimpleToast) showSimpleToast('Bill saved successfully!', 'success');
        } else {
          alertFn('Failed to save bill', 'error', 'Save Failed');
          return;
        }
      } catch (error) {
        console.error('Error saving bill:', error);
        alertFn('Failed to save bill. Please try again.', 'error', 'Save Failed');
        return;
      }
    }

    // Now print the bill using the existing bill ID
    if (billId) {
      // Open print window
      window.open(`/api/bills/${billId}/print`, '_blank');

      // Show success message
      if (showSimpleToast) showSimpleToast('Print window opened', 'success');

      // Reset the billing form after printing
      setTimeout(async () => {
        if (resetBillingForm) await resetBillingForm();
        // Clear the current bill ID
        window.currentBillId = null;
      }, 1000); // Small delay to ensure print window opens first
    } else {
      alertFn('Failed to get bill ID for printing', 'error', 'Print Failed');
    }
  }

  // Initialize Print Button
  function initializePrintButton() {
    const printBtn = document.getElementById('printBtn');
    if (printBtn) {
      printBtn.addEventListener('click', async function (e) {
        e.preventDefault();
        await handlePrintClick();
      });
    }
  }

  // Save Bill functionality
  function initializeSaveBill() {
    setTimeout(() => {
      const saveBillBtn = document.getElementById('saveBillBtn');

      if (saveBillBtn) {
        saveBillBtn.addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          handleSaveBillClick();
        });
      }
    }, 1000);
  }

  // WhatsApp functionality
  function initializeWhatsApp() {
    const whatsappBtn = document.getElementById('whatsappBtn');

    if (whatsappBtn) {
      // Remove any existing event listeners to prevent duplicates
      whatsappBtn.removeEventListener('click', handleWhatsAppClick);
      whatsappBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        handleWhatsAppClick();
      });
    }
  }

  // Expose to namespace
  window.BillingActions = {
    prepareBillData,
    handleSaveBillClick,
    handleWhatsAppClick,
    handlePrintClick,
    initializeSaveBill,
    initializeWhatsApp,
    initializePrintButton
  };

  // Global aliases for backward compatibility
  window.prepareBillData = prepareBillData;
  window.handleSaveBillClick = handleSaveBillClick;
  window.handleWhatsAppClick = handleWhatsAppClick;
  window.handlePrintClick = handlePrintClick;
  window.initializeSaveBill = initializeSaveBill;
  window.initializeWhatsApp = initializeWhatsApp;
  window.initializePrintButton = initializePrintButton;

})();
