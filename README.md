# Tailor POS System

A modern, full-featured Point of Sale (POS) system designed specifically for tailoring businesses. Built with Flask, SQLite, and a beautiful modern UI.

**Last Updated: 2025-07-19**

---

## 🚦 Plan Management & Licensing

Tailor POS now supports a flexible, config-driven licensing system with three plans:

- **Trial:** All features for 15 days (free)
- **Basic:** All features for 1 month, then only basic features (billing, product/customer management)
- **PRO:** Lifetime access to all features

Plan status, expiry, and feature access are managed via `config.json` and enforced in both backend and frontend. Upgrades and plan changes are supported via API and UI.

### Plan Enforcement
- **Trial Expiry:** All features locked after 15 days
- **Basic Expiry:** PRO features (dashboard, customer search, backup/restore) locked after 1 month
- **PRO:** Never expires, all features always available

---

## ⚙️ Configuration: `config.json`

All plan details, feature definitions, UI lock styles, and upgrade options are defined in `config.json`. You can customize:
- Plan durations, prices, and expiry behaviors
- Which features are enabled/locked per plan
- UI messages and lock overlays
- Upgrade pricing and flows

---

## 🛠️ Backend Features & API Endpoints

### Plan Management APIs
- `GET /api/plan/status` — Get current plan status and expiry
- `POST /api/plan/upgrade` — Change/upgrade plan (trial, basic, pro)
- `GET /api/plan/features` — List enabled/locked features
- `GET /api/plan/check-feature/<feature>` — Check if a feature is enabled
- `GET /api/plan/config` — Get plan config for frontend
- `POST /api/plan/expire-trial` — (Debug) Expire trial instantly
- `POST /api/plan/reset-trial` — (Debug) Reset trial to today

### Plan Logic
- See `plan_manager.py` for all backend plan logic and expiry calculations
- See `test_plan_manager.py` for backend plan logic tests

---

## 🖥️ Frontend Features

- **UI plan enforcement:** All feature access is locked/unlocked based on plan status
- **Upgrade prompts:** Users see upgrade modals and lock overlays when features are restricted
- **Debug page:** `/debug-plan` for interactive plan testing and switching

---

## 🧪 Testing & Debugging

- **Debug Page:** `/debug-plan` — Test plan status, expiry, and switch between plans instantly
- **Backend Test Script:** `python test_plan_manager.py` — Run backend plan logic tests

---

## 📁 .gitignore & Excluded Files

If you do not want to push the `bkpup/` directory to git, add this to your `.gitignore`:
```
bkpup/
```

---

## 3-Tier Product Versions & Pricing

| Feature                | <span title="All features for 15 days">Trial<br><sub>(15 days)</sub></span> | <span title="All features for 1 month, then some features lock">Basic<br><sub>(1 month, then limited)</sub></span> | <span title="Full features, lifetime">PRO<br><sub>(Lifetime)</sub></span> |
|------------------------|:------:|:----------------------:|:------:|
| Billing                | ✅     | ✅                     | ✅     |
| Product/Customer Mgmt  | ✅     | ✅                     | ✅     |
| Dashboard              | ✅     | <span title="Locked after 1 month">🔒</span> | ✅     |
| Customer Search        | ✅     | <span title="Locked after 1 month">🔒</span> | ✅     |
| DB Backup/Restore      | ✅     | <span title="Locked after 1 month">🔒</span> | ✅     |

**Legend:** ✅ = Available, 🔒 = Locked after 1 month in Basic

| Version         | Features                                                                 | Price         |
|-----------------|--------------------------------------------------------------------------|--------------|
| **Tailor Trial**| All features for 15 days                                                 | Free         |
| **Tailor Basic**| All features for 1 month, then locks PRO features (Dashboard, Customer Search, DB backup/Restore) | $X/month     |
| **Tailor PRO**  | All features, lifetime access                                            | $Y (one-time)|

---

## Features

### 🎯 Core Features
- **Product Management**: Manage product types and individual products with pricing
- **Customer Management**: Store and manage customer information
- **Billing System**: Create and print professional bills with VAT calculation
- **VAT Management**: Configure and manage VAT rates with effective dates
- **Dashboard Analytics**: Real-time business insights and revenue tracking

