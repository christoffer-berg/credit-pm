from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from schemas.financial import Financial, FinancialCreate, FinancialUpdate
from services.auth import verify_token
from services.financial_processor import process_financial_data
from core.database import get_supabase

router = APIRouter()

@router.post("/{company_id}/upload")
async def upload_financials(
    company_id: str,
    file: UploadFile = File(...),
    current_user = Depends(verify_token)
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Only Excel and CSV files are supported")
    
    try:
        financials = await process_financial_data(file, company_id)
        return {"message": f"Processed {len(financials)} financial records", "data": financials}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{company_id}", response_model=List[Financial])
async def get_company_financials(
    company_id: str,
    current_user = Depends(verify_token)
):
    supabase = get_supabase()
    
    result = supabase.table("financials").select("*").eq("company_id", company_id).order("year", desc=True).execute()
    return result.data

@router.post("/", response_model=Financial)
async def create_financial(
    financial: FinancialCreate,
    current_user = Depends(verify_token)
):
    supabase = get_supabase()
    
    try:
        result = supabase.table("financials").insert(financial.model_dump()).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))