from flask import Blueprint, session, request, jsonify

i18n_api = Blueprint('i18n_api', __name__)

@i18n_api.route('/api/language/switch', methods=['POST'])
def switch_language():
    """Switch user language preference"""
    try:
        data = request.get_json()
        language = data.get('language', 'en')
        
        if language not in ['en', 'ar']:
            return jsonify({'error': 'Invalid language'}), 400
        
        set_user_language(language)
        
        return jsonify({
            'success': True, 
            'language': language,
            'message': get_translated_text('language_switched', language)
        })
        
    except Exception as e:
        print(f"DEBUG: Error in switch_language: {e}")
        return jsonify({'error': 'Failed to switch language'}), 500

@i18n_api.route('/api/language/current', methods=['GET'])
def get_current_language():
    """Get current user language preference"""
    try:
        language = get_user_language()
        return jsonify({
            'success': True,
            'language': language,
            'is_rtl': language == 'ar'
        })
        
    except Exception as e:
        print(f"DEBUG: Error in get_current_language: {e}")
        return jsonify({'error': 'Failed to get language preference'}), 500

def number_to_arabic_words(number):
    """Convert number to Arabic words"""
    if number == 0:
        return "صفر"
    
    # Arabic number words
    ones = {
        0: "", 1: "واحد", 2: "اثنان", 3: "ثلاثة", 4: "أربعة", 5: "خمسة",
        6: "ستة", 7: "سبعة", 8: "ثمانية", 9: "تسعة", 10: "عشرة",
        11: "أحد عشر", 12: "اثنا عشر", 13: "ثلاثة عشر", 14: "أربعة عشر", 15: "خمسة عشر",
        16: "ستة عشر", 17: "سبعة عشر", 18: "ثمانية عشر", 19: "تسعة عشر"
    }
    
    tens = {
        2: "عشرون", 3: "ثلاثون", 4: "أربعون", 5: "خمسون",
        6: "ستون", 7: "سبعون", 8: "ثمانون", 9: "تسعون"
    }
    
    hundreds = {
        1: "مائة", 2: "مئتان", 3: "ثلاثمائة", 4: "أربعمائة", 5: "خمسمائة",
        6: "ستمائة", 7: "سبعمائة", 8: "ثمانمائة", 9: "تسعمائة"
    }
    
    def convert_less_than_one_thousand(n):
        if n == 0:
            return ""
        
        if n < 20:
            return ones[n]
        
        if n < 100:
            if n % 10 == 0:
                return tens[n // 10]
            else:
                return ones[n % 10] + " و " + tens[n // 10]
        
        if n < 1000:
            if n % 100 == 0:
                return hundreds[n // 100]
            else:
                return hundreds[n // 100] + " و " + convert_less_than_one_thousand(n % 100)
    
    # Split into integer and decimal parts
    integer_part = int(number)
    decimal_part = round((number - integer_part) * 100)
    
    # Convert integer part
    if integer_part == 0:
        result = "صفر"
    elif integer_part < 1000:
        result = convert_less_than_one_thousand(integer_part)
    else:
        # Handle thousands
        thousands_count = integer_part // 1000
        remainder = integer_part % 1000
        
        if thousands_count == 1:
            result = "ألف"
        elif thousands_count == 2:
            result = "ألفان"
        elif thousands_count < 11:
            result = ones[thousands_count] + " آلاف"
        else:
            result = convert_less_than_one_thousand(thousands_count) + " ألف"
        
        if remainder > 0:
            result += " و " + convert_less_than_one_thousand(remainder)
    
    # Add currency
    result += " درهم"
    
    # Add decimal part if exists
    if decimal_part > 0:
        if decimal_part == 1:
            result += " و فلس واحد"
        else:
            result += " و " + convert_less_than_one_thousand(decimal_part) + " فلس"
    
    result += " فقط"
    return result

def get_user_language():
    """Get user's preferred language from session or default to English"""
    return session.get('language', 'en')

def set_user_language(language):
    """Set user's preferred language in session"""
    session['language'] = language

def translate_text(text, language='en'):
    """Translate text based on language"""
    translations = {
        'en': {
            # Navigation
            'app': 'App',
            'pricing': 'Pricing',
            'professional_business_management': 'Professional Business Management',
            'sign_in': 'Sign In',
            'sign_up': 'Sign Up',
            'logout': 'Logout',
            
            # Dashboard
            'dashboard': 'Dashboard',
            'total_revenue': 'Total Revenue',
            'total_bills': 'Total Bills',
            'total_customers': 'Total Customers',
            'total_products': 'Total Products',
            'recent_bills': 'Recent Bills',
            'top_products': 'Top Products',
            'employee_performance': 'Employee Performance',
            
            # Operations
            'operations': 'Operations',
            'billing': 'Billing',
            'products': 'Products',
            'customers': 'Customers',
            'employees': 'Employees',
            'vat_rates': 'VAT Rates',
            'advanced_reports': 'Advanced Reports',
            'shop_settings': 'Shop Settings',
            
            # Common Actions
            'add': 'Add',
            'edit': 'Edit',
            'delete': 'Delete',
            'save': 'Save',
            'cancel': 'Cancel',
            'close': 'Close',
            'search': 'Search',
            'filter': 'Filter',
            'download': 'Download',
            'print': 'Print',
            'preview': 'Preview',
            
            # Status
            'pending': 'Pending',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
            'paid': 'Paid',
            'unpaid': 'Unpaid',
            
            # Messages
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information',
            'loading': 'Loading...',
            'no_data_found': 'No data found',
            'are_you_sure': 'Are you sure?',
            'this_action_cannot_be_undone': 'This action cannot be undone',
            
            # Forms
            'name': 'Name',
            'phone': 'Phone',
            'email': 'Email',
            'address': 'Address',
            'city': 'City',
            'area': 'Area',
            'position': 'Position',
            'rate': 'Rate',
            'quantity': 'Quantity',
            'total': 'Total',
            'subtotal': 'Subtotal',
            'vat': 'VAT',
            'discount': 'Discount',
            'advance_paid': 'Advance Paid',
            'balance': 'Balance',
            'payment_method': 'Payment Method',
            'cash': 'Cash',
            'card': 'Card',
            'bank_transfer': 'Bank Transfer',
            
            # Reports
            'invoices': 'Invoices',
            'employees': 'Employees',
            'products': 'Products',
            'from_date': 'From Date',
            'to_date': 'To Date',
            'bill_number': 'Bill #',
            'bill_date': 'Bill Date',
            'delivery_date': 'Delivery Date',
            'customer_name': 'Customer Name',
            'status': 'Status',
            'amount': 'Amount',
            'revenue': 'Revenue',
            'performance': 'Performance',
            
            # Setup Wizard
            'shop_type': 'Shop Type',
            'shop_name': 'Shop Name',
            'contact_number': 'Contact Number',
            'choose_plan': 'Choose Plan',
            'trial': 'Trial',
            'basic': 'Basic',
            'pro': 'Pro',
            'days': 'Days',
            'year': 'Year',
            'next': 'Next',
            'previous': 'Previous',
            'finish': 'Finish',
            
            # Plans
            'trial_plan': 'Trial Plan',
            'basic_plan': 'Basic Plan',
            'pro_plan': 'Pro Plan',
            'enterprise_plan': 'Enterprise Plan',
            'features': 'Features',
            'upgrade': 'Upgrade',
            'current_plan': 'Current Plan',
            'plan_expires': 'Plan Expires',
            'unlimited': 'Unlimited',
            'limited': 'Limited',
            
            # Settings
            'settings': 'Settings',
            'logo_url': 'Logo URL',
            'working_hours': 'Working Hours',
            'static_info': 'Static Information',
            'invoice_template': 'Invoice Template',
            'dynamic_template': 'Dynamic Template',
            'static_template': 'Static Template',
            
            # Authentication
            'login': 'Login',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            'forgot_password': 'Forgot Password?',
            'remember_me': 'Remember Me',
            'dont_have_account': "Don't have an account?",
            'already_have_account': 'Already have an account?',
            'sign_up_here': 'Sign up here',
            'sign_in_here': 'Sign in here',
            'mobile_login': 'Mobile Login',
            'otp': 'OTP',
            'send_otp': 'Send OTP',
            'verify_otp': 'Verify OTP',
            'shop_code': 'Shop Code',
            'enter_shop_code': 'Enter Shop Code',
            
            # Currency
            'aed': 'AED',
            'dirhams': 'Dirhams',
            'fils': 'Fils',
            'only': 'Only',
            
            # Time
            'today': 'Today',
            'yesterday': 'Yesterday',
            'this_week': 'This Week',
            'this_month': 'This Month',
            'this_year': 'This Year',
            'last_week': 'Last Week',
            'last_month': 'Last Month',
            'last_year': 'Last Year',
            
            # Charts
            'sales': 'Sales',
            'revenue_chart': 'Revenue Chart',
            'sales_chart': 'Sales Chart',
            'performance_chart': 'Performance Chart',
            'heatmap': 'Heatmap',
            
            # Notifications
            'notification': 'Notification',
            'notifications': 'Notifications',
            'new_bill': 'New Bill',
            'payment_received': 'Payment Received',
            'low_stock': 'Low Stock',
            'expiring_plan': 'Expiring Plan',
            
            # Help
            'help': 'Help',
            'support': 'Support',
            'documentation': 'Documentation',
            'contact_us': 'Contact Us',
            'feedback': 'Feedback',
            'bug_report': 'Bug Report',
            'feature_request': 'Feature Request',
            
            # Language
            'language': 'Language',
            'english': 'English',
            'arabic': 'Arabic',
            'switch_language': 'Switch Language',
            
            # Default text
            'default': text
        },
        'ar': {
            # Navigation
            'app': 'التطبيق',
            'pricing': 'الأسعار',
            'professional_business_management': 'إدارة الأعمال الاحترافية',
            'sign_in': 'تسجيل الدخول',
            'sign_up': 'إنشاء حساب',
            'logout': 'تسجيل الخروج',
            
            # Dashboard
            'dashboard': 'لوحة التحكم',
            'total_revenue': 'إجمالي الإيرادات',
            'total_bills': 'إجمالي الفواتير',
            'total_customers': 'إجمالي العملاء',
            'total_products': 'إجمالي المنتجات',
            'recent_bills': 'الفواتير الحديثة',
            'top_products': 'أفضل المنتجات',
            'employee_performance': 'أداء الموظفين',
            
            # Operations
            'operations': 'العمليات',
            'billing': 'الفواتير',
            'products': 'المنتجات',
            'customers': 'العملاء',
            'employees': 'الموظفون',
            'vat_rates': 'معدلات الضريبة',
            'advanced_reports': 'التقارير المتقدمة',
            'shop_settings': 'إعدادات المتجر',
            
            # Common Actions
            'add': 'إضافة',
            'edit': 'تعديل',
            'delete': 'حذف',
            'save': 'حفظ',
            'cancel': 'إلغاء',
            'close': 'إغلاق',
            'search': 'بحث',
            'filter': 'تصفية',
            'download': 'تحميل',
            'print': 'طباعة',
            'preview': 'معاينة',
            
            # Status
            'pending': 'قيد الانتظار',
            'completed': 'مكتمل',
            'cancelled': 'ملغي',
            'paid': 'مدفوع',
            'unpaid': 'غير مدفوع',
            
            # Messages
            'success': 'نجح',
            'error': 'خطأ',
            'warning': 'تحذير',
            'info': 'معلومات',
            'loading': 'جاري التحميل...',
            'no_data_found': 'لم يتم العثور على بيانات',
            'are_you_sure': 'هل أنت متأكد؟',
            'this_action_cannot_be_undone': 'لا يمكن التراجع عن هذا الإجراء',
            
            # Forms
            'name': 'الاسم',
            'phone': 'الهاتف',
            'email': 'البريد الإلكتروني',
            'address': 'العنوان',
            'city': 'المدينة',
            'area': 'المنطقة',
            'position': 'المنصب',
            'rate': 'السعر',
            'quantity': 'الكمية',
            'total': 'الإجمالي',
            'subtotal': 'المجموع الفرعي',
            'vat': 'الضريبة',
            'discount': 'الخصم',
            'advance_paid': 'المدفوع مسبقاً',
            'balance': 'الرصيد',
            'payment_method': 'طريقة الدفع',
            'cash': 'نقداً',
            'card': 'بطاقة',
            'bank_transfer': 'تحويل بنكي',
            
            # Reports
            'invoices': 'الفواتير',
            'employees': 'الموظفون',
            'products': 'المنتجات',
            'from_date': 'من تاريخ',
            'to_date': 'إلى تاريخ',
            'bill_number': 'رقم الفاتورة',
            'bill_date': 'تاريخ الفاتورة',
            'delivery_date': 'تاريخ التسليم',
            'customer_name': 'اسم العميل',
            'status': 'الحالة',
            'amount': 'المبلغ',
            'revenue': 'الإيرادات',
            'performance': 'الأداء',
            
            # Setup Wizard
            'shop_type': 'نوع المتجر',
            'shop_name': 'اسم المتجر',
            'contact_number': 'رقم الاتصال',
            'choose_plan': 'اختر الخطة',
            'trial': 'تجريبي',
            'basic': 'أساسي',
            'pro': 'احترافي',
            'days': 'أيام',
            'year': 'سنة',
            'next': 'التالي',
            'previous': 'السابق',
            'finish': 'إنهاء',
            
            # Plans
            'trial_plan': 'الخطة التجريبية',
            'basic_plan': 'الخطة الأساسية',
            'pro_plan': 'الخطة الاحترافية',
            'enterprise_plan': 'خطة المؤسسة',
            'features': 'الميزات',
            'upgrade': 'ترقية',
            'current_plan': 'الخطة الحالية',
            'plan_expires': 'تنتهي الخطة',
            'unlimited': 'غير محدود',
            'limited': 'محدود',
            
            # Settings
            'settings': 'الإعدادات',
            'logo_url': 'رابط الشعار',
            'working_hours': 'ساعات العمل',
            'static_info': 'معلومات ثابتة',
            'invoice_template': 'قالب الفاتورة',
            'dynamic_template': 'قالب ديناميكي',
            'static_template': 'قالب ثابت',
            
            # Authentication
            'login': 'تسجيل الدخول',
            'password': 'كلمة المرور',
            'confirm_password': 'تأكيد كلمة المرور',
            'forgot_password': 'نسيت كلمة المرور؟',
            'remember_me': 'تذكرني',
            'dont_have_account': 'ليس لديك حساب؟',
            'already_have_account': 'لديك حساب بالفعل؟',
            'sign_up_here': 'إنشاء حساب هنا',
            'sign_in_here': 'تسجيل الدخول هنا',
            'mobile_login': 'تسجيل الدخول بالجوال',
            'otp': 'رمز التحقق',
            'send_otp': 'إرسال رمز التحقق',
            'verify_otp': 'التحقق من الرمز',
            'shop_code': 'رمز المتجر',
            'enter_shop_code': 'أدخل رمز المتجر',
            
            # Currency
            'aed': 'درهم',
            'dirhams': 'دراهم',
            'fils': 'فلس',
            'only': 'فقط',
            
            # Time
            'today': 'اليوم',
            'yesterday': 'أمس',
            'this_week': 'هذا الأسبوع',
            'this_month': 'هذا الشهر',
            'this_year': 'هذا العام',
            'last_week': 'الأسبوع الماضي',
            'last_month': 'الشهر الماضي',
            'last_year': 'العام الماضي',
            
            # Charts
            'sales': 'المبيعات',
            'revenue_chart': 'رسم بياني للإيرادات',
            'sales_chart': 'رسم بياني للمبيعات',
            'performance_chart': 'رسم بياني للأداء',
            'heatmap': 'خريطة حرارية',
            
            # Notifications
            'notification': 'إشعار',
            'notifications': 'الإشعارات',
            'new_bill': 'فاتورة جديدة',
            'payment_received': 'تم استلام الدفع',
            'low_stock': 'المخزون منخفض',
            'expiring_plan': 'الخطة تنتهي قريباً',
            
            # Help
            'help': 'المساعدة',
            'support': 'الدعم',
            'documentation': 'الوثائق',
            'contact_us': 'اتصل بنا',
            'feedback': 'التعليقات',
            'bug_report': 'تقرير خطأ',
            'feature_request': 'طلب ميزة',
            
            # Language
            'language': 'اللغة',
            'english': 'الإنجليزية',
            'arabic': 'العربية',
            'switch_language': 'تغيير اللغة',
            
            # Default text
            'default': text
        }
    }
    
    return translations.get(language, {}).get(text, text)

def get_translated_text(text, language=None):
    """Get translated text for current user language"""
    if language is None:
        language = get_user_language()
    return translate_text(text, language)
