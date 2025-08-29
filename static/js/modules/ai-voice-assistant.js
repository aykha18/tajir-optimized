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
        this.isWaitingForSelection = false; // New flag for product selection mode
        
        console.log('AI Voice Assistant: Initializing...');
        this.initializeSpeechRecognition();
        this.setupVoiceCommands();
        console.log('AI Voice Assistant: Initialized successfully');
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
            
            console.log('AI Voice Assistant: Speech recognition configured');
            
            // Event handlers
            this.recognition.onstart = () => {
                console.log('AI Voice Assistant: Started listening');
                this.isListening = true;
                this.updateUI('listening');
                this.showVoiceFeedback('Listening for your command...');
            };

            this.recognition.onresult = (event) => {
                const result = event.results[0];
                const command = result[0].transcript.toLowerCase().trim();
                const confidence = result[0].confidence;
                
                console.log('AI Voice Assistant: Command received:', command, 'Confidence:', confidence);
                this.showVoiceFeedback(`Heard: "${command}"`);
                
                // Process command after a short delay to show what was heard
                setTimeout(() => {
                    this.processCommand(command);
                }, 500);
            };

                         this.recognition.onerror = (event) => {
                 console.error('AI Voice Assistant: Speech recognition error:', event.error);
                 console.error('AI Voice Assistant: Error details:', event);
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
                         console.log('AI Voice Assistant: Recognition aborted - this is normal when stopping');
                         return; // Don't show error for normal aborts
                     default:
                         errorMessage = `Speech recognition error: ${event.error}`;
                 }
                 
                 this.showVoiceFeedback(errorMessage);
                 this.speak(errorMessage);
                 
                 // If we're waiting for selection, try to restart after error
                 if (this.isWaitingForSelection && this.pendingProductSelection) {
                     setTimeout(() => {
                         console.log('AI Voice Assistant: Restarting listening after error...');
                         this.startListening();
                     }, 1000);
                 } else {
                     this.updateUI('error');
                 }
             };

                         this.recognition.onend = () => {
                 console.log('AI Voice Assistant: Stopped listening');
                 this.isListening = false;
                 
                 // If we're waiting for product selection, continue listening
                 if (this.isWaitingForSelection && this.pendingProductSelection) {
                     console.log('AI Voice Assistant: Continuing to listen for product selection...');
                     setTimeout(() => {
                         this.startListening();
                     }, 500); // Increased delay to prevent rapid restarts
                 } else {
                     this.updateUI('idle');
                 }
             };

            console.log('AI Voice Assistant: Speech recognition initialized successfully');
            
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
                handler: (matches) => this.addProduct(1, matches[1]) // Default to quantity 1
            },
            'add product': {
                pattern: /add\s+product\s+(\d+)\s+(.+)/i,
                handler: (matches) => this.addProduct(matches[1], matches[2])
            },
            'add product without quantity': {
                pattern: /add\s+product\s+(.+)/i,
                handler: (matches) => this.addProduct(1, matches[1]) // Default to quantity 1
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
        
        console.log('AI Voice Assistant: Voice commands configured');
    }

    /**
     * Process voice command
     */
    processCommand(command) {
        console.log('AI Voice Assistant: Processing command:', command);
        this.addToHistory(command);
        
        // Check each command pattern
        for (const [cmdName, cmd] of Object.entries(this.commands)) {
            const matches = command.match(cmd.pattern);
            if (matches) {
                console.log('AI Voice Assistant: Matched command:', cmdName, 'with matches:', matches);
                try {
                    cmd.handler(matches);
                    return;
                } catch (error) {
                    console.error('AI Voice Assistant: Error executing command:', error);
                    this.speak('Sorry, there was an error executing that command');
                }
            }
        }
        
        // No matching command found
        console.log('AI Voice Assistant: No matching command found for:', command);
        
        // Special handling for pending product selection
        if (this.pendingProductSelection) {
            console.log('AI Voice Assistant: Checking if command is a number for product selection...');
            const numberMatch = command.match(/^(\d+)$/);
            if (numberMatch) {
                const number = parseInt(numberMatch[1]);
                console.log('AI Voice Assistant: Found number for product selection:', number);
                this.selectProductByNumber(number);
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
            console.log('AI Voice Assistant: Adding product - Quantity:', quantity, 'Name:', productName);
            console.log('AI Voice Assistant: Starting product search...');
            
            // Get the billing system's product input and trigger search
            const productInput = document.getElementById('productInput') || document.querySelector('input[placeholder*="product" i]');
            console.log('AI Voice Assistant: Looking for product input field:', productInput);
            if (!productInput) {
                console.log('AI Voice Assistant: Product input field not found. Available inputs:');
                const allInputs = document.querySelectorAll('input');
                allInputs.forEach((input, index) => {
                    console.log(`${index}: ${input.id} - ${input.placeholder} - ${input.value}`);
                });
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
            
            console.log('AI Voice Assistant: Looking for product dropdown:', productDropdown);
            if (productDropdown) {
                // Find all product options that match our search
                const productOptions = productDropdown.querySelectorAll('.product-option-mobile');
                console.log('AI Voice Assistant: Found product options:', productOptions.length);
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
                    console.log('AI Voice Assistant: Auto-selecting single product:', selectedProduct.name);
                    
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
                    console.log('AI Voice Assistant: Looking for addItemBtn button:', addButton);
                    if (addButton) {
                        console.log('AI Voice Assistant: Found addItemBtn, clicking it...');
                        addButton.click();
                        console.log('AI Voice Assistant: Button clicked successfully');
                        this.speak(`Added ${quantity} ${selectedProduct.name} to the bill`);
                    } else {
                        console.log('AI Voice Assistant: addItemBtn not found. Available buttons:');
                        const allButtons = document.querySelectorAll('button');
                        allButtons.forEach((btn, index) => {
                            console.log(`${index}: ${btn.id} - ${btn.textContent}`);
                        });
                        this.speak(`Selected ${selectedProduct.name} but could not add to bill. Please click the add button manually.`);
                    }
                } else {
                    // Multiple products found - ask user to choose
                    this.speak(`Found ${matchingProducts.length} products. Please say which one you want.`);
                    
                    // List the options
                    matchingProducts.forEach((product, index) => {
                        console.log(`${index + 1}. ${product.name} - ${product.price} AED`);
                    });
                    
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
                         console.log('AI Voice Assistant: Starting continuous listening for product selection...');
                         this.startListening();
                     }, 2000);
                }
            } else {
                this.speak('Product dropdown not found. Please make sure you are on the billing page.');
            }
            
        } catch (error) {
            console.error('AI Voice Assistant: Error adding product:', error);
            console.error('AI Voice Assistant: Error stack:', error.stack);
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
            console.log('AI Voice Assistant: Finding customer - Query:', query);
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
                customers.forEach(customer => {
                    console.log(`- ${customer.name} (${customer.phone}) from ${customer.city}`);
                });
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
     * Get price for product
     */
    async getPrice(productName) {
        try {
            console.log('AI Voice Assistant: Getting price - Name:', productName);
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
        console.log('AI Voice Assistant: Creating bill');
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
        console.log('AI Voice Assistant: Printing bill');
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
        console.log('AI Voice Assistant: Clearing bill');
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
        console.log('AI Voice Assistant: Showing help');
        const helpText = `
            I can help you with billing. Here are some commands you can use:
            
            Add products: 
            - "Add 2 shirts" (with quantity)
            - "Add product blouse padded" (quantity defaults to 1)
            - "Add trouser" (quantity defaults to 1)
            
            Find customers: "Find customer Ahmed" or "Search customer 0501234567"
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
        console.log('AI Voice Assistant: Toggle called, isListening:', this.isListening);
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    /**
     * Test method to verify the voice assistant is working
     */
    test() {
        console.log('AI Voice Assistant: Test method called');
        this.speak('Voice assistant is working. You can now try voice commands.');
        this.showVoiceFeedback('Voice assistant is working. Try saying "help" for available commands.');
        
        // Test command processing
        setTimeout(() => {
            this.processCommand('help');
        }, 2000);
    }

         /**
      * Manual command processing for testing
      */
     testCommand(command) {
         console.log('AI Voice Assistant: Testing command:', command);
         this.processCommand(command.toLowerCase());
     }
     
     /**
      * Test speech recognition specifically
      */
     testSpeechRecognition() {
         console.log('AI Voice Assistant: Testing speech recognition...');
         console.log('AI Voice Assistant: Recognition object:', this.recognition);
         console.log('AI Voice Assistant: Is listening:', this.isListening);
         console.log('AI Voice Assistant: Is waiting for selection:', this.isWaitingForSelection);
         
         if (this.recognition) {
             console.log('AI Voice Assistant: Starting test recognition...');
             this.startListening();
         } else {
             console.error('AI Voice Assistant: No recognition object available');
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
        console.log('AI Voice Assistant: User selected product:', selectedProduct.name);
        
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
            console.log('AI Voice Assistant: Looking for addItemBtn button:', addButton);
            if (addButton) {
                console.log('AI Voice Assistant: Found addItemBtn, clicking it...');
                addButton.click();
                console.log('AI Voice Assistant: Button clicked successfully');
                this.speak(`Added ${quantity} ${selectedProduct.name} to the bill`);
            } else {
                console.log('AI Voice Assistant: addItemBtn not found. Available buttons:');
                const allButtons = document.querySelectorAll('button');
                allButtons.forEach((btn, index) => {
                    console.log(`${index}: ${btn.id} - ${btn.textContent}`);
                });
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

// Add test methods to window for debugging
window.testVoiceAssistant = () => {
    if (window.AIVoiceAssistant) {
        window.AIVoiceAssistant.test();
    } else {
        console.error('AI Voice Assistant not initialized');
    }
};

window.testVoiceCommand = (command) => {
    if (window.AIVoiceAssistant) {
        window.AIVoiceAssistant.testCommand(command);
    } else {
        console.error('AI Voice Assistant not initialized');
    }
};

// Add a simple test button to the page for debugging
document.addEventListener('DOMContentLoaded', function() {
    // Create a test button
    const testButton = document.createElement('button');
    testButton.textContent = '🔧 Test Voice Assistant';
    testButton.style.cssText = `
        position: fixed;
        top: 10px;
        left: 10px;
        background: #ff6b6b;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        cursor: pointer;
        z-index: 10000;
        font-size: 12px;
    `;
    testButton.onclick = () => {
        console.log('=== VOICE ASSISTANT DEBUG ===');
        console.log('1. Testing basic functionality...');
        
        if (window.AIVoiceAssistant) {
            console.log('✅ Voice Assistant is initialized');
            console.log('2. Testing speech synthesis...');
            window.AIVoiceAssistant.speak('Testing voice assistant. Can you hear this?');
            
            console.log('3. Testing command processing...');
            window.AIVoiceAssistant.testCommand('help');
            
            console.log('4. Testing speech recognition...');
            if (window.AIVoiceAssistant.recognition) {
                console.log('✅ Speech recognition is available');
                console.log('5. Starting listening test...');
                window.AIVoiceAssistant.startListening();
            } else {
                console.log('❌ Speech recognition not available');
                alert('Speech recognition not supported in this browser. Try Chrome or Edge.');
            }
        } else {
            console.log('❌ Voice Assistant not initialized');
            alert('Voice Assistant failed to initialize. Check console for errors.');
        }
    };
    
    document.body.appendChild(testButton);
    
    // Also add a manual command input
    const commandInput = document.createElement('input');
    commandInput.placeholder = 'Type a command to test (e.g., help)';
    commandInput.style.cssText = `
        position: fixed;
        top: 50px;
        left: 10px;
        width: 200px;
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 3px;
        z-index: 10000;
        font-size: 12px;
    `;
    commandInput.onkeypress = (e) => {
        if (e.key === 'Enter') {
            const command = commandInput.value;
            console.log('Testing command:', command);
            window.testVoiceCommand(command);
            commandInput.value = '';
        }
    };
    
    document.body.appendChild(commandInput);
});
