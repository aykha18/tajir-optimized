// Tajir POS - Main JavaScript File
// Plan management variables
let userPlan = null;
let enabledFeatures = [];
let lockedFeatures = [];
let planConfig = null;
let isPlanLoaded = false;

// Global variables for billing
let customers = [];

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Tajir POS - Initializing...');
    
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Initialize plan management
    initializePlanManagement();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize billing functionality
    initializeBilling();
    
    // Initialize WhatsApp functionality
    initializeWhatsApp();
    
    console.log('Tajir POS - Initialized successfully');
});

// Navigation functionality
function initializeNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const pages = document.querySelectorAll('.page');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            navBtns.forEach(b => b.classList.remove('bg-neutral-700', 'ring-2', 'ring-indigo-500/60'));
            // Add active class to clicked button
            btn.classList.add('bg-neutral-700', 'ring-2', 'ring-indigo-500/60');

            // Hide all pages
            pages.forEach(p => p.classList.add('hidden'));

            // Show target page
            const targetPage = document.getElementById(btn.dataset.go);
            if (targetPage) {
                targetPage.classList.remove('hidden');
                // Update page title
                const pageTitle = document.getElementById('pageTitle');
                if (pageTitle) {
                    const titleElement = targetPage.querySelector('h3');
                    if (titleElement) {
                        pageTitle.textContent = titleElement.textContent;
                    }
                }
                
                // Load data for specific sections
                if (btn.dataset.go === 'customerSec') {
                    loadCustomers();
                } else if (btn.dataset.go === 'productTypeSec') {
                    loadProductTypes();
                } else if (btn.dataset.go === 'productSec') {
                    loadProducts();
                } else if (btn.dataset.go === 'employeeSec') {
                    loadEmployees();
                } else if (btn.dataset.go === 'vatSec') {
                    loadVatRates();
                }
            }
        });
    });
}

// Billing functionality
function initializeBilling() {
    // Initialize billing event listeners
    initializeBillingEventListeners();
}

// Initialize billing event listeners
function initializeBillingEventListeners() {
    // Bill date change listener
    const billDateElement = document.getElementById('billDate');
    if (billDateElement) {
        billDateElement.addEventListener('change', function() {
            const billDate = new Date(this.value);
            const delivery = new Date(billDate);
            delivery.setDate(billDate.getDate() + 3);
            const deliveryIso = delivery.toISOString().split('T')[0];
            
            const deliveryDateElement = document.getElementById('deliveryDate');
            const trialDateElement = document.getElementById('trialDate');
            
            if (deliveryDateElement) deliveryDateElement.value = deliveryIso;
            if (trialDateElement) trialDateElement.value = deliveryIso;
        });
    }
}

// WhatsApp functionality
function initializeWhatsApp() {
    const whatsappBtn = document.getElementById('whatsappBtn');
    if (whatsappBtn) {
        whatsappBtn.addEventListener('click', handleWhatsAppClick);
    }
    
    // WhatsApp modal event listeners
    const closeWhatsappModal = document.getElementById('closeWhatsappModal');
    if (closeWhatsappModal) {
        closeWhatsappModal.addEventListener('click', closeWhatsAppModal);
    }

    const whatsappModalCancel = document.getElementById('whatsappModalCancel');
    if (whatsappModalCancel) {
        whatsappModalCancel.addEventListener('click', closeWhatsAppModal);
    }

    const whatsappModalSend = document.getElementById('whatsappModalSend');
    if (whatsappModalSend) {
        whatsappModalSend.addEventListener('click', handleWhatsAppSend);
    }
}

// Handle WhatsApp button click
async function handleWhatsAppClick() {
    if (window.bill && window.bill.length === 0) {
        showToast('Please add items to the bill before sending WhatsApp.', 'error');
        return;
    }
    
    // Check if WhatsApp feature is enabled
    if (!enabledFeatures.includes('whatsapp_integration')) {
        showToast('WhatsApp integration is not available in your plan. Please upgrade to use this feature.', 'error');
        return;
    }
    
    // Populate WhatsApp modal with current bill details
    const customerName = document.getElementById('billCustomer')?.value?.trim() || '';
    const customerPhone = document.getElementById('billMobile')?.value?.trim() || '';
    const billNumber = document.getElementById('billNumber')?.value?.trim() || '';
    const totalAmount = window.bill ? window.bill.reduce((sum, i) => sum + i.total, 0) : 0;
    const vatPercent = parseFloat(document.getElementById('vatPercent')?.value) || 0;
    const vatAmount = totalAmount * vatPercent / 100;
    const finalTotal = totalAmount + vatAmount;
    
    // Update WhatsApp modal details
    const whatsappInvoiceDetails = document.getElementById('whatsappInvoiceDetails');
    if (whatsappInvoiceDetails) {
        whatsappInvoiceDetails.innerHTML = `
            <div><strong>Bill #:</strong> ${billNumber || 'Auto-generated'}</div>
            <div><strong>Customer:</strong> ${customerName || 'Not specified'}</div>
            <div><strong>Phone:</strong> ${customerPhone || 'Not specified'}</div>
            <div><strong>Items:</strong> ${window.bill ? window.bill.length : 0} items</div>
            <div><strong>Total:</strong> AED ${finalTotal.toFixed(2)}</div>
        `;
    }
    
    // Pre-fill phone number if available
    const whatsappPhone = document.getElementById('whatsappPhone');
    if (whatsappPhone && customerPhone) {
        whatsappPhone.value = customerPhone;
    }
    
    // Show WhatsApp modal
    const whatsappModal = document.getElementById('whatsappModal');
    if (whatsappModal) {
        whatsappModal.classList.remove('hidden');
        if (whatsappPhone) {
            whatsappPhone.focus();
        }
    }
}

