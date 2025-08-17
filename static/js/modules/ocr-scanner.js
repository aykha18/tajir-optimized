/**
 * OCR Scanner Module
 * Handles image upload and text extraction using OCR
 */
class OCRScanner {
    constructor() {
        this.isInitialized = false;
        this.currentStep = 1;
        this.uploadedFiles = [];
        this.extractedTexts = [];
        this.init();
    }

    init() {
        this.createModal();
        this.bindEvents();
        this.isInitialized = true;
        console.log('OCR Scanner initialized');
    }

    createModal() {
        const modalHTML = `
            <div id="ocrModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden">
                <div class="flex items-center justify-center min-h-screen p-4">
                    <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                        <!-- Header -->
                        <div class="flex items-center justify-between p-6 border-b">
                            <h2 class="text-xl font-semibold text-gray-800 flex items-center gap-2">
                                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                OCR Text Scanner
                            </h2>
                            <button onclick="window.ocrScanner.closeModal()" class="text-gray-400 hover:text-gray-600">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                </svg>
                            </button>
                        </div>

                        <!-- Content -->
                        <div class="p-6">
                            <!-- Step 1: Upload Images -->
                            <div id="ocrStep1" class="ocr-step">
                                <div class="text-center mb-6">
                                    <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                                        </svg>
                                    </div>
                                    <h3 class="text-lg font-medium text-gray-900 mb-2">Upload Images</h3>
                                    <p class="text-gray-600">Upload images containing text you want to extract</p>
                                </div>

                                <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
                                    <input type="file" id="ocrFileInput" multiple accept="image/*" class="hidden">
                                    <div class="space-y-4">
                                        <svg class="w-12 h-12 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                        </svg>
                                        <div>
                                            <button onclick="document.getElementById('ocrFileInput').click()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                                                Choose Images
                                            </button>
                                            <p class="text-sm text-gray-500 mt-2">or drag and drop images here</p>
                                        </div>
                                    </div>
                                </div>

                                <!-- File Preview -->
                                <div id="ocrFilePreview" class="mt-6 hidden">
                                    <h4 class="font-medium text-gray-900 mb-3">Selected Images:</h4>
                                    <div id="ocrFileList" class="grid grid-cols-2 md:grid-cols-3 gap-4"></div>
                                </div>

                                <div class="flex justify-end mt-6">
                                    <button onclick="window.ocrScanner.showStep(2)" id="ocrNextBtn" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed" disabled>
                                        Extract Text
                                    </button>
                                </div>
                            </div>

                            <!-- Step 2: Processing -->
                            <div id="ocrStep2" class="ocr-step hidden">
                                <div class="text-center py-8">
                                    <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                    </div>
                                    <h3 class="text-lg font-medium text-gray-900 mb-2">Processing Images</h3>
                                    <p class="text-gray-600">Extracting text from your images...</p>
                                    <div id="ocrProgress" class="mt-4">
                                        <div class="bg-gray-200 rounded-full h-2">
                                            <div id="ocrProgressBar" class="bg-blue-600 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                                        </div>
                                        <p id="ocrProgressText" class="text-sm text-gray-500 mt-2">Starting...</p>
                                    </div>
                                </div>
                            </div>

                            <!-- Step 3: Results -->
                            <div id="ocrStep3" class="ocr-step hidden">
                                <div class="text-center mb-6">
                                    <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                    <h3 class="text-lg font-medium text-gray-900 mb-2">Text Extraction Complete</h3>
                                    <p class="text-gray-600">Review and copy the extracted text</p>
                                </div>

                                <div id="ocrResults" class="space-y-4"></div>

                                <div class="flex justify-between mt-6">
                                    <button onclick="window.ocrScanner.showStep(1)" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                                        Upload More
                                    </button>
                                    <button onclick="window.ocrScanner.closeModal()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                                        Done
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add modal to body if it doesn't exist
        if (!document.getElementById('ocrModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }
    }

    bindEvents() {
        // File input change event
        document.addEventListener('change', (e) => {
            if (e.target.id === 'ocrFileInput') {
                this.handleFileSelection(e.target.files);
            }
        });

        // Drag and drop events
        const dropZone = document.querySelector('#ocrModal .border-dashed');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('border-blue-400', 'bg-blue-50');
            });

            dropZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dropZone.classList.remove('border-blue-400', 'bg-blue-50');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('border-blue-400', 'bg-blue-50');
                this.handleFileSelection(e.dataTransfer.files);
            });
        }
    }

    handleFileSelection(files) {
        this.uploadedFiles = Array.from(files).filter(file => 
            file.type.startsWith('image/')
        );

        if (this.uploadedFiles.length === 0) {
            showModernAlert('Please select valid image files.', 'error');
            return;
        }

        this.displayFilePreview();
        document.getElementById('ocrNextBtn').disabled = false;
    }

    displayFilePreview() {
        const previewContainer = document.getElementById('ocrFilePreview');
        const fileList = document.getElementById('ocrFileList');
        
        previewContainer.classList.remove('hidden');
        fileList.innerHTML = '';

        this.uploadedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'relative bg-gray-100 rounded-lg p-2';
                fileItem.innerHTML = `
                    <img src="${e.target.result}" alt="${file.name}" class="w-full h-24 object-cover rounded">
                    <div class="mt-2 text-xs text-gray-600 truncate">${file.name}</div>
                    <button onclick="window.ocrScanner.removeFile(${index})" class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600">
                        ×
                    </button>
                `;
                fileList.appendChild(fileItem);
            };
            reader.readAsDataURL(file);
        });
    }

    removeFile(index) {
        this.uploadedFiles.splice(index, 1);
        this.displayFilePreview();
        
        if (this.uploadedFiles.length === 0) {
            document.getElementById('ocrFilePreview').classList.add('hidden');
            document.getElementById('ocrNextBtn').disabled = true;
        }
    }

    async processImages() {
        this.showStep(2);
        
        const formData = new FormData();
        this.uploadedFiles.forEach(file => {
            formData.append('images', file);
        });

        const progressBar = document.getElementById('ocrProgressBar');
        const progressText = document.getElementById('ocrProgressText');
        
        try {
            progressText.textContent = 'Uploading images...';
            progressBar.style.width = '25%';

            const response = await fetch('/api/ocr/extract-batch', {
                method: 'POST',
                body: formData
            });

            progressBar.style.width = '75%';
            progressText.textContent = 'Processing images...';

            const result = await response.json();

            progressBar.style.width = '100%';
            progressText.textContent = 'Complete!';

            if (result.success) {
                this.extractedTexts = result.results;
                setTimeout(() => this.showStep(3), 500);
            } else {
                throw new Error(result.error || 'Failed to extract text');
            }

        } catch (error) {
            console.error('OCR processing error:', error);
            showModernAlert(`Error processing images: ${error.message}`, 'error');
            this.showStep(1);
        }
    }

    displayResults() {
        const resultsContainer = document.getElementById('ocrResults');
        resultsContainer.innerHTML = '';

        this.extractedTexts.forEach((result, index) => {
            const resultCard = document.createElement('div');
            resultCard.className = 'bg-gray-50 rounded-lg p-4 border';
            
            const confidenceColor = result.confidence > 70 ? 'text-green-600' : 
                                  result.confidence > 40 ? 'text-yellow-600' : 'text-red-600';
            
            resultCard.innerHTML = `
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <h4 class="font-medium text-gray-900">${result.filename}</h4>
                        <p class="text-sm text-gray-500">Confidence: <span class="${confidenceColor} font-medium">${result.confidence.toFixed(1)}%</span></p>
                    </div>
                    <button onclick="window.ocrScanner.copyText(${index})" class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                        Copy Text
                    </button>
                </div>
                <div class="bg-white rounded border p-3 max-h-32 overflow-y-auto">
                    <pre class="text-sm text-gray-700 whitespace-pre-wrap">${result.success ? result.text || 'No text detected' : result.error}</pre>
                </div>
            `;
            
            resultsContainer.appendChild(resultCard);
        });
    }

    copyText(index) {
        const result = this.extractedTexts[index];
        if (result.success && result.text) {
            navigator.clipboard.writeText(result.text).then(() => {
                showSimpleToast('Text copied to clipboard!', 'success');
            }).catch(() => {
                showModernAlert('Failed to copy text. Please select and copy manually.', 'warning');
            });
        }
    }

    showStep(step) {
        this.currentStep = step;
        
        // Hide all steps
        document.querySelectorAll('.ocr-step').forEach(el => el.classList.add('hidden'));
        
        // Show current step
        document.getElementById(`ocrStep${step}`).classList.remove('hidden');
        
        // Handle step-specific actions
        if (step === 2) {
            this.processImages();
        } else if (step === 3) {
            this.displayResults();
        }
    }

    showModal() {
        document.getElementById('ocrModal').classList.remove('hidden');
        this.showStep(1);
        this.reset();
    }

    closeModal() {
        document.getElementById('ocrModal').classList.add('hidden');
        this.reset();
    }

    reset() {
        this.currentStep = 1;
        this.uploadedFiles = [];
        this.extractedTexts = [];
        
        // Reset file input
        const fileInput = document.getElementById('ocrFileInput');
        if (fileInput) fileInput.value = '';
        
        // Reset UI
        document.getElementById('ocrFilePreview').classList.add('hidden');
        document.getElementById('ocrNextBtn').disabled = true;
        document.getElementById('ocrProgressBar').style.width = '0%';
        document.getElementById('ocrProgressText').textContent = 'Starting...';
    }
}

// Initialize OCR scanner when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize OCR scanner
    const ocrScanner = new OCRScanner();
    
    // Export for global access
    window.ocrScanner = ocrScanner;
    
    console.log('OCR Scanner initialized:', window.ocrScanner);
});

// Also initialize immediately if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already loaded, initialize immediately
    const ocrScanner = new OCRScanner();
    window.ocrScanner = ocrScanner;
    console.log('OCR Scanner initialized immediately:', window.ocrScanner);
}
