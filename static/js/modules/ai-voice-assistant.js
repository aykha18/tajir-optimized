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
            this.recognition.maxAlternatives = 1;
            
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
                this.isListening = false;
                this.updateUI('error');
                
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
                }
                
                this.showVoiceFeedback(errorMessage);
                this.speak(errorMessage);
            };

            this.recognition.onend = () => {
                console.log('AI Voice Assistant: Stopped listening');
                this.isListening = false;
                this.updateUI('idle');
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
        this.speak('I did not understand that command. Say help for available commands.');
        this.showVoiceFeedback('Command not recognized. Say "help" for available commands.');
    }

    /**
     * Add product to bill
     */
    async addProduct(quantity, productName) {
        try {
            console.log('AI Voice Assistant: Adding product - Quantity:', quantity, 'Name:', productName);
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
            console.error('AI Voice Assistant: Error adding product:', error);
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
