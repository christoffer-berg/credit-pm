#!/usr/bin/env python3
"""
Test script for the market analysis OpenRouter integration.
"""
import asyncio
import sys
import os
sys.path.append('/Users/christofferberg/Documents/My programs/Credit-PM/backend')

from services.market_analysis import market_analysis_service

async def test_market_analysis():
    """Test the market analysis service."""
    
    print("Testing Market Analysis Service with OpenRouter")
    print("=" * 50)
    
    # Test configuration
    business_area = "management consultancy"
    country = "sweden"
    
    print(f"Business Area: {business_area}")
    print(f"Country: {country}")
    print()
    
    # Test 1: Generate search queries for market demand
    print("1. Testing search query generation...")
    try:
        queries_result = await market_analysis_service.generate_search_queries(
            business_area=business_area,
            analysis_type="market_demand",
            country=country
        )
        
        print("✅ Search queries generated successfully:")
        print(f"   Topic: {queries_result.get('topic', 'N/A')}")
        queries = queries_result.get('searchQueries', [])
        for i, query in enumerate(queries, 1):
            print(f"   {i}. {query}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to generate search queries: {e}")
        print()
    
    # Test 2: Conduct market research with sample queries
    print("2. Testing market research with OpenRouter...")
    sample_queries = [
        "How large is the market for management consultancy in Sweden?",
        "What are the growth trends in Swedish management consulting market?",
        "What factors drive demand for management consulting services?",
        "How seasonal is demand in the management consultancy sector?"
    ]
    
    try:
        research_result = await market_analysis_service.conduct_market_research(
            business_area=business_area,
            search_queries=sample_queries,
            analysis_type="market_demand",
            country=country
        )
        
        print("✅ Market research completed successfully:")
        print("   Research content preview:")
        preview = research_result[:300] if len(research_result) > 300 else research_result
        print(f"   {preview}...")
        print(f"   Total content length: {len(research_result)} characters")
        print()
        
    except Exception as e:
        print(f"❌ Failed to conduct market research: {e}")
        print()
    
    # Test 3: Generate comprehensive analysis (limited test)
    print("3. Testing comprehensive market analysis (sample)...")
    try:
        # We'll only test one analysis type to avoid hitting API limits
        analysis_result = await market_analysis_service.generate_comprehensive_market_analysis(
            business_area=business_area,
            country=country
        )
        
        print("✅ Comprehensive analysis structure:")
        print(f"   Business Area: {analysis_result.get('business_area', 'N/A')}")
        print(f"   Country: {analysis_result.get('country', 'N/A')}")
        
        analyses = analysis_result.get('analyses', {})
        print(f"   Analysis sections: {len(analyses)}")
        for section_name, section_data in analyses.items():
            if "error" in section_data:
                print(f"   - {section_name}: ❌ {section_data['error']}")
            else:
                queries_count = len(section_data.get('search_queries', []))
                content_length = len(section_data.get('research_content', ''))
                print(f"   - {section_name}: ✅ {queries_count} queries, {content_length} chars")
        print()
        
    except Exception as e:
        print(f"❌ Failed comprehensive analysis: {e}")
        print()
    
    print("Testing completed!")

if __name__ == "__main__":
    # Check environment variables
    if not os.getenv("open_router_url"):
        print("❌ Missing open_router_url in environment")
        sys.exit(1)
    
    if not os.getenv("Authorization"):
        print("❌ Missing Authorization header in environment")
        sys.exit(1)
        
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Missing OPENAI_API_KEY in environment")
        sys.exit(1)
    
    print("✅ Environment variables configured")
    print()
    
    # Run the test
    asyncio.run(test_market_analysis())