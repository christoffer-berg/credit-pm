from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from services.auth import verify_token
from services.document_exporter import export_to_word, export_to_pdf
from core.database import get_supabase
import tempfile
import os

router = APIRouter()

@router.post("/{case_id}/word")
async def export_case_to_word(
    case_id: str,
    current_user = Depends(verify_token)
):
    supabase = get_supabase()
    
    try:
        case_result = supabase.table("pm_cases").select("*").eq("id", case_id).execute()
        if not case_result.data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case = case_result.data[0]
        
        company_result = supabase.table("companies").select("*").eq("id", case["company_id"]).execute()
        company = company_result.data[0] if company_result.data else None
        
        sections_result = supabase.table("pm_sections").select("*").eq("case_id", case_id).execute()
        sections = sections_result.data
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        file_path = export_to_word(case, company, sections, temp_file.name)
        
        return FileResponse(
            path=file_path,
            filename=f"credit_pm_{case['title'].replace(' ', '_')}.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{case_id}/pdf")
async def export_case_to_pdf(
    case_id: str,
    current_user = Depends(verify_token)
):
    supabase = get_supabase()
    
    try:
        case_result = supabase.table("pm_cases").select("*").eq("id", case_id).execute()
        if not case_result.data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case = case_result.data[0]
        
        company_result = supabase.table("companies").select("*").eq("id", case["company_id"]).execute()
        company = company_result.data[0] if company_result.data else None
        
        sections_result = supabase.table("pm_sections").select("*").eq("case_id", case_id).execute()
        sections = sections_result.data
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        file_path = export_to_pdf(case, company, sections, temp_file.name)
        
        return FileResponse(
            path=file_path,
            filename=f"credit_pm_{case['title'].replace(' ', '_')}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))