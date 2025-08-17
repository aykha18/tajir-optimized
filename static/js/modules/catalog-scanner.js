/**
 * Catalog Scanner Module
 * Provides functionality to scan shop catalogs and automatically create product types and products
 */

class CatalogScanner {
    constructor() {
        this.catalogData = [];
        this.analysis = null;
        this.suggestions = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.createUI();
    }

    createUI() {
        // Create the catalog scanner modal
        const modalHTML = `
            <div id="catalogScannerModal" class="fixed inset-0 bg-black bg-opacity-50 hidden z-50">
                <div class="flex items-center justify-center min-h-screen p-4">
                    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                        <div class="flex items-center justify-between p-6 border-b">
                            <h2 class="text-2xl font-bold text-gray-800">Catalog Scanner</h2>
                            <button onclick="window.catalogScanner.closeModal()" class="text-gray-500 hover:text-gray-700">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>
                        
                        <div class="p-6">
                            <!-- Step 1: Upload Catalog -->
                            <div id="step1" class="step-content">
                                <h3 class="text-lg font-semibold mb-4">Step 1: Upload Your Catalog</h3>
                                <div class="mb-6">
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        Upload CSV/Excel file or paste catalog data
                                    </label>
                                    <div class="mb-3">
                                        <a href="/static/sample_catalog.csv" download class="text-blue-600 hover:text-blue-800 text-sm underline">
                                            📥 Download Sample CSV Template
                                        </a>
                                    </div>
                                    <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                                        <input type="file" id="catalogFile" accept=".csv,.xlsx,.xls" class="hidden">
                                        <button onclick="document.getElementById('catalogFile').click()" 
                                                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mb-4">
                                            Choose File
                                        </button>
                                        <p class="text-sm text-gray-500">or</p>
                                        <button onclick="window.catalogScanner.showManualInput()" 
                                                class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mt-2">
                                            Enter Data Manually
                                        </button>
                                    </div>
                                </div>
                                
                                <div id="manualInput" class="hidden">
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        Paste your catalog data (JSON format)
                                    </label>
                                    <textarea id="catalogDataInput" rows="10" 
                                              class="w-full border border-gray-300 rounded-md p-3"
                                              placeholder='[{"name": "Product Name", "price": 25.00, "category": "Category Name", "description": "Product description"}]'></textarea>
                                    <button onclick="window.catalogScanner.processManualData()" 
                                            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mt-2">
                                        Process Data
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Step 2: Analysis Results -->
                            <div id="step2" class="step-content hidden">
                                <h3 class="text-lg font-semibold mb-4">Step 2: Analysis Results</h3>
                                <div id="analysisResults" class="space-y-4"></div>
                                <div class="flex justify-between mt-6">
                                    <button onclick="window.catalogScanner.showStep(1)" 
                                            class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
                                        Back
                                    </button>
                                    <button onclick="window.catalogScanner.showStep(3)" 
                                            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                                        Continue to Suggestions
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Step 3: Product Suggestions -->
                            <div id="step3" class="step-content hidden">
                                <h3 class="text-lg font-semibold mb-4">Step 3: Product Suggestions</h3>
                                <div id="suggestionsResults" class="space-y-4"></div>
                                <div class="flex justify-between mt-6">
                                    <button onclick="window.catalogScanner.showStep(2)" 
                                            class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
                                        Back
                                    </button>
                                    <button onclick="window.catalogScanner.createProducts()" 
                                            class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                                        Create Products
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    bindEvents() {
        // File upload handling
        document.addEventListener('change', (e) => {
            if (e.target.id === 'catalogFile') {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    }

    showModal() {
        document.getElementById('catalogScannerModal').classList.remove('hidden');
        this.showStep(1);
    }

    closeModal() {
        document.getElementById('catalogScannerModal').classList.add('hidden');
        this.resetData();
    }

    showStep(step) {
        // Hide all steps
        document.querySelectorAll('.step-content').forEach(el => el.classList.add('hidden'));
        
        // Show selected step
        document.getElementById(`step${step}`).classList.remove('hidden');
        
        // Update step-specific content
        if (step === 2 && this.analysis) {
            this.displayAnalysis();
        } else if (step === 3 && this.suggestions) {
            this.displaySuggestions();
        }
    }

    showManualInput() {
        document.getElementById('manualInput').classList.remove('hidden');
    }

    async handleFileUpload(file) {
        if (!file) return;

        try {
            const data = await this.readFile(file);
            this.processCatalogData(data);
        } catch (error) {
            showModernAlert('Error reading file: ' + error.message, 'error');
        }
    }

    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                try {
                    const content = e.target.result;
                    let data;
                    
                    if (file.name.endsWith('.csv')) {
                        data = this.parseCSV(content);
                    } else {
                        // For Excel files, assume JSON format for now
                        data = JSON.parse(content);
                    }
                    
                    resolve(data);
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    parseCSV(content) {
        const lines = content.split('\n');
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim()) {
                const values = lines[i].split(',').map(v => v.trim());
                const item = {};
                
                headers.forEach((header, index) => {
                    item[header] = values[index] || '';
                });
                
                data.push(item);
            }
        }
        
        return data;
    }

    processManualData() {
        const input = document.getElementById('catalogDataInput').value;
        try {
            const data = JSON.parse(input);
            this.processCatalogData(data);
        } catch (error) {
            showModernAlert('Invalid JSON format. Please check your data.', 'error');
        }
    }

    async processCatalogData(data) {
        try {
            // Validate and clean data
            const cleanedData = this.cleanCatalogData(data);
            
            if (cleanedData.length === 0) {
                showModernAlert('No valid catalog data found.', 'error');
                return;
            }
            
            this.catalogData = cleanedData;
            
            // Send to backend for analysis
            const response = await fetch('/api/catalog/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ catalog: cleanedData })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.analysis = result.analysis;
                this.suggestions = result.suggestions;
                this.showStep(2);
            } else {
                showModernAlert('Analysis failed: ' + result.error, 'error');
            }
            
        } catch (error) {
            showModernAlert('Error processing catalog data: ' + error.message, 'error');
        }
    }

    cleanCatalogData(data) {
        const cleaned = [];
        
        for (const item of data) {
            const name = item.name || item.product_name || item.title || '';
            const price = parseFloat(item.price || item.rate || item.cost || 0);
            const category = item.category || item.type || item.product_type || '';
            const description = item.description || item.desc || '';
            
            if (name && price > 0) {
                cleaned.push({
                    name: name.trim(),
                    price: price,
                    category: category.trim(),
                    description: description.trim()
                });
            }
        }
        
        return cleaned;
    }

    displayAnalysis() {
        const container = document.getElementById('analysisResults');
        
        const html = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold mb-2">Summary</h4>
                    <p><strong>Total Items:</strong> ${this.analysis.total_items}</p>
                    <p><strong>Categories Found:</strong> ${Object.keys(this.analysis.categories).length}</p>
                    <p><strong>Price Ranges:</strong> ${Object.keys(this.analysis.price_ranges).length}</p>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold mb-2">Categories</h4>
                    ${Object.entries(this.analysis.categories).map(([category, data]) => `
                        <div class="mb-2">
                            <strong>${category}:</strong> ${data.count} items (Avg: AED ${data.avg_price.toFixed(2)})
                        </div>
                    `).join('')}
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold mb-2">Price Distribution</h4>
                    ${Object.entries(this.analysis.price_ranges).map(([range, count]) => `
                        <div class="mb-2">
                            <strong>${range}:</strong> ${count} items
                        </div>
                    `).join('')}
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold mb-2">Common Patterns</h4>
                    ${this.analysis.common_patterns.slice(0, 10).map(pattern => `
                        <span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2 mb-1">${pattern}</span>
                    `).join('')}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    displaySuggestions() {
        const container = document.getElementById('suggestionsResults');
        
        let html = '<div class="space-y-6">';
        
        // Product Types
        if (this.suggestions.product_types.length > 0) {
            html += `
                <div>
                    <h4 class="font-semibold mb-3">Suggested Product Types (${this.suggestions.product_types.length})</h4>
                    <div class="space-y-3">
                        ${this.suggestions.product_types.map(type => `
                            <div class="border border-gray-200 rounded-lg p-4">
                                <div class="flex items-center justify-between mb-2">
                                    <h5 class="font-medium">${type.name}</h5>
                                    <span class="text-sm text-gray-500">${type.products.length} products</span>
                                </div>
                                <p class="text-sm text-gray-600 mb-3">${type.description}</p>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                                    ${type.products.map(product => `
                                        <div class="text-sm bg-gray-50 p-2 rounded">
                                            <strong>${product.name}</strong> - AED ${product.rate}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Recommendations
        if (this.suggestions.recommendations.length > 0) {
            html += `
                <div>
                    <h4 class="font-semibold mb-3">Recommendations</h4>
                    <div class="space-y-2">
                        ${this.suggestions.recommendations.map(rec => `
                            <div class="bg-blue-50 border-l-4 border-blue-400 p-3">
                                <p class="text-sm">${rec.suggestion}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
    }

    async createProducts() {
        try {
            const response = await fetch('/api/catalog/auto-create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ suggestions: this.suggestions })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showModernAlert(result.message, 'success');
                this.closeModal();
                
                // Refresh product lists if they exist
                if (typeof loadProducts === 'function') {
                    loadProducts();
                }
                if (typeof loadProductTypes === 'function') {
                    loadProductTypes();
                }
            } else {
                showModernAlert('Failed to create products: ' + result.error, 'error');
            }
            
        } catch (error) {
            showModernAlert('Error creating products: ' + error.message, 'error');
        }
    }

    resetData() {
        this.catalogData = [];
        this.analysis = null;
        this.suggestions = null;
        
        // Reset UI
        document.getElementById('catalogFile').value = '';
        document.getElementById('catalogDataInput').value = '';
        document.getElementById('manualInput').classList.add('hidden');
        document.getElementById('analysisResults').innerHTML = '';
        document.getElementById('suggestionsResults').innerHTML = '';
    }
}

// Initialize catalog scanner when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize catalog scanner
    const catalogScanner = new CatalogScanner();
    
    // Export for global access
    window.catalogScanner = catalogScanner;
    
    console.log('Catalog Scanner initialized:', window.catalogScanner);
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already loaded, initialize immediately
    const catalogScanner = new CatalogScanner();
    window.catalogScanner = catalogScanner;
    console.log('Catalog Scanner initialized immediately:', window.catalogScanner);
}
