# Billing System Test Cases

## Overview
This document contains comprehensive test cases for the Tajir POS Billing System. All test cases are designed for Selenium-based automated testing.

## Test Environment Setup
- **Base URL**: `http://localhost:5000`
- **Browser**: Chrome/Firefox (Selenium WebDriver)
- **Test Data**: Pre-populated database with sample products, customers, and employees

---

## 1. Billing Form Initialization Tests

### TC-001: Billing Page Load
**Objective**: Verify billing page loads correctly with all form elements
**Steps**:
1. Navigate to `/app`
2. Click on "Billing" section
3. Verify billing form is displayed
**Expected Results**:
- Billing form is visible
- All form fields are present and enabled
- Bill number field is auto-populated
- Date fields show current date

### TC-002: Form Field Validation - Required Fields
**Objective**: Test validation for required fields
**Steps**:
1. Clear all form fields
2. Click "Add" button without entering product
3. Verify validation message appears
**Expected Results**:
- "Product Required" alert appears
- Form prevents submission

### TC-003: Smart Defaults Initialization
**Objective**: Verify smart defaults are set correctly
**Steps**:
1. Load billing page
2. Check date fields
**Expected Results**:
- Bill Date = Today's date
- Delivery Date = Bill Date + 3 days
- Trial Date = Bill Date + 1 day

---

## 2. Customer Management Tests

### TC-004: Customer Type Selection
**Objective**: Test customer type dropdown functionality
**Steps**:
1. Select "Individual" from customer type dropdown
2. Verify business fields are hidden
3. Select "Business" from customer type dropdown
4. Verify business fields are visible
**Expected Results**:
- Individual: Business fields hidden
- Business: Business fields visible (Business Name, TRN, Business Address)

### TC-005: Customer Mobile Number Auto-Fetch
**Objective**: Test customer auto-population by mobile number
**Steps**:
1. Enter existing customer mobile number in "Mobile" field
2. Wait for auto-fetch
3. Verify customer details are populated
**Expected Results**:
- Customer name auto-populated
- City and area auto-populated
- Recent customers list updated

### TC-006: Recent Customers Display
**Objective**: Test recent customers functionality
**Steps**:
1. Load billing page
2. Check recent customers section
**Expected Results**:
- Recent customers list is displayed
- Customer names are clickable
- Clicking customer populates form

### TC-007: Customer Quick Search
**Objective**: Test customer search functionality
**Steps**:
1. Type in customer name field
2. Verify dropdown appears with matching customers
3. Select a customer from dropdown
**Expected Results**:
- Search dropdown appears
- Matching customers displayed
- Selection populates form fields

---

## 3. Product Management Tests

### TC-008: Product Autocomplete Search
**Objective**: Test product search and selection
**Steps**:
1. Click on "Product" field
2. Type product name
3. Verify dropdown appears
4. Select product from dropdown
**Expected Results**:
- Product dropdown appears
- Products filtered by search term
- Rate field auto-populated with product price
- Product name appears in field

### TC-009: Product Rate Display
**Objective**: Verify product rates display correctly
**Steps**:
1. Search for products
2. Check rate display in dropdown
**Expected Results**:
- Rates displayed in green bold font
- Format: "AED [amount]"
- Rate auto-populates in rate field

### TC-010: Product Validation
**Objective**: Test product selection validation
**Steps**:
1. Type invalid product name
2. Click "Add" button
3. Verify validation message
**Expected Results**:
- "Please select a product from the search results" message
- Form prevents submission

### TC-011: Product Quick Add Mode
**Objective**: Test quick add mode functionality
**Steps**:
1. Click "Quick Add Mode" button
2. Verify interface changes
3. Add product using quick mode
**Expected Results**:
- Interface switches to quick add mode
- Simplified product entry
- Product added successfully

---

## 4. Master/Employee Selection Tests

### TC-012: Master Autocomplete
**Objective**: Test master selection functionality
**Steps**:
1. Click on "Master" field
2. Type employee name
3. Select master from dropdown
4. Verify selection
**Expected Results**:
- Master dropdown appears
- Employees filtered by search
- Selected master appears in field
- Master ID stored for backend

