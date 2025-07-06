#!/usr/bin/env python3
"""
Apply P1 fixes to existing database
"""

import sys
from pathlib import Path

# Import ETL pipeline
from etl import ETLPipeline

def main():
    print("Applying P1 fixes to restaurant_calculator.db...")
    
    # Create ETL pipeline
    etl = ETLPipeline('restaurant_calculator.db')
    
    try:
        # Run the full ETL with fixes
        etl.run_full_etl()
        
        print("\nP1 fixes completed successfully!")
        print("Check audit_reports/ for the delta report.")
        
    except Exception as e:
        print(f"Error applying fixes: {e}")
        sys.exit(1)
    finally:
        etl.close()

if __name__ == '__main__':
    main()