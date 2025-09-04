-- Complete Database Schema
-- Extracted from local PostgreSQL database

-- Table: audit_log
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER NOT NULL DEFAULT nextval('audit_log_id_seq'::regclass),
    user_id INTEGER,
    action VARCHAR(100),
    resource VARCHAR(100),
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE audit_log ADD CONSTRAINT fk_audit_log_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS audit_log_id_seq;

-- Table: bill_items
CREATE TABLE IF NOT EXISTS bill_items (
    item_id INTEGER NOT NULL DEFAULT nextval('bill_items_item_id_seq'::regclass),
    user_id INTEGER,
    bill_id INTEGER,
    product_id INTEGER,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    advance_paid DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vat_amount DECIMAL(10,2) DEFAULT 0,
    PRIMARY KEY (item_id)
);

ALTER TABLE bill_items ADD CONSTRAINT fk_bill_items_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE bill_items ADD CONSTRAINT fk_bill_items_bill_id FOREIGN KEY (bill_id) REFERENCES bills(bill_id);
ALTER TABLE bill_items ADD CONSTRAINT fk_bill_items_product_id FOREIGN KEY (product_id) REFERENCES products(product_id);

CREATE SEQUENCE IF NOT EXISTS bill_items_item_id_seq;

-- Table: bills
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER NOT NULL DEFAULT nextval('bills_bill_id_seq'::regclass),
    user_id INTEGER,
    bill_number VARCHAR(50) NOT NULL,
    customer_id INTEGER,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    customer_city VARCHAR(100),
    customer_area VARCHAR(100),
    bill_date DATE NOT NULL,
    delivery_date DATE,
    payment_method VARCHAR(50),
    subtotal DECIMAL(10,2) DEFAULT 0,
    vat_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    advance_paid DECIMAL(10,2) DEFAULT 0,
    balance_amount DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending'::character varying,
    master_id INTEGER,
    trial_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_trn VARCHAR(50),
    customer_type VARCHAR(50),
    business_name VARCHAR(255),
    business_address TEXT,
    uuid VARCHAR(100),
    PRIMARY KEY (bill_id)
);

ALTER TABLE bills ADD CONSTRAINT fk_bills_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE bills ADD CONSTRAINT fk_bills_customer_id FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

CREATE SEQUENCE IF NOT EXISTS bills_bill_id_seq;

-- Table: cities
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER NOT NULL DEFAULT nextval('cities_city_id_seq'::regclass),
    city_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (city_id)
);

CREATE SEQUENCE IF NOT EXISTS cities_city_id_seq;

-- Table: city_area
CREATE TABLE IF NOT EXISTS city_area (
    area_id INTEGER NOT NULL DEFAULT nextval('city_area_area_id_seq'::regclass),
    area_name VARCHAR(100) NOT NULL,
    city_id INTEGER,
    PRIMARY KEY (area_id)
);

ALTER TABLE city_area ADD CONSTRAINT fk_city_area_city_id FOREIGN KEY (city_id) REFERENCES cities(city_id);

CREATE SEQUENCE IF NOT EXISTS city_area_area_id_seq;

-- Table: customer_loyalty
CREATE TABLE IF NOT EXISTS customer_loyalty (
    loyalty_id INTEGER NOT NULL DEFAULT nextval('customer_loyalty_loyalty_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    total_points INTEGER DEFAULT 0,
    available_points INTEGER DEFAULT 0,
    lifetime_points INTEGER DEFAULT 0,
    tier_level VARCHAR(20) DEFAULT 'Bronze'::character varying,
    tier_points_threshold INTEGER DEFAULT 0,
    join_date DATE DEFAULT CURRENT_DATE,
    last_purchase_date DATE,
    total_purchases INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0.00,
    referral_code VARCHAR(20),
    referred_by INTEGER,
    birthday DATE,
    anniversary_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (loyalty_id)
);

ALTER TABLE customer_loyalty ADD CONSTRAINT fk_customer_loyalty_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE customer_loyalty ADD CONSTRAINT fk_customer_loyalty_customer_id FOREIGN KEY (customer_id) REFERENCES customers(customer_id);
ALTER TABLE customer_loyalty ADD CONSTRAINT fk_customer_loyalty_referred_by FOREIGN KEY (referred_by) REFERENCES customer_loyalty(loyalty_id);

CREATE SEQUENCE IF NOT EXISTS customer_loyalty_loyalty_id_seq;

-- Table: customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER NOT NULL DEFAULT nextval('customers_customer_id_seq'::regclass),
    user_id INTEGER,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(100),
    area VARCHAR(100),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trn VARCHAR(50),
    customer_type VARCHAR(50),
    business_name VARCHAR(255),
    business_address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (customer_id)
);

