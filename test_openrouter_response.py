#!/usr/bin/env python3
"""
Test script to check OpenRouter/Perplexity response structure.
"""
import asyncio
import httpx
import json
import os

async def test_openrouter_response():
    """Test OpenRouter response to see source structure."""
    
    # Get credentials from environment
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    authorization = "Bearer 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"
    
    # Test payload
    payload = {
        "model": "perplexity/sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a skilled market researcher specialized in credit risks in banking. You will receive questions and a business area, and you are to perform in-depth research on those topics with the provided queries."
            },
            {
                "role": "user",
                "content": "Business area: management consultancy, Country: sweden, Research queries: How large is the market for management consultancy in Sweden?, What are the growth trends in Swedish management consulting market?"
            }
        ]
    }
    
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("Making request to OpenRouter...")
            response = await client.post(
                openrouter_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            print("=== FULL RESPONSE STRUCTURE ===")
            print(json.dumps(result, indent=2))
            
            print("\n=== CONTENT ONLY ===")
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(content)
            
            print("\n=== ANALYSIS ===")
            print(f"Response keys: {list(result.keys())}")
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                print(f"Choice keys: {list(choice.keys())}")
                if "message" in choice:
                    message = choice["message"]
                    print(f"Message keys: {list(message.keys())}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter_response())