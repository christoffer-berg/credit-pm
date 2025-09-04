#!/usr/bin/env python3
"""
Simple test script to validate PM generation functionality 
without requiring full dependency installation.
"""

def test_pm_generation_logic():
    """Test the core PM generation logic without external dependencies."""
    
    # Mock data structures
    mock_company = {
        "id": "test-company-id",
        "name": "Test Company AB", 
        "organization_number": "5566778899",
        "business_description": "Technology consulting services",
        "industry_code": "62090"
    }
    
    mock_case = {
        "id": "test-case-id",
        "company_id": "test-company-id",
        "title": "Credit PM for Test Company AB",
        "status": "draft"
    }
    
    mock_financials = [
        {"year": 2023, "revenue": 10000000, "profit": 1500000, "assets": 8000000, "liabilities": 3000000},
        {"year": 2022, "revenue": 9000000, "profit": 1200000, "assets": 7500000, "liabilities": 2800000},
        {"year": 2021, "revenue": 8500000, "profit": 1000000, "assets": 7000000, "liabilities": 2600000}
    ]
    
    mock_context = {
        "financials": mock_financials,
        "financial_ratios": {
            "profit_margin": 15.0,
            "revenue_growth": 11.1,
            "debt_to_assets": 37.5
        },
        "credit_score": {
            "score": 650,
            "rating": "A",
            "factors": ["Strong profitability", "Positive revenue growth"]
        },
        "case": mock_case,
        "company": mock_company
    }
    
    # Test prompt generation functions
    print("Testing PM Generation Prompts:")
    print("=" * 50)
    
    # Test purpose prompt
    purpose_prompt = generate_purpose_prompt(mock_company, mock_case, mock_context)
    print("✓ Purpose prompt generated")
    assert "Test Company AB" in purpose_prompt
    assert "5566778899" in purpose_prompt
    
    # Test business description prompt
    business_prompt = generate_business_description_prompt(mock_company, mock_case, mock_context)
    print("✓ Business description prompt generated")
    assert "Technology consulting services" in business_prompt
    
    # Test financial analysis prompt
    financial_prompt = generate_financial_analysis_prompt(mock_company, mock_case, mock_context)
    print("✓ Financial analysis prompt generated")
    print("DEBUG: Financial prompt:", financial_prompt[:500])
    assert "15.00%" in financial_prompt  # Profit margin
    assert "11.10%" in financial_prompt  # Revenue growth
    
    # Test credit analysis prompt
    credit_prompt = generate_credit_analysis_prompt(mock_company, mock_case, mock_context)
    print("✓ Credit analysis prompt generated")
    assert "650/1000" in credit_prompt  # Credit score
    assert "Strong profitability" in credit_prompt
    
    # Test credit proposal prompt
    proposal_prompt = generate_credit_proposal_prompt(mock_company, mock_case, mock_context)
    print("✓ Credit proposal prompt generated")
    assert "15.0% margin" in proposal_prompt
    
    print("\n✅ All PM generation tests passed!")
    return True


def generate_purpose_prompt(company, case, context=None):
    """Mock version of purpose prompt generator."""
    company_name = company.get("name", "the company") if company else "the company"
    return f"""
    Write a brief purpose statement for a credit memo analyzing {company_name}.
    
    Company Information:
    - Name: {company.get("name", "Unknown") if company else "Unknown"}
    - Organization Number: {company.get("organization_number", "Unknown") if company else "Unknown"}
    - Business: {company.get("business_description", "Unknown business") if company else "Unknown business"}
    
    The purpose should be 2-3 sentences explaining why this credit analysis is being conducted.
    """

def generate_business_description_prompt(company, case, context=None):
    """Mock version of business description prompt generator."""
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

def generate_financial_analysis_prompt(company, case, context=None):
    """Mock version of financial analysis prompt generator."""
    company_name = company.get("name", "the company") if company else "the company"
    
    financial_context = ""
    ratios_context = ""
    
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
    
    return f"""
    Write a comprehensive financial analysis for {company_name}.
    {financial_context}
    {ratios_context}
    
    Include detailed analysis of:
    - Revenue trends, growth patterns, and profitability metrics
    - Financial strength indicators and balance sheet stability
    - Key financial ratios and their implications for creditworthiness
    
    Provide specific quantitative insights and identify key strengths and weaknesses.
    Write 3-4 paragraphs with professional banking language and clear risk assessment.
    """

def generate_credit_analysis_prompt(company, case, context=None):
    """Mock version of credit analysis prompt generator."""
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
    
    return f"""
    Write a comprehensive credit risk analysis for {company_name} operating in {industry}.
    {credit_score_context}
    
    Provide detailed assessment of:
    - Primary credit risk factors and available mitigants
    - Financial risk profile based on calculated metrics
    - Overall creditworthiness and risk rating justification
    
    Write 3-4 paragraphs with structured risk assessment and specific recommendations.
    """

def generate_credit_proposal_prompt(company, case, context=None):
    """Mock version of credit proposal prompt generator."""
    company_name = company.get("name", "the company") if company else "the company"
    
    financial_summary = ""
    if context and context.get("financial_ratios"):
        ratios = context["financial_ratios"]
        if 'profit_margin' in ratios and 'revenue_growth' in ratios:
            financial_summary = f"\nFinancial Position Summary:\n- Current profitability: {ratios['profit_margin']:.1f}% margin\n- Revenue trend: {ratios['revenue_growth']:.1f}% growth\n"
    
    return f"""
    Write a comprehensive credit proposal for {company_name}.
    {financial_summary}
    
    Structure your recommendation to include:
    - Recommended credit facility type and proposed amount
    - Proposed interest rate, fees, and key commercial terms
    - Financial covenants and ongoing monitoring requirements
    
    Provide a clear final recommendation with detailed rationale.
    Write 3-4 paragraphs with specific commercial terms.
    """

if __name__ == "__main__":
    test_pm_generation_logic()