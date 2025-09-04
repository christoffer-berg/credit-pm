from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Any
from schemas.pm_section import PMSection, PMSectionCreate, PMSectionUpdate
from services.auth import verify_token
from services.ai_generator import generate_section_content
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

@router.post("/{case_id}/generate", response_model=PMSection)
async def generate_section(
    case_id: str,
    section_type: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    supabase = get_supabase()
    
    try:
        case_result = supabase.table("pm_cases").select("*").eq("id", case_id).execute()
        if not case_result.data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case = case_result.data[0]
        company_result = supabase.table("companies").select("*").eq("id", case["company_id"]).execute()
        company = company_result.data[0] if company_result.data else None
        
        ai_content = await generate_section_content(section_type, company, case)
        
        # Check if section already exists
        existing_section = supabase.table("pm_sections").select("*").eq("case_id", case_id).eq("section_type", section_type).execute()
        
        if existing_section.data:
            # Update existing section
            section_result = supabase.table("pm_sections").update({
                "ai_content": ai_content,
                "version": existing_section.data[0]["version"] + 1,
                "updated_at": "NOW()"
            }).eq("id", existing_section.data[0]["id"]).execute()
        else:
            # Create new section
            section_result = supabase.table("pm_sections").insert({
                "case_id": case_id,
                "section_type": section_type,
                "title": section_type.replace("_", " ").title(),
                "ai_content": ai_content,
                "version": 1
            }).execute()
        
        return section_result.data[0]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{case_id}", response_model=List[PMSection])
async def get_case_sections(
    case_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    supabase = get_supabase()
    
    result = supabase.table("pm_sections").select("*").eq("case_id", case_id).execute()
    return result.data

@router.put("/{section_id}", response_model=PMSection)
async def update_section(
    section_id: str,
    section_update: PMSectionUpdate,
    current_user: Optional[Any] = Depends(optional_auth())
):
    supabase = get_supabase()
    
    try:
        result = supabase.table("pm_sections").update({
            "user_content": section_update.user_content
        }).eq("id", section_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Section not found")
        
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))