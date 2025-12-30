from flask import Blueprint, request, jsonify, session
import logging
import json
from db.connection import get_db_connection, get_placeholder, execute_query, execute_update
from api.utils import get_current_user_id
from difflib import SequenceMatcher

catalog_api = Blueprint('catalog_api', __name__)
logger = logging.getLogger(__name__)

# Helper Functions
def analyze_catalog_data(catalog_data):
    """Analyze catalog data to extract patterns and categories"""
    analysis = {
        'total_items': len(catalog_data),
        'categories': {},
        'price_ranges': {},
        'common_patterns': []
    }
    
    for item in catalog_data:
        name = item.get('name', '').lower()
        price = item.get('price', 0)
        category = item.get('category', '')
        
        # Analyze by category
        if category:
            if category not in analysis['categories']:
                analysis['categories'][category] = {
                    'count': 0,
                    'avg_price': 0,
                    'min_price': float('inf'),
                    'max_price': 0,
                    'products': []
                }
            
            cat_data = analysis['categories'][category]
            cat_data['count'] += 1
            cat_data['products'].append({
                'name': item.get('name', ''),
                'price': price,
                'description': item.get('description', '')
            })
            
            # Update price statistics
            total_price = cat_data['avg_price'] * (cat_data['count'] - 1) + price
            cat_data['avg_price'] = total_price / cat_data['count']
            cat_data['min_price'] = min(cat_data['min_price'], price)
            cat_data['max_price'] = max(cat_data['max_price'], price)
        
        # Analyze price ranges
        price_range = get_price_range(price)
        if price_range not in analysis['price_ranges']:
            analysis['price_ranges'][price_range] = 0
        analysis['price_ranges'][price_range] += 1
        
        # Extract common patterns from product names
        patterns = extract_name_patterns(name)
        analysis['common_patterns'].extend(patterns)
    
    # Remove duplicates from patterns
    analysis['common_patterns'] = list(set(analysis['common_patterns']))
    
    return analysis

def get_price_range(price):
    """Categorize price into ranges"""
    if price <= 10:
        return 'Budget (≤10)'
    elif price <= 25:
        return 'Standard (11-25)'
    elif price <= 50:
        return 'Premium (26-50)'
    elif price <= 100:
        return 'High-end (51-100)'
    else:
        return 'Luxury (>100)'

def extract_name_patterns(name):
    """Extract common patterns from product names"""
    patterns = []
    
    # Common keywords that might indicate product types
    keywords = [
        'shirt', 'pants', 'dress', 'suit', 'coat', 'blazer', 'kurti', 'saree',
        'lehenga', 'gown', 'abaya', 'kaftan', 'anarkali', 'palazzo', 'trouser',
        'blouse', 'salwar', 'patiala', 'sharara', 'gharara', 'jumpsuit'
    ]
    
    for keyword in keywords:
        if keyword in name:
            patterns.append(keyword)
    
    # Extract size patterns
    size_patterns = ['xs', 's', 'm', 'l', 'xl', 'xxl', 'plus']
    for size in size_patterns:
        if size in name:
            patterns.append(f'size_{size}')
    
    # Extract material patterns
    material_patterns = ['cotton', 'silk', 'polyester', 'wool', 'linen', 'denim']
    for material in material_patterns:
        if material in name:
            patterns.append(f'material_{material}')
    
    return patterns