ALTER TABLE customers ADD CONSTRAINT fk_customers_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS customers_customer_id_seq;

-- Table: employees
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER NOT NULL DEFAULT nextval('employees_employee_id_seq'::regclass),
    user_id INTEGER,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    position VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    address TEXT,
    PRIMARY KEY (employee_id)
);

ALTER TABLE employees ADD CONSTRAINT fk_employees_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS employees_employee_id_seq;

-- Table: error_logs
CREATE TABLE IF NOT EXISTS error_logs (
    log_id INTEGER NOT NULL DEFAULT nextval('error_logs_log_id_seq'::regclass),
    timestamp TEXT,
    level VARCHAR(20),
    operation VARCHAR(100),
    table_name VARCHAR(100),
    error_message TEXT,
    user_id INTEGER,
    data_snapshot TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id)
);

ALTER TABLE error_logs ADD CONSTRAINT fk_error_logs_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS error_logs_log_id_seq;

-- Table: expense_categories
CREATE TABLE IF NOT EXISTS expense_categories (
    category_id INTEGER NOT NULL DEFAULT nextval('expense_categories_category_id_seq'::regclass),
    user_id INTEGER,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (category_id)
);

ALTER TABLE expense_categories ADD CONSTRAINT fk_expense_categories_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS expense_categories_category_id_seq;

-- Table: expenses
CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER NOT NULL DEFAULT nextval('expenses_expense_id_seq'::regclass),
    user_id INTEGER,
    category_id INTEGER,
    expense_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    payment_method VARCHAR(50),
    receipt_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (expense_id)
);

ALTER TABLE expenses ADD CONSTRAINT fk_expenses_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE expenses ADD CONSTRAINT fk_expenses_category_id FOREIGN KEY (category_id) REFERENCES expense_categories(category_id);

CREATE SEQUENCE IF NOT EXISTS expenses_expense_id_seq;

