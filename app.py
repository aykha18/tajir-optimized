from flask import Flask, request
import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

import logging
from api.logging_config import setup_logging
from db.init import init_db
from api.customers import customers_api
from api.products import products_api
from api.bills import bills_api
from api.employees import employees_api
from api.analytics import analytics_api, analytics_pages
from api.shop_settings import shop_settings_api
from api.expenses import expenses_api
from api.admin import admin_api
from api.catalog import catalog_api
from api.plans import plans_api
from api.subscriptions import subscriptions_api
from api.auth import auth_api
from api.reports import reports_api
from api.email import email_api
from api.setup import setup_api
from api.i18n import i18n_api
from api.whatsapp import whatsapp_api
from api.loyalty import loyalty_api
from api.ocr import ocr_api, setup_ocr
from api.ai import ai_api
from api.pages import pages_api

def create_app():
    logger = setup_logging()
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    @app.after_request
    def after_request(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    app.register_blueprint(customers_api)
    app.register_blueprint(products_api)
    app.register_blueprint(bills_api)
    app.register_blueprint(employees_api)
    app.register_blueprint(analytics_api)
    app.register_blueprint(analytics_pages)
    app.register_blueprint(shop_settings_api)
    app.register_blueprint(expenses_api)
    app.register_blueprint(admin_api)
    app.register_blueprint(catalog_api)
    app.register_blueprint(plans_api)
    app.register_blueprint(subscriptions_api)
    app.register_blueprint(auth_api)
    app.register_blueprint(reports_api)
    app.register_blueprint(email_api)
    app.register_blueprint(setup_api)
    app.register_blueprint(ai_api)
    app.register_blueprint(i18n_api)
    app.register_blueprint(whatsapp_api)
    app.register_blueprint(loyalty_api)
    app.register_blueprint(ocr_api)
    app.register_blueprint(pages_api)
    @app.route('/app', endpoint='app_page')
    def app_page_alias():
        from flask import redirect, url_for
        return redirect(url_for('pages_api.app_page'))
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://images.unsplash.com https://*.unsplash.com; "
            "connect-src 'self' https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net https://images.unsplash.com https://*.unsplash.com; "
            "worker-src 'self' blob:; "
            "child-src 'self' blob:;"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        return response
    return app


if __name__ == '__main__':
    app = create_app()
    setup_ocr()
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
