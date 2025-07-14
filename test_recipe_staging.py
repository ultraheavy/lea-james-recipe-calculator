#!/usr/bin/env python3
"""
Test script for recipe staging system
"""

import os
import sys
from recipe_staging_loader import RecipeStagingLoader

def main():
    # Initialize the loader
    loader = RecipeStagingLoader()
    
    # Initialize the staging table
    print("Initializing staging table...")
    loader.init_staging_table()
    print("✓ Staging table initialized")
    
    # Path to the original CSV file
    csv_path = "/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca/reference/LJ_DATA_Ref/Lea_Janes_Recipe_List_Summary.csv"
    
    if os.path.exists(csv_path):
        print(f"\nLoading CSV file: {csv_path}")
        stats = loader.load_csv(csv_path, "TEST_BATCH_001")
        
        print("\nLoad Statistics:")
        print(f"  Batch ID: {stats['batch_id']}")
        print(f"  Total rows: {stats['total_rows']}")
        print(f"  Loaded: {stats['loaded']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Needs review: {stats['needs_review']}")
        print(f"  Duplicates: {stats['duplicates']}")
        
        print("\n✓ Recipe staging test completed successfully!")
        print(f"\nAccess the admin interface at: http://localhost:8888/admin/staging/recipes-list/")
    else:
        print(f"Error: CSV file not found at {csv_path}")

if __name__ == "__main__":
    main()