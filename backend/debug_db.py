#!/usr/bin/env python3
"""
Debug script to check database contents
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    supabase = create_client(url, key)
    
    # Check users table
    print("=== USERS ===")
    users = supabase.table("users").select("*").execute()
    print(f"Found {len(users.data)} users:")
    for user in users.data[:3]:  # Show first 3
        print(f"  - {user}")
    
    # Check companies
    print("\n=== COMPANIES ===")
    companies = supabase.table("companies").select("*").execute()
    print(f"Found {len(companies.data)} companies:")
    for company in companies.data[:3]:
        print(f"  - {company}")
    
    # Check cases
    print("\n=== PM CASES ===")
    cases = supabase.table("pm_cases").select("*").execute()
    print(f"Found {len(cases.data)} cases:")
    for case in cases.data[:3]:
        print(f"  - {case}")

if __name__ == "__main__":
    main()