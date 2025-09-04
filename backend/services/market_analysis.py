import httpx
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from core.config import settings
import os

class MarketAnalysisService:
    def __init__(self):
        self.openrouter_url = os.getenv("open_router_url")
        self.authorization_header = os.getenv("Authorization")
        
    async def generate_search_queries(self, business_area: str, analysis_type: str, country: str = "sweden") -> Dict[str, Any]:
        """
        Generate search queries for a specific analysis type using OpenAI.
        """
        try:
            if not settings.openai_api_key:
                return {
                    "error": "OpenAI API key not configured",
                    "topic": business_area,
                    "searchQueries": self._get_fallback_queries(analysis_type, business_area)
                }
            
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            
            # Load the appropriate prompt from AgentInstructions_example.xml
            prompts = self._load_agent_instructions()
            
            if analysis_type not in prompts:
                return {
                    "error": f"Unknown analysis type: {analysis_type}",
                    "topic": business_area,
                    "searchQueries": self._get_fallback_queries(analysis_type, business_area)
                }
            
            prompt_template = prompts[analysis_type]
            prompt = prompt_template.replace("{business_area}", business_area).replace("{country}", country)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a search query generation agent. Generate exactly 4 unique, well-crafted search queries for market research. Return only valid JSON in the format: {\"topic\": \"topic_name\", \"searchQueries\": [\"query1\", \"query2\", \"query3\", \"query4\"]}"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            # Parse JSON response
            queries_data = json.loads(content)
            
            # Ensure the expected format
            if "searchQueries" not in queries_data:
                # Try to extract queries from different formats
                queries = []
                if isinstance(queries_data, dict):
                    # If it's a dict with individual query keys
                    for key, value in queries_data.items():
                        if key.startswith('query') and isinstance(value, str):
                            queries.append(value)
                    
                    queries_data = {
                        "topic": business_area,
                        "searchQueries": queries[:4]  # Limit to 4 queries
                    }
                else:
                    queries_data = {
                        "topic": business_area,
                        "searchQueries": self._get_fallback_queries(analysis_type, business_area)
                    }
            
            return queries_data
            
        except Exception as e:
            return {
                "error": f"Failed to generate search queries: {str(e)}",
                "topic": business_area,
                "searchQueries": self._get_fallback_queries(analysis_type, business_area)
            }
    
    async def conduct_market_research(self, business_area: str, search_queries: List[str], analysis_type: str, country: str = "sweden") -> str:
        """
        Conduct market research using OpenRouter with perplexity/sonar model.
        """
        if not self.openrouter_url or not self.authorization_header:
            return f"OpenRouter not configured. Market research for {business_area} would be conducted here with proper OpenRouter configuration."
        
        # Load the appropriate market analysis prompt
        prompt_template = self._load_market_analysis_prompt(analysis_type)
        
        # Format the prompt with the business area, country, and search queries
        formatted_queries = "\n".join([f"- {query}" for query in search_queries])
        
        research_prompt = prompt_template.format(
            business_area=business_area,
            country=country,
            search_queries=formatted_queries
        )
        
        # System message for the market researcher
        system_message = "You are a skilled market researcher specialized in credit risks in banking. You will receive questions and a business area, and you are to perform in-depth research on those topics with the provided queries. Provide comprehensive analysis suitable for banking credit risk assessment."
        
        # User message combining business area and queries
        user_message = f"Business area: {business_area}, Country: {country}, Research queries: {', '.join(search_queries)}"
        
        payload = {
            "model": "perplexity/sonar",
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
        
        headers = {
            "Authorization": self.authorization_header,
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.openrouter_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0  # Reduced timeout to avoid hanging
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Debug: Log the full response to understand the structure
                print(f"DEBUG: Full OpenRouter/Perplexity response: {json.dumps(result, indent=2)}")
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Debug: Log the content to see how sources are formatted
                    print(f"DEBUG: Perplexity content: {content}")
                    
                    # Extract and format sources from perplexity response
                    formatted_content = self._format_perplexity_sources(content, result)
                    
                    return formatted_content
                else:
                    return f"No research results available for {business_area}"
                    
        except httpx.HTTPError as e:
            return f"Error conducting market research: HTTP {e.response.status_code if e.response else 'error'}"
        except Exception as e:
            return f"Error conducting market research: {str(e)}"
    
    async def generate_comprehensive_market_analysis(self, business_area: str, country: str = "sweden") -> Dict[str, Any]:
        """
        Generate a comprehensive market analysis covering all aspects.
        """
        analysis_types = [
            "market_demand",
            "revenue_profitability", 
            "competitive_landscape",
            "regulation_environment",
            "operational_factors",
            "financing_capital",
            "innovation_technology"
        ]
        
        results = {
            "business_area": business_area,
            "country": country,
            "analyses": {}
        }
        
        for analysis_type in analysis_types:
            try:
                # Generate search queries for this analysis type
                queries_result = await self.generate_search_queries(business_area, analysis_type, country)
                
                if "error" in queries_result:
                    results["analyses"][analysis_type] = {
                        "error": queries_result["error"],
                        "search_queries": [],
                        "research_content": ""
                    }
                    continue
                
                search_queries = queries_result.get("searchQueries", [])
                
                # Conduct research using the generated queries
                if search_queries:
                    research_content = await self.conduct_market_research(
                        business_area, search_queries, analysis_type, country
                    )
                else:
                    research_content = f"No search queries generated for {analysis_type}"
                
                results["analyses"][analysis_type] = {
                    "search_queries": search_queries,
                    "research_content": research_content
                }
                
            except Exception as e:
                results["analyses"][analysis_type] = {
                    "error": f"Failed to complete {analysis_type}: {str(e)}",
                    "search_queries": [],
                    "research_content": ""
                }
        
        return results
    
    def _load_agent_instructions(self) -> Dict[str, str]:
        """
        Load agent instructions from AgentInstructions_example.xml
        """
        instructions_file = "/Users/christofferberg/Documents/My programs/Credit-PM/AgentInstructions_example.xml"
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse the XML and extract instructions for different types
            # This is a simplified extraction - you might want to use proper XML parsing
            prompts = {
                "market_demand": self._extract_section_prompt(content, 0),
                "revenue_profitability": self._extract_section_prompt(content, 1), 
                "competitive_landscape": self._extract_section_prompt(content, 2),
                "regulation_environment": self._extract_section_prompt(content, 3),
                "operational_factors": self._extract_section_prompt(content, 4),
                "financing_capital": self._extract_section_prompt(content, 5),
                "innovation_technology": self._extract_section_prompt(content, 6)
            }
            
            return prompts
            
        except Exception as e:
            # Fallback prompts if file can't be loaded
            return {
                "market_demand": "Generate 4 search queries about market demand and size for {business_area} in {country}.",
                "revenue_profitability": "Generate 4 search queries about revenue streams and profitability for {business_area} in {country}.",
                "competitive_landscape": "Generate 4 search queries about competitive landscape for {business_area} in {country}.",
                "regulation_environment": "Generate 3 search queries about regulations affecting {business_area} in {country}.",
                "operational_factors": "Generate 4 search queries about operational factors for {business_area} in {country}.",
                "financing_capital": "Generate 3 search queries about financing needs for {business_area} in {country}.",
                "innovation_technology": "Generate 3 search queries about technology trends for {business_area} in {country}."
            }
    
    def _extract_section_prompt(self, content: str, section_index: int) -> str:
        """
        Extract a specific section prompt from the XML content.
        """
        # Split by AgentInstructions tags and get the appropriate section
        sections = content.split('<AgentInstructions>')
        if len(sections) > section_index + 1:
            section = sections[section_index + 1].split('</AgentInstructions>')[0]
            # Extract the key parts for prompt generation
            return f"Based on the business area {{business_area}} in {{country}}, generate search queries as specified in the instructions."
        
        return "Generate relevant search queries for {business_area} in {country}."
    
    def _load_market_analysis_prompt(self, analysis_type: str) -> str:
        """
        Load market analysis prompt template from XML file.
        """
        prompts_file = "/Users/christofferberg/Documents/My programs/Credit-PM/market_analysis_prompts.xml"
        
        try:
            with open(prompts_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Map analysis types to XML prompt sections
            prompt_mapping = {
                "market_demand": "MarketDemandPrompt",
                "revenue_profitability": "RevenueProfitabilityPrompt",
                "competitive_landscape": "CompetitiveLandscapePrompt", 
                "regulation_environment": "RegulationEnvironmentPrompt",
                "operational_factors": "OperationalFactorsPrompt",
                "financing_capital": "FinancingCapitalPrompt",
                "innovation_technology": "InnovationTechnologyPrompt"
            }
            
            prompt_section = prompt_mapping.get(analysis_type, "MarketDemandPrompt")
            
            # Extract the specific prompt section (simplified - you might want proper XML parsing)
            start_tag = f"<{prompt_section}>"
            end_tag = f"</{prompt_section}>"
            
            start_idx = content.find(start_tag)
            end_idx = content.find(end_tag)
            
            if start_idx != -1 and end_idx != -1:
                prompt_content = content[start_idx:end_idx + len(end_tag)]
                return prompt_content
            
        except Exception as e:
            pass
        
        # Fallback prompt if XML can't be loaded
        return """
        Analyze {business_area} in {country} focusing on the following research queries:
        {search_queries}
        
        Provide comprehensive analysis suitable for banking credit risk assessment.
        """
    
    def _get_fallback_queries(self, analysis_type: str, business_area: str) -> List[str]:
        """
        Get fallback search queries when OpenAI is not available.
        """
        fallback_queries = {
            "market_demand": [
                f"How large is the market for {business_area}?",
                f"What are the growth trends in {business_area} market?",
                f"What factors drive demand for {business_area}?",
                f"How seasonal is demand in the {business_area} sector?"
            ],
            "revenue_profitability": [
                f"What are typical revenue streams for {business_area}?",
                f"What are typical profit margins in {business_area}?",
                f"What drives profitability in {business_area}?",
                f"How predictable are revenues in {business_area}?"
            ],
            "competitive_landscape": [
                f"Who are the main competitors in {business_area}?",
                f"How competitive is the {business_area} market?",
                f"What are barriers to entry in {business_area}?",
                f"Are there disruptive threats in {business_area}?"
            ],
            "regulation_environment": [
                f"What regulations affect {business_area}?",
                f"What regulatory changes are coming for {business_area}?",
                f"How exposed is {business_area} to regulatory risk?"
            ],
            "operational_factors": [
                f"What are typical cost structures in {business_area}?",
                f"How resilient are supply chains in {business_area}?",
                f"Is {business_area} labor or capital intensive?",
                f"How standardized are offerings in {business_area}?"
            ],
            "financing_capital": [
                f"What are typical financing needs for {business_area}?",
                f"How leveraged are firms in {business_area}?",
                f"What role does capital access play in {business_area}?"
            ],
            "innovation_technology": [
                f"How is technology changing {business_area}?",
                f"What role does R&D play in {business_area}?",
                f"Are there innovation opportunities in {business_area}?"
            ]
        }
        
        return fallback_queries.get(analysis_type, [
            f"What are the key market factors for {business_area}?",
            f"How is the {business_area} industry performing?",
            f"What are the main risks in {business_area}?",
            f"What are growth prospects for {business_area}?"
        ])
    
    def _format_perplexity_sources(self, content: str, full_response: Dict = None) -> str:
        """
        Format perplexity response to make sources clickable links.
        Perplexity may include sources in different parts of the response:
        - In the content directly
        - In separate 'sources' or 'citations' fields
        - As metadata in the response
        """
        import re
        
        # Extract sources from perplexity response structure
        sources = []
        if full_response:
            # Check for citations array at top level
            if "citations" in full_response:
                print(f"DEBUG: Found citations in response: {full_response['citations']}")
                for url in full_response["citations"]:
                    sources.append(url)
            
            # Check for annotations in message (more detailed source info)
            if "choices" in full_response and len(full_response["choices"]) > 0:
                choice = full_response["choices"][0]
                if "message" in choice and "annotations" in choice["message"]:
                    print(f"DEBUG: Found annotations: {choice['message']['annotations']}")
                    for annotation in choice["message"]["annotations"]:
                        if annotation.get("type") == "url_citation":
                            url_citation = annotation.get("url_citation", {})
                            sources.append({
                                "url": url_citation.get("url", ""),
                                "title": url_citation.get("title", ""),
                                "type": "url_citation"
                            })
        
        # Pattern to find URLs in the content
        url_pattern = r'https?://[^\s\)]+(?:\.[^\s\)]+)*'
        
        # Find all URLs in the content
        urls = re.findall(url_pattern, content)
        
        # Pattern to find citations like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        citations = re.findall(citation_pattern, content)
        
        # Create formatted content with clickable links
        formatted_content = content
        
        # Replace URLs with markdown links
        for url in set(urls):  # Use set to avoid duplicates
            # Clean the URL (remove trailing punctuation)
            clean_url = re.sub(r'[.,;:!?]+$', '', url)
            if clean_url != url:
                # Replace the original URL with the clean one
                formatted_content = formatted_content.replace(url, clean_url)
            
            # Create a shorter display text for the link
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', clean_url)
            display_text = domain_match.group(1) if domain_match else clean_url
            
            # Replace with markdown link format
            markdown_link = f"[{display_text}]({clean_url})"
            formatted_content = formatted_content.replace(clean_url, markdown_link)
        
        # Add sources found in the response metadata
        if sources:
            formatted_content += "\n\n**Sources:**\n"
            for i, source in enumerate(sources, 1):
                if isinstance(source, dict) and source.get("type") == "url_citation":
                    # Handle perplexity annotation format
                    url = source.get('url', '')
                    title = source.get('title', '')
                    if url and title:
                        # Clean up the title (remove protocol and www)
                        clean_title = title.replace('www.', '').replace('http://', '').replace('https://', '')
                        formatted_content += f"{i}. [{clean_title}]({url})\n"
                    elif url:
                        # Fallback to domain extraction
                        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                        display_text = domain_match.group(1) if domain_match else url
                        formatted_content += f"{i}. [{display_text}]({url})\n"
                elif isinstance(source, str):
                    # Handle direct URL citations
                    if source.startswith('http'):
                        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', source)
                        display_text = domain_match.group(1) if domain_match else source
                        formatted_content += f"{i}. [{display_text}]({source})\n"
                    else:
                        formatted_content += f"{i}. {source}\n"
                elif isinstance(source, dict):
                    # Handle other structured source objects
                    url = source.get('url', source.get('link', ''))
                    title = source.get('title', source.get('name', ''))
                    if url and title:
                        formatted_content += f"{i}. [{title}]({url})\n"
                    elif url:
                        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                        display_text = domain_match.group(1) if domain_match else url
                        formatted_content += f"{i}. [{display_text}]({url})\n"
                    else:
                        formatted_content += f"{i}. {title or source}\n"
        elif citations and not urls:
            formatted_content += "\n\n**Note**: This analysis includes citations. The full source URLs may be available in the original perplexity response."
        
        # Look for common source indicators and format them
        source_patterns = [
            (r'Sources?:\s*', '**Sources:**\n'),
            (r'References?:\s*', '**References:**\n'),
            (r'Citations?:\s*', '**Citations:**\n'),
        ]
        
        for pattern, replacement in source_patterns:
            formatted_content = re.sub(pattern, replacement, formatted_content, flags=re.IGNORECASE)
        
        return formatted_content
    
    def _extract_sources_from_field(self, field_data) -> List:
        """
        Extract sources from a field in the response.
        """
        sources = []
        if isinstance(field_data, list):
            sources.extend(field_data)
        elif isinstance(field_data, dict):
            # Look for URL-like keys
            for key, value in field_data.items():
                if 'url' in key.lower() or 'link' in key.lower() or 'source' in key.lower():
                    sources.append({key: value})
        elif isinstance(field_data, str):
            sources.append(field_data)
        
        return sources

# Global instance
market_analysis_service = MarketAnalysisService()