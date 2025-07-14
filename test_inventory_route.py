#!/usr/bin/env python3
"""Test if inventory staging routes are registered"""

from flask import Flask
import sys

# Create a test app
test_app = Flask(__name__)

# Try to import and register the blueprint
try:
    from inventory_staging_admin import inventory_staging_bp
    test_app.register_blueprint(inventory_staging_bp)
    print("✓ Blueprint registered successfully")
    
    # List all registered routes
    print("\nRegistered routes:")
    for rule in test_app.url_map.iter_rules():
        if 'inventory' in rule.rule:
            print(f"  {rule.rule} -> {rule.endpoint}")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Also check if the main app has the routes
try:
    from app import app
    print("\nMain app routes with 'inventory':")
    for rule in app.url_map.iter_rules():
        if 'inventory' in rule.rule:
            print(f"  {rule.rule} -> {rule.endpoint}")
except Exception as e:
    print(f"Could not check main app: {e}")