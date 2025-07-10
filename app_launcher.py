#!/usr/bin/env python3
"""
Launcher script that bypasses database initialization
since we already have the database set up with the new schema
"""

import os
import sys

# Set environment variable to skip DB init
os.environ['SKIP_DB_INIT'] = '1'

# Import and modify the app module
import app

# Monkey patch the init_database function to do nothing
def dummy_init():
    print("Database already initialized - skipping init")
    pass

app.init_database = dummy_init

# Run the app
if __name__ == '__main__':
    app.app.run(debug=False, host='0.0.0.0', port=8888)