### 📊 Product Categories
The system comes pre-loaded with common tailoring products:
- **Saree**: Fall stitching, petticoat, belt stitching
- **Kurti**: With/without lining options
- **Palazzo**: With/without lining options
- **Trouser/Pant**: With/without lining options
- **Shirt**: Regular shirts
- **Salwar Suit**: Various lining options
- **Blouse**: Padded/non-padded options
- **Kaftan**: With/without lining options
- **Patiala Suit**: Various lining options
- **Abaya**: Stitching services
- **Anarkali**: 8 kaliyan design
- **Gown**: Stitching services
- **Jump Suit**: Complete jumpsuit
- **Lehenga**: Stitching and choli options
- **Designer Items**: One piece and blouse options
- **Sharara/Gharara**: With kurti combinations
- **Coat/Blazer**: Professional wear
- **Dress**: Indo-western and western styles

### 💰 Pricing Structure
All products come with pre-configured pricing based on market standards:
- Saree fall stitching: AED 30
- Kurti (no lining): AED 55
- Shirt: AED 100
- Lehenga choli: AED 320
- Coat/Blazer: AED 350
- And many more...

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd tailor_pos
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   Open your web browser and navigate to: `http://localhost:5000`

## Database Structure

The application uses SQLite with the following main tables:

### `product_types`
- `type_id` (Primary Key)
- `type_name` (Unique)
- `created_at`

### `products`
- `product_id` (Primary Key)
- `type_id` (Foreign Key to product_types)
- `product_name`
- `rate` (Price in AED)
- `description`
- `is_active`
- `created_at`

### `customers`
- `customer_id` (Primary Key)
- `name`
- `phone` (Unique)
- `city`
- `area`
- `email`
- `address`
- `created_at`

### `bills`
- `bill_id` (Primary Key)
- `bill_number` (Unique)
- `customer_id` (Foreign Key to customers)
- `customer_name`
- `customer_phone`
- `customer_city`
- `customer_area`
- `bill_date`
- `delivery_date`
- `payment_method`
- `subtotal`
- `vat_amount`
- `total_amount`
- `advance_paid`
- `balance_amount`
- `status`
- `created_at`

### `bill_items`
- `item_id` (Primary Key)
- `bill_id` (Foreign Key to bills)
- `product_id` (Foreign Key to products)
- `product_name`
- `quantity`
- `rate`
- `discount`
- `advance_paid`
- `total_amount`
- `created_at`

### `vat_rates`
- `vat_id` (Primary Key)
- `rate_percentage`
- `effective_from`
- `effective_to`
- `is_active`
- `created_at`

## Usage Guide

### 1. Product Types Management
- Navigate to "Product Types" in the sidebar
- Add new product types (e.g., "Wedding Wear", "Casual Wear")
- Delete unused types (only if no products are associated)

### 2. Products Management
- Navigate to "Products" in the sidebar
- Select a product type
- Add product name and price
- View all products in the table below

### 3. Customer Management
- Navigate to "Customers" in the sidebar
- Add customer details: name, phone, city, area
- View all customers in the list

### 4. VAT Configuration
- Navigate to "VAT %" in the sidebar
- Set VAT percentage and effective dates
- Multiple VAT rates can be configured for different periods

### 5. Billing Process
- Navigate to "Billing" in the sidebar
- Fill in customer details and bill information
- Select products from the dropdown
- Adjust quantities, rates, discounts, and advance payments
- Click "Print Receipt" to generate and print the bill

### 6. Dashboard Analytics
- Navigate to "Dashboard" in the sidebar
- View today's revenue, bills, pending orders, and customer count
- Analyze monthly revenue trends
- Track top-selling products

## API Endpoints

The application provides RESTful API endpoints for all operations:

### Product Types
- `GET /api/product-types` - Get all product types
- `POST /api/product-types` - Add new product type
- `DELETE /api/product-types/<id>` - Delete product type

### Products
- `GET /api/products` - Get all products
- `POST /api/products` - Add new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

### Customers
- `GET /api/customers` - Get all customers
- `POST /api/customers` - Add new customer
- `PUT /api/customers/<id>` - Update customer
- `DELETE /api/customers/<id>` - Delete customer

