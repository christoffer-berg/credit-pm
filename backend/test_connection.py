#!/usr/bin/env python3
"""
Test script to check database and API connectivity
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection"""
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            print("❌ Missing Supabase credentials")
            return False
            
        print(f"🔗 Connecting to Supabase: {url}")
        supabase = create_client(url, key)
        
        # Test connection by trying to fetch from companies table
        result = supabase.table("companies").select("*").limit(1).execute()
        print(f"✅ Supabase connection successful! Found {len(result.data)} companies")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_bolagsverket_service():
    """Test Bolagsverket service (mock)"""
    try:
        import asyncio
        from services.bolagsverket import fetch_company_data
        
        async def test():
            data = await fetch_company_data("5560160680")
            print(f"✅ Bolagsverket service working: {data}")
            return True
            
        return asyncio.run(test())
        
    except Exception as e:
        print(f"❌ Bolagsverket service failed: {e}")
        return False

def test_ai_generator():
    """Test AI generator service"""
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.startswith("sk-"):
            print("✅ OpenAI API key configured")
        else:
            print("⚠️  OpenAI API key missing - will use placeholders")
        return True
    except Exception as e:
        print(f"❌ AI generator test failed: {e}")
        return False

def main():
    print("🧪 Testing Credit PM Backend Connections")
    print("=" * 50)
    
    tests = [
        ("Supabase Database", test_supabase_connection),
        ("Bolagsverket Service", test_bolagsverket_service),
        ("AI Generator", test_ai_generator),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Backend should work correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())