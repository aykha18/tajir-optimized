// Enhanced Expense Management Module

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
        }, 10);
        
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
        this.currentCategory = null;
        this.isEditing = false;
        this.isSubmitting = false;
        this.isSubmittingCategory = false;
        this.statistics = {
            totalExpenses: 0,
            monthExpenses: 0,
            totalCategories: 0,
            avgPerDay: 0,
            totalExpensesLastMonth: 0,
            monthExpensesLastMonth: 0,
            avgPerDayLastWeek: 0
        };
        this.init();
    }

    async init() {
        await this.loadCategories();
        await this.loadExpenses();
        this.setupEventListeners();
        this.renderCategories();
        this.renderExpenses();
        this.updateStatistics();
        this.updateDashboard();
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

        // Close modals when clicking outside
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModals();
                }
            });
        });

        // Close modals with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModals();
            }
        });
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/expense-categories');
            if (response.ok) {
                this.categories = await response.json();
                this.populateCategoryDropdowns();
                this.updateStatistics();
            }
        } catch (error) {
            console.error('Error loading categories:', error);
            showToast('Error loading categories', 'error');
        }
    }

    async loadExpenses() {
        try {
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
                this.renderExpenses();
                this.updateStatistics();
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

        // Also populate the filter dropdown
        const filterSelect = document.getElementById('expenseCategoryFilter');
        if (filterSelect) {
            filterSelect.innerHTML = '<option value="">All Categories</option>';
            this.categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.category_id;
                option.textContent = category.category_name;
                filterSelect.appendChild(option);
            });
        }
    }

    updateStatistics() {
        // Calculate total expenses
        this.statistics.totalExpenses = this.expenses.reduce((sum, expense) => sum + parseFloat(expense.amount), 0);
        
        // Calculate current month expenses
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();
        this.statistics.monthExpenses = this.expenses.filter(expense => {
            const expenseDate = new Date(expense.expense_date);
            return expenseDate.getMonth() === currentMonth && expenseDate.getFullYear() === currentYear;
        }).reduce((sum, expense) => sum + parseFloat(expense.amount), 0);

        // Calculate total categories
        this.statistics.totalCategories = this.categories.length;

        // Calculate average per day (last 30 days)
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const recentExpenses = this.expenses.filter(expense => {
            const expenseDate = new Date(expense.expense_date);
            return expenseDate >= thirtyDaysAgo;
        });
        const totalRecentExpenses = recentExpenses.reduce((sum, expense) => sum + parseFloat(expense.amount), 0);
        this.statistics.avgPerDay = totalRecentExpenses / 30;

        // Update UI
        this.updateStatisticsUI();
    }

    updateStatisticsUI() {
        const totalExpensesEl = document.getElementById('totalExpenses');
        const monthExpensesEl = document.getElementById('monthExpenses');
        const totalCategoriesEl = document.getElementById('totalCategories');
        const avgPerDayEl = document.getElementById('avgPerDay');

        if (totalExpensesEl) {
            totalExpensesEl.textContent = `AED ${this.statistics.totalExpenses.toFixed(2)}`;
        }
        if (monthExpensesEl) {
            monthExpensesEl.textContent = `AED ${this.statistics.monthExpenses.toFixed(2)}`;
        }
        if (totalCategoriesEl) {
            totalCategoriesEl.textContent = this.statistics.totalCategories;
        }
        if (avgPerDayEl) {
            avgPerDayEl.textContent = `AED ${this.statistics.avgPerDay.toFixed(2)}`;
        }
    }

    renderCategories() {
        const container = document.getElementById('categoriesContainer');
        if (!container) return;

        if (this.categories.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="p-4 bg-gradient-to-br from-slate-800/60 to-slate-700/60 backdrop-blur-xl rounded-2xl border border-slate-600/30">
                        <svg data-lucide="folder" class="w-16 h-16 text-slate-400 mx-auto mb-4"></svg>
                        <h3 class="text-lg font-semibold text-white mb-2">No Categories Yet</h3>
                        <p class="text-slate-400 mb-4">Create your first expense category to get started</p>
                        <button onclick="expenseManager.showCategoryModal()" class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-200">
                            <svg data-lucide="plus" class="w-4 h-4 mr-2"></svg>
                            Add Category
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.categories.map(category => {
            const categoryExpenses = this.expenses.filter(expense => expense.category_id === category.category_id);
            const totalAmount = categoryExpenses.reduce((sum, expense) => sum + parseFloat(expense.amount), 0);
            const expenseCount = categoryExpenses.length;

            return `
                <div class="bg-gradient-to-br from-slate-800/80 to-slate-700/80 backdrop-blur-xl rounded-2xl p-6 border border-slate-600/30 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 group">
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex-1">
                            <h3 class="text-lg font-semibold text-white group-hover:text-indigo-300 transition-colors">${category.category_name}</h3>
                            <p class="text-sm text-slate-400 mt-1">${category.description || 'No description'}</p>
                        </div>
                        <div class="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                            <button onclick="expenseManager.editCategory(${category.category_id})" 
                                    class="p-2 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/20 rounded-lg transition-all duration-200">
                                <svg data-lucide="edit" class="w-4 h-4"></svg>
                            </button>
                            <button onclick="expenseManager.deleteCategory(${category.category_id})" 
                                    class="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-lg transition-all duration-200">
                                <svg data-lucide="trash-2" class="w-4 h-4"></svg>
                            </button>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="text-center p-3 bg-slate-700/50 rounded-lg">
                            <p class="text-2xl font-bold text-white">${expenseCount}</p>
                            <p class="text-xs text-slate-400">Expenses</p>
                        </div>
                        <div class="text-center p-3 bg-slate-700/50 rounded-lg">
                            <p class="text-lg font-bold text-white">AED ${totalAmount.toFixed(2)}</p>
                            <p class="text-xs text-slate-400">Total</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderExpenses() {
        const container = document.getElementById('expensesContainer');
        if (!container) return;

        if (this.expenses.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <div class="p-8 bg-gradient-to-br from-slate-800/60 to-slate-700/60 backdrop-blur-xl rounded-2xl border border-slate-600/30">
                        <svg data-lucide="currency" class="w-16 h-16 text-slate-400 mx-auto mb-4"></svg>
                        <h3 class="text-lg font-semibold text-white mb-2">No Expenses Found</h3>
                        <p class="text-slate-400 mb-4">Start tracking your business expenses to see them here</p>
                        <button onclick="expenseManager.showExpenseModal()" class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-200">
                            <svg data-lucide="plus" class="w-4 h-4 mr-2"></svg>
                            Add First Expense
                        </button>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.expenses.map(expense => {
            const date = new Date(expense.expense_date);
            const formattedDate = date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
            const timeAgo = this.getTimeAgo(date);

            return `
                <div class="bg-gradient-to-br from-slate-800/80 to-slate-700/80 backdrop-blur-xl rounded-2xl p-6 border border-slate-600/30 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 group">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="flex items-center space-x-3 mb-3">
                                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-indigo-300 border border-indigo-500/30">
                                    ${expense.category_name}
                                </span>
                                <span class="text-sm text-slate-400">
                                    ${formattedDate}
                                </span>
                                <span class="text-xs text-slate-500">
                                    ${timeAgo}
                                </span>
                            </div>
                            <h3 class="text-xl font-bold text-white mb-2 group-hover:text-indigo-300 transition-colors">
                                AED ${parseFloat(expense.amount).toFixed(2)}
                            </h3>
                            <p class="text-sm text-slate-300 mb-3">
                                ${expense.description || 'No description'}
                            </p>
                            <div class="flex items-center space-x-4 text-xs text-slate-500">
                                <span class="flex items-center">
                                    <svg data-lucide="credit-card" class="w-3 h-3 mr-1"></svg>
                                    ${expense.payment_method}
                                </span>
                                ${expense.receipt_url ? `
                                    <a href="${expense.receipt_url}" target="_blank" class="flex items-center text-indigo-400 hover:text-indigo-300 transition-colors">
                                        <svg data-lucide="file-text" class="w-3 h-3 mr-1"></svg>
                                        Receipt
                                    </a>
                                ` : ''}
                            </div>
                        </div>
                        <div class="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                            <button onclick="expenseManager.editExpense(${expense.expense_id})" 
                                    class="p-2 text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/20 rounded-lg transition-all duration-200">
                                <svg data-lucide="edit" class="w-4 h-4"></svg>
                            </button>
                            <button onclick="expenseManager.deleteExpense(${expense.expense_id})" 
                                    class="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-lg transition-all duration-200">
                                <svg data-lucide="trash-2" class="w-4 h-4"></svg>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
        return `${Math.floor(diffInSeconds / 2592000)}mo ago`;
    }

    showCategoryModal(category = null) {
        this.currentCategory = category;
        this.isEditing = !!category;
        
        const modal = document.getElementById('categoryModal');
        const title = modal.querySelector('.modal-title');
        const form = document.getElementById('categoryForm');
        const nameInput = document.getElementById('categoryName');
        const descInput = document.getElementById('categoryDescription');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        title.textContent = this.isEditing ? 'Edit Category' : 'Add Category';
        submitBtn.textContent = this.isEditing ? 'Update Category' : 'Save Category';
        nameInput.value = category?.category_name || '';
        descInput.value = category?.description || '';
        
        modal.classList.remove('hidden');
        nameInput.focus();
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
        const submitBtn = form.querySelector('button[type="submit"]');
        
        title.textContent = this.isEditing ? 'Edit Expense' : 'Add Expense';
        submitBtn.textContent = this.isEditing ? 'Update Expense' : 'Save Expense';
        dateInput.value = expense?.expense_date || new Date().toISOString().split('T')[0];
        amountInput.value = expense?.amount || '';
        descInput.value = expense?.description || '';
        categorySelect.value = expense?.category_id || '';
        paymentSelect.value = expense?.payment_method || 'Cash';
        receiptInput.value = expense?.receipt_url || '';
        
        modal.classList.remove('hidden');
        categorySelect.focus();
    }

    async handleCategorySubmit(e) {
        e.preventDefault();
        
        if (this.isSubmittingCategory) return;
        
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
                this.updateStatistics();
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
        
        if (this.isSubmitting) return;
        
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
                this.updateStatistics();
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
                this.updateStatistics();
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
                this.updateStatistics();
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
        return;
    }
    
    const container = document.getElementById('expensesContainer');
    if (container && !window.expenseManager) {
        window.expenseManager = new ExpenseManager();
        expenseManagerInitialized = true;
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
        initializeExpenseManager();
    }
};
