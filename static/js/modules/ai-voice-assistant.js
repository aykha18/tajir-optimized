/**
 * AI Voice Assistant for Billing
 * Handles voice commands for product selection, customer search, price queries, and bill generation
 */
class AIVoiceAssistant {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.commandHistory = [];
        this.maxHistorySize = 10;
        this.isWaitingForSelection = false;
        
        this.initializeSpeechRecognition();
        this.setupVoiceCommands();
    }

    /**
     * Initialize speech recognition
     */
    initializeSpeechRecognition() {
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.error('AI Voice Assistant: Speech recognition not supported in this browser');
            this.showVoiceFeedback('Speech recognition not supported in this browser');
            return;
        }

        try {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure recognition settings
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 3;
            this.recognition.serviceURI = '';
            
            // Event handlers
            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateUI('listening');
                this.showVoiceFeedback('Listening for your command...');
            };

            this.recognition.onresult = (event) => {
                const result = event.results[0];
                const command = result[0].transcript.toLowerCase().trim();
                const confidence = result[0].confidence;
                
                this.showVoiceFeedback(`Heard: "${command}"`);
                
                // Process command after a short delay to show what was heard
                setTimeout(() => {
                    this.processCommand(command);
                }, 500);
            };

            this.recognition.onerror = (event) => {
                console.error('AI Voice Assistant: Speech recognition error:', event.error);
                this.isListening = false;
                
                let errorMessage = 'Sorry, I did not understand that. Please try again.';
                
                switch (event.error) {
                    case 'not-allowed':
                        errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
                        break;
                    case 'no-speech':
                        errorMessage = 'No speech detected. Please speak clearly and try again.';
                        break;
                    case 'audio-capture':
                        errorMessage = 'Audio capture error. Please check your microphone.';
                        break;
                    case 'network':
                        errorMessage = 'Network error. Please check your internet connection.';
                        break;
                    case 'aborted':
                        return; // Don't show error for normal aborts
                    default:
                        errorMessage = `Speech recognition error: ${event.error}`;
                }
                
                this.showVoiceFeedback(errorMessage);
                this.speak(errorMessage);
                
                // If we're waiting for selection, try to restart after error
                if (this.isWaitingForSelection && this.pendingProductSelection) {
                    setTimeout(() => {
                        this.startListening();
                    }, 1000);
                } else {
                    this.updateUI('error');
                }
            };

            this.recognition.onend = () => {
                this.isListening = false;
                
                // If we're waiting for product selection, continue listening
                if (this.isWaitingForSelection && this.pendingProductSelection) {
                    setTimeout(() => {
                        this.startListening();
                    }, 500);
                } else {
                    this.updateUI('idle');
                }
            };
            
        } catch (error) {
            console.error('AI Voice Assistant: Error initializing speech recognition:', error);
            this.showVoiceFeedback('Error initializing voice recognition');
        }
    }

    /**
     * Setup voice command patterns and handlers
     */
    setupVoiceCommands() {
        this.commands = {
            // Product commands
            'add with quantity': {
                pattern: /add\s+(\d+)\s+(.+)/i,
                handler: (matches) => this.addProduct(matches[1], matches[2])
            },
            'add without quantity': {
                pattern: /add\s+(.+)/i,
                handler: (matches) => this.addProduct(1, matches[1])
            },
            'add product': {
                pattern: /add\s+product\s+(\d+)\s+(.+)/i,
                handler: (matches) => this.addProduct(matches[1], matches[2])
            },
            'add product without quantity': {
                pattern: /add\s+product\s+(.+)/i,
                handler: (matches) => this.addProduct(1, matches[1])
            },
            
            // Product selection commands (for when multiple products found)
            'select product number': {
                pattern: /(?:select|choose|pick)\s+(?:product\s+)?(\d+)/i,
                handler: (matches) => this.selectProductByNumber(parseInt(matches[1]))
            },
            'select first': {
                pattern: /(?:select|choose|pick)\s+first/i,
                handler: () => this.selectProductByNumber(1)
            },
            'select second': {
                pattern: /(?:select|choose|pick)\s+second/i,
                handler: () => this.selectProductByNumber(2)
            },
            'select third': {
                pattern: /(?:select|choose|pick)\s+third/i,
                handler: () => this.selectProductByNumber(3)
            },
            'select fourth': {
                pattern: /(?:select|choose|pick)\s+fourth/i,
                handler: () => this.selectProductByNumber(4)
            },
            'select fifth': {
                pattern: /(?:select|choose|pick)\s+fifth/i,
                handler: () => this.selectProductByNumber(5)
            },
            'select number': {
                pattern: /(\d+)/i,
                handler: (matches) => this.selectProductByNumber(parseInt(matches[1]))
            },
            'cancel selection': {
                pattern: /cancel/i,
                handler: () => this.cancelProductSelection()
            },
            
            // Customer commands
            'find customer': {
                pattern: /find\s+customer\s+(.+)/i,
                handler: (matches) => this.findCustomer(matches[1])
            },
            'search customer': {
                pattern: /search\s+customer\s+(.+)/i,
                handler: (matches) => this.findCustomer(matches[1])
            },
            'customer': {
                pattern: /customer\s+(.+)/i,
                handler: (matches) => this.findCustomer(matches[1])
            },
            
            // Customer selection commands (for when multiple customers found)
            'select customer number': {
                pattern: /(?:select|choose|pick)\s+(?:customer\s+)?(\d+)/i,
                handler: (matches) => this.selectCustomerByNumber(parseInt(matches[1]))
            },
            'select first customer': {
                pattern: /(?:select|choose|pick)\s+first\s+customer/i,
                handler: () => this.selectCustomerByNumber(1)
            },
            'select second customer': {
                pattern: /(?:select|choose|pick)\s+second\s+customer/i,
                handler: () => this.selectCustomerByNumber(2)
            },
            'select third customer': {
                pattern: /(?:select|choose|pick)\s+third\s+customer/i,
                handler: () => this.selectCustomerByNumber(3)
            },
            'select fourth customer': {
                pattern: /(?:select|choose|pick)\s+fourth\s+customer/i,
                handler: () => this.selectCustomerByNumber(4)
            },
            'select fifth customer': {
                pattern: /(?:select|choose|pick)\s+fifth\s+customer/i,
                handler: () => this.selectCustomerByNumber(5)
            },
            'cancel customer selection': {
                pattern: /cancel\s+customer/i,
                handler: () => this.cancelCustomerSelection()
            },
            
            // Price queries
            'price': {
                pattern: /price\s+(.+)/i,
                handler: (matches) => this.getPrice(matches[1])
            },
            'how much': {
                pattern: /how\s+much\s+(.+)/i,
                handler: (matches) => this.getPrice(matches[1])
            },
            'cost': {
                pattern: /cost\s+(.+)/i,
                handler: (matches) => this.getPrice(matches[1])
            },
            
            // Bill commands
            'create bill': {
                pattern: /create\s+bill/i,
                handler: () => this.createBill()
            },
            'generate bill': {
                pattern: /generate\s+bill/i,
                handler: () => this.createBill()
            },
            'print bill': {
                pattern: /print\s+bill/i,
                handler: () => this.printBill()
            },
            
            // Navigation commands
            'clear': {
                pattern: /clear/i,
                handler: () => this.clearBill()
            },
            'reset': {
                pattern: /reset/i,
                handler: () => this.resetBill()
            },
            
            // Help commands
            'help': {
                pattern: /help/i,
                handler: () => this.showHelp()
            },
            'what can you do': {
                pattern: /what\s+can\s+you\s+do/i,
                handler: () => this.showHelp()
            }
        };
    }

    /**
     * Process voice command
     */
    processCommand(command) {
        this.addToHistory(command);
        
        // Check each command pattern
        for (const [cmdName, cmd] of Object.entries(this.commands)) {
            const matches = command.match(cmd.pattern);
            if (matches) {
                try {
                    cmd.handler(matches);
                    return;
                } catch (error) {
                    console.error('AI Voice Assistant: Error executing command:', error);
                    this.speak('Sorry, there was an error executing that command');
                }
            }
        }
        
        // Special handling for pending product selection
        if (this.pendingProductSelection) {
            const numberMatch = command.match(/^(\d+)$/);
            if (numberMatch) {
                const number = parseInt(numberMatch[1]);
                this.selectProductByNumber(number);
                return;
            }
        }
        
        // Special handling for pending customer selection
        if (this.pendingCustomerSelection) {
            const numberMatch = command.match(/^(\d+)$/);
            if (numberMatch) {
                const number = parseInt(numberMatch[1]);
                this.selectCustomerByNumber(number);
                return;
            }
        }
        
        this.speak('I did not understand that command. Say help for available commands.');
        this.showVoiceFeedback('Command not recognized. Say "help" for available commands.');
    }

    /**
     * Add product to bill
     */
    async addProduct(quantity, productName) {
        try {
            // Get the billing system's product input and trigger search
            const productInput = document.getElementById('productInput') || document.querySelector('input[placeholder*="product" i]');
            if (!productInput) {
                this.speak('Product input field not found. Please make sure you are on the billing page.');
                return;
            }
            
            // Set the product name in the input to trigger the dropdown
            productInput.value = productName;
            productInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Wait a moment for the dropdown to populate
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Look for the product dropdown and select the first matching product
            const productDropdown = document.querySelector('.product-suggestion-mobile') || 
                                  document.querySelector('.product-dropdown') || 
                                  document.querySelector('[class*="product-dropdown"]') ||
                                  document.querySelector('[class*="dropdown"]');
            
            if (productDropdown) {
                // Find all product options that match our search
                const productOptions = productDropdown.querySelectorAll('.product-option-mobile');
                const matchingProducts = [];
                
                for (const option of productOptions) {
                    const optionName = option.getAttribute('data-product-name');
                    if (optionName && optionName.toLowerCase().includes(productName.toLowerCase())) {
                        matchingProducts.push({
                            element: option,
                            name: option.getAttribute('data-product-name'),
                            price: option.getAttribute('data-product-price')
                        });
                    }
                }
                
                if (matchingProducts.length === 0) {
                    this.speak(`Product "${productName}" not found. Please check the spelling or try a different product name.`);
                } else if (matchingProducts.length === 1) {
                    // Only one product found - automatically select it
                    const selectedProduct = matchingProducts[0];
                    
                    // Click the product option to select it
                    selectedProduct.element.click();
                    
                    // Wait for the product to be selected
                    await new Promise(resolve => setTimeout(resolve, 500));
                    
                    // Set the quantity
                    const quantityInput = document.getElementById('quantity');
                    if (quantityInput) {
                        quantityInput.value = quantity;
                        quantityInput.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    
                    // Add to bill
                    const addButton = document.getElementById('addItemBtn');
                    if (addButton) {
                        addButton.click();
                        this.speak(`Added ${quantity} ${selectedProduct.name} to the bill`);
                    } else {
                        this.speak(`Selected ${selectedProduct.name} but could not add to bill. Please click the add button manually.`);
                    }
                } else {
                    // Multiple products found - ask user to choose
                    this.speak(`Found ${matchingProducts.length} products. Please say which one you want.`);
                    
                    // Store the matching products for selection
                    this.pendingProductSelection = {
                        products: matchingProducts,
                        quantity: quantity,
                        originalCommand: productName
                    };
                    
                    // Set waiting flag for continuous listening
                    this.isWaitingForSelection = true;
                    
                    // Give user options to choose from
                    const ordinals = ['first', 'second', 'third', 'fourth', 'fifth'];
                    const optionsText = matchingProducts.map((product, index) => {
                        const ordinal = ordinals[index] || `${index + 1}`;
                        return `${ordinal} for ${product.name}`;
                    }).join(', ');
                    
                    this.speak(`Say ${optionsText}, or say cancel to cancel.`);
                    
                    // Continue listening for the user's selection
                    setTimeout(() => {
                        this.startListening();
                    }, 2000);
                }
            } else {
                this.speak('Product dropdown not found. Please make sure you are on the billing page.');
            }
            
        } catch (error) {
            console.error('AI Voice Assistant: Error adding product:', error);
            this.speak('Sorry, there was an error adding the product. Please try again.');
        }
    }

    /**
     * Search for products
     */
    async searchProducts(query) {
        try {
            const response = await fetch(`/api/products?search=${encodeURIComponent(query)}`);
            const products = await response.json();
            return products.filter(p => p.is_active);
        } catch (error) {
            console.error('AI Voice Assistant: Error searching products:', error);
            return [];
        }
    }

    /**
     * Add product to bill (integration with billing system)
     */
    addProductToBill(product, quantity) {
        // Integration with existing billing system
        if (window.BillingSystem) {
            window.BillingSystem.addProductToBill(product, quantity);
        } else if (window.MobileBillingV3) {
            window.MobileBillingV3.addProductToBill(product, quantity);
        }
    }

    /**
     * Find customer by name or phone
     */
    async findCustomer(query) {
        try {
            // Get the customer input field and trigger search
            const customerInput = document.getElementById('billCustomer');
            if (!customerInput) {
                this.speak('Customer input field not found. Please make sure you are on the billing page.');
                return;
            }
            
            // Set the search query in the input to trigger the dropdown
            customerInput.value = query;
            customerInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Wait a moment for the dropdown to populate
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Look for the customer dropdown
            const customerDropdown = document.querySelector('.customer-suggestion') || 
                                   document.querySelector('.customer-dropdown') || 
                                   document.querySelector('[class*="customer-dropdown"]');
            
            if (customerDropdown) {
                // Find all customer options that match our search
                const customerOptions = customerDropdown.querySelectorAll('.customer-option');
                const matchingCustomers = [];
                
                for (const option of customerOptions) {
                    const customerName = option.getAttribute('data-customer-name');
                    const customerPhone = option.getAttribute('data-customer-phone');
                    if (customerName && (customerName.toLowerCase().includes(query.toLowerCase()) || 
                                        (customerPhone && customerPhone.includes(query)))) {
                        matchingCustomers.push({
                            element: option,
                            name: customerName,
                            phone: customerPhone,
                            city: option.getAttribute('data-customer-city') || '',
                            area: option.getAttribute('data-customer-area') || '',
                            email: option.getAttribute('data-customer-email') || '',
                            address: option.getAttribute('data-customer-address') || '',
                            trn: option.getAttribute('data-customer-trn') || '',
                            customer_type: option.getAttribute('data-customer-type') || 'Individual',
                            business_name: option.getAttribute('data-business-name') || '',
                            business_address: option.getAttribute('data-business-address') || ''
                        });
                    }
                }
                
                if (matchingCustomers.length === 0) {
                    this.speak(`No customer found matching ${query}. Please try a different search term.`);
                } else if (matchingCustomers.length === 1) {
                    // Only one customer found - automatically select it
                    const selectedCustomer = matchingCustomers[0];
                    
                    // Click the customer option to select it
                    selectedCustomer.element.click();
                    
                    this.speak(`Selected customer ${selectedCustomer.name} from ${selectedCustomer.city}`);
                } else {
                    // Multiple customers found - ask user to choose
                    this.speak(`Found ${matchingCustomers.length} customers. Please say which one you want.`);
                    
                    // Store the matching customers for selection
                    this.pendingCustomerSelection = {
                        customers: matchingCustomers,
                        originalCommand: query
                    };
                    
                    // Set waiting flag for continuous listening
                    this.isWaitingForSelection = true;
                    
                    // Give user options to choose from
                    const ordinals = ['first', 'second', 'third', 'fourth', 'fifth'];
                    const optionsText = matchingCustomers.map((customer, index) => {
                        const ordinal = ordinals[index] || `${index + 1}`;
                        return `${ordinal} for ${customer.name} from ${customer.city}`;
                    }).join(', ');
                    
                    this.speak(`Say ${optionsText}, or say cancel to cancel.`);
                    
                    // Continue listening for the user's selection
                    setTimeout(() => {
                        this.startListening();
                    }, 2000);
                }
            } else {
                // Fallback to API search if dropdown not found
                const response = await fetch(`/api/customers?search=${encodeURIComponent(query)}`);
                const customers = await response.json();
                
                if (customers.length === 0) {
                    this.speak(`No customer found matching ${query}`);
                    return;
                }
                
                if (customers.length === 1) {
                    const customer = customers[0];
                    this.selectCustomer(customer);
                    this.speak(`Selected customer ${customer.name} from ${customer.city}`);
                } else {
                    this.speak(`Found ${customers.length} customers. Please be more specific.`);
                }
            }
            
        } catch (error) {
            console.error('AI Voice Assistant: Error finding customer:', error);
            this.speak('Sorry, there was an error finding the customer');
        }
    }

    /**
     * Select customer (integration with billing system)
     */
    selectCustomer(customer) {
        if (window.BillingSystem) {
            window.BillingSystem.selectCustomer(customer);
        } else if (window.MobileBillingV3) {
            window.MobileBillingV3.selectCustomer(customer);
        }
    }

    /**
     * Select customer by number when multiple customers are found
     */
    async selectCustomerByNumber(number) {
        if (!this.pendingCustomerSelection) {
            this.speak('No customer selection pending. Please search for a customer first.');
            return;
        }
        
        const { customers, originalCommand } = this.pendingCustomerSelection;
        
        if (number < 1 || number > customers.length) {
            this.speak(`Please select a number between 1 and ${customers.length}`);
            return;
        }
        
        const selectedCustomer = customers[number - 1];
        
        try {
            // Click the customer option to select it
            selectedCustomer.element.click();
            
            this.speak(`Selected customer ${selectedCustomer.name} from ${selectedCustomer.city}`);
            
            // Clear pending selection and waiting flag
            this.pendingCustomerSelection = null;
            this.isWaitingForSelection = false;
            
        } catch (error) {
            console.error('AI Voice Assistant: Error selecting customer:', error);
            this.speak('Sorry, there was an error selecting the customer. Please try again.');
        }
    }
    
    /**
     * Cancel pending customer selection
     */
    cancelCustomerSelection() {
        if (this.pendingCustomerSelection) {
            this.speak('Customer selection cancelled.');
            this.pendingCustomerSelection = null;
            this.isWaitingForSelection = false;
        } else {
            this.speak('No customer selection to cancel.');
        }
    }

    /**
     * Get price for product
     */
    async getPrice(productName) {
        try {
            const products = await this.searchProducts(productName);
            
            if (products.length === 0) {
                this.speak(`No product found matching ${productName}`);
                return;
            }
            
            if (products.length === 1) {
                const product = products[0];
                this.speak(`${product.product_name} costs ${product.rate} AED`);
            } else {
                this.speak(`Found ${products.length} products. Here are the prices:`);
                products.forEach(product => {
                    console.log(`${product.product_name}: ${product.rate} AED`);
                });
            }
        } catch (error) {
            console.error('AI Voice Assistant: Error getting price:', error);
            this.speak('Sorry, there was an error getting the price');
        }
    }

    /**
     * Create bill
     */
    createBill() {
        if (window.BillingSystem) {
            window.BillingSystem.createBill();
            this.speak('Bill created successfully');
        } else if (window.MobileBillingV3) {
            window.MobileBillingV3.createBill();
            this.speak('Bill created successfully');
        } else {
            this.speak('Billing system not available');
        }
    }

    /**
     * Print bill
     */
    printBill() {
        if (window.BillingSystem) {
            window.BillingSystem.printBill();
            this.speak('Printing bill');
        } else if (window.MobileBillingV3) {
            window.MobileBillingV3.printBill();
            this.speak('Printing bill');
        } else {
            this.speak('Billing system not available');
        }
    }

    /**
     * Clear bill
     */
    clearBill() {
        if (window.BillingSystem) {
            window.BillingSystem.clearBill();
            this.speak('Bill cleared');
        } else if (window.MobileBillingV3) {
            window.MobileBillingV3.clearBill();
            this.speak('Bill cleared');
        } else {
            this.speak('Billing system not available');
        }
    }

    /**
     * Reset bill
     */
    resetBill() {
        this.clearBill();
    }

    /**
     * Show help
     */
    showHelp() {
        const helpText = `
            I can help you with billing. Here are some commands you can use:
            
            Add products: 
            - "Add 2 shirts" (with quantity)
            - "Add product blouse padded" (quantity defaults to 1)
            - "Add trouser" (quantity defaults to 1)
            
            Find customers: 
            - "Find customer Ahmed" or "Search customer 0501234567"
            - "Customer Fahad" or "Customer Al Balushi"
            - When multiple customers found, say "first", "second", etc.
            
            Check prices: "Price kurti" or "How much shirt"
            Create bill: "Create bill" or "Generate bill"
            Print bill: "Print bill"
            Clear bill: "Clear" or "Reset"
            
            Try saying one of these commands!
        `;
        
        this.speak('Here are the available commands. Check the console for details.');
        console.log(helpText);
    }

    /**
     * Start listening for voice commands
     */
    startListening() {
        if (!this.recognition) {
            this.speak('Speech recognition is not supported in this browser');
            return;
        }
        
        if (this.isListening) {
            this.stopListening();
            return;
        }
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('AI Voice Assistant: Error starting speech recognition:', error);
            this.speak('Error starting voice recognition');
        }
    }

    /**
     * Stop listening
     */
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    /**
     * Speak text using speech synthesis
     */
    speak(text) {
        if (this.synthesis) {
            // Stop any current speech
            this.synthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9; // Slightly slower for clarity
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            
            this.synthesis.speak(utterance);
        }
        
        // Also show in UI
        this.showVoiceFeedback(text);
    }

    /**
     * Show voice feedback in UI
     */
    showVoiceFeedback(text) {
        // Create or update voice feedback element
        let feedbackEl = document.getElementById('voice-feedback');
        if (!feedbackEl) {
            feedbackEl = document.createElement('div');
            feedbackEl.id = 'voice-feedback';
            feedbackEl.className = 'fixed top-4 right-4 bg-indigo-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 max-w-sm';
            document.body.appendChild(feedbackEl);
        }
        
        feedbackEl.textContent = text;
        feedbackEl.style.display = 'block';
        
        // Hide after 3 seconds
        setTimeout(() => {
            feedbackEl.style.display = 'none';
        }, 3000);
    }

    /**
     * Update UI based on listening state
     */
    updateUI(state) {
        const button = document.getElementById('voice-assistant-btn');
        if (!button) return;
        
        const icon = button.querySelector('svg');
        const text = button.querySelector('span');
        
        switch (state) {
            case 'listening':
                button.className = 'bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2 animate-pulse';
                if (icon) icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>';
                if (text) text.textContent = 'Listening...';
                break;
            case 'error':
                button.className = 'bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2';
                if (icon) icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>';
                if (text) text.textContent = 'Error';
                break;
            case 'idle':
            default:
                button.className = 'bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2';
                if (icon) icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>';
                if (text) text.textContent = 'Voice Assistant';
                break;
        }
    }

    /**
     * Add command to history
     */
    addToHistory(command) {
        this.commandHistory.unshift(command);
        if (this.commandHistory.length > this.maxHistorySize) {
            this.commandHistory.pop();
        }
    }

    /**
     * Get command history
     */
    getHistory() {
        return [...this.commandHistory];
    }

    /**
     * Clear command history
     */
    clearHistory() {
        this.commandHistory = [];
    }

    /**
     * Switch language
     */
    switchLanguage(lang) {
        if (this.recognition) {
            this.recognition.lang = lang;
            this.speak(`Language switched to ${lang === 'ar-SA' ? 'Arabic' : 'English'}`);
        }
    }

    /**
     * Toggle voice assistant
     */
    toggle() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    /**
     * Select product by number when multiple products are found
     */
    async selectProductByNumber(number) {
        if (!this.pendingProductSelection) {
            this.speak('No product selection pending. Please search for a product first.');
            return;
        }
        
        const { products, quantity, originalCommand } = this.pendingProductSelection;
        
        if (number < 1 || number > products.length) {
            this.speak(`Please select a number between 1 and ${products.length}`);
            return;
        }
        
        const selectedProduct = products[number - 1];
        
        try {
            // Click the product option to select it
            selectedProduct.element.click();
            
            // Wait for the product to be selected
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Set the quantity
            const quantityInput = document.getElementById('quantity');
            if (quantityInput) {
                quantityInput.value = quantity;
                quantityInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            // Add to bill
            const addButton = document.getElementById('addItemBtn');
            if (addButton) {
                addButton.click();
                this.speak(`Added ${quantity} ${selectedProduct.name} to the bill`);
            } else {
                this.speak(`Selected ${selectedProduct.name} but could not add to bill. Please click the add button manually.`);
            }
            
            // Clear pending selection and waiting flag
            this.pendingProductSelection = null;
            this.isWaitingForSelection = false;
            
        } catch (error) {
            console.error('AI Voice Assistant: Error selecting product:', error);
            this.speak('Sorry, there was an error selecting the product. Please try again.');
        }
    }
    
    /**
     * Cancel pending product selection
     */
    cancelProductSelection() {
        if (this.pendingProductSelection) {
            this.speak('Product selection cancelled.');
            this.pendingProductSelection = null;
            this.isWaitingForSelection = false;
        } else {
            this.speak('No product selection to cancel.');
        }
    }
}

// Initialize the AI Voice Assistant
window.AIVoiceAssistant = new AIVoiceAssistant();