-- Table: loyalty_config
CREATE TABLE IF NOT EXISTS loyalty_config (
    config_id INTEGER NOT NULL DEFAULT nextval('loyalty_config_config_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    program_name VARCHAR(255) DEFAULT 'Loyalty Program'::character varying,
    is_active BOOLEAN DEFAULT TRUE,
    points_per_aed DECIMAL(5,2) DEFAULT 1.00,
    aed_per_point DECIMAL(5,2) DEFAULT 0.01,
    min_points_redemption INTEGER DEFAULT 100,
    max_points_redemption_percent INTEGER DEFAULT 20,
    birthday_bonus_points INTEGER DEFAULT 50,
    anniversary_bonus_points INTEGER DEFAULT 100,
    referral_bonus_points INTEGER DEFAULT 200,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (config_id)
);

ALTER TABLE loyalty_config ADD CONSTRAINT fk_loyalty_config_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS loyalty_config_config_id_seq;

-- Table: loyalty_ledger
CREATE TABLE IF NOT EXISTS loyalty_ledger (
    id INTEGER NOT NULL DEFAULT nextval('loyalty_ledger_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    bill_id INTEGER,
    points_change INTEGER NOT NULL,
    reason TEXT NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE SEQUENCE IF NOT EXISTS loyalty_ledger_id_seq;

-- Table: loyalty_rewards
CREATE TABLE IF NOT EXISTS loyalty_rewards (
    reward_id INTEGER NOT NULL DEFAULT nextval('loyalty_rewards_reward_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    reward_name VARCHAR(255) NOT NULL,
    reward_type VARCHAR(20) NOT NULL,
    points_cost INTEGER DEFAULT 0,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reward_id)
);

ALTER TABLE loyalty_rewards ADD CONSTRAINT fk_loyalty_rewards_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS loyalty_rewards_reward_id_seq;

-- Table: loyalty_settings
CREATE TABLE IF NOT EXISTS loyalty_settings (
    id INTEGER NOT NULL DEFAULT nextval('loyalty_settings_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    earn_rate_numerator INTEGER NOT NULL DEFAULT 1,
    earn_rate_denominator INTEGER NOT NULL DEFAULT 100,
    redeem_value_numerator INTEGER NOT NULL DEFAULT 1,
    redeem_value_denominator INTEGER NOT NULL DEFAULT 1,
    max_redeem_percent INTEGER NOT NULL DEFAULT 50,
    min_bill_amount DECIMAL NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE SEQUENCE IF NOT EXISTS loyalty_settings_id_seq;

-- Table: loyalty_tiers
CREATE TABLE IF NOT EXISTS loyalty_tiers (
    tier_id INTEGER NOT NULL DEFAULT nextval('loyalty_tiers_tier_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    tier_name VARCHAR(50) NOT NULL,
    tier_level VARCHAR(20) NOT NULL,
    points_threshold INTEGER NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    bonus_points_multiplier DECIMAL(3,2) DEFAULT 1.00,
    free_delivery BOOLEAN DEFAULT FALSE,
    priority_service BOOLEAN DEFAULT FALSE,
    exclusive_offers BOOLEAN DEFAULT FALSE,
    color_code VARCHAR(7) DEFAULT '#CD7F32'::character varying,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tier_id)
);

ALTER TABLE loyalty_tiers ADD CONSTRAINT fk_loyalty_tiers_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS loyalty_tiers_tier_id_seq;

-- Table: loyalty_transactions
CREATE TABLE IF NOT EXISTS loyalty_transactions (
    transaction_id INTEGER NOT NULL DEFAULT nextval('loyalty_transactions_transaction_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    loyalty_id INTEGER NOT NULL,
    bill_id INTEGER,
    transaction_type VARCHAR(20) NOT NULL,
    points_amount INTEGER NOT NULL,
    aed_amount DECIMAL(10,2) DEFAULT 0.00,
    description TEXT,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id)
);

ALTER TABLE loyalty_transactions ADD CONSTRAINT fk_loyalty_transactions_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE loyalty_transactions ADD CONSTRAINT fk_loyalty_transactions_loyalty_id FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id);
ALTER TABLE loyalty_transactions ADD CONSTRAINT fk_loyalty_transactions_bill_id FOREIGN KEY (bill_id) REFERENCES bills(bill_id);

CREATE SEQUENCE IF NOT EXISTS loyalty_transactions_transaction_id_seq;

-- Table: otp_codes
CREATE TABLE IF NOT EXISTS otp_codes (
    id INTEGER NOT NULL DEFAULT nextval('otp_codes_id_seq'::regclass),
    mobile VARCHAR(20) NOT NULL,
    otp_code VARCHAR(10) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE SEQUENCE IF NOT EXISTS otp_codes_id_seq;

-- Table: personalized_offers
CREATE TABLE IF NOT EXISTS personalized_offers (
    offer_id INTEGER NOT NULL DEFAULT nextval('personalized_offers_offer_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    loyalty_id INTEGER NOT NULL,
    offer_title VARCHAR(255) NOT NULL,
    offer_description TEXT,
    offer_type VARCHAR(20) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    points_bonus INTEGER DEFAULT 0,
    min_purchase_amount DECIMAL(10,2) DEFAULT 0.00,
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (offer_id)
);

ALTER TABLE personalized_offers ADD CONSTRAINT fk_personalized_offers_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE personalized_offers ADD CONSTRAINT fk_personalized_offers_loyalty_id FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id);

CREATE SEQUENCE IF NOT EXISTS personalized_offers_offer_id_seq;

-- Table: product_types
CREATE TABLE IF NOT EXISTS product_types (
    type_id INTEGER NOT NULL DEFAULT nextval('product_types_type_id_seq'::regclass),
    user_id INTEGER,
    type_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    PRIMARY KEY (type_id)
);

ALTER TABLE product_types ADD CONSTRAINT fk_product_types_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS product_types_type_id_seq;

-- Table: products
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER NOT NULL DEFAULT nextval('products_product_id_seq'::regclass),
    user_id INTEGER,
    type_id INTEGER,
    product_name VARCHAR(255) NOT NULL,
    rate DECIMAL(10,2) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    barcode VARCHAR(100),
    PRIMARY KEY (product_id)
);

ALTER TABLE products ADD CONSTRAINT fk_products_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE products ADD CONSTRAINT fk_products_type_id FOREIGN KEY (type_id) REFERENCES product_types(type_id);

CREATE SEQUENCE IF NOT EXISTS products_product_id_seq;

-- Table: reward_redemptions
CREATE TABLE IF NOT EXISTS reward_redemptions (
    redemption_id INTEGER NOT NULL DEFAULT nextval('reward_redemptions_redemption_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    loyalty_id INTEGER NOT NULL,
    reward_id INTEGER NOT NULL,
    bill_id INTEGER,
    points_used INTEGER NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    redemption_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (redemption_id)
);

ALTER TABLE reward_redemptions ADD CONSTRAINT fk_reward_redemptions_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);
ALTER TABLE reward_redemptions ADD CONSTRAINT fk_reward_redemptions_loyalty_id FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id);
ALTER TABLE reward_redemptions ADD CONSTRAINT fk_reward_redemptions_reward_id FOREIGN KEY (reward_id) REFERENCES loyalty_rewards(reward_id);
ALTER TABLE reward_redemptions ADD CONSTRAINT fk_reward_redemptions_bill_id FOREIGN KEY (bill_id) REFERENCES bills(bill_id);

CREATE SEQUENCE IF NOT EXISTS reward_redemptions_redemption_id_seq;

-- Table: shop_settings
CREATE TABLE IF NOT EXISTS shop_settings (
    setting_id INTEGER NOT NULL DEFAULT nextval('shop_settings_setting_id_seq'::regclass),
    user_id INTEGER,
    shop_name VARCHAR(255),
    address TEXT,
    trn VARCHAR(50),
    logo_url TEXT,
    shop_mobile VARCHAR(20),
    working_hours TEXT,
    invoice_static_info TEXT,
    use_dynamic_invoice_template BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    city VARCHAR(100),
    area VARCHAR(100),
    payment_mode VARCHAR(50),
    enable_trial_date BOOLEAN DEFAULT FALSE,
    enable_delivery_date BOOLEAN DEFAULT FALSE,
    enable_advance_payment BOOLEAN DEFAULT FALSE,
    enable_customer_notes BOOLEAN DEFAULT FALSE,
    enable_employee_assignment BOOLEAN DEFAULT FALSE,
    default_delivery_days INTEGER DEFAULT 7,
    default_trial_days INTEGER DEFAULT 3,
    default_employee_id INTEGER,
    enable_loyalty_program BOOLEAN DEFAULT FALSE,
    loyalty_program_name TEXT DEFAULT 'Loyalty Program'::text,
    loyalty_points_per_aed DECIMAL(5,2) DEFAULT 1.00,
    loyalty_aed_per_point DECIMAL(5,2) DEFAULT 0.01,
    points_per_currency DECIMAL(10,2) DEFAULT 1.0,
    min_purchase_amount DECIMAL(10,2) DEFAULT 0.0,
    points_expiry_days INTEGER DEFAULT 365,
    referral_bonus_points INTEGER DEFAULT 100,
    PRIMARY KEY (setting_id)
);

ALTER TABLE shop_settings ADD CONSTRAINT fk_shop_settings_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS shop_settings_setting_id_seq;

-- Table: user_actions
CREATE TABLE IF NOT EXISTS user_actions (
    action_id INTEGER NOT NULL DEFAULT nextval('user_actions_action_id_seq'::regclass),
    timestamp TEXT,
    action VARCHAR(100),
    user_id INTEGER,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (action_id)
);

ALTER TABLE user_actions ADD CONSTRAINT fk_user_actions_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS user_actions_action_id_seq;

-- Table: user_plans
CREATE TABLE IF NOT EXISTS user_plans (
    plan_id INTEGER NOT NULL DEFAULT nextval('user_plans_plan_id_seq'::regclass),
    user_id INTEGER,
    plan_type VARCHAR(50) NOT NULL,
    plan_start_date DATE,
    plan_end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (plan_id)
);

ALTER TABLE user_plans ADD CONSTRAINT fk_user_plans_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS user_plans_plan_id_seq;

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER NOT NULL DEFAULT nextval('users_user_id_seq'::regclass),
    email VARCHAR(255) NOT NULL,
    mobile VARCHAR(20),
    shop_code VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    shop_name VARCHAR(255),
    shop_type VARCHAR(100),
    contact_number VARCHAR(20),
    email_address VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE SEQUENCE IF NOT EXISTS users_user_id_seq;

-- Table: vat_rates
CREATE TABLE IF NOT EXISTS vat_rates (
    vat_id INTEGER NOT NULL DEFAULT nextval('vat_rates_vat_id_seq'::regclass),
    user_id INTEGER,
    rate_percentage DECIMAL(5,2) NOT NULL,
    effective_from DATE,
    effective_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (vat_id)
);

ALTER TABLE vat_rates ADD CONSTRAINT fk_vat_rates_user_id FOREIGN KEY (user_id) REFERENCES users(user_id);

CREATE SEQUENCE IF NOT EXISTS vat_rates_vat_id_seq;

