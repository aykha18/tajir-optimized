-- Tailor POS Database Schema
-- Database: pos_tailor

-- Product Types Table
CREATE TABLE IF NOT EXISTS product_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES product_types(type_id)
);

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    city TEXT,
    area TEXT,
  --landmark TEXT,
    email TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VAT Rates Table
CREATE TABLE IF NOT EXISTS vat_rates (
    vat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rate_percentage DECIMAL(5,2) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills Table
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT UNIQUE,
    customer_id INTEGER,
    customer_name TEXT,
    customer_phone TEXT,
    customer_city TEXT,
    customer_area TEXT,
    bill_date DATE NOT NULL,
    delivery_date DATE,
    payment_method TEXT DEFAULT 'Cash',
    subtotal DECIMAL(10,2) DEFAULT 0,
    vat_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    advance_paid DECIMAL(10,2) DEFAULT 0,
    balance_amount DECIMAL(10,2) DEFAULT 0,
    status TEXT DEFAULT 'Pending',
    master_id INTEGER, -- New: references employees
    trial_date DATE,   -- New: trial date for the bill
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (master_id) REFERENCES employees(employee_id)
);

-- Bill Items Table
CREATE TABLE IF NOT EXISTS bill_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    product_id INTEGER,
    product_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    rate DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    advance_paid DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Cities Table
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL UNIQUE
);

-- City Areas Table
CREATE TABLE IF NOT EXISTS city_area (
    area_id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_name TEXT NOT NULL,
    city_id INTEGER,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Employees Table
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default product types
INSERT OR IGNORE INTO product_types (type_name) VALUES 
('Saree'),
('Kurti'),
('Palazzo'),
('Trouser/Pant'),
('Shirt'),
('Salwar Suit'),
('Blouse'),
('Kaftan'),
('Patiala Suit'),
('Abaya'),
('Anarkali'),
('Gown'),
('Jump Suit'),
('Lehenga'),
('Designer Items'),
('Sharara/Gharara'),
('Coat/Blazer'),
('Dress');

-- Insert default products based on the provided pricing
INSERT OR IGNORE INTO products (type_id, product_name, rate, description) VALUES
-- Saree Products
(1, 'Saree Fall Stitching with Fall Fabric', 30.00, 'Saree fall stitching with fall fabric'),
(1, 'Saree Petticoat Stitching', 40.00, 'Saree petticoat stitching'),
(1, 'Saree Belt Stitching', 150.00, 'Saree belt stitching'),

-- Kurti Products
(2, 'Kurti (No Lining)', 55.00, 'Kurti without lining'),
(2, 'Kurti with Lining', 75.00, 'Kurti with lining'),

-- Palazzo Products
(3, 'Palazzo No Lining', 80.00, 'Palazzo without lining'),
(3, 'Palazzo with Lining', 105.00, 'Palazzo with lining'),

-- Trouser/Pant Products
(4, 'Trouser or Pant No Lining', 80.00, 'Trouser or pant without lining'),
(4, 'Trousers Pants with Lining', 100.00, 'Trousers or pants with lining'),

-- Shirt Products
(5, 'Shirt', 100.00, 'Regular shirt'),

-- Salwar Suit Products
(6, 'Salwar Suit No Lining', 100.00, 'Salwar suit without lining'),
(6, 'Salwar Suit Half/Top Lining', 115.00, 'Salwar suit with half or top lining'),
(6, 'Salwar Suit with Full Lining', 125.00, 'Salwar suit with full lining'),

-- Blouse Products
(7, 'Blouse Non Padded', 115.00, 'Blouse without padding'),
(7, 'Blouse Padded', 150.00, 'Blouse with padding'),

-- Kaftan Products
(8, 'Kaftan No Lining', 100.00, 'Kaftan without lining'),
(8, 'Kaftan with Lining', 125.00, 'Kaftan with lining'),

-- Patiala Suit Products
(9, 'Patiala Suit No Lining', 125.00, 'Patiala suit without lining'),
(9, 'Patiala Suit with Half/Top Lining', 140.00, 'Patiala suit with half or top lining'),
(9, 'Patiala Suit with Lining', 150.00, 'Patiala suit with full lining'),

-- Abaya Products
(10, 'Abaya Stitching', 125.00, 'Abaya stitching'),

-- Anarkali Products
(11, 'Anarkali (8 Kaliyan)', 160.00, 'Anarkali with 8 kaliyan'),

-- Gown Products
(12, 'Gown Stitching', 150.00, 'Gown stitching'),

-- Jump Suit Products
(13, 'Jump Suit', 170.00, 'Jump suit'),

-- Lehenga Products
(14, 'Lehenga Stitching', 195.00, 'Lehenga stitching'),
(14, 'Lehenga Choli', 320.00, 'Lehenga choli'),

-- Designer Items
(15, 'Designer One Piece', 195.00, 'Designer one piece'),
(15, 'Designer Blouse', 150.00, 'Designer blouse'),

-- Sharara/Gharara Products
(16, 'Sharara/Gharara with Kurti', 240.00, 'Sharara or Gharara with kurti'),

-- Coat/Blazer Products
(17, 'Coat/Blazer', 350.00, 'Coat or blazer'),
(17, 'Coat Pant/Suit 2 Piece', 450.00, 'Coat pant or suit 2 piece'),

-- Dress Products
(18, 'Dress Indo Western', 150.00, 'Indo western dress'),
(18, 'Dress Western', 225.00, 'Western dress');

-- Insert default VAT rate
INSERT OR IGNORE INTO vat_rates (rate_percentage, effective_from, effective_to) VALUES
(5.00, '2018-01-01', '2099-12-31');

-- Insert all major UAE cities
INSERT OR IGNORE INTO cities (city_name) VALUES
('Abu Dhabi'),
('Ajman'),
('Al Ain'),
('Dubai'),
('Fujairah'),
('Kalba'),
('Khor Fakkan'),
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
CREATE INDEX IF NOT EXISTS idx_products_type_id ON products(type_id);
CREATE INDEX IF NOT EXISTS idx_bills_customer_id ON bills(customer_id);
CREATE INDEX IF NOT EXISTS idx_bills_bill_date ON bills(bill_date);
CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);

-- User Plans Table (for pricing plan management)
CREATE TABLE IF NOT EXISTS user_plans (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_type TEXT NOT NULL DEFAULT 'trial' CHECK (plan_type IN ('trial', 'basic', 'pro')),
    plan_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    plan_end_date DATE,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default user plan (trial)
INSERT OR IGNORE INTO user_plans (user_id, plan_type, plan_start_date) VALUES (1, 'trial', CURRENT_DATE); 
