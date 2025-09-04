# Configurable Input Fields Feature

## Overview

The Configurable Input Fields feature allows shop owners to customize which billing fields are available based on their business type. This makes the POS system more flexible and user-friendly for different types of businesses like Tailor Shops, Perfume Shops, Laundry Shops, etc.

## Features

### Configurable Fields

1. **Trial Date** - For fitting appointments (Tailor Shops)
2. **Delivery Date** - For order completion dates
3. **Advance Payment** - Allow partial payments vs full payment only
4. **Customer Notes** - Enable/disable customer notes field
5. **Employee Assignment** - Enable/disable master/employee assignment
6. **Default Delivery Days** - Set default delivery timeline

### Business Type Examples

#### Tailor Shops
- ✅ Trial Date: Enabled (for fittings)
- ✅ Delivery Date: Enabled (for completion)
- ✅ Advance Payment: Enabled (partial payments)
- ✅ Customer Notes: Enabled
- ✅ Employee Assignment: Enabled (masters/employees)

#### Perfume Shops
- ❌ Trial Date: Disabled (not applicable)
- ❌ Delivery Date: Disabled (immediate sales)
- ✅ Advance Payment: Enabled
- ✅ Customer Notes: Enabled
- ❌ Employee Assignment: Disabled (if not needed)

#### Laundry Shops
- ❌ Trial Date: Disabled (not applicable)
- ✅ Delivery Date: Enabled (for pickup)
- ✅ Advance Payment: Enabled
- ✅ Customer Notes: Enabled
- ❌ Employee Assignment: Disabled (if not needed)

## Database Schema

### New Fields Added to `shop_settings` Table

```sql
-- Configurable Input Fields
enable_trial_date BOOLEAN DEFAULT 1,
enable_delivery_date BOOLEAN DEFAULT 1,
enable_advance_payment BOOLEAN DEFAULT 1,
enable_customer_notes BOOLEAN DEFAULT 1,
enable_employee_assignment BOOLEAN DEFAULT 1,
default_delivery_days INTEGER DEFAULT 3,
city TEXT DEFAULT '',
area TEXT DEFAULT ''
```

## API Endpoints

### Get Billing Configuration
```
GET /api/shop-settings/billing-config
```

**Response:**
```json
{
  "success": true,
  "config": {
    "enable_trial_date": true,
    "enable_delivery_date": true,
    "enable_advance_payment": true,
    "enable_customer_notes": true,
    "enable_employee_assignment": true,
    "default_delivery_days": 3
  }
}
```

### Update Shop Settings (Enhanced)
```
PUT /api/shop-settings
```

**Request Body:**
```json
{
  "shop_name": "My Shop",
  "address": "Shop Address",
  "trn": "TRN123456",
  "city": "Dubai",
  "area": "Deira",
  "logo_url": "https://example.com/logo.png",
  "shop_mobile": "0501234567",
  "working_hours": "9 AM - 6 PM",
  "invoice_static_info": "Thank you for your business",
  "use_dynamic_invoice_template": true,
  "payment_mode": "advance",
  "enable_trial_date": true,
  "enable_delivery_date": true,
  "enable_advance_payment": true,
  "enable_customer_notes": true,
  "enable_employee_assignment": true,
  "default_delivery_days": 3
}
```

## Implementation Phases

### Phase 1: Database & API ✅
- [x] Database schema updates
- [x] Migration script
- [x] API endpoints for billing configuration
- [x] Enhanced shop settings API

### Phase 2: Shop Settings Interface
- [ ] Add billing configuration section to shop settings
- [ ] Toggle switches for each configurable field
- [ ] Default delivery days input
- [ ] Save/load configuration

### Phase 3: Dynamic Billing UI
- [ ] Hide/show billing fields based on configuration
- [ ] Update desktop billing interface
- [ ] Update mobile billing interface
- [ ] Maintain data integrity

### Phase 4: Mobile Integration
- [ ] Update mobile billing to respect field configuration
- [ ] Test on different screen sizes
- [ ] Ensure responsive design

## Usage

### For Shop Owners

1. **Access Shop Settings**
   - Go to Shop Settings in the main navigation
   - Find the "Billing Configuration" section

2. **Configure Fields**
   - Toggle each field on/off based on your business needs
   - Set default delivery days
   - Save settings

3. **Apply Changes**
   - Changes take effect immediately
   - Billing interface updates dynamically
   - Hidden fields are completely removed from the interface

### For Developers

1. **Check Field Configuration**
   ```javascript
   const response = await fetch('/api/shop-settings/billing-config');
   const { config } = await response.json();
   
   if (config.enable_trial_date) {
     // Show trial date field
   }
   ```

2. **Conditional Rendering**
   ```javascript
   // Example: Show/hide trial date field
   const trialDateField = document.getElementById('trialDate');
   if (trialDateField && billingConfig.enable_trial_date) {
     trialDateField.style.display = 'block';
   } else if (trialDateField) {
     trialDateField.style.display = 'none';
   }
   ```

## Migration

### Running the Migration

```bash
python migrate_configurable_fields.py
```

### What the Migration Does

1. **Adds New Columns** to `shop_settings` table
2. **Sets Default Values** for existing records
3. **Preserves Existing Data** - no data loss
4. **Handles Errors** gracefully

### Rollback (if needed)

```sql
-- Remove configurable fields (if needed)
ALTER TABLE shop_settings DROP COLUMN enable_trial_date;
ALTER TABLE shop_settings DROP COLUMN enable_delivery_date;
ALTER TABLE shop_settings DROP COLUMN enable_advance_payment;
ALTER TABLE shop_settings DROP COLUMN enable_customer_notes;
ALTER TABLE shop_settings DROP COLUMN enable_employee_assignment;
ALTER TABLE shop_settings DROP COLUMN default_delivery_days;
```

## Benefits

1. **Business Flexibility** - Adapt to different business types
2. **User Experience** - Only show relevant fields
3. **Reduced Complexity** - Hide unnecessary options
4. **Future-Proof** - Easy to add more configurable fields
5. **Data Integrity** - Prevent invalid data entry

## Future Enhancements

1. **Business Type Templates** - Pre-configured settings for common business types
2. **Field Dependencies** - Some fields depend on others being enabled
3. **Custom Field Labels** - Allow shops to rename fields
4. **Field Validation Rules** - Custom validation per business type
5. **Import/Export Settings** - Share configurations between shops

## Testing

### Test Cases

1. **Default Configuration** - All fields enabled
2. **Perfume Shop** - Disable trial_date and delivery_date
3. **Laundry Shop** - Disable trial_date, keep delivery_date
4. **Tailor Shop** - All fields enabled
5. **Edge Cases** - Invalid configurations, missing data

### Test Scenarios

1. **Field Visibility** - Hidden fields should not appear in UI
2. **Data Persistence** - Settings should save and load correctly
3. **API Responses** - All endpoints should return correct data
4. **Mobile Responsiveness** - Works on all screen sizes
5. **Performance** - No impact on billing performance

## Support

For issues or questions about the Configurable Input Fields feature:

1. Check this documentation
2. Review the API endpoints
3. Test with different configurations
4. Check browser console for errors
5. Verify database migration completed successfully
