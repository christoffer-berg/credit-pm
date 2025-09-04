#!/usr/bin/env python3
"""
Migration script to add contact info fields to companies table
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.database import get_supabase

def run_migration():
    supabase = get_supabase()
    
    # SQL to add new columns
    migration_sql = """
    ALTER TABLE companies 
    ADD COLUMN IF NOT EXISTS website VARCHAR(255),
    ADD COLUMN IF NOT EXISTS email VARCHAR(255),
    ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
    ADD COLUMN IF NOT EXISTS address TEXT,
    ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255);
    """
    
    try:
        # Execute the migration using supabase rpc (raw SQL)
        result = supabase.rpc('execute_sql', {'sql': migration_sql}).execute()
        print("✅ Migration completed successfully!")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
        # Try alternative approach with individual ALTER statements
        print("Trying individual column additions...")
        
        columns_to_add = [
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS website VARCHAR(255);",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS email VARCHAR(255);", 
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS phone VARCHAR(50);",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS address TEXT;",
            "ALTER TABLE companies ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255);"
        ]
        
        for sql in columns_to_add:
            try:
                supabase.rpc('execute_sql', {'sql': sql}).execute()
                print(f"✅ Added column: {sql}")
            except Exception as col_error:
                print(f"❌ Failed to add column {sql}: {col_error}")

if __name__ == "__main__":
    run_migration()