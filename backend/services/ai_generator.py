from openai import OpenAI
from typing import Dict, Optional, Any
from core.config import settings
from core.database import get_supabase
from services.financial_processor import calculate_financial_ratios, generate_financial_forecast, calculate_credit_score

# Initialize OpenAI client
client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

async def generate_section_content(
    section_type: str,
    company: Optional[Dict],
    case: Dict,
    context_data: Optional[Dict] = None
) -> str:
    """
    Generate AI content for PM sections using OpenAI API.
    """
    
    if not client:
        return f"[AI content for {section_type} would be generated here with OpenAI API key configured]"
    
    prompts = {
        "purpose": generate_purpose_prompt,
        "business_description": generate_business_description_prompt,
        "market_analysis": generate_market_analysis_prompt,
        "financial_analysis": generate_financial_analysis_prompt,
        "credit_analysis": generate_credit_analysis_prompt,
        "credit_proposal": generate_credit_proposal_prompt,
    }
    
    if section_type not in prompts:
        raise ValueError(f"Unknown section type: {section_type}")
    
    try:
        prompt = prompts[section_type](company, case, context_data)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert banking credit analyst writing professional credit memos. Write clear, concise, and analytical content suitable for internal bank documentation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        # Log the AI generation for audit
        await log_ai_generation(case["id"], section_type, prompt, content, "gpt-4")
        
        return content
        
    except Exception as e:
        return f"Error generating AI content: {str(e)}"

def generate_purpose_prompt(company: Optional[Dict], case: Dict, context: Optional[Dict] = None) -> str:
    company_name = company.get("name", "the company") if company else "the company"
    return f"""
    Write a brief purpose statement for a credit memo analyzing {company_name}.
    
    Company Information:
    - Name: {company.get("name", "Unknown") if company else "Unknown"}
    - Organization Number: {company.get("organization_number", "Unknown") if company else "Unknown"}
    - Business: {company.get("business_description", "Unknown business") if company else "Unknown business"}
    
    The purpose should be 2-3 sentences explaining why this credit analysis is being conducted.
    """

def generate_business_description_prompt(company: Optional[Dict], case: Dict, context: Optional[Dict] = None) -> str:
    company_name = company.get("name", "the company") if company else "the company"
    business_desc = company.get("business_description", "general business operations") if company else "general business operations"
    
    return f"""
    Write a comprehensive business description for {company_name}.
    
    Company Information:
    - Name: {company.get("name", "Unknown") if company else "Unknown"}
    - Business Description: {business_desc}
    - Industry Code: {company.get("industry_code", "Unknown") if company else "Unknown"}
    
    Include:
    - Core business activities
    - Market position
    - Key products/services
    - Business model overview
    
    Write 2-3 paragraphs with professional banking language.
    """

def generate_market_analysis_prompt(company: Optional[Dict], case: Dict, context: Optional[Dict] = None) -> str:
    industry_code = company.get("industry_code", "general industry") if company else "general industry"
    company_name = company.get("name", "the company") if company else "the company"
    
    return f"""
    Write a market analysis for {company_name} operating in industry code {industry_code}.
    
    Include analysis of:
    - Industry outlook and trends
    - Market size and growth prospects
    - Competitive landscape
    - Key market risks and opportunities
    - Regulatory environment
    
    Write 2-3 paragraphs with specific insights relevant to credit risk assessment.
    """