// Close WhatsApp modal
function closeWhatsAppModal() {
    const whatsappModal = document.getElementById('whatsappModal');
    const whatsappStatus = document.getElementById('whatsappStatus');
    if (whatsappModal) whatsappModal.classList.add('hidden');
    if (whatsappStatus) whatsappStatus.classList.add('hidden');
}

// Handle WhatsApp send
async function handleWhatsAppSend() {
    const phoneNumber = document.getElementById('whatsappPhone')?.value?.trim();
    const language = document.getElementById('whatsappLanguage')?.value || 'en';
    const statusDiv = document.getElementById('whatsappStatus');
    const sendBtn = document.getElementById('whatsappModalSend');
    
    if (!phoneNumber) {
        showToast('Please enter a phone number.', 'error');
        return;
    }
    
    // Basic phone number validation
    const phoneRegex = /^[\+]?[0-9\s\-\(\)]+$/;
    if (!phoneRegex.test(phoneNumber)) {
        showToast('Please enter a valid phone number.', 'error');
        return;
    }
    
    // Disable send button and show loading
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg> Generating...';
    }
    
    try {
        // For now, just show success message
        if (statusDiv) {
            statusDiv.innerHTML = '<div class="text-green-400">✅ WhatsApp link generated successfully!</div>';
            statusDiv.classList.remove('hidden');
        }
        
        showToast('WhatsApp functionality is ready!', 'success');
        
        // Close modal after delay
        setTimeout(() => {
            closeWhatsAppModal();
        }, 2000);
        
    } catch (error) {
        console.error('WhatsApp error:', error);
        if (statusDiv) {
            statusDiv.innerHTML = `<div class="text-red-400">❌ Error: ${error.message}</div>`;
            statusDiv.classList.remove('hidden');
        }
        showToast('Failed to generate WhatsApp link. Please try again.', 'error');
    } finally {
        // Re-enable send button
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<svg data-lucide="message-circle" class="w-4 h-4"></svg> Send WhatsApp';
        }
    }
}

// Plan management functions
async function initializePlanManagement() {
    try {
        // Load plan status and config
        const [planStatus, configData] = await Promise.all([
            fetch('/api/plan/status').then(r => r.json()),
            fetch('/api/plan/config').then(r => r.json())
        ]);
        
        userPlan = planStatus;
        planConfig = configData;
        enabledFeatures = planStatus.enabled_features || [];
        lockedFeatures = planStatus.locked_features || [];
        isPlanLoaded = true;
        
        // Store plan data
        userPlan = {
            plan: planStatus.plan,
            expired: planStatus.expired,
            enabledFeatures,
            lockedFeatures
        };
        
        // Apply plan restrictions
        applyPlanRestrictions();
        
        // Show warnings if any
        if (planStatus.warnings && planStatus.warnings.length > 0) {
            showPlanWarnings(planStatus.warnings);
        }
        
        // Show upgrade prompt if trial expired
        if (planStatus.expired && planStatus.plan === 'trial') {
            showUpgradePrompt();
        }
        
    } catch (error) {
        console.error('Error loading plan:', error);
        // Default to trial if error
        userPlan = { plan: 'trial', expired: false };
        enabledFeatures = ['billing', 'product_management', 'customer_management'];
        lockedFeatures = ['dashboard', 'customer_search', 'db_backup_restore'];
        isPlanLoaded = true;
        applyPlanRestrictions();
    }
}

// Apply plan restrictions
function applyPlanRestrictions() {
    if (!isPlanLoaded) return;
    
    // Lock navigation buttons for disabled features
    const navButtons = {
        'dashboard': document.querySelector('[data-go="dashSec"]'),
        'customer_search': document.querySelector('[data-go="customerSec"]'),
        'db_backup_restore': document.querySelector('[data-go="settingsSec"]')
    };
    
    // Apply restrictions to navigation
    Object.entries(navButtons).forEach(([feature, button]) => {
        if (button && lockedFeatures.includes(feature)) {
            button.disabled = true;
            button.classList.add('opacity-50', 'cursor-not-allowed');
            button.title = `Upgrade to PRO to access ${feature.replace('_', ' ')}`;
            
            // Add lock icon
            const lockIcon = document.createElement('svg');
            lockIcon.className = 'w-3 h-3 ml-1';
            lockIcon.innerHTML = '<path fill="currentColor" d="M12 1a3 3 0 0 1 3 3v3a1 1 0 0 0 1 1h1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1V4a3 3 0 0 1 3-3z"/>';
            button.appendChild(lockIcon);
        }
    });
}

// Show toast messages
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300`;
    
    // Set colors based on type
    const colors = {
        success: 'bg-green-600 text-white',
        error: 'bg-red-600 text-white',
        warning: 'bg-yellow-600 text-white',
        info: 'bg-blue-600 text-white'
    };
    
    toast.setAttribute('class', `${toast.className} ${colors[type] || colors.info}`);
    toast.textContent = message;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Placeholder functions for data loading
function loadCustomers() {
    console.log('Loading customers...');
    // Implementation would go here
}

function loadProductTypes() {
    console.log('Loading product types...');
    // Implementation would go here
}

function loadProducts() {
    console.log('Loading products...');
    // Implementation would go here
}

function loadEmployees() {
    console.log('Loading employees...');
    // Implementation would go here
}

function loadVatRates() {
    console.log('Loading VAT rates...');
    // Implementation would go here
}

function showPlanWarnings(warnings) {
    console.log('Plan warnings:', warnings);
    // Implementation would go here
}

function showUpgradePrompt() {
    console.log('Showing upgrade prompt...');
    // Implementation would go here
} 