def generate_product_suggestions(analysis):
    """Generate product type and product suggestions based on analysis"""
    suggestions = {
        'product_types': [],
        'recommendations': []
    }
    
    # Create product types from categories
    for category, data in analysis['categories'].items():
        if data['count'] >= 2:  # Only suggest types with multiple products
            type_suggestion = {
                'name': category.title(),
                'description': f'Products in {category} category with {data["count"]} items',
                'products': []
            }
            
            # Suggest products for this type
            for product in data['products']:
                product_suggestion = {
                    'name': product['name'],
                    'rate': product['price'],
                    'description': product.get('description', '')
                }
                type_suggestion['products'].append(product_suggestion)
            
            suggestions['product_types'].append(type_suggestion)
    
    # Generate recommendations based on patterns
    if analysis['common_patterns']:
        pattern_recommendations = []
        for pattern in analysis['common_patterns'][:10]:  # Limit to top 10 patterns
            pattern_recommendations.append({
                'pattern': pattern,
                'suggestion': f'Consider creating a "{pattern.title()}" product type'
            })
        suggestions['recommendations'].extend(pattern_recommendations)
    
    # Price range recommendations
    price_recommendations = []
    for price_range, count in analysis['price_ranges'].items():
        if count >= 3:
            price_recommendations.append({
                'price_range': price_range,
                'count': count,
                'suggestion': f'{count} products in {price_range} range - consider bulk pricing'
            })
        suggestions['recommendations'].extend(price_recommendations)
    
    return suggestions

def check_existing_items(user_id, suggestions):
    """Check which items already exist in the database"""
    conn = get_db_connection()
    existing_items = {
        'product_types': {},
        'products': {}
    }
    
    try:
        # Check existing product types
        for type_suggestion in suggestions.get('product_types', []):
            type_name = type_suggestion['name']
            placeholder = get_placeholder()
            existing_type = execute_update(conn, 
                f'SELECT type_id, type_name FROM product_types WHERE user_id = {placeholder} AND type_name = {placeholder}', 
                (user_id, type_name)
            ).fetchone()
            
            if existing_type:
                existing_items['product_types'][type_name] = {
                    'exists': True,
                    'type_id': existing_type['type_id'],
                    'type_name': existing_type['type_name']
                }
            else:
                existing_items['product_types'][type_name] = {
                    'exists': False
                }
        
        # Check existing products
        for type_suggestion in suggestions.get('product_types', []):
            for product_suggestion in type_suggestion.get('products', []):
                product_name = product_suggestion['name']
                placeholder = get_placeholder()
                existing_product = execute_update(conn, 
                    f'SELECT product_id, product_name, rate FROM products WHERE user_id = {placeholder} AND product_name = {placeholder}', 
                    (user_id, product_name)
                ).fetchone()
                
                if existing_product:
                    existing_items['products'][product_name] = {
                        'exists': True,
                        'product_id': existing_product['product_id'],
                        'product_name': existing_product['product_name'],
                        'current_rate': existing_product['rate'],
                        'new_rate': product_suggestion['rate']
                    }
                else:
                    existing_items['products'][product_name] = {
                        'exists': False
                    }
        
        return existing_items
        
    finally:
        conn.close()

def find_similar_products(user_id, product_name, threshold=0.8):
    """Find similar products using fuzzy matching"""
    
    conn = get_db_connection()
    similar_products = []
    
    try:
        # Get all existing products
        placeholder = get_placeholder()
        existing_products = execute_update(conn, 
            f'SELECT product_id, product_name, rate FROM products WHERE user_id = {placeholder}', 
            (user_id,)
        ).fetchall()
        
        for product in existing_products:
            similarity = SequenceMatcher(None, product_name.lower(), product['product_name'].lower()).ratio()
            if similarity >= threshold:
                similar_products.append({
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'rate': product['rate'],
                    'similarity': similarity
                })
        
        # Sort by similarity
        similar_products.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_products
        
    finally:
        conn.close()

