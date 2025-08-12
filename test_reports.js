// Test script for Advanced Reports functionality
// Run this in the browser console on the main app page

console.log('🧪 Testing Advanced Reports functionality...');

function testAdvancedReports() {
    console.log('🔍 Testing Advanced Reports...');
    
    // Check if we're on the reports page
    const reportsSection = document.getElementById('advancedReportsSec');
    if (!reportsSection) {
        console.log('❌ Advanced Reports section not found');
        return;
    }
    
    console.log('✅ Advanced Reports section found');
    
    // Check if section is visible
    if (reportsSection.classList.contains('hidden')) {
        console.log('⚠️ Advanced Reports section is hidden');
    } else {
        console.log('✅ Advanced Reports section is visible');
    }
    
    // Check for required elements
    const requiredElements = [
        'invFromDate', 'invToDate', 'invProducts', 'invEmployees', 
        'invCity', 'invArea', 'invStatus', 'invoices-table-body'
    ];
    
    console.log('🔍 Checking required elements:');
    requiredElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            console.log(`  ✅ ${elementId}: Found`);
        } else {
            console.log(`  ❌ ${elementId}: NOT found`);
        }
    });
    
    // Check if initializeReports function exists
    if (typeof window.initializeReports === 'function') {
        console.log('✅ initializeReports function exists');
    } else {
        console.log('❌ initializeReports function NOT found');
    }
    
    // Test API endpoints
    testReportsAPI();
}

async function testReportsAPI() {
    console.log('🌐 Testing Reports API endpoints...');
    
    const endpoints = [
        '/api/reports/invoices',
        '/api/reports/employees', 
        '/api/reports/products'
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`  Testing ${endpoint}...`);
            const response = await fetch(endpoint);
            console.log(`    Status: ${response.status}`);
            if (response.ok) {
                const data = await response.json();
                console.log(`    ✅ Success - Data length: ${Array.isArray(data) ? data.length : 'N/A'}`);
            } else {
                console.log(`    ❌ Error: ${response.statusText}`);
            }
        } catch (error) {
            console.log(`    ❌ Fetch error: ${error.message}`);
        }
    }
}

// Test tab functionality
function testReportsTabs() {
    console.log('📑 Testing Reports tabs...');
    
    const tabButtons = document.querySelectorAll('.report-tab-btn');
    console.log(`  Found ${tabButtons.length} tab buttons`);
    
    tabButtons.forEach((btn, index) => {
        const tabName = btn.getAttribute('data-tab');
        console.log(`  Tab ${index + 1}: ${tabName}`);
        
        // Check if corresponding content exists
        const content = document.getElementById(tabName);
        if (content) {
            console.log(`    ✅ Content for ${tabName} found`);
        } else {
            console.log(`    ❌ Content for ${tabName} NOT found`);
        }
    });
}

// Test filter functionality
function testReportsFilters() {
    console.log('🔧 Testing Reports filters...');
    
    const filterElements = [
        'invFromDate', 'invToDate', 'invProducts', 'invEmployees',
        'invCity', 'invArea', 'invStatus'
    ];
    
    filterElements.forEach(filterId => {
        const element = document.getElementById(filterId);
        if (element) {
            console.log(`  ✅ ${filterId}: ${element.tagName} - ${element.type || 'select'}`);
        } else {
            console.log(`  ❌ ${filterId}: NOT found`);
        }
    });
}

// Run all tests
function runAllReportsTests() {
    console.log('🚀 Running all Advanced Reports tests...');
    testAdvancedReports();
    testReportsTabs();
    testReportsFilters();
}

// Auto-run tests
runAllReportsTests();

// Make functions available globally
window.testAdvancedReports = testAdvancedReports;
window.testReportsAPI = testReportsAPI;
window.testReportsTabs = testReportsTabs;
window.testReportsFilters = testReportsFilters;
window.runAllReportsTests = runAllReportsTests;

console.log('💡 You can run individual tests:');
console.log('  - testAdvancedReports()');
console.log('  - testReportsAPI()');
console.log('  - testReportsTabs()');
console.log('  - testReportsFilters()');
console.log('  - runAllReportsTests()');
