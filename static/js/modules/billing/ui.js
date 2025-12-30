// Billing UI Module
// Handles modals, alerts, and UI interactions

;(function() {
    
    // Helper to format amount (wraps window.formatAmount)
    function formatAmount(val) {
        return window.formatAmount ? window.formatAmount(val) : (parseFloat(val) || 0).toFixed(2);
    }

    function showPaymentModal({ billNum, customer, paid, due, max, total, delivery, status, onOk }) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';

        modal.innerHTML = `
          <div class="bg-neutral-900 border border-neutral-700 rounded-xl p-6 max-w-md w-full mx-4">
            <h3 class="text-lg font-semibold mb-4">Payment Details</h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-neutral-400">Bill #:</span>
                <span class="font-medium">${billNum}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-400">Customer:</span>
                <span class="font-medium">${customer}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-400">Total Amount:</span>
                <span class="font-medium text-green-400">AED ${formatAmount(total)}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-400">Advance Paid:</span>
                <span class="font-medium text-blue-400">AED ${formatAmount(paid)}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-400">Balance Due:</span>
                <span class="font-medium text-red-400">AED ${formatAmount(due)}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-400">Delivery Date:</span>
                <span class="font-medium">${delivery}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-400">Status:</span>
                <span class="font-medium ${status === 'Completed' ? 'text-green-400' : 'text-yellow-400'}">${status}</span>
              </div>
              <div class="mt-4 pt-4 border-t border-neutral-700">
                <label class="block text-sm font-medium text-neutral-300 mb-2">Payment Amount:</label>
                <input type="number" step="0.01" min="0" max="${due}" value="${due}" 
                       class="w-full px-3 py-2 bg-neutral-800 border border-neutral-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-400/60 focus:border-transparent payment-amount-input"
                       placeholder="Enter payment amount">
              </div>
            </div>
            <div class="flex gap-3 mt-6">
              <button class="flex-1 px-4 py-2 rounded-lg border border-neutral-600 hover:bg-neutral-800 transition-colors cancel-btn">
                Cancel
              </button>
              <button class="flex-1 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white transition-colors ok-btn">
                Mark as Paid
              </button>
            </div>
          </div>
        `;

        document.body.appendChild(modal);

        function cleanup() {
            document.body.removeChild(modal);
        }

        function onOkClick() {
            const paymentAmount = parseFloat(modal.querySelector('.payment-amount-input').value) || 0;
            cleanup();
            if (onOk) {
                try {
                    onOk(paymentAmount);
                } catch (error) {
                    console.error('Error in payment onOk callback:', error);
                }
            }
        }

        function onCancelClick() {
            cleanup();
        }

        modal.querySelector('.ok-btn').addEventListener('click', onOkClick);
        modal.querySelector('.cancel-btn').addEventListener('click', onCancelClick);

        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                onCancelClick();
            }
        });
    }

    function showPaymentProgressModal(onDone) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';

        modal.innerHTML = `
          <div class="bg-neutral-900 border border-neutral-700 rounded-xl p-6 max-w-md w-full mx-4">
            <div class="text-center">
              <div class="w-16 h-16 mx-auto mb-4 bg-indigo-600/20 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8 text-indigo-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
              </div>
              <h3 class="text-lg font-semibold mb-2">Processing Payment</h3>
              <p class="text-neutral-400 mb-4">Please wait while we process your payment...</p>
              <div class="w-full bg-neutral-700 rounded-full h-2">
                <div class="bg-indigo-600 h-2 rounded-full animate-pulse" style="width: 60%"></div>
              </div>
            </div>
          </div>
        `;

        document.body.appendChild(modal);

        function animateStep() {
            const progressBar = modal.querySelector('.bg-indigo-600');
            let width = 60;

            const interval = setInterval(() => {
                width += Math.random() * 10;
                if (width >= 100) {
                    width = 100;
                    clearInterval(interval);
                    setTimeout(() => {
                        document.body.removeChild(modal);
                        if (onDone) onDone();
                    }, 500);
                }
                progressBar.style.width = width + '%';
            }, 200);
        }

        setTimeout(animateStep, 1000);
    }

    // Modern Alert System
    function showModernAlert(message, type = 'info', title = null) {
        // For "Item added" messages, show a simple toast instead of modal
        if (message.includes('Item added') && type === 'success') {
            showSimpleToast('Item Added', 'success');
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center';

        // Determine colors based on type
        let iconColor, bgColor, borderColor, textColor;
        switch (type) {
            case 'success':
                iconColor = 'text-green-400';
                bgColor = 'bg-green-600/20';
                borderColor = 'border-green-500/30';
                textColor = 'text-green-400';
                break;
            case 'error':
                iconColor = 'text-red-400';
                bgColor = 'bg-red-600/20';
                borderColor = 'border-red-500/30';
                textColor = 'text-red-400';
                break;
            case 'warning':
                iconColor = 'text-yellow-400';
                bgColor = 'bg-yellow-600/20';
                borderColor = 'border-yellow-500/30';
                textColor = 'text-yellow-400';
                break;
            default:
                iconColor = 'text-blue-400';
                bgColor = 'bg-blue-600/20';
                borderColor = 'border-blue-500/30';
                textColor = 'text-blue-400';
        }

        // Get appropriate icon
        let iconSvg;
        switch (type) {
            case 'success':
                iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>`;
                break;
            case 'error':
                iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>`;
                break;
            case 'warning':
                iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>`;
                break;
            default:
                iconSvg = `<svg class="w-6 h-6 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>`;
        }

        modal.innerHTML = `
          <div class="bg-neutral-900 border ${borderColor} rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 ${bgColor} rounded-full flex items-center justify-center">
                  ${iconSvg}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                ${title ? `<h3 class="text-lg font-semibold text-white mb-1">${title}</h3>` : ''}
                <p class="text-sm text-neutral-300">${message}</p>
              </div>
            </div>
            <div class="mt-6 flex justify-end">
              <button class="px-4 py-2 bg-neutral-700 hover:bg-neutral-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 focus:ring-offset-neutral-900">
                OK
              </button>
            </div>
          </div>
        `;

        document.body.appendChild(modal);

        // Auto-remove after 5 seconds for success/info, 8 seconds for warnings, 10 seconds for errors
        const autoRemoveTime = type === 'success' || type === 'info' ? 5000 : type === 'warning' ? 8000 : 10000;
        const autoRemove = setTimeout(() => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        }, autoRemoveTime);

        // Manual close
        const closeModal = () => {
            clearTimeout(autoRemove);
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        };

        modal.querySelector('button').addEventListener('click', closeModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        // Keyboard support
        const handleKeydown = (e) => {
            if (e.key === 'Escape' || e.key === 'Enter') {
                closeModal();
                document.removeEventListener('keydown', handleKeydown);
            }
        };
        document.addEventListener('keydown', handleKeydown);
    }

    function showSimpleToast(message, type = 'info') {
        // Remove any existing toasts
        const existingToasts = document.querySelectorAll('.simple-toast');
        existingToasts.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = 'simple-toast fixed top-4 right-4 z-50 transform transition-all duration-300 ease-out translate-x-full';

        // Determine colors based on type
        let bgColor, textColor, iconColor;
        switch (type) {
            case 'success':
                bgColor = 'bg-gradient-to-r from-green-500 to-green-600';
                textColor = 'text-white';
                iconColor = 'text-green-100';
                break;
            case 'error':
                bgColor = 'bg-red-600';
                textColor = 'text-white';
                iconColor = 'text-red-100';
                break;
            case 'warning':
                bgColor = 'bg-yellow-600';
                textColor = 'text-white';
                iconColor = 'text-yellow-100';
                break;
            case 'info':
                bgColor = 'bg-gradient-to-r from-green-500 to-green-600';
                textColor = 'text-white';
                iconColor = 'text-green-100';
                break;
            default:
                bgColor = 'bg-gradient-to-r from-green-500 to-green-600';
                textColor = 'text-white';
                iconColor = 'text-green-100';
        }

        toast.innerHTML = `
          <div class="${bgColor} ${textColor} px-4 py-3 rounded-lg shadow-lg flex items-center space-x-2 max-w-sm">
            <svg class="w-5 h-5 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span class="text-sm font-medium">${message}</span>
          </div>
        `;
        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);

        // Auto-remove after 2 seconds
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 2000);
    }

    function togglePrint() {
        const printSection = document.getElementById('printSection');
        if (printSection) {
            printSection.classList.toggle('hidden');
        }
    }

    // Setup Mobile Billing Toggle
    function setupMobileBillingToggle() {
        const mobileBillingToggle = document.getElementById('mobileBillingToggle');
        if (mobileBillingToggle) {
            mobileBillingToggle.addEventListener('click', function () {
                // Show mobile billing interface
                if (window.TajirPWA && window.TajirPWA.mobileBilling) {
                    try {
                        window.TajirPWA.mobileBilling.showMobileBilling();
                    } catch (error) {
                        console.error('Error showing mobile billing:', error);
                        showModernAlert('Mobile billing encountered an error. Please try again.', 'error', 'Error');
                    }
                } else {
                    console.warn('Mobile billing not available');
                    showModernAlert('Mobile billing is not available. Please refresh the page.', 'warning', 'Feature Unavailable');
                }
            });
        }

        // Setup Mobile Billing V3 Toggle
        const mobileBillingToggleV3 = document.getElementById('mobileBillingToggleV3');
        if (mobileBillingToggleV3) {
            mobileBillingToggleV3.addEventListener('click', function () {
                console.log('Mobile Billing V3 Toggle clicked');
                // Show mobile billing V3 interface
                if (window.mobileBillingV3) {
                    try {
                        window.mobileBillingV3.show();
                    } catch (error) {
                        console.error('Error showing mobile billing V3:', error);
                        showModernAlert('Mobile billing V3 encountered an error. Please try again.', 'error', 'Error');
                    }
                } else {
                    console.warn('Mobile billing V3 not available');
                    showModernAlert('Mobile billing V3 is not available. Please refresh the page.', 'warning', 'Feature Unavailable');
                }
            });
        }

        // Setup Mobile Billing Banner
        const mobileBillingBannerBtn = document.getElementById('mobileBillingBannerBtn');
        if (mobileBillingBannerBtn) {
            mobileBillingBannerBtn.addEventListener('click', function () {
                if (window.mobileBillingV3) {
                    try {
                        window.mobileBillingV3.show();
                        // Hide the banner after clicking
                        const banner = document.getElementById('mobileBillingBanner');
                        if (banner) {
                            banner.style.opacity = '0';
                            banner.style.transform = 'translateY(-20px)';
                            setTimeout(() => {
                                banner.style.display = 'none';
                            }, 300);
                        }
                    } catch (error) {
                        console.error('Error showing mobile billing V3 from banner:', error);
                        showModernAlert('Mobile billing encountered an error. Please try again.', 'error', 'Error');
                    }
                } else {
                    console.warn('Mobile billing V3 not available');
                    showModernAlert('Mobile billing is not available. Please refresh the page.', 'warning', 'Feature Unavailable');
                }
            });
        }

        // Auto-hide mobile billing banner after 10 seconds
        const mobileBillingBanner = document.getElementById('mobileBillingBanner');
        if (mobileBillingBanner) {
            setTimeout(() => {
                mobileBillingBanner.style.opacity = '0';
                mobileBillingBanner.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    mobileBillingBanner.style.display = 'none';
                }, 300);
            }, 10000);
        }
    }

    // Helper function to reset the entire billing form
    async function resetBillingForm() {
        // Clear the bill array
        if (window.bill) {
            window.bill.length = 0;
        }

        // Clear current bill ID to allow new bill creation
        window.currentBillId = null;

        // Clear customer fields
        if (window.BillingCustomer && window.BillingCustomer.clear) {
            window.BillingCustomer.clear();
        }

        // Clear billing form fields (both desktop and mobile)
        if (window.BillingItems && window.BillingItems.clearBillingForm) {
            window.BillingItems.clearBillingForm('desktop');
            window.BillingItems.clearBillingForm('mobile');
        }

        // Clear master fields
        const masterNameElement = document.getElementById('masterName');
        const masterNameMobileElement = document.getElementById('masterNameMobile');
        if (masterNameElement) {
            masterNameElement.value = '';
            masterNameElement.removeAttribute('data-selected-master');
        }
        if (masterNameMobileElement) {
            masterNameMobileElement.value = '';
            masterNameMobileElement.removeAttribute('data-selected-master');
        }

        // Clear bill details
        const billNumberElement = document.getElementById('billNumber');
        const billDateElement = document.getElementById('billDate');
        const deliveryDateElement = document.getElementById('deliveryDate');
        const trialDateElement = document.getElementById('trialDate');
        const billNotesElement = document.getElementById('billNotes');

        if (billNumberElement) billNumberElement.value = '';
        if (billDateElement) billDateElement.value = '';
        if (deliveryDateElement) deliveryDateElement.value = '';
        if (trialDateElement) trialDateElement.value = '';
        if (billNotesElement) billNotesElement.value = '';

        // Reset actual form element if exists
        const form = document.getElementById('billingForm');
        if (form) {
            form.reset();
        }

        // Update the bill table display and totals
        if (window.BillingTotals && window.BillingTotals.refreshBillingUI) {
            window.BillingTotals.refreshBillingUI();
        } else if (window.refreshBillingUI) {
            window.refreshBillingUI();
        }

        // Set default dates and bill number
        if (window.BillingConfig) {
            if (window.BillingConfig.apply) window.BillingConfig.apply();
            if (window.BillingConfig.setBasicDefaultDates) await window.BillingConfig.setBasicDefaultDates();
            if (window.BillingConfig.setDefaultBillingDates) window.BillingConfig.setDefaultBillingDates();
        } else {
             // Fallback to global functions
            if (typeof setDefaultBillingDates === 'function') {
                setDefaultBillingDates();
            }
            if (typeof setBasicDefaultDates === 'function') {
                await setBasicDefaultDates();
            }
            if (typeof applyBillingConfiguration === 'function') {
                applyBillingConfiguration();
            }
        }

        if (window.BillingTotals && window.BillingTotals.setActionButtonsState) {
            window.BillingTotals.setActionButtonsState(false);
        }
    }

    // Export to Namespace
    window.BillingUI = {
        showPaymentModal,
        showPaymentProgressModal,
        showModernAlert,
        showSimpleToast,
        togglePrint,
        setupMobileBillingToggle,
        resetBillingForm
    };

    // Global aliases for backward compatibility
    window.showPaymentModal = showPaymentModal;
    window.showPaymentProgressModal = showPaymentProgressModal;
    window.showModernAlert = showModernAlert;
    window.showSimpleToast = showSimpleToast;
    window.togglePrint = togglePrint;
    window.setupMobileBillingToggle = setupMobileBillingToggle;
    window.resetBillingForm = resetBillingForm;

    // Export to window
    window.showPaymentModal = showPaymentModal;
    window.showPaymentProgressModal = showPaymentProgressModal;
    window.showModernAlert = showModernAlert;
    window.showSimpleToast = showSimpleToast;

})();