### VAT Rates
- `GET /api/vat-rates` - Get all VAT rates
- `POST /api/vat-rates` - Add new VAT rate
- `DELETE /api/vat-rates/<id>` - Delete VAT rate

### Bills
- `GET /api/bills` - Get all bills
- `POST /api/bills` - Create new bill
- `GET /api/bills/<id>` - Get specific bill
- `DELETE /api/bills/<id>` - Delete bill
- `GET /api/bills/<id>/print` - Print bill

### Dashboard
- `GET /api/dashboard` - Get dashboard analytics

## Customization

### Adding New Products
1. First add a product type if needed
2. Navigate to Products section
3. Select the product type
4. Add product name and price
5. The product will be available for billing immediately

### Modifying Prices
1. Navigate to Products section
2. Find the product in the table
3. Click edit (if implemented) or delete and recreate
4. Update the price as needed

### Customizing Bill Template
Edit the `templates/print_bill.html` file to:
- Change business name and contact information
- Modify layout and styling
- Add company logo
- Customize footer text

## Security Features

- Input validation on all forms
- SQL injection prevention through parameterized queries
- XSS protection through proper HTML escaping
- CSRF protection (can be enhanced further)

## Performance Optimizations

- Database indexes on frequently queried columns
- Efficient SQL queries with proper joins
- Client-side caching for static assets
- Responsive design for mobile devices

## Troubleshooting

### Common Issues

1. **Database not created**
   - Ensure the application has write permissions in the directory
   - Check if `database_schema.sql` exists

2. **Port already in use**
   - Change the port in `app.py` line: `app.run(debug=True, host='0.0.0.0', port=5001)`

3. **Dependencies not installed**
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility

4. **Print not working**
   - Ensure pop-up blockers are disabled
   - Check browser print settings

## Future Enhancements

- User authentication and role-based access
- Inventory management
- Customer loyalty program
- Multi-branch support
- Advanced reporting and analytics
- Mobile app integration
- Payment gateway integration
- Backup and restore functionality

## Support

For technical support or feature requests, please contact the development team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This is a production-ready application designed for small to medium tailoring businesses. The database comes pre-loaded with common tailoring products and pricing, but can be fully customized to meet specific business requirements. 

## New Features (2024)

### 👥 Employees Management
- Add, edit, and delete employees (Masters) from the Employees section
- Assign a Master to each bill with autocomplete in billing
- Track employee performance and revenue

### 🧑‍🔧 Master & Trial Date in Billing
- Select a Master (employee) for each bill
- Add a Trial Date for each bill
- Both fields are saved and shown in printouts

### 🧾 Bill Number Auto-Generation
- Bill # is auto-generated in the format `BILL-YYYYMMDD-XXX` (editable by user)
- Ensures unique, sequential bill numbers per day

### 📈 Advanced Analytics
- Dashboard includes:
  - Top 5 Employees by Revenue (bar chart)
  - Revenue Share by Employee (pie chart)
  - Monthly Revenue (vertical bar chart with color effects)
  - Interactive, modern charts with tooltips and effects

### 🖨️ Enhanced Bill Printout
- Printout includes Master (employee) name and Trial Date
- Professional, customizable layout

### 💡 UI/UX Improvements
- Modern toast notifications for errors/info
- Autocomplete for city, area, and master fields
- Visual effects on charts (3D, gradients, hover)

## How to Push to GitHub

1. **Initialize Git (if not already):**
   ```bash
   git init
   git remote add origin https://github.com/yourusername/yourrepo.git
   ```
2. **Add all changes:**
   ```bash
   git add .
   ```
3. **Commit your changes:**
   ```bash
   git commit -m "Add employee management, advanced analytics, and UI improvements"
   ```
4. **Push to GitHub:**
   ```bash
   git push -u origin main
   ```
   *(If your default branch is 'master', use 'master' instead of 'main')*

--- 

## Change Log

### 2025-07-16
- Fixed Payment Progress Modal HTML placement and ensured only one instance exists.
- Payment Progress Modal now animates and shows after successful payment.
- Improved Mark as Paid logic to use the progress modal and show success only after completion.
- Introduced 3-tier product structure (Trial, Basic, PRO) with feature matrix.
- Updated README.md with pricing, features, and last updated date. 