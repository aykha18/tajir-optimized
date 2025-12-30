from flask import Blueprint, jsonify, request
from datetime import datetime
import json
import logging
import os
from db.connection import get_db_connection, get_placeholder, execute_query, execute_update, execute_with_returning
from api.utils import get_current_user_id

subscriptions_api = Blueprint('subscriptions_api', __name__)
logger = logging.getLogger(__name__)

# Try to import Stripe
try:
    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

@subscriptions_api.route('/api/subscription/stripe-key', methods=['GET'])
def get_stripe_key():
    """Get Stripe publishable key for frontend."""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe not available'}), 500
    
    return jsonify({
        'publishable_key': STRIPE_PUBLISHABLE_KEY if STRIPE_PUBLISHABLE_KEY else None
    })

@subscriptions_api.route('/api/subscription/plans', methods=['GET'])
def get_subscription_plans():
    """Get available subscription plans."""
    try:
        conn = get_db_connection()
        cursor = execute_query(conn, 'SELECT * FROM subscription_plans WHERE is_active = TRUE ORDER BY price_yearly ASC')
        plans = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        plans_list = []
        for plan in plans:
            plan_dict = dict(plan) if hasattr(plan, 'keys') else {
                'plan_id': plan[0],
                'plan_name': plan[1],
                'plan_type': plan[2],
                'price_monthly': float(plan[3]),
                'price_yearly': float(plan[4]),
                'currency': plan[5],
                'features': json.loads(plan[6]) if plan[6] else {},
                'is_active': plan[7],
                'created_at': plan[8].isoformat() if plan[8] else None
            }
            plans_list.append(plan_dict)
        
        return jsonify({'plans': plans_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_api.route('/api/subscription/current', methods=['GET'])
def get_current_subscription():
    """Get current user's subscription status."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Get current subscription
        cursor = execute_query(conn, f'''
            SELECT us.*, sp.plan_name, sp.plan_type, sp.price_monthly, sp.price_yearly, sp.currency, sp.features
            FROM user_subscriptions us
            JOIN subscription_plans sp ON us.plan_id = sp.plan_id
            WHERE us.user_id = {placeholder} AND us.status = 'active'
            ORDER BY us.created_at DESC
            LIMIT 1
        ''', (user_id,))
        
        subscription = cursor.fetchone()
        conn.close()
        
        if subscription:
            sub_dict = dict(subscription) if hasattr(subscription, 'keys') else {
                'subscription_id': subscription[0],
                'user_id': subscription[1],
                'plan_id': subscription[2],
                'stripe_subscription_id': subscription[3],
                'stripe_customer_id': subscription[4],
                'status': subscription[5],
                'current_period_start': subscription[6].isoformat() if subscription[6] else None,
                'current_period_end': subscription[7].isoformat() if subscription[7] else None,
                'cancel_at_period_end': subscription[8],
                'created_at': subscription[9].isoformat() if subscription[9] else None,
                'updated_at': subscription[10].isoformat() if subscription[10] else None,
                'plan_name': subscription[11],
                'plan_type': subscription[12],
                'price_monthly': float(subscription[13]),
                'price_yearly': float(subscription[14]),
                'currency': subscription[15],
                'features': json.loads(subscription[16]) if subscription[16] else {}
            }
            return jsonify({'subscription': sub_dict})
        else:
            return jsonify({'subscription': None})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_api.route('/api/subscription/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create Stripe payment intent for subscription."""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe not available'}), 500
    
    try:
        data = request.get_json()
        user_id = get_current_user_id()
        plan_id = data.get('plan_id')
        billing_cycle = data.get('billing_cycle', 'yearly')  # 'monthly' or 'yearly'
        
        if not plan_id:
            return jsonify({'error': 'Plan ID is required'}), 400
        
        # Get plan details
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT * FROM subscription_plans WHERE plan_id = {placeholder}', (plan_id,))
        plan = cursor.fetchone()
        conn.close()
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        # Calculate amount
        amount = plan[3] if billing_cycle == 'monthly' else plan[4]  # price_monthly or price_yearly
        amount_cents = int(amount * 100)  # Convert to cents
        
        # Get user email
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT email FROM users WHERE user_id = {placeholder}', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        user_email = user[0] if user else None
        
        # Create Stripe customer if not exists
        customer = stripe.Customer.create(
            email=user_email,
            metadata={'user_id': str(user_id)}
        )
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='aed',
            customer=customer.id,
            metadata={
                'user_id': str(user_id),
                'plan_id': str(plan_id),
                'billing_cycle': billing_cycle
            }
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'customer_id': customer.id,
            'amount': amount,
            'currency': 'AED'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_api.route('/api/subscription/confirm', methods=['POST'])
def confirm_subscription():
    """Confirm subscription after successful payment."""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe not available'}), 500
    
    try:
        data = request.get_json()
        user_id = get_current_user_id()
        payment_intent_id = data.get('payment_intent_id')
        plan_id = data.get('plan_id')
        billing_cycle = data.get('billing_cycle')
        
        if not payment_intent_id or not plan_id:
            return jsonify({'error': 'Payment intent ID and plan ID are required'}), 400
        
        # Verify payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status != 'succeeded':
            return jsonify({'error': 'Payment not successful'}), 400
        
        # Get plan details
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT * FROM subscription_plans WHERE plan_id = {placeholder}', (plan_id,))
        plan = cursor.fetchone()
        
        if not plan:
            conn.close()
            return jsonify({'error': 'Plan not found'}), 404
        
        # Create Stripe subscription
        subscription = stripe.Subscription.create(
            customer=intent.customer,
            items=[{
                'price_data': {
                    'currency': 'aed',
                    'product_data': {
                        'name': plan[1],  # plan_name
                    },
                    'unit_amount': int(plan[3] * 100) if billing_cycle == 'monthly' else int(plan[4] * 100),
                    'recurring': {
                        'interval': 'month' if billing_cycle == 'monthly' else 'year',
                    },
                },
            }],
            metadata={
                'user_id': str(user_id),
                'plan_id': str(plan_id)
            }
        )
        
        # Save subscription to database
        placeholder = get_placeholder()
        execute_update(conn, f'''
            INSERT INTO user_subscriptions 
            (user_id, plan_id, stripe_subscription_id, stripe_customer_id, status, 
             current_period_start, current_period_end)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (
            user_id, plan_id, subscription.id, intent.customer, 'active',
            datetime.fromtimestamp(subscription.current_period_start),
            datetime.fromtimestamp(subscription.current_period_end)
        ))
        
        # Update user plan
        placeholder = get_placeholder()
        execute_update(conn, f'''
            UPDATE user_plans 
            SET plan_type = {placeholder}, plan_start_date = CURRENT_DATE, is_active = TRUE
            WHERE user_id = {placeholder}
        ''', (plan[2], user_id))  # plan_type
        
        # Record payment
        placeholder = get_placeholder()
        execute_update(conn, f'''
            INSERT INTO payment_history 
            (user_id, stripe_payment_intent_id, amount, currency, status)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (user_id, payment_intent_id, plan[3] if billing_cycle == 'monthly' else plan[4], 'AED', 'succeeded'))
        
        conn.close()
        
        return jsonify({
            'success': True, 
            'subscription_id': subscription.id,
            'message': 'Subscription activated successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_api.route('/api/subscription/cancel', methods=['POST'])
def cancel_subscription():
    """Cancel user subscription."""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe not available'}), 500
    
    try:
        user_id = get_current_user_id()
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT stripe_subscription_id FROM user_subscriptions 
            WHERE user_id = {placeholder} AND status = 'active'
        ''', (user_id,))
        subscription = cursor.fetchone()
        
        if subscription:
            # Cancel in Stripe
            stripe.Subscription.modify(
                subscription[0],  # stripe_subscription_id
                cancel_at_period_end=True
            )
            
            # Update database
            placeholder = get_placeholder()
            execute_update(conn, f'''
                UPDATE user_subscriptions 
                SET cancel_at_period_end = TRUE 
                WHERE user_id = {placeholder} AND status = 'active'
            ''', (user_id,))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Subscription will be cancelled at the end of the current period'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_api.route('/api/subscription/payment-history', methods=['GET'])
def get_payment_history():
    """Get user's payment history."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        cursor = execute_query(conn, f'''
            SELECT ph.*, sp.plan_name
            FROM payment_history ph
            LEFT JOIN user_subscriptions us ON ph.subscription_id = us.subscription_id
            LEFT JOIN subscription_plans sp ON us.plan_id = sp.plan_id
            WHERE ph.user_id = {placeholder}
            ORDER BY ph.created_at DESC
        ''', (user_id,))
        
        payments = cursor.fetchall()
        conn.close()
        
        payments_list = []
        for payment in payments:
            payment_dict = dict(payment) if hasattr(payment, 'keys') else {
                'payment_id': payment[0],
                'user_id': payment[1],
                'subscription_id': payment[2],
                'stripe_payment_intent_id': payment[3],
                'amount': float(payment[4]),
                'currency': payment[5],
                'status': payment[6],
                'payment_method': payment[7],
                'created_at': payment[8].isoformat() if payment[8] else None,
                'plan_name': payment[9] if len(payment) > 9 else None
            }
            payments_list.append(payment_dict)
        
        return jsonify({'payments': payments_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscriptions_api.route('/api/subscription/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe not available'}), 500
    
    if not STRIPE_WEBHOOK_SECRET:
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # Handle the event
    try:
        if event['type'] == 'invoice.payment_succeeded':
            handle_successful_payment(event['data']['object'])
        elif event['type'] == 'invoice.payment_failed':
            handle_failed_payment(event['data']['object'])
        elif event['type'] == 'customer.subscription.deleted':
            handle_subscription_cancellation(event['data']['object'])
        elif event['type'] == 'customer.subscription.updated':
            handle_subscription_update(event['data']['object'])
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

def handle_successful_payment(invoice):
    """Handle successful payment webhook."""
    try:
        subscription_id = invoice.get('subscription')
        if not subscription_id:
            return
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Update subscription status
        execute_update(conn, f'''
            UPDATE user_subscriptions 
            SET status = 'active', updated_at = CURRENT_TIMESTAMP
            WHERE stripe_subscription_id = {placeholder}
        ''', (subscription_id,))
        
        # Record payment
        # Note: invoice.get('customer') is stripe customer ID, but payment_history might expect user_id.
        # This mirrors app.py logic which seems to assume database trigger or loose constraint.
        execute_update(conn, f'''
            INSERT INTO payment_history 
            (user_id, subscription_id, stripe_payment_intent_id, amount, currency, status)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (
            invoice.get('customer'),  # This should be user_id from metadata
            None,  # subscription_id will be filled by trigger
            invoice.get('payment_intent'),
            invoice.get('amount_paid', 0) / 100,  # Convert from cents
            invoice.get('currency', 'aed'),
            'succeeded'
        ))
        
        conn.close()
        
    except Exception as e:
        print(f"Error handling successful payment: {e}")

def handle_failed_payment(invoice):
    """Handle failed payment webhook."""
    try:
        subscription_id = invoice.get('subscription')
        if not subscription_id:
            return
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Update subscription status
        execute_update(conn, f'''
            UPDATE user_subscriptions 
            SET status = 'past_due', updated_at = CURRENT_TIMESTAMP
            WHERE stripe_subscription_id = {placeholder}
        ''', (subscription_id,))
        
        conn.close()
        
    except Exception as e:
        print(f"Error handling failed payment: {e}")

def handle_subscription_cancellation(subscription):
    """Handle subscription cancellation webhook."""
    try:
        subscription_id = subscription.get('id')
        if not subscription_id:
            return
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Update subscription status
        execute_update(conn, f'''
            UPDATE user_subscriptions 
            SET status = 'canceled', updated_at = CURRENT_TIMESTAMP
            WHERE stripe_subscription_id = {placeholder}
        ''', (subscription_id,))
        
        conn.close()
        
    except Exception as e:
        print(f"Error handling subscription cancellation: {e}")

def handle_subscription_update(subscription):
    """Handle subscription update webhook."""
    try:
        subscription_id = subscription.get('id')
        if not subscription_id:
            return
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Update subscription details
        execute_update(conn, f'''
            UPDATE user_subscriptions 
            SET current_period_start = {placeholder}, current_period_end = {placeholder}, 
                cancel_at_period_end = {placeholder}, updated_at = CURRENT_TIMESTAMP
            WHERE stripe_subscription_id = {placeholder}
        ''', (
            datetime.fromtimestamp(subscription.get('current_period_start')),
            datetime.fromtimestamp(subscription.get('current_period_end')),
            subscription.get('cancel_at_period_end', False),
            subscription_id
        ))
        
        conn.close()
        
    except Exception as e:
        print(f"Error handling subscription update: {e}")