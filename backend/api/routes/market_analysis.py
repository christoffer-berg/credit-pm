from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from services.market_analysis import market_analysis_service

router = APIRouter(prefix="/market-analysis", tags=["market-analysis"])

class MarketAnalysisRequest(BaseModel):
    business_area: str
    country: str = "sweden"

class SearchQueriesRequest(BaseModel):
    business_area: str
    analysis_type: str  # market_demand, revenue_profitability, etc.
    country: str = "sweden"

class ResearchRequest(BaseModel):
    business_area: str
    search_queries: List[str]
    analysis_type: str
    country: str = "sweden"

@router.post("/comprehensive")
async def generate_comprehensive_analysis(request: MarketAnalysisRequest):
    """
    Generate a comprehensive market analysis covering all aspects.
    """
    try:
        result = await market_analysis_service.generate_comprehensive_market_analysis(
            business_area=request.business_area,
            country=request.country
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate market analysis: {str(e)}")

@router.post("/search-queries")
async def generate_search_queries(request: SearchQueriesRequest):
    """
    Generate search queries for a specific analysis type.
    """
    try:
        result = await market_analysis_service.generate_search_queries(
            business_area=request.business_area,
            analysis_type=request.analysis_type,
            country=request.country
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate search queries: {str(e)}")

@router.post("/research")
async def conduct_research(request: ResearchRequest):
    """
    Conduct market research using OpenRouter with specific queries.
    """
    try:
        result = await market_analysis_service.conduct_market_research(
            business_area=request.business_area,
            search_queries=request.search_queries,
            analysis_type=request.analysis_type,
            country=request.country
        )
        return {"research_content": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to conduct research: {str(e)}")

@router.get("/analysis-types")
async def get_analysis_types():
    """
    Get available analysis types.
    """
    return {
        "analysis_types": [
            {
                "key": "market_demand",
                "name": "Market Demand & Size",
                "description": "Analyze market demand patterns, size, and growth prospects"
            },
            {
                "key": "revenue_profitability", 
                "name": "Revenue & Profitability",
                "description": "Analyze revenue streams, profitability patterns, and financial performance"
            },
            {
                "key": "competitive_landscape",
                "name": "Competitive Landscape", 
                "description": "Analyze competitive positioning, market share, and competitive threats"
            },
            {
                "key": "regulation_environment",
                "name": "Regulation & External Environment",
                "description": "Analyze regulatory requirements and external environmental factors"
            },
            {
                "key": "operational_factors",
                "name": "Operational & Structural Factors",
                "description": "Analyze operational efficiency, cost structures, and business model factors"
            },
            {
                "key": "financing_capital",
                "name": "Financing & Capital Structure", 
                "description": "Analyze capital requirements, financing needs, and funding sources"
            },
            {
                "key": "innovation_technology",
                "name": "Innovation & Technology",
                "description": "Analyze technology trends, innovation requirements, and digital transformation"
            }
        ]
    }