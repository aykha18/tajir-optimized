// Expense Management Module

// Define showToast globally if it doesn't already exist
if (typeof window.showToast === 'undefined') {
    window.showToast = function(msg, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg text-white font-medium transform translate-x-full transition-transform duration-300 ${
            type === 'success' ? 'bg-green-600' :
            type === 'error' ? 'bg-red-600' :
            type === 'warning' ? 'bg-yellow-600' :
            'bg-blue-600'
        }`;
        toast.textContent = msg;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
            toast.classList.add('translate-x-0');
        }, 10); // Small delay to allow CSS transition
        
        setTimeout(() => {
            toast.classList.remove('translate-x-0');
            toast.classList.add('translate-x-full');
            toast.addEventListener('transitionend', () => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            });
        }, duration);
    };
}

class ExpenseManager {
    constructor() {
        this.categories = [];
        this.expenses = [];
        this.currentExpense = null;
        this.isEditing = false;
        this.isSubmitting = false;
        this.isSubmittingCategory = false;
        this.init();
    }

    async init() {
        console.log('ExpenseManager: Initializing...');
        await this.loadCategories();
        await this.loadExpenses();
        this.setupEventListeners();
        this.renderCategories();
        this.renderExpenses();
        this.updateDashboard();
        console.log('ExpenseManager: Initialization complete');
    }

    setupEventListeners() {
        // Category management
        document.getElementById('addCategoryBtn')?.addEventListener('click', () => this.showCategoryModal());
        document.getElementById('categoryForm')?.addEventListener('submit', (e) => this.handleCategorySubmit(e));
        
        // Expense management
        document.getElementById('addExpenseBtn')?.addEventListener('click', () => this.showExpenseModal());
        document.getElementById('expenseForm')?.addEventListener('submit', (e) => this.handleExpenseSubmit(e));
        
        // Filters
        document.getElementById('expenseSearch')?.addEventListener('input', (e) => this.filterExpenses(e.target.value));
        document.getElementById('expenseDateFrom')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('expenseDateTo')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('expenseCategoryFilter')?.addEventListener('change', () => this.applyFilters());
        
        // Export
        document.getElementById('exportExpensesBtn')?.addEventListener('click', () => this.exportExpenses());
        
        // Close modals
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => this.closeModals());
        });
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/expense-categories');
            if (response.ok) {
                this.categories = await response.json();
                this.populateCategoryDropdowns();
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            showToast('Error loading categories', 'error');
        }
    }

    async loadExpenses() {
        try {
            console.log('ExpenseManager: Loading expenses...');
            const params = new URLSearchParams();
            const dateFrom = document.getElementById('expenseDateFrom')?.value;
            const dateTo = document.getElementById('expenseDateTo')?.value;
            const categoryId = document.getElementById('expenseCategoryFilter')?.value;
            const search = document.getElementById('expenseSearch')?.value;

            if (dateFrom) params.append('start_date', dateFrom);
            if (dateTo) params.append('end_date', dateTo);
            if (categoryId) params.append('category_id', categoryId);
            if (search) params.append('search', search);

            const response = await fetch(`/api/expenses?${params}`);
            if (response.ok) {
                this.expenses = await response.json();
                console.log('ExpenseManager: Loaded', this.expenses.length, 'expenses');
                this.renderExpenses();
            } else {
                console.error('ExpenseManager: Failed to load expenses, status:', response.status);
            }
        } catch (error) {
            console.error('Error loading expenses:', error);
            showToast('Error loading expenses', 'error');
        }
    }

    // Public method to refresh expenses (can be called from console for debugging)
    async refreshExpenses() {
        console.log('ExpenseManager: Manual refresh requested');
        await this.loadExpenses();
    }

    populateCategoryDropdowns() {
        const categorySelects = document.querySelectorAll('.expense-category-select');
        categorySelects.forEach(select => {
            select.innerHTML = '<option value="">Select Category</option>';
            this.categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.category_id;
                option.textContent = category.category_name;
                select.appendChild(option);
            });
        });
    }

    renderCategories() {
        const container = document.getElementById('categoriesContainer');
        if (!container) return;

        container.innerHTML = this.categories.map(category => `
            <div class="bg-neutral-800/60 backdrop-blur rounded-lg p-4 shadow-sm border border-neutral-700 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg font-semibold text-white">${category.category_name}</h3>
                        <p class="text-sm text-neutral-400 mt-1">${category.description || 'No description'}</p>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="expenseManager.editCategory(${category.category_id})" 
                                class="text-indigo-400 hover:text-indigo-300 transition">
                            <svg data-lucide="edit" class="w-4 h-4"></svg>
                        </button>
                        <button onclick="expenseManager.deleteCategory(${category.category_id})" 
                                class="text-red-400 hover:text-red-300 transition">
                            <svg data-lucide="trash-2" class="w-4 h-4"></svg>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderExpenses() {
        const container = document.getElementById('expensesContainer');
        if (!container) return;

        if (this.expenses.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <svg data-lucide="currency" class="w-12 h-12 text-neutral-400 mx-auto mb-4"></svg>
                    <p class="text-neutral-400">No expenses found</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.expenses.map(expense => `
            <div class="bg-neutral-800/60 backdrop-blur rounded-lg p-4 shadow-sm border border-neutral-700 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center space-x-3">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-900 text-indigo-200">
                                ${expense.category_name}
                            </span>
                            <span class="text-sm text-neutral-400">
                                ${new Date(expense.expense_date).toLocaleDateString()}
                            </span>
                        </div>
                        <h3 class="text-lg font-semibold text-white mt-2">
                            AED ${parseFloat(expense.amount).toFixed(2)}
                        </h3>
                        <p class="text-sm text-neutral-400 mt-1">
                            ${expense.description || 'No description'}
                        </p>
                        <div class="flex items-center space-x-4 mt-2 text-xs text-neutral-500">
                            <span><svg data-lucide="credit-card" class="w-3 h-3 mr-1"></svg>${expense.payment_method}</span>
                            ${expense.receipt_url ? `<a href="${expense.receipt_url}" target="_blank" class="text-indigo-400 hover:text-indigo-300 transition"><svg data-lucide="file-text" class="w-3 h-3 mr-1"></svg>Receipt</a>` : ''}
                        </div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="expenseManager.editExpense(${expense.expense_id})" 
                                class="text-indigo-400 hover:text-indigo-300 transition">
                            <svg data-lucide="edit" class="w-4 h-4"></svg>
                        </button>
                        <button onclick="expenseManager.deleteExpense(${expense.expense_id})" 
                                class="text-red-400 hover:text-red-300 transition">
                            <svg data-lucide="trash-2" class="w-4 h-4"></svg>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    showCategoryModal(category = null) {
        this.currentCategory = category;
        this.isEditing = !!category;
        
        const modal = document.getElementById('categoryModal');
        const title = modal.querySelector('.modal-title');
        const form = document.getElementById('categoryForm');
        const nameInput = document.getElementById('categoryName');
        const descInput = document.getElementById('categoryDescription');
        
        title.textContent = this.isEditing ? 'Edit Category' : 'Add Category';
        nameInput.value = category?.category_name || '';
        descInput.value = category?.description || '';
        
        modal.classList.remove('hidden');
    }

    showExpenseModal(expense = null) {
        this.currentExpense = expense;
        this.isEditing = !!expense;
        
        const modal = document.getElementById('expenseModal');
        const title = modal.querySelector('.modal-title');
        const form = document.getElementById('expenseForm');
        const dateInput = document.getElementById('expenseDate');
        const amountInput = document.getElementById('expenseAmount');
        const descInput = document.getElementById('expenseDescription');
        const categorySelect = document.getElementById('expenseCategory');
        const paymentSelect = document.getElementById('expensePaymentMethod');
        const receiptInput = document.getElementById('expenseReceiptUrl');
        
        title.textContent = this.isEditing ? 'Edit Expense' : 'Add Expense';
        dateInput.value = expense?.expense_date || new Date().toISOString().split('T')[0];
        amountInput.value = expense?.amount || '';
        descInput.value = expense?.description || '';
        categorySelect.value = expense?.category_id || '';
        paymentSelect.value = expense?.payment_method || 'Cash';
        receiptInput.value = expense?.receipt_url || '';
        
        modal.classList.remove('hidden');
    }

    async handleCategorySubmit(e) {
        e.preventDefault();
        
        // Prevent duplicate submissions
        if (this.isSubmittingCategory) {
            console.log('Category form submission already in progress, ignoring duplicate');
            return;
        }
        
        this.isSubmittingCategory = true;
        const submitButton = e.target.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Saving...';
        submitButton.disabled = true;
        
        try {
            const formData = new FormData(e.target);
            const data = {
                category_name: formData.get('category_name').trim(),
                description: formData.get('description').trim()
            };
            
            if (!data.category_name) {
                showToast('Category name is required', 'error');
                return;
            }
            
            const url = this.isEditing ? `/api/expense-categories/${this.currentCategory.category_id}` : '/api/expense-categories';
            const method = this.isEditing ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showToast(this.isEditing ? 'Category updated successfully' : 'Category added successfully', 'success');
                this.closeModals();
                await this.loadCategories();
                this.renderCategories();
            } else {
                const error = await response.json();
                showToast(error.error || 'Failed to save category', 'error');
            }
        } catch (error) {
            console.error('Error saving category:', error);
            showToast('Error saving category', 'error');
        } finally {
            this.isSubmittingCategory = false;
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    }

    async handleExpenseSubmit(e) {
        e.preventDefault();
        
        // Prevent duplicate submissions
        if (this.isSubmitting) {
            console.log('Form submission already in progress, ignoring duplicate');
            return;
        }
        
        this.isSubmitting = true;
        const submitButton = e.target.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Saving...';
        submitButton.disabled = true;
        
        try {
            const formData = new FormData(e.target);
            const data = {
                category_id: formData.get('category_id'),
                expense_date: formData.get('expense_date'),
                amount: formData.get('amount'),
                description: formData.get('description').trim(),
                payment_method: formData.get('payment_method'),
                receipt_url: formData.get('receipt_url').trim()
            };
            
            if (!data.category_id || !data.expense_date || !data.amount) {
                showToast('Category, date, and amount are required', 'error');
                return;
            }
            
            const url = this.isEditing ? `/api/expenses/${this.currentExpense.expense_id}` : '/api/expenses';
            const method = this.isEditing ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showToast(this.isEditing ? 'Expense updated successfully' : 'Expense added successfully', 'success');
                this.closeModals();
                await this.loadExpenses();
                this.updateDashboard();
            } else {
                const error = await response.json();
                showToast(error.error || 'Failed to save expense', 'error');
            }
        } catch (error) {
            console.error('Error saving expense:', error);
            showToast('Error saving expense', 'error');
        } finally {
            this.isSubmitting = false;
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
    }

    async editCategory(categoryId) {
        const category = this.categories.find(c => c.category_id === categoryId);
        if (category) {
            this.showCategoryModal(category);
        }
    }

    async deleteCategory(categoryId) {
        if (!confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/expense-categories/${categoryId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showToast('Category deleted successfully', 'success');
                await this.loadCategories();
                this.renderCategories();
            } else {
                const error = await response.json();
                showToast(error.error || 'Failed to delete category', 'error');
            }
        } catch (error) {
            console.error('Error deleting category:', error);
            showToast('Error deleting category', 'error');
        }
    }

    async editExpense(expenseId) {
        const expense = this.expenses.find(e => e.expense_id === expenseId);
        if (expense) {
            this.showExpenseModal(expense);
        }
    }

    async deleteExpense(expenseId) {
        if (!confirm('Are you sure you want to delete this expense? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/expenses/${expenseId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showToast('Expense deleted successfully', 'success');
                await this.loadExpenses();
                this.updateDashboard();
            } else {
                const error = await response.json();
                showToast(error.error || 'Failed to delete expense', 'error');
            }
        } catch (error) {
            console.error('Error deleting expense:', error);
            showToast('Error deleting expense', 'error');
        }
    }

    filterExpenses(search) {
        this.applyFilters();
    }

    applyFilters() {
        this.loadExpenses();
    }

    async exportExpenses() {
        try {
            const params = new URLSearchParams();
            const dateFrom = document.getElementById('expenseDateFrom')?.value;
            const dateTo = document.getElementById('expenseDateTo')?.value;
            const categoryId = document.getElementById('expenseCategoryFilter')?.value;

            if (dateFrom) params.append('start_date', dateFrom);
            if (dateTo) params.append('end_date', dateTo);
            if (categoryId) params.append('category_id', categoryId);

            const response = await fetch(`/api/expenses/download?${params}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'expenses.csv';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showToast('Expenses exported successfully', 'success');
            }
        } catch (error) {
            console.error('Error exporting expenses:', error);
            showToast('Error exporting expenses', 'error');
        }
    }

    closeModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
        this.currentCategory = null;
        this.currentExpense = null;
        this.isEditing = false;
    }

    async updateDashboard() {
        try {
            const response = await fetch('/api/dashboard');
            if (response.ok) {
                const data = await response.json();
                this.updateDashboardCards(data);
            }
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    updateDashboardCards(data) {
        // Update expense-related dashboard cards if they exist
        const todayExpensesCard = document.getElementById('todayExpensesCard');
        const monthExpensesCard = document.getElementById('monthExpensesCard');
        
        if (todayExpensesCard) {
            todayExpensesCard.querySelector('.card-value').textContent = `AED ${data.total_expenses_today.toFixed(2)}`;
        }
        
        if (monthExpensesCard) {
            monthExpensesCard.querySelector('.card-value').textContent = `AED ${data.total_expenses_month.toFixed(2)}`;
        }
    }
}

// SIMPLE SINGLE INSTANCE INITIALIZATION
let expenseManagerInitialized = false;

function initializeExpenseManager() {
    // Only initialize once
    if (expenseManagerInitialized) {
        console.log('ExpenseManager already initialized, skipping...');
        return;
    }
    
    const container = document.getElementById('expensesContainer');
    if (container && !window.expenseManager) {
        console.log('Initializing ExpenseManager...');
        window.expenseManager = new ExpenseManager();
        expenseManagerInitialized = true;
        console.log('ExpenseManager initialized successfully');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeExpenseManager);
} else {
    initializeExpenseManager();
}

// Global function for manual refresh (for debugging)
window.refreshExpenses = function() {
    if (window.expenseManager) {
        window.expenseManager.refreshExpenses();
    } else {
        console.log('ExpenseManager not initialized, initializing now...');
        initializeExpenseManager();
    }
};