### TC-013: Master Validation
**Objective**: Test master selection validation
**Steps**:
1. Leave master field empty
2. Try to create bill
3. Verify validation message
**Expected Results**:
- "Master Required" message appears
- Form prevents submission

---

## 5. Item Addition Tests

### TC-014: Add Single Item
**Objective**: Test adding a single item to bill
**Steps**:
1. Select product
2. Set quantity to 2
3. Set rate to 100
4. Click "Add" button
**Expected Results**:
- Item appears in bill table
- Quantity: 2, Rate: 100, Total: 200
- "Item Added" toast appears
- Form fields reset

### TC-015: Add Multiple Items
**Objective**: Test adding multiple items
**Steps**:
1. Add first item
2. Add second item
3. Add third item
4. Verify all items in table
**Expected Results**:
- All items appear in bill table
- Totals calculated correctly
- Each item shows "Item Added" toast

### TC-016: Item with Discount
**Objective**: Test item with discount
**Steps**:
1. Select product
2. Set quantity to 1
3. Set rate to 100
4. Set discount to 10
5. Click "Add"
**Expected Results**:
- Item added with discount
- Total calculated as (Rate × Qty) - Discount
- Discount column shows 10

### TC-017: Item with Advance Payment
**Objective**: Test item with advance payment
**Steps**:
1. Select product
2. Set advance to 50
3. Click "Add"
**Expected Results**:
- Item added with advance
- Advance column shows 50
- Balance calculated correctly

### TC-018: Item with VAT
**Objective**: Test VAT calculation
**Steps**:
1. Select product
2. Set VAT % to 10
3. Click "Add"
**Expected Results**:
- VAT calculated correctly
- VAT amount displayed
- Total includes VAT

### TC-019: Item Validation - Quantity
**Objective**: Test quantity validation
**Steps**:
1. Select product
2. Set quantity to 0
3. Click "Add"
**Expected Results**:
- "Please enter a valid quantity" message
- Form prevents submission

### TC-020: Item Validation - Rate
**Objective**: Test rate validation
**Steps**:
1. Select product
2. Set rate to 0
3. Click "Add"
**Expected Results**:
- "Please enter a valid price" message
- Form prevents submission

---

## 6. Bill Table Management Tests

### TC-021: Remove Item from Bill
**Objective**: Test removing items from bill
**Steps**:
1. Add multiple items to bill
2. Click "Remove" button on first item
3. Verify item removed
**Expected Results**:
- Item removed from table
- Totals recalculated
- Bill table updated

### TC-022: Edit Item in Bill
**Objective**: Test editing items in bill
**Steps**:
1. Add item to bill
2. Click "Edit" button
3. Modify quantity/rate
4. Save changes
**Expected Results**:
- Item opens in edit mode
- Changes saved successfully
- Totals recalculated

### TC-023: Bill Table Display
**Objective**: Verify bill table displays correctly
**Steps**:
1. Add multiple items with different configurations
2. Check table display
**Expected Results**:
- All columns visible (Product, Qty, Rate, Discount, Advance, VAT, Total, Actions)
- Data formatted correctly
- Totals calculated accurately

---

## 7. Payment and Totals Tests

### TC-024: Subtotal Calculation
**Objective**: Test subtotal calculation
**Steps**:
1. Add items: 2×100, 1×50, 1×200
2. Verify subtotal
**Expected Results**:
- Subtotal = 450 (2×100 + 1×50 + 1×200)

### TC-025: VAT Calculation
**Objective**: Test VAT calculation
**Steps**:
1. Add items with 5% VAT
2. Verify VAT amount
**Expected Results**:
- VAT calculated as 5% of subtotal
- VAT amount displayed correctly

### TC-026: Advance Payment Calculation
**Objective**: Test advance payment handling
**Steps**:
1. Add items with advance payments
2. Verify total advance
**Expected Results**:
- Total advance calculated
- Balance due calculated correctly

### TC-027: Final Total Calculation
**Objective**: Test final total calculation
**Steps**:
1. Add items with various configurations
2. Check final total
**Expected Results**:
- Final total = Subtotal + VAT - Total Advance
- All calculations accurate

---

