from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from schemas.company import Company, CompanyCreate, CompanyUpdate
from services.auth import verify_token
from services.web_search import generate_enhanced_business_description
from core.database import get_supabase
import os

# Development flag - set to False to disable auth
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

def optional_auth():
    """Optional authentication dependency"""
    if REQUIRE_AUTH:
        return Depends(verify_token)
    else:
        return lambda: {"id": "3859bee9-fcf3-4105-872c-96063162830f"}  # Use existing dev user

router = APIRouter()

@router.post("/", response_model=Company)
async def create_company(
    company: CompanyCreate,
    current_user = Depends(verify_token)
):
    supabase = get_supabase()
    
    try:
        result = supabase.table("companies").insert({
            "organization_number": company.organization_number,
            "name": company.name,
            "business_description": company.business_description,
            "industry_code": company.industry_code
        }).execute()
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Company])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(verify_token)
):
    supabase = get_supabase()
    
    result = supabase.table("companies").select("*").range(skip, skip + limit - 1).execute()
    return result.data

@router.get("/{company_id}", response_model=Company)
async def get_company(
    company_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    supabase = get_supabase()
    
    result = supabase.table("companies").select("*").eq("id", company_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return result.data[0]

@router.put("/{company_id}")
async def update_company(
    company_id: str,
    company_data: Dict[str, Any],
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Update company information"""
    supabase = get_supabase()
    
    # Check if company exists
    existing = supabase.table("companies").select("id").eq("id", company_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update company data
    result = supabase.table("companies").update(company_data).eq("id", company_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to update company")
    
    return result.data[0]

@router.post("/{company_id}/generate-description")
async def generate_company_description(
    company_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Generate enhanced business description using web search and AI"""
    supabase = get_supabase()
    
    # Get company data
    result = supabase.table("companies").select("*").eq("id", company_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company = result.data[0]
    company_name = company.get("name")
    website = company.get("website")
    existing_description = company.get("business_description")
    
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name is required for description generation")
    
    try:
        # Generate enhanced description
        enhanced_description = await generate_enhanced_business_description(
            company_name=company_name,
            website=website,
            existing_description=existing_description
        )
        
        # Update company with enhanced description
        update_result = supabase.table("companies").update({
            "business_description": enhanced_description
        }).eq("id", company_id).execute()
        
        if not update_result.data:
            raise HTTPException(status_code=400, detail="Failed to update company description")
        
        return {
            "company_id": company_id,
            "generated_description": enhanced_description,
            "company": update_result.data[0]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate description: {str(e)}")