# Routes
@catalog_api.route('/api/catalog/scan', methods=['POST'])
def scan_catalog():
    """Scan existing catalog and suggest product types and products"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        catalog_data = data.get('catalog', [])
        
        if not catalog_data:
            return jsonify({'success': False, 'error': 'No catalog data provided'}), 400
        
        # Analyze catalog data to extract patterns
        product_analysis = analyze_catalog_data(catalog_data)
        
        # Generate suggestions
        suggestions = generate_product_suggestions(product_analysis)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'analysis': product_analysis
        })
        
    except Exception as e:
        logger.error(f"Catalog scan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@catalog_api.route('/api/catalog/check-duplicates', methods=['POST'])
def check_catalog_duplicates():
    """Check for duplicates before creating products"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        suggestions = data.get('suggestions', {})
        
        if not suggestions:
            return jsonify({'success': False, 'error': 'No suggestions provided'}), 400
        
        # Check existing items
        existing_items = check_existing_items(user_id, suggestions)
        
        # Find similar products
        similar_products = {}
        for type_suggestion in suggestions.get('product_types', []):
            for product_suggestion in type_suggestion.get('products', []):
                product_name = product_suggestion['name']
                similar = find_similar_products(user_id, product_name)
                if similar:
                    similar_products[product_name] = similar
        
        # Calculate statistics
        total_types = len(suggestions.get('product_types', []))
        total_products = sum(len(t.get('products', [])) for t in suggestions.get('product_types', []))
        
        existing_types = sum(1 for t in existing_items['product_types'].values() if t['exists'])
        existing_products = sum(1 for p in existing_items['products'].values() if p['exists'])
        
        new_types = total_types - existing_types
        new_products = total_products - existing_products
        
        return jsonify({
            'success': True,
            'analysis': {
                'total_types': total_types,
                'total_products': total_products,
                'existing_types': existing_types,
                'existing_products': existing_products,
                'new_types': new_types,
                'new_products': new_products,
                'duplicate_percentage': (existing_products / total_products * 100) if total_products > 0 else 0
            },
            'existing_items': existing_items,
            'similar_products': similar_products
        })
        
    except Exception as e:
        logger.error(f"Duplicate check error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@catalog_api.route('/api/catalog/auto-create', methods=['POST'])
def auto_create_products():
    """Automatically create product types and products from catalog scan"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        suggestions = data.get('suggestions', {})
        
        if not suggestions:
            return jsonify({'success': False, 'error': 'No suggestions provided'}), 400
        
        conn = get_db_connection()
        created_types = []
        created_products = []
        
        try:
            # Create product types first
            for type_suggestion in suggestions.get('product_types', []):
                type_name = type_suggestion['name']
                description = type_suggestion.get('description', f'Products in {type_name} category')
                
                # Check if type already exists
                placeholder = get_placeholder()
                existing = execute_update(conn, 
                    f'SELECT type_id FROM product_types WHERE user_id = {placeholder} AND type_name = {placeholder}', 
                    (user_id, type_name)
                ).fetchone()
                
                if not existing:
                    cursor = conn.cursor()
                    placeholder = get_placeholder()
                    cursor.execute(
                        f'INSERT INTO product_types (user_id, type_name, description) VALUES ({placeholder}, {placeholder}, {placeholder})',
                        (user_id, type_name, description)
                    )
                    type_id = cursor.lastrowid
                    created_types.append({
                        'type_id': type_id,
                        'name': type_name,
                        'description': description
                    })
                else:
                    type_id = existing['type_id']
                
                # Create products for this type
                for product_suggestion in type_suggestion.get('products', []):
                    product_name = product_suggestion['name']
                    rate = product_suggestion['rate']
                    product_description = product_suggestion.get('description', '')
                    
                    # Check if product already exists
                    placeholder = get_placeholder()
                    existing_product = execute_update(conn, 
                        f'SELECT product_id FROM products WHERE user_id = {placeholder} AND product_name = {placeholder}', 
                        (user_id, product_name)
                    ).fetchone()
                    
                    if not existing_product:
                        cursor = conn.cursor()
                        placeholder = get_placeholder()
                        cursor.execute(
                            f'INSERT INTO products (user_id, type_id, product_name, rate, description) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                            (user_id, type_id, product_name, rate, product_description)
                        )
                        created_products.append({
                            'product_id': cursor.lastrowid,
                            'name': product_name,
                            'type_name': type_name,
                            'rate': rate,
                            'description': product_description
                        })
            return jsonify({
                'success': True,
                'message': f'Successfully created {len(created_types)} product types and {len(created_products)} products',
                'created_types': created_types,
                'created_products': created_products
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Auto-create products error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
