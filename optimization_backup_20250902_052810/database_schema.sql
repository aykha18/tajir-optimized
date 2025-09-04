-- Tailor POS Database Schema - Multi-Tenant Version
-- Database: pos_tailor

-- Users Table (Main tenant table)
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    mobile TEXT UNIQUE,
    shop_code TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    shop_name TEXT NOT NULL,
    shop_type TEXT,
    contact_number TEXT,
    email_address TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Plans Table (for pricing plan management)
CREATE TABLE IF NOT EXISTS user_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_type TEXT NOT NULL DEFAULT 'trial' CHECK (plan_type IN ('trial', 'basic', 'pro')),
    plan_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    plan_end_date DATE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Shop Settings Table
CREATE TABLE IF NOT EXISTS shop_settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    shop_name TEXT DEFAULT 'Tajir',
    address TEXT DEFAULT '',
    trn TEXT DEFAULT '',
    logo_url TEXT DEFAULT '',
    shop_mobile TEXT DEFAULT '',
    working_hours TEXT DEFAULT '',
    invoice_static_info TEXT DEFAULT '',
    use_dynamic_invoice_template BOOLEAN DEFAULT 0,
    payment_mode TEXT DEFAULT 'advance' CHECK (payment_mode IN ('advance', 'full')),
    -- Configurable Input Fields
    enable_trial_date BOOLEAN DEFAULT 1,
    enable_delivery_date BOOLEAN DEFAULT 1,
    enable_advance_payment BOOLEAN DEFAULT 1,
    enable_customer_notes BOOLEAN DEFAULT 1,
    enable_employee_assignment BOOLEAN DEFAULT 1,
    default_delivery_days INTEGER DEFAULT 3,
    default_trial_days INTEGER DEFAULT 3,
    default_employee_id INTEGER,
    city TEXT DEFAULT '',
    area TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- OTP Codes Table
CREATE TABLE IF NOT EXISTS otp_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mobile TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    is_used BOOLEAN DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Types Table (per tenant)
CREATE TABLE IF NOT EXISTS product_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(user_id, type_name)
);

-- Products Table (per tenant)
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    barcode TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (type_id) REFERENCES product_types(type_id)
);

-- Customers Table (per tenant)
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    city TEXT,
    area TEXT,
    email TEXT,
    address TEXT,
    trn TEXT,
    customer_type TEXT DEFAULT 'Individual' CHECK (customer_type IN ('Individual', 'Business')),
    business_name TEXT,
    business_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- VAT Rates Table (per tenant)
CREATE TABLE IF NOT EXISTS vat_rates (
    vat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    rate_percentage DECIMAL(5,2) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Employees Table (per tenant)
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    email TEXT,
    position TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Bills Table (per tenant)
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bill_number TEXT,
    customer_id INTEGER,
    customer_name TEXT,
    customer_phone TEXT,
    customer_city TEXT,
    customer_area TEXT,
    customer_trn TEXT,
    uuid TEXT,
    bill_date DATE NOT NULL,
    delivery_date DATE,
    payment_method TEXT DEFAULT 'Cash',
    subtotal DECIMAL(10,2) DEFAULT 0,
    vat_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    advance_paid DECIMAL(10,2) DEFAULT 0,
    balance_amount DECIMAL(10,2) DEFAULT 0,
    status TEXT DEFAULT 'Pending',
    master_id INTEGER,
    trial_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (master_id) REFERENCES employees(employee_id),
    UNIQUE(user_id, bill_number)
);

-- Bill Items Table (per tenant)
CREATE TABLE IF NOT EXISTS bill_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bill_id INTEGER NOT NULL,
    product_id INTEGER,
    product_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    rate DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    vat_amount DECIMAL(10,2) DEFAULT 0,
    advance_paid DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Cities Table (shared across all tenants)
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL UNIQUE
);