def generate_financial_analysis_prompt(company: Optional[Dict], case: Dict, context: Optional[Dict] = None) -> str:
    company_name = company.get("name", "the company") if company else "the company"
    
    financial_context = ""
    ratios_context = ""
    forecast_context = ""
    
    if context and context.get("financials"):
        financials = context["financials"]
        financial_context = f"\nHistorical Financial Data (Last 3 Years):\n"
        for year_data in financials[-3:]:
            financial_context += f"- {year_data.get('year', 'Unknown')}: Revenue {year_data.get('revenue', 'N/A')}, Profit {year_data.get('profit', 'N/A')}, Assets {year_data.get('assets', 'N/A')}, Liabilities {year_data.get('liabilities', 'N/A')}\n"
    
    if context and context.get("financial_ratios"):
        ratios = context["financial_ratios"]
        ratios_context = f"\nCalculated Financial Ratios:\n"
        for ratio_name, ratio_value in ratios.items():
            if isinstance(ratio_value, (int, float)):
                ratios_context += f"- {ratio_name.replace('_', ' ').title()}: {ratio_value:.2f}%\n"
    
    if context and context.get("financial_forecast"):
        forecast = context["financial_forecast"]
        if "base_case" in forecast and "revenue" in forecast["base_case"]:
            forecast_years = forecast.get("forecast_years", [])
            revenue_forecast = forecast["base_case"]["revenue"]
            forecast_context = f"\nFinancial Forecast (Next 3 Years):\n"
            for year, revenue in zip(forecast_years, revenue_forecast):
                forecast_context += f"- {year}: Projected Revenue {revenue:,.0f}\n"
    
    return f"""
    Write a comprehensive financial analysis for {company_name}.
    {financial_context}
    {ratios_context}
    {forecast_context}
    
    Include detailed analysis of:
    - Revenue trends, growth patterns, and profitability metrics
    - Financial strength indicators and balance sheet stability
    - Key financial ratios and their implications for creditworthiness
    - Cash flow generation and working capital management
    - Debt capacity, leverage ratios, and capital structure
    - Forward-looking projections and scenario analysis
    
    Provide specific quantitative insights and identify key strengths and weaknesses.
    Write 3-4 paragraphs with professional banking language and clear risk assessment.
    """

def generate_credit_analysis_prompt(company: Optional[Dict], case: Dict, context: Optional[Dict] = None) -> str:
    company_name = company.get("name", "the company") if company else "the company"
    industry = company.get("industry_code", "general industry") if company else "general industry"
    
    credit_score_context = ""
    if context and context.get("credit_score") and not context["credit_score"].get("error"):
        score_data = context["credit_score"]
        credit_score_context = f"""
    
    Credit Score Analysis:
    - Calculated Score: {score_data.get('score', 'N/A')}/1000
    - Credit Rating: {score_data.get('rating', 'N/A')}
    - Key Factors: {', '.join(score_data.get('factors', []))}"""
    
    ratios_summary = ""
    if context and context.get("financial_ratios"):
        ratios = context["financial_ratios"]
        ratios_summary = f"\nFinancial Performance Indicators:\n"
        if 'profit_margin' in ratios:
            ratios_summary += f"- Profit Margin: {ratios['profit_margin']:.2f}%\n"
        if 'debt_to_assets' in ratios:
            ratios_summary += f"- Debt to Assets: {ratios['debt_to_assets']:.2f}%\n"
        if 'revenue_growth' in ratios:
            ratios_summary += f"- Revenue Growth: {ratios['revenue_growth']:.2f}%\n"
    
    return f"""
    Write a comprehensive credit risk analysis for {company_name} operating in {industry}.
    {credit_score_context}
    {ratios_summary}
    
    Provide detailed assessment of:
    - Primary credit risk factors and available mitigants
    - Industry-specific risks and market positioning
    - Management quality and operational capabilities
    - Financial risk profile based on calculated metrics
    - Debt service and repayment capacity analysis
    - Security/collateral considerations and recovery prospects
    - Overall creditworthiness and risk rating justification
    
    Conclude with a recommended risk rating (Low Risk/Medium Risk/High Risk) with clear justification based on the quantitative and qualitative factors.
    Write 3-4 paragraphs with structured risk assessment and specific recommendations.
    """

def generate_credit_proposal_prompt(company: Optional[Dict], case: Dict, context: Optional[Dict] = None) -> str:
    company_name = company.get("name", "the company") if company else "the company"
    
    financial_summary = ""
    if context and context.get("financial_ratios"):
        ratios = context["financial_ratios"]
        if 'profit_margin' in ratios and 'revenue_growth' in ratios:
            financial_summary = f"\nFinancial Position Summary:\n- Current profitability: {ratios['profit_margin']:.1f}% margin\n- Revenue trend: {ratios['revenue_growth']:.1f}% growth\n"
    
    credit_rating_context = ""
    if context and context.get("credit_score") and not context["credit_score"].get("error"):
        rating = context["credit_score"].get("rating", "N/A")
        credit_rating_context = f"- Internal Credit Rating: {rating}\n"
    
    return f"""
    Write a comprehensive credit proposal for {company_name}.
    {financial_summary}
    {credit_rating_context}
    
    Structure your recommendation to include:
    - Recommended credit facility type and proposed amount (based on financial capacity)
    - Proposed interest rate, fees, and key commercial terms
    - Security requirements and collateral arrangements
    - Financial covenants and ongoing monitoring requirements
    - Risk mitigants and conditions precedent to drawdown
    - Expected relationship profitability and strategic value
    - Approval conditions and implementation timeline
    
    Provide a clear final recommendation (APPROVE/DECLINE/CONDITIONAL APPROVAL) with detailed rationale based on the financial analysis and risk assessment.
    Write 3-4 paragraphs with specific commercial terms, amounts, and implementation details.
    """