## 8. Bill Creation Tests

### TC-028: Create Basic Bill
**Objective**: Test creating a basic bill
**Steps**:
1. Fill customer details
2. Select master
3. Add items
4. Click "WhatsApp" button
**Expected Results**:
- Bill created successfully
- WhatsApp window opens
- Form resets for new bill

### TC-029: Create Business Bill
**Objective**: Test creating business bill
**Steps**:
1. Select "Business" customer type
2. Fill business details (name, TRN, address)
3. Add items
4. Create bill
**Expected Results**:
- Business fields populated
- Bill created with business details
- TRN included in bill

### TC-030: Bill with Notes
**Objective**: Test bill with notes
**Steps**:
1. Add notes to bill
2. Create bill
3. Verify notes saved
**Expected Results**:
- Notes saved with bill
- Notes appear in bill details

### TC-031: Bill with Custom Dates
**Objective**: Test bill with custom dates
**Steps**:
1. Set custom bill date
2. Set custom delivery date
3. Set custom trial date
4. Create bill
**Expected Results**:
- All dates saved correctly
- Dates appear in bill details

---

## 9. WhatsApp Integration Tests

### TC-032: WhatsApp Message Generation
**Objective**: Test WhatsApp message generation
**Steps**:
1. Create bill with items
2. Click "WhatsApp" button
3. Verify WhatsApp window
**Expected Results**:
- WhatsApp window opens
- Message pre-filled with bill details
- Phone number included

### TC-033: WhatsApp Message Content
**Objective**: Verify WhatsApp message content
**Steps**:
1. Create bill with specific items
2. Generate WhatsApp message
3. Check message content
**Expected Results**:
- Bill number included
- Customer details included
- Item details included
- Total amount included
- Shop details included

---

## 10. Email Integration Tests

### TC-034: Email Bill Generation
**Objective**: Test email bill generation
**Steps**:
1. Create bill with items
2. Click "Email" button
3. Verify email functionality
**Expected Results**:
- Email modal appears
- Bill details included
- Email sent successfully

### TC-035: Email Validation
**Objective**: Test email validation
**Steps**:
1. Create bill without email
2. Try to send email
3. Verify validation
**Expected Results**:
- Email validation message
- Form prevents sending

---

## 11. Print Functionality Tests

### TC-036: Print Bill
**Objective**: Test bill printing
**Steps**:
1. Create bill with items
2. Click "Print" button
3. Verify print functionality
**Expected Results**:
- Print preview appears
- Bill formatted correctly
- Print dialog opens

### TC-037: Print Bill Content
**Objective**: Verify print content
**Steps**:
1. Create bill with specific details
2. Print bill
3. Check print content
**Expected Results**:
- All bill details included
- Items listed correctly
- Totals calculated accurately
- Shop details included

---

## 12. Search and Reprint Tests

### TC-038: Search Invoice
**Objective**: Test invoice search
**Steps**:
1. Click "Search & Reprint" button
2. Enter bill number
3. Search for invoice
**Expected Results**:
- Search modal appears
- Search results displayed
- Invoice details shown

### TC-039: Reprint Invoice
**Objective**: Test invoice reprinting
**Steps**:
1. Search for existing invoice
2. Click "Reprint" button
3. Verify reprint
**Expected Results**:
- Invoice reprinted successfully
- Same content as original

---

## 13. Form Reset Tests

### TC-040: Form Reset After Bill Creation
**Objective**: Test form reset after bill creation
**Steps**:
1. Create bill successfully
2. Verify form reset
**Expected Results**:
- All fields cleared
- Bill table empty
- New bill number generated
- Dates reset to defaults

### TC-041: Manual Form Reset
**Objective**: Test manual form reset
**Steps**:
1. Fill form with data
2. Click reset button (if available)
3. Verify form cleared
**Expected Results**:
- All fields cleared
- Form ready for new bill

---

## 14. Error Handling Tests

### TC-042: Network Error Handling
**Objective**: Test network error handling
**Steps**:
1. Disconnect network
2. Try to create bill
3. Verify error handling
**Expected Results**:
- Error message displayed
- User informed of issue
- Form remains functional