-- City Areas Table (shared across all tenants)
CREATE TABLE IF NOT EXISTS city_area (
    area_id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_name TEXT NOT NULL,
    city_id INTEGER,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Insert default cities
INSERT OR IGNORE INTO cities (city_name) VALUES
('Abu Dhabi'),
('Ajman'),
('Dubai'),
('Fujairah'),
('Ras Al Khaimah'),
('Sharjah'),
('Umm Al Quwain');

delete from city_area where area_id not IN
(select MAX(area_id) from city_area group by area_name);
-- Insert Dubai Areas (DUBAI_AREAS)
INSERT OR IGNORE INTO city_area (area_name, city_id) VALUES
('Al Barsha', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Al Karama', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Al Nahda', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Al Qusais', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Bur Dubai', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Business Bay', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Deira', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Discovery Gardens', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Downtown Dubai', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Dubai Marina', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('International City', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Jumeirah', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Jumeirah Lake Towers', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Jumeirah Village Circle', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Mirdif', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Palm Jumeirah', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Satwa', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Silicon Oasis', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Tecom', (SELECT city_id FROM cities WHERE city_name = 'Dubai')),
('Umm Suqeim', (SELECT city_id FROM cities WHERE city_name = 'Dubai'));

-- Insert Abu Dhabi Areas (ABU_DHABI_AREAS)
INSERT OR IGNORE INTO city_area (area_name, city_id) VALUES
('Al Khalidiyah', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Al Reem Island', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Khalifa City', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Mohammed Bin Zayed City', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Mussafah', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Al Mushrif', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Al Bateen', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Al Raha Beach', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Al Shamkha', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Saadiyat Island', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi')),
('Yas Island', (SELECT city_id FROM cities WHERE city_name = 'Abu Dhabi'));

-- Insert Sharjah Areas (SHARJAH_AREAS)
INSERT OR IGNORE INTO city_area (area_name, city_id) VALUES
('Al Nahda', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Taawun', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Majaz', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Qasimia', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Khan', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Rolla', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Muweilah', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Nabba', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Yarmook', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Jazzat', (SELECT city_id FROM cities WHERE city_name = 'Sharjah')),
('Al Ghubaiba', (SELECT city_id FROM cities WHERE city_name = 'Sharjah'));

-- Insert Ajman Areas (AJMAN_AREAS)
INSERT OR IGNORE INTO city_area (area_name, city_id) VALUES
('Al Nuaimia', (SELECT city_id FROM cities WHERE city_name = 'Ajman')),
('Al Rashidiya', (SELECT city_id FROM cities WHERE city_name = 'Ajman')),
('Al Jurf', (SELECT city_id FROM cities WHERE city_name = 'Ajman')),
('Al Mowaihat', (SELECT city_id FROM cities WHERE city_name = 'Ajman')),
('Ajman Industrial Area', (SELECT city_id FROM cities WHERE city_name = 'Ajman')),
('Al Hamidiya', (SELECT city_id FROM cities WHERE city_name = 'Ajman')),
('Al Rawda', (SELECT city_id FROM cities WHERE city_name = 'Ajman')),
('Al Bustan', (SELECT city_id FROM cities WHERE city_name = 'Ajman'));

-- Insert Ras Al Khaimah Areas (RAK_AREAS)
INSERT OR IGNORE INTO city_area (area_name, city_id) VALUES
('Al Nakheel', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah')),
('Al Dhait', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah')),
('Al Hamra Village', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah')),
('Mina Al Arab', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah')),
('Julfar', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah')),
('Al Qurm', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah')),
('Al Mamourah', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah')),
('Al Rams', (SELECT city_id FROM cities WHERE city_name = 'Ras Al Khaimah'));

-- Insert Fujairah Areas (FUJAIRAH_AREAS)
INSERT OR IGNORE INTO city_area (area_name, city_id) VALUES
('Al Faseel', (SELECT city_id FROM cities WHERE city_name = 'Fujairah')),
('Al Ittihad', (SELECT city_id FROM cities WHERE city_name = 'Fujairah')),
('Sakamkam', (SELECT city_id FROM cities WHERE city_name = 'Fujairah')),
('Murbah', (SELECT city_id FROM cities WHERE city_name = 'Fujairah')),
('Al Gurfa', (SELECT city_id FROM cities WHERE city_name = 'Fujairah')),
('Al Hayl', (SELECT city_id FROM cities WHERE city_name = 'Fujairah'));

-- Insert Umm Al Quwain Areas (UAQ_AREAS)
INSERT OR IGNORE INTO city_area (area_name, city_id) VALUES
('Al Maidan', (SELECT city_id FROM cities WHERE city_name = 'Umm Al Quwain')),
('Al Raas', (SELECT city_id FROM cities WHERE city_name = 'Umm Al Quwain')),
('Al Salamah', (SELECT city_id FROM cities WHERE city_name = 'Umm Al Quwain')),
('Al Haditha', (SELECT city_id FROM cities WHERE city_name = 'Umm Al Quwain')),
('Al Ramlah', (SELECT city_id FROM cities WHERE city_name = 'Umm Al Quwain')),
('Al Hawiyah', (SELECT city_id FROM cities WHERE city_name = 'Umm Al Quwain'));

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);
CREATE INDEX IF NOT EXISTS idx_products_type_id ON products(type_id);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_customer_id ON bills(customer_id);
CREATE INDEX IF NOT EXISTS idx_bills_bill_date ON bills(bill_date);
CREATE INDEX IF NOT EXISTS idx_bill_items_user_id ON bill_items(user_id);
CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id);
CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_product_types_user_id ON product_types(user_id);
CREATE INDEX IF NOT EXISTS idx_vat_rates_user_id ON vat_rates(user_id);
CREATE INDEX IF NOT EXISTS idx_employees_user_id ON employees(user_id);
CREATE INDEX IF NOT EXISTS idx_user_plans_user_id ON user_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_shop_settings_user_id ON shop_settings(user_id);

-- Performance Optimization Indexes (NEW)
-- Composite indexes for multi-column queries
CREATE INDEX IF NOT EXISTS idx_products_user_active ON products(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_products_user_type_active ON products(user_id, type_id, is_active);
CREATE INDEX IF NOT EXISTS idx_customers_user_active ON customers(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_customers_user_type ON customers(user_id, customer_type);
CREATE INDEX IF NOT EXISTS idx_bills_user_status ON bills(user_id, status);
CREATE INDEX IF NOT EXISTS idx_bills_user_date_status ON bills(user_id, bill_date, status);
CREATE INDEX IF NOT EXISTS idx_bill_items_user_bill ON bill_items(user_id, bill_id);
CREATE INDEX IF NOT EXISTS idx_bill_items_user_product ON bill_items(user_id, product_id);

-- Text search indexes for customer search optimization
CREATE INDEX IF NOT EXISTS idx_customers_name_search ON customers(user_id, name);
CREATE INDEX IF NOT EXISTS idx_customers_business_search ON customers(user_id, business_name);
CREATE INDEX IF NOT EXISTS idx_customers_phone_search ON customers(user_id, phone);
CREATE INDEX IF NOT EXISTS idx_customers_trn_search ON customers(user_id, trn);

-- Date-based indexes for analytics and reporting
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_bills_delivery_date ON bills(user_id, delivery_date);
CREATE INDEX IF NOT EXISTS idx_bills_trial_date ON bills(user_id, trial_date);
CREATE INDEX IF NOT EXISTS idx_expenses_date_user ON expenses(user_id, expense_date);

-- Product search and filtering indexes
CREATE INDEX IF NOT EXISTS idx_products_name_search ON products(user_id, product_name);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(user_id, barcode);
CREATE INDEX IF NOT EXISTS idx_product_types_name ON product_types(user_id, type_name);

-- Employee and customer relationship indexes
CREATE INDEX IF NOT EXISTS idx_bills_master_id ON bills(user_id, master_id);
CREATE INDEX IF NOT EXISTS idx_customers_city_area ON customers(user_id, city, area);

-- Partial indexes for active records (SQLite optimization)
CREATE INDEX IF NOT EXISTS idx_products_active_only ON products(user_id, type_id, product_name) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS idx_customers_active_only ON customers(user_id, name, phone) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS idx_bills_pending_only ON bills(user_id, bill_date, customer_id) WHERE status = 'Pending';

-- Indexes for aggregation queries
CREATE INDEX IF NOT EXISTS idx_bill_items_amount ON bill_items(user_id, total_amount);
CREATE INDEX IF NOT EXISTS idx_bills_amount ON bills(user_id, total_amount, bill_date);
CREATE INDEX IF NOT EXISTS idx_expenses_amount ON expenses(user_id, amount, expense_date);

-- Indexes for foreign key relationships (performance)
CREATE INDEX IF NOT EXISTS idx_bills_customer_fk ON bills(customer_id, user_id);
CREATE INDEX IF NOT EXISTS idx_bills_employee_fk ON bills(master_id, user_id);
CREATE INDEX IF NOT EXISTS idx_bill_items_product_fk ON bill_items(product_id, user_id);
CREATE INDEX IF NOT EXISTS idx_bill_items_bill_fk ON bill_items(bill_id, user_id);
CREATE INDEX IF NOT EXISTS idx_products_type_fk ON products(type_id, user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_category_fk ON expenses(category_id, user_id);

-- Create error_logs table for DML error logging
CREATE TABLE IF NOT EXISTS error_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    operation TEXT NOT NULL,
    table_name TEXT NOT NULL,
    error_message TEXT NOT NULL,
    user_id INTEGER,
    data_snapshot TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create user_actions table for audit trail
CREATE TABLE IF NOT EXISTS user_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    user_id INTEGER,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create indexes for logging tables
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_operation ON error_logs(operation);
CREATE INDEX IF NOT EXISTS idx_user_actions_timestamp ON user_actions(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_action ON user_actions(action);

-- Expense Management Tables (per tenant)
CREATE TABLE IF NOT EXISTS expense_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(user_id, category_name)
);

CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    expense_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    payment_method TEXT DEFAULT 'Cash',
    receipt_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES expense_categories(category_id)
);

-- Create indexes for expense tables
CREATE INDEX IF NOT EXISTS idx_expense_categories_user_id ON expense_categories(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_category_id ON expenses(category_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);

-- Insert default expense categories for existing users
INSERT OR IGNORE INTO expense_categories (user_id, category_name, description) VALUES
(1, 'Rent', 'Shop rent and utilities'),
(1, 'Supplies', 'Raw materials and supplies'),
(1, 'Equipment', 'Machines and tools'),
(1, 'Marketing', 'Advertising and promotion'),
(1, 'Transportation', 'Delivery and travel costs'),
(1, 'Utilities', 'Electricity, water, internet'),
(1, 'Maintenance', 'Equipment and shop maintenance'),
(1, 'Miscellaneous', 'Other expenses');

-- Insert default user (for backward compatibility)
INSERT OR IGNORE INTO users (user_id, email, shop_code, password_hash, shop_name, shop_type, contact_number, email_address) VALUES
(1, 'admin@tailorpos.com', 'SHOP001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq', 'Tajir', 'tailors', '+971 50 123 4567', 'admin@tailorpos.com');

-- Insert default user plan
INSERT OR IGNORE INTO user_plans (user_id, plan_type, plan_start_date) VALUES (1, 'trial', CURRENT_DATE);

-- Insert default shop settings
INSERT OR IGNORE INTO shop_settings (setting_id, user_id, shop_name, address, trn, logo_url, shop_mobile, working_hours, invoice_static_info, use_dynamic_invoice_template) VALUES
(1, 1, 'Tajir', '', '', '', '', '', '', 0); 
