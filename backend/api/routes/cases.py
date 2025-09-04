from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from schemas.pm_case import PMCase, PMCaseCreate, PMCaseUpdate
from services.auth import verify_token
from services.bolagsverket import fetch_company_data
from services.ai_generator import generate_complete_pm
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

@router.post("/", response_model=PMCase)
async def create_case(
    case_data: PMCaseCreate,
    current_user: Optional[Any] = Depends(optional_auth())
):
    supabase = get_supabase()
    
    try:
        company_data = await fetch_company_data(case_data.organization_number)
        
        company_result = supabase.table("companies").insert({
            "organization_number": case_data.organization_number,
            "name": company_data.get("name", "Unknown Company"),
            "business_description": company_data.get("business_description"),
            "industry_code": company_data.get("industry_code")
        }).execute()
        
        company_id = company_result.data[0]["id"]
        
        title = case_data.title or f"Credit PM for {company_data.get('name', 'Company')}"
        
        case_result = supabase.table("pm_cases").insert({
            "company_id": company_id,
            "title": title,
            "status": "draft",
            "version": 1,
            "created_by": current_user.get("id", "3859bee9-fcf3-4105-872c-96063162830f") if current_user else "3859bee9-fcf3-4105-872c-96063162830f"
        }).execute()
        
        return case_result.data[0]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[PMCase])
async def list_cases(
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[Any] = Depends(optional_auth())
):
    supabase = get_supabase()
    
    result = supabase.table("pm_cases").select("*").range(skip, skip + limit - 1).execute()
    return result.data

@router.get("/{case_id}", response_model=PMCase)
async def get_case(
    case_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    supabase = get_supabase()
    
    result = supabase.table("pm_cases").select("*").eq("id", case_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return result.data[0]

@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """
    Delete a PM case and all related data (sections, audit logs, company if no other cases use it).
    """
    supabase = get_supabase()
    
    try:
        # First check if the case exists
        case_result = supabase.table("pm_cases").select("*").eq("id", case_id).execute()
        if not case_result.data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case = case_result.data[0]
        company_id = case["company_id"]
        
        # Get all section IDs for this case to delete audit logs
        sections_result = supabase.table("pm_sections").select("id").eq("case_id", case_id).execute()
        section_ids = [section["id"] for section in sections_result.data]
        
        # Delete audit logs related to this case
        try:
            audit_result = supabase.table("audit_log").delete().eq("case_id", case_id).execute()
            print(f"Deleted audit logs for case {case_id}: {len(audit_result.data) if audit_result.data else 0} records")
        except Exception as e:
            print(f"Error deleting audit logs for case {case_id}: {e}")
        
        # Delete audit logs related to sections of this case
        for section_id in section_ids:
            try:
                section_audit_result = supabase.table("audit_log").delete().eq("section_id", section_id).execute()
                print(f"Deleted audit logs for section {section_id}: {len(section_audit_result.data) if section_audit_result.data else 0} records")
            except Exception as e:
                print(f"Error deleting audit logs for section {section_id}: {e}")
        
        # Delete all sections for this case (CASCADE should handle this but let's be explicit)
        try:
            sections_delete_result = supabase.table("pm_sections").delete().eq("case_id", case_id).execute()
            print(f"Deleted sections for case {case_id}: {len(sections_delete_result.data) if sections_delete_result.data else 0} records")
        except Exception as e:
            print(f"Error deleting sections for case {case_id}: {e}")
            raise e
        
        # Delete the case
        try:
            case_delete_result = supabase.table("pm_cases").delete().eq("id", case_id).execute()
            print(f"Deleted case {case_id}: {len(case_delete_result.data) if case_delete_result.data else 0} records")
        except Exception as e:
            print(f"Error deleting case {case_id}: {e}")
            raise e
        
        # Check if the company is used by other cases
        other_cases = supabase.table("pm_cases").select("id").eq("company_id", company_id).execute()
        if not other_cases.data:
            # Delete document embeddings for this company
            try:
                embeddings_result = supabase.table("document_embeddings").delete().eq("company_id", company_id).execute()
                print(f"Deleted embeddings for company {company_id}: {len(embeddings_result.data) if embeddings_result.data else 0} records")
            except Exception as e:
                print(f"Error deleting embeddings for company {company_id}: {e}")
            
            # Delete financial data for this company (CASCADE should handle this)
            try:
                financials_result = supabase.table("financials").delete().eq("company_id", company_id).execute()
                print(f"Deleted financials for company {company_id}: {len(financials_result.data) if financials_result.data else 0} records")
            except Exception as e:
                print(f"Error deleting financials for company {company_id}: {e}")
            
            # Delete the company
            try:
                company_delete_result = supabase.table("companies").delete().eq("id", company_id).execute()
                print(f"Deleted company {company_id}: {len(company_delete_result.data) if company_delete_result.data else 0} records")
            except Exception as e:
                print(f"Error deleting company {company_id}: {e}")
        
        return {"message": "Case deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in delete_case for {case_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Failed to delete case: {str(e)}")

@router.post("/{case_id}/generate", response_model=Dict[str, Any])
async def generate_case_pm(
    case_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """
    Generate a complete PM with all sections for the given case.
    This will create or update all standard PM sections with AI-generated content.
    """
    try:
        result = await generate_complete_pm(case_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))