### TC-043: Server Error Handling
**Objective**: Test server error handling
**Steps**:
1. Simulate server error
2. Try to create bill
3. Verify error handling
**Expected Results**:
- Error message displayed
- User informed of issue
- Form remains functional

---

## 15. Mobile Responsiveness Tests

### TC-044: Mobile Layout
**Objective**: Test mobile responsiveness
**Steps**:
1. Resize browser to mobile size
2. Test billing form
3. Verify mobile layout
**Expected Results**:
- Form adapts to mobile size
- Touch targets appropriate
- No horizontal scrolling

### TC-045: Mobile Touch Interactions
**Objective**: Test mobile touch interactions
**Steps**:
1. Use mobile device or touch simulation
2. Test all form interactions
3. Verify touch functionality
**Expected Results**:
- All buttons touchable
- Dropdowns work on touch
- Form submission works

---

## 16. Performance Tests

### TC-046: Large Bill Performance
**Objective**: Test performance with large bills
**Steps**:
1. Add 50+ items to bill
2. Test form responsiveness
3. Create bill
**Expected Results**:
- Form remains responsive
- No lag in interactions
- Bill created successfully

### TC-047: Product Search Performance
**Objective**: Test product search performance
**Steps**:
1. Search with large product database
2. Test search speed
3. Verify results
**Expected Results**:
- Search results appear quickly
- No lag in typing
- Results accurate

---

## 17. Data Persistence Tests

### TC-048: Form Data Persistence
**Objective**: Test form data persistence
**Steps**:
1. Fill form partially
2. Navigate away and back
3. Check form state
**Expected Results**:
- Form data preserved (if intended)
- Or form cleared (if intended)

### TC-049: Bill Data Persistence
**Objective**: Test bill data persistence
**Steps**:
1. Create bill
2. Refresh page
3. Search for bill
**Expected Results**:
- Bill saved to database
- Bill retrievable after refresh

---

## 18. Accessibility Tests

### TC-050: Keyboard Navigation
**Objective**: Test keyboard navigation
**Steps**:
1. Navigate form using Tab key
2. Test all form elements
3. Verify keyboard functionality
**Expected Results**:
- All elements accessible via keyboard
- Tab order logical
- Enter key works for submission

### TC-051: Screen Reader Compatibility
**Objective**: Test screen reader compatibility
**Steps**:
1. Use screen reader
2. Navigate billing form
3. Verify accessibility
**Expected Results**:
- All elements have proper labels
- Form structure logical
- Error messages announced

---

## Test Data Requirements

### Sample Products
- Test Product 1 (Dry Cleaning - AED 100)
- Test Product 2 (Tailoring - AED 150)
- Test Product 3 (Laundry - AED 75)
- Test Print Function (Dry Cleaning - AED 200)

### Sample Customers
- John Doe (Mobile: 1234567890, City: Dubai, Area: Downtown)
- Jane Smith (Mobile: 0987654321, City: Abu Dhabi, Area: Marina)
- Business Customer (Mobile: 5555555555, TRN: 123456789, Business: Test Corp)

### Sample Employees/Masters
- Master Ahmed (ID: 1)
- Master Sarah (ID: 2)
- Master Mike (ID: 3)

---

## Test Execution Notes

### Prerequisites
1. Application running on localhost:5000
2. Database populated with test data
3. Selenium WebDriver configured
4. Chrome/Firefox browser available

### Test Execution Order
1. Run initialization tests first
2. Run form validation tests
3. Run functionality tests
4. Run integration tests
5. Run performance tests last

### Expected Test Results
- All tests should pass
- No JavaScript errors in console
- All API calls return 200 status
- Database operations successful

### Failure Criteria
- Any test case fails
- JavaScript errors in console
- API calls return error status
- Database operations fail
- UI elements not responding

---

## Maintenance Notes

### Regular Updates
- Update test data as application evolves
- Add new test cases for new features
- Remove obsolete test cases
- Update selectors if UI changes

### Test Environment
- Keep test environment isolated
- Use separate test database
- Reset test data between test runs
- Monitor test execution time

### Reporting
- Generate test execution reports
- Track test coverage metrics
- Document any test failures
- Maintain test case documentation 