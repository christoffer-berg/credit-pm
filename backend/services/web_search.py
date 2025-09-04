from typing import List, Dict, Optional
import urllib.parse
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from core.config import settings

async def search_company_info(company_name: str, website: Optional[str] = None) -> Dict:
    """
    Search for company information using web searches and website content
    """
    results = {
        "company_name": company_name,
        "website": website,
        "web_search_results": [],
        "website_content": "",
        "synthesis": ""
    }
    
    try:
        # Perform web search for company information
        search_results = await perform_web_search(company_name)
        results["web_search_results"] = search_results
        
        # If website is provided, scrape website content
        if website:
            website_content = await scrape_website_content(website)
            results["website_content"] = website_content
            
        # Generate synthesis of all collected information
        synthesis = generate_company_synthesis(company_name, search_results, results["website_content"])
        results["synthesis"] = synthesis
        
    except Exception as e:
        results["error"] = f"Error searching company info: {str(e)}"
        
    return results

async def perform_web_search(company_name: str) -> List[Dict]:
    """
    Perform a web search for company information using DuckDuckGo
    """
    search_results = []
    
    try:
        # Use DuckDuckGo search API (no API key required)
        search_query = f'"{company_name}" company business description'
        encoded_query = urllib.parse.quote_plus(search_query)
        
        # DuckDuckGo Instant Answer API
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract relevant information
                    if data.get('AbstractText'):
                        search_results.append({
                            "source": "DuckDuckGo",
                            "content": data['AbstractText'],
                            "url": data.get('AbstractURL', '')
                        })
                    
                    # Extract related topics
                    for topic in data.get('RelatedTopics', [])[:3]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            search_results.append({
                                "source": "DuckDuckGo Related",
                                "content": topic['Text'],
                                "url": topic.get('FirstURL', '')
                            })
    
    except Exception as e:
        search_results.append({
            "error": f"Search failed: {str(e)}"
        })
    
    return search_results

async def scrape_website_content(website_url: str) -> str:
    """
    Scrape basic content from company website
    """
    try:
        # Ensure URL has protocol
        if not website_url.startswith(('http://', 'https://')):
            website_url = f"https://{website_url}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(website_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; Company Info Bot)'
            }) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Parse HTML with BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Extract text content
                    text = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Return first 2000 characters to avoid too much content
                    return text[:2000] + "..." if len(text) > 2000 else text
                    
    except Exception as e:
        return f"Error scraping website: {str(e)}"
    
    return ""

def generate_company_synthesis(company_name: str, search_results: List[Dict], website_content: str) -> str:
    """
    Generate a synthesis of company information from search results and website content
    """
    synthesis_parts = []
    
    # Add search results content
    for result in search_results:
        if result.get('content') and not result.get('error'):
            synthesis_parts.append(result['content'])
    
    # Add website content if available
    if website_content and not website_content.startswith("Error"):
        # Extract key business-related sentences from website
        sentences = website_content.split('. ')
        business_sentences = []
        
        business_keywords = [
            'company', 'business', 'services', 'products', 'industry', 
            'market', 'customers', 'solutions', 'technology', 'expertise',
            'founded', 'established', 'specializes', 'provides', 'offers'
        ]
        
        for sentence in sentences[:10]:  # Look at first 10 sentences
            if any(keyword.lower() in sentence.lower() for keyword in business_keywords):
                business_sentences.append(sentence.strip())
        
        if business_sentences:
            synthesis_parts.extend(business_sentences[:3])  # Take top 3 relevant sentences
    
    # Combine all parts
    if synthesis_parts:
        return '. '.join(synthesis_parts[:5])  # Limit to 5 parts maximum
    else:
        return f"Limited information available about {company_name}. Manual research may be required for comprehensive business description."

async def generate_enhanced_business_description(company_name: str, website: Optional[str] = None, existing_description: Optional[str] = None) -> str:
    """
    Generate an enhanced business description using web search and AI
    """
    # Perform web search
    search_info = await search_company_info(company_name, website)
    
    # Prepare context for AI
    context_parts = []
    
    if existing_description:
        context_parts.append(f"Existing description: {existing_description}")
    
    if search_info.get("synthesis"):
        context_parts.append(f"Web research: {search_info['synthesis']}")
    
    if search_info.get("website_content"):
        context_parts.append(f"Website content: {search_info['website_content'][:500]}")
    
    # If we have web information, use it to generate enhanced description
    if context_parts:
        from services.ai_generator import client
        
        if client:
            try:
                prompt = f"""
                Generate a comprehensive business description for {company_name} based on the following information:
                
                {chr(10).join(context_parts)}
                
                Create a professional business description that includes:
                - Core business activities and main products/services
                - Industry and market position
                - Key business characteristics and competitive advantages
                - Company background and establishment details (if available)
                
                Write 2-3 paragraphs in professional banking language suitable for credit analysis.
                Focus on factual information and avoid speculation.
                """
                
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a professional business analyst creating accurate company descriptions for banking and credit analysis purposes."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=500,
                    temperature=0.2
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                return f"Enhanced description generation failed: {str(e)}. Using web research: {search_info.get('synthesis', 'No additional information found.')}"
        else:
            return search_info.get('synthesis', f'No additional information found about {company_name}.')
    else:
        return f"Unable to find additional information about {company_name} from web sources."