// VAT Listeners Module
// Handles VAT input changes and recalculations

window.VATListeners = (function () {

    function getVatConfig() {
        if (window.BillingTotals && window.BillingTotals.getVatConfig) {
            return window.BillingTotals.getVatConfig();
        }
        // Fallback or use global
        return window.getVatConfig ? window.getVatConfig() : { currentVatPercent: 5, includeVatInPrice: false };
    }

    function recalcAllItemsForCurrentVat() {
        console.log('🚀 recalcAllItemsForCurrentVat function called!');
        const { currentVatPercent: currentVat, includeVatInPrice } = getVatConfig();

        const billArray = window.bill || [];
        
        if (billArray && billArray.length > 0) {
            billArray.forEach((it) => {
                if (window.BillingTotals && window.BillingTotals.recomputeItemTotals) {
                    window.BillingTotals.recomputeItemTotals(it, currentVat, includeVatInPrice);
                } else if (window.recomputeItemTotals) {
                    window.recomputeItemTotals(it, currentVat, includeVatInPrice);
                }
            });

            if (window.BillingTotals && window.BillingTotals.refreshBillingUI) {
                window.BillingTotals.refreshBillingUI();
            } else if (window.refreshBillingUI) {
                window.refreshBillingUI();
            }
        }
    }

    function updateVatSummaryLabel() {
        const vatLabel = document.getElementById('vatLabel');
        if (vatLabel) {
            const { currentVatPercent } = getVatConfig();
            vatLabel.textContent = `Tax (${currentVatPercent}%):`;
        }
    }

    function setup() {
        const vatInputs = [
            document.getElementById('vatPercent'),
            document.getElementById('vatPercentMobile')
        ].filter(Boolean);

        let debounceId = null;
        function debouncedHandle() {
            if (debounceId) clearTimeout(debounceId);
            debounceId = setTimeout(() => {
                if (typeof window.onVatInputChange === 'function') {
                    window.onVatInputChange();
                } else {
                    recalcAllItemsForCurrentVat();
                }
                updateVatSummaryLabel();
            }, 150);
        }

        vatInputs.forEach(input => {
            // Remove existing listeners to avoid duplicates
            input.removeEventListener('input', debouncedHandle);
            input.removeEventListener('change', debouncedHandle);
            
            // Add new listeners
            input.addEventListener('input', debouncedHandle);
            input.addEventListener('change', debouncedHandle);
        });

        console.log(`✓ VAT listeners attached to ${vatInputs.length} elements`);
    }

    return {
        setup,
        recalcAllItemsForCurrentVat,
        updateVatSummaryLabel
    };
})();

// Global alias for backward compatibility
window.recalcAllItemsForCurrentVat = window.VATListeners.recalcAllItemsForCurrentVat;
window.attachVatChangeListeners = window.VATListeners.setup;
