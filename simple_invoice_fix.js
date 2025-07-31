// Simple Invoice Number Generation Fix
// Replace the problematic JavaScript sections with this clean version

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing invoice number generation...');
    
    // Simple invoice number generation
    async function generateInvoiceNumber() {
        try {
            const resp = await fetch('/api/next-bill-number');
            if (resp.ok) {
                const data = await resp.json();
                if (data && data.bill_number) {
                    const billNumberInput = document.getElementById('billNumber');
                    if (billNumberInput) {
                        billNumberInput.value = data.bill_number;
                        console.log('Generated invoice number:', data.bill_number);
                    }
                }
            }
        } catch (error) {
            console.error('Error generating invoice number:', error);
        }
    }

    // Generate invoice number when billing section is accessed
    const billingBtn = document.querySelector('.nav-btn[data-go="billingSec"]');
    if (billingBtn) {
        billingBtn.addEventListener('click', generateInvoiceNumber);
    }

    // Generate invoice number on page load
    generateInvoiceNumber();

    console.log('Invoice number generation initialized');
}); 