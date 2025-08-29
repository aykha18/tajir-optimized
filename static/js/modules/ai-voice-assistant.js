/**
 * AI Voice Assistant for Billing
 * Handles voice commands for product selection, customer search, price queries, and bill generation
 */
class AIVoiceAssistant {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.currentContext = 'billing'; // billing, customer-search, product-search
        this.commandHistory = [];
        this.maxHistorySize = 10;
        
        this.initializeSpeechRecognition();
        this.setupVoiceCommands();
    }

    /**
     * Initialize speech recognition
     */
    initializeSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported in this browser');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US'; // Can be changed to 'ar-SA' for Arabic
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI('listening');
            this.speak('Listening for your command');
        };

        this.recognition.onresult = (event) => {
            const command = event.results[0][0].transcript.toLowerCase();
            console.log('Voice command received:', command);
            this.processCommand(command);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateUI('error');
            this.speak('Sorry, I did not understand that. Please try again.');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUI('idle');
        };
    }

    /**
     * Setup voice command patterns and handlers
     */
    setupVoiceCommands() {
        this.commands = {
            // Product commands
            'add': {
                pattern: /add\s+(\d+)\s+(.+)/i,
                handler: (matches) => this.addProduct(matches[1], matches[2])
            },
            'add product': {
                pattern: /add\s+product\s+(\d+)\s+(.+)/i,
                handler: (matches) => this.addProduct(matches[1], matches[2])
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
                    console.error('Error executing command:', error);
                    this.speak('Sorry, there was an error executing that command');
                }
            }
        }
        
        // No matching command found
        this.speak('I did not understand that command. Say help for available commands.');
    }

    /**
     * Add product to bill
     */
    async addProduct(quantity, productName) {
        try {
            // Search for product
            const products = await this.searchProducts(productName);
            
            if (products.length === 0) {
                this.speak(`No product found matching ${productName}`);
                return;
            }
            
            if (products.length === 1) {
                const product = products[0];
                this.addProductToBill(product, parseInt(quantity));
                this.speak(`Added ${quantity} ${product.product_name} at ${product.rate} AED`);
            } else {
                // Multiple products found, ask user to choose
                this.speak(`Found ${products.length} products. Please be more specific or say the exact product name.`);
                products.forEach(product => {
                    console.log(`- ${product.product_name} (${product.rate} AED)`);
                });
            }
        } catch (error) {
            console.error('Error adding product:', error);
            this.speak('Sorry, there was an error adding the product');
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
            console.error('Error searching products:', error);
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
            console.error('Error finding customer:', error);
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
            console.error('Error getting price:', error);
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
            
            Add products: "Add 2 shirts" or "Add product 1 trouser"
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
            console.error('Error starting speech recognition:', error);
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
}

// Initialize the AI Voice Assistant
window.AIVoiceAssistant = new AIVoiceAssistant();
