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

-- Insert default user (for backward compatibility)
INSERT OR IGNORE INTO users (user_id, email, shop_code, password_hash, shop_name, shop_type, contact_number, email_address) VALUES
(1, 'admin@tailorpos.com', 'SHOP001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq', 'Tajir', 'tailors', '+971 50 123 4567', 'admin@tailorpos.com');

-- Insert default user plan
INSERT OR IGNORE INTO user_plans (user_id, plan_type, plan_start_date) VALUES (1, 'trial', CURRENT_DATE);

-- Insert default shop settings
INSERT OR IGNORE INTO shop_settings (setting_id, user_id, shop_name, address, trn, logo_url, shop_mobile, working_hours, invoice_static_info, use_dynamic_invoice_template) VALUES
(1, 1, 'Tajir', '', '', '', '', '', '', 0); 