async def generate_complete_pm(case_id: str) -> Dict[str, Any]:
    """
    Generate a complete PM with all sections for a given case.
    """
    supabase = get_supabase()
    
    try:
        # Get case and company data
        case_result = supabase.table("pm_cases").select("*").eq("id", case_id).execute()
        if not case_result.data:
            raise ValueError(f"Case {case_id} not found")
        
        case = case_result.data[0]
        
        # Get company data
        company_result = supabase.table("companies").select("*").eq("id", case["company_id"]).execute()
        company = company_result.data[0] if company_result.data else None
        
        # Get financial data and calculate metrics
        financials = []
        financial_ratios = {}
        credit_score = None
        financial_forecast = None
        
        if company:
            financials_result = supabase.table("financials").select("*").eq("company_id", company["id"]).order("year", desc=True).execute()
            financials = financials_result.data
            
            # Calculate financial analysis
            if financials:
                financial_ratios = calculate_financial_ratios(financials)
                credit_score = await calculate_credit_score(company["id"])
                financial_forecast = await generate_financial_forecast(company["id"])
        
        context_data = {
            "financials": financials,
            "financial_ratios": financial_ratios,
            "credit_score": credit_score,
            "financial_forecast": financial_forecast,
            "case": case,
            "company": company
        }
        
        # Define the standard sections in order
        sections_to_generate = [
            "purpose",
            "market_analysis",
            "financial_analysis",
            "credit_analysis",
            "credit_proposal"
        ]
        
        generated_sections = {}
        
        # Generate each section
        for section_type in sections_to_generate:
            try:
                # Check if section already exists
                existing_section = supabase.table("pm_sections").select("*").eq("case_id", case_id).eq("section_type", section_type).execute()
                
                if existing_section.data:
                    # Update existing section
                    ai_content = await generate_section_content(section_type, company, case, context_data)
                    
                    updated_section = supabase.table("pm_sections").update({
                        "ai_content": ai_content,
                        "version": existing_section.data[0]["version"] + 1
                    }).eq("id", existing_section.data[0]["id"]).execute()
                    
                    generated_sections[section_type] = updated_section.data[0]
                else:
                    # Create new section
                    ai_content = await generate_section_content(section_type, company, case, context_data)
                    
                    new_section = supabase.table("pm_sections").insert({
                        "case_id": case_id,
                        "section_type": section_type,
                        "title": section_type.replace("_", " ").title(),
                        "ai_content": ai_content,
                        "version": 1
                    }).execute()
                    
                    generated_sections[section_type] = new_section.data[0]
                    
            except Exception as e:
                print(f"Error generating section {section_type}: {e}")
                # Continue with other sections even if one fails
                generated_sections[section_type] = {
                    "error": f"Failed to generate {section_type}: {str(e)}"
                }
        
        # Update case status to indicate PM generation is complete
        supabase.table("pm_cases").update({
            "status": "in_progress",
            "updated_at": "NOW()"
        }).eq("id", case_id).execute()
        
        # Log the complete PM generation
        await log_ai_generation(case_id, "complete_pm", f"Generated complete PM with {len(sections_to_generate)} sections", f"Successfully generated: {list(generated_sections.keys())}", "gpt-4")
        
        return {
            "case_id": case_id,
            "status": "success",
            "sections": generated_sections,
            "message": f"Generated {len(generated_sections)} sections successfully"
        }
        
    except Exception as e:
        error_msg = f"Failed to generate complete PM: {str(e)}"
        await log_ai_generation(case_id, "complete_pm_error", "Complete PM generation failed", error_msg, "gpt-4")
        raise Exception(error_msg)

async def log_ai_generation(
    case_id: str,
    section_type: str,
    prompt: str,
    response: str,
    model_version: str
) -> None:
    """
    Log AI generation to audit trail.
    """
    try:
        supabase = get_supabase()
        
        supabase.table("audit_log").insert({
            "case_id": case_id,
            "action": f"ai_generate_{section_type}",
            "prompt": prompt,
            "ai_response": response,
            "model_version": model_version,
            "user_id": None  # System generated
        }).execute()
        
    except Exception as e:
        print(f"Failed to log AI generation: {e}")  # Log error but don't fail the request