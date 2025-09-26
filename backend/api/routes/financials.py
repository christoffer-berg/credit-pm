from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from typing import List, Optional, Any, Dict
import os
import json
from datetime import datetime
from pathlib import Path

from schemas.financial_data import (
    FinancialStatement, FinancialDataCreate, FinancialDataUpdate, 
    FinancialProjection, FinancialAnalysis, AllabolagCompanyData, PDFUploadResponse
)
from services.auth import verify_token
from services.allabolag_scraper import fetch_allabolag_data, AllabolagScraper
from services.pdf_parser import parse_financial_pdf_file, FinancialPDFParser
from services.financial_projections import create_financial_projections, ProjectionAssumptions
from services.financial_analyzer import analyze_company_financials
from core.database import get_supabase
from core.config import settings

# Development flag - set to False to disable auth
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

def optional_auth():
    """Optional authentication dependency"""
    if REQUIRE_AUTH:
        return Depends(verify_token)
    else:
        return lambda: {"id": "3859bee9-fcf3-4105-872c-96063162830f"}  # Use existing dev user

router = APIRouter()

@router.get("/companies/{company_id}/allabolag", response_model=Dict[str, Any])
async def fetch_allabolag_financial_data(
    company_id: str,
    org_number: Optional[str] = Query(None, description="Organization number"),
    company_name: Optional[str] = Query(None, description="Company name"),
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Fetch financial data from allabolag.se"""
    supabase = get_supabase()
    
    try:
        # Get company info if not provided
        if not org_number and not company_name:
            company_result = supabase.table("companies").select("*").eq("id", company_id).execute()
            if not company_result.data:
                raise HTTPException(status_code=404, detail="Company not found")
            
            company = company_result.data[0]
            org_number = company.get("organization_number")
            company_name = company.get("name")
        
        if not org_number and not company_name:
            raise HTTPException(status_code=400, detail="Organization number or company name required")
        
        # Fetch data from allabolag.se
        allabolag_data = await fetch_allabolag_data(org_number, company_name)
        
        if not allabolag_data["success"]:
            raise HTTPException(status_code=404, detail="No financial data found on allabolag.se")
        
        # Store financial statements in database
        if allabolag_data["financial_statements"]:
            for stmt_data in allabolag_data["financial_statements"]:
                # Check if statement already exists
                existing = supabase.table("financial_statements").select("id").eq("company_id", company_id).eq("year", stmt_data["year"]).execute()
                
                if existing.data:
                    # Update existing
                    supabase.table("financial_statements").update({
                        **stmt_data,
                        "company_id": company_id,
                        "updated_at": "NOW()"
                    }).eq("id", existing.data[0]["id"]).execute()
                else:
                    # Insert new
                    supabase.table("financial_statements").insert({
                        **stmt_data,
                        "company_id": company_id
                    }).execute()
        
        return {
            "success": True,
            "data": allabolag_data,
            "statements_imported": len(allabolag_data["financial_statements"]),
            "source": "allabolag.se"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching allabolag data: {str(e)}")

@router.post("/companies/{company_id}/upload-pdf", response_model=PDFUploadResponse)
async def upload_financial_pdf(
    company_id: str,
    file: UploadFile = File(...),
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Upload and parse financial PDF document"""
    
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    supabase = get_supabase()
    
    try:
        # Verify company exists
        company_result = supabase.table("companies").select("id").eq("id", company_id).execute()
        if not company_result.data:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Read file content
        file_content = await file.read()
        
        # Enforce 50MB size limit using actual bytes read
        if len(file_content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Parse PDF
        parse_result = await parse_financial_pdf_file(file_content, file.filename, company_id)
        
        # Store document record
        document_record = supabase.table("financial_documents").insert({
            "company_id": company_id,
            "filename": file.filename,
            "file_path": parse_result["upload_path"],
            "file_size": len(file_content),
            "mime_type": file.content_type,
            "parsing_status": parse_result["parsing_status"],
            "extracted_data": parse_result.get("extracted_data"),
            "error_message": parse_result.get("error_message"),
            "uploaded_by": (current_user.get("id") if isinstance(current_user, dict) else None) if current_user else None
        }).execute()
        
        # If parsing was successful, store financial statements
        if parse_result["parsing_status"] == "completed" and parse_result.get("extracted_data", {}).get("financial_statements"):
            for stmt_data in parse_result["extracted_data"]["financial_statements"]:
                # Check if statement already exists
                existing = supabase.table("financial_statements").select("id").eq("company_id", company_id).eq("year", stmt_data["year"]).execute()
                
                stmt_data["company_id"] = company_id
                stmt_data["source_document"] = file.filename
                
                if existing.data:
                    # Update existing
                    supabase.table("financial_statements").update({
                        **stmt_data,
                        "updated_at": "NOW()"
                    }).eq("id", existing.data[0]["id"]).execute()
                else:
                    # Insert new
                    supabase.table("financial_statements").insert(stmt_data).execute()
        
        response = PDFUploadResponse(**parse_result)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.get("/companies/{company_id}/statements", response_model=List[FinancialStatement])
async def get_financial_statements(
    company_id: str,
    years: Optional[List[int]] = Query(None, description="Specific years to retrieve"),
    limit: Optional[int] = Query(10, description="Maximum number of statements to return"),
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Get financial statements for a company"""
    supabase = get_supabase()
    
    try:
        query = supabase.table("financial_statements").select("*").eq("company_id", company_id)
        
        if years:
            query = query.in_("year", years)
        
        result = query.order("year", desc=True).limit(limit).execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving financial statements: {str(e)}")

@router.post("/companies/{company_id}/statements", response_model=FinancialStatement)
async def create_financial_statement(
    company_id: str,
    statement: FinancialStatement,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Create or update a financial statement"""
    supabase = get_supabase()
    
    try:
        # Verify company exists
        company_result = supabase.table("companies").select("id").eq("id", company_id).execute()
        if not company_result.data:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Use Pydantic v2 JSON mode to ensure date/Decimal are serializable
        statement_data = statement.model_dump(mode="json")
        statement_data["company_id"] = company_id
        
        # Check if statement already exists for this year
        existing = supabase.table("financial_statements").select("id").eq("company_id", company_id).eq("year", statement.year).execute()
        
        if existing.data:
            # Update existing
            result = supabase.table("financial_statements").update({
                **statement_data,
                "updated_at": "NOW()"
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            # Insert new
            result = supabase.table("financial_statements").insert(statement_data).execute()
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating financial statement: {str(e)}")

@router.put("/statements/{statement_id}", response_model=FinancialStatement)
async def update_financial_statement(
    statement_id: str,
    statement_update: FinancialDataUpdate,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Update a specific financial statement"""
    supabase = get_supabase()
    
    try:
        # Verify statement exists
        existing = supabase.table("financial_statements").select("*").eq("id", statement_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Financial statement not found")
        
        # Update with first statement from the update (assuming single statement update)
        if not statement_update.financial_statements:
            raise HTTPException(status_code=400, detail="No financial statement data provided")
        
        # Ensure JSON-serializable types for Supabase
        update_data = statement_update.financial_statements[0].model_dump(mode="json")
        update_data["updated_at"] = "NOW()"
        
        result = supabase.table("financial_statements").update(update_data).eq("id", statement_id).execute()
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating financial statement: {str(e)}")

@router.post("/companies/{company_id}/projections", response_model=Dict[str, Any])
async def generate_financial_projections(
    company_id: str,
    assumptions: Optional[Dict[str, Any]] = None,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Generate financial projections based on historical data"""
    supabase = get_supabase()
    
    try:
        # Get historical financial statements
        statements_result = supabase.table("financial_statements").select("*").eq("company_id", company_id).order("year", desc=True).limit(10).execute()
        
        if not statements_result.data:
            raise HTTPException(status_code=404, detail="No historical financial data found")
        
        # Convert to FinancialStatement objects
        historical_statements = [FinancialStatement(**data) for data in statements_result.data]
        
        # Generate projections
        projections_result = await create_financial_projections(
            historical_data=historical_statements,
            assumptions=assumptions
        )
        
        if not projections_result["success"]:
            raise HTTPException(status_code=400, detail=projections_result.get("error", "Failed to generate projections"))
        
        # Store projections in database
        for projection_data in projections_result["projections"]:
            # Check if projection already exists
            existing = supabase.table("financial_projections").select("id").eq("company_id", company_id).eq("year", projection_data["year"]).execute()
            
            projection_record = {
                "company_id": company_id,
                "year": projection_data["year"],
                "revenue_growth": float(projection_data["revenue_growth"]) if projection_data["revenue_growth"] else None,
                "margin_assumptions": projection_data["margin_assumptions"],
                "projected_revenue": float(projection_data["projected_revenue"]) if projection_data["projected_revenue"] else None,
                "projected_ebitda": float(projection_data["projected_ebitda"]) if projection_data["projected_ebitda"] else None,
                "projected_net_profit": float(projection_data["projected_net_profit"]) if projection_data["projected_net_profit"] else None,
                "assumptions": projection_data["assumptions"],
                "confidence_level": projection_data["confidence_level"]
            }
            
            if existing.data:
                # Update existing
                supabase.table("financial_projections").update({
                    **projection_record,
                    "updated_at": "NOW()"
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Insert new
                supabase.table("financial_projections").insert(projection_record).execute()
        
        return projections_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating projections: {str(e)}")

@router.get("/companies/{company_id}/projections", response_model=List[FinancialProjection])
async def get_financial_projections(
    company_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Get stored financial projections for a company"""
    supabase = get_supabase()
    
    try:
        result = supabase.table("financial_projections").select("*").eq("company_id", company_id).order("year").execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving projections: {str(e)}")

@router.post("/companies/{company_id}/analyze", response_model=Dict[str, Any])
async def generate_financial_analysis(
    company_id: str,
    case_id: Optional[str] = None,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Generate comprehensive financial analysis"""
    supabase = get_supabase()
    
    try:
        # Get historical financial statements
        statements_result = supabase.table("financial_statements").select("*").eq("company_id", company_id).order("year", desc=True).limit(10).execute()
        
        if not statements_result.data:
            raise HTTPException(status_code=404, detail="No historical financial data found for analysis")
        
        # Generate analysis
        analysis_result = await analyze_company_financials(
            company_id=company_id,
            historical_data=statements_result.data,
            case_id=case_id
        )
        
        if not analysis_result["success"]:
            raise HTTPException(status_code=400, detail=analysis_result.get("error", "Failed to generate analysis"))
        
        # Store analysis in database
        analysis_record = {
            "company_id": company_id,
            "case_id": case_id,
            "analysis_text": analysis_result["analysis"]["analysis_text"],
            "key_metrics": analysis_result["analysis"]["key_metrics"],
            "years_analyzed": [stmt["year"] for stmt in statements_result.data],
            "projection_years": [proj["year"] for proj in analysis_result["analysis"]["projections"]],
            "model_used": "gpt-4"
        }
        
        supabase.table("financial_analyses").insert(analysis_record).execute()
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating financial analysis: {str(e)}")

@router.get("/companies/{company_id}/analyses", response_model=List[Dict[str, Any]])
async def get_financial_analyses(
    company_id: str,
    case_id: Optional[str] = Query(None),
    limit: Optional[int] = Query(5),
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Get stored financial analyses for a company"""
    supabase = get_supabase()
    
    try:
        query = supabase.table("financial_analyses").select("*").eq("company_id", company_id)
        
        if case_id:
            query = query.eq("case_id", case_id)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analyses: {str(e)}")

@router.get("/companies/{company_id}/documents", response_model=List[Dict[str, Any]])
async def get_financial_documents(
    company_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Get uploaded financial documents for a company"""
    supabase = get_supabase()
    
    try:
        result = supabase.table("financial_documents").select("*").eq("company_id", company_id).order("upload_date", desc=True).execute()
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_financial_document(
    document_id: str,
    delete_statements: Optional[bool] = Query(False, description="Also delete financial statements parsed from this document"),
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Delete an uploaded financial document and optionally its parsed statements"""
    supabase = get_supabase()
    try:
        # Fetch document
        existing = supabase.table("financial_documents").select("*").eq("id", document_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Document not found")
        doc = existing.data[0]

        # Attempt to remove file from filesystem
        file_path = doc.get("file_path")
        if file_path:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
            except Exception:
                # Do not fail the whole request if file deletion fails
                pass

        # Optionally delete parsed statements sourced from this document
        deleted_statements = 0
        if delete_statements:
            try:
                del_res = supabase.table("financial_statements").delete() \
                    .eq("company_id", doc.get("company_id")) \
                    .eq("source_document", doc.get("filename")).execute()
                if del_res.data:
                    deleted_statements = len(del_res.data)
            except Exception:
                # Keep proceeding even if this fails
                pass

        # Delete document record
        supabase.table("financial_documents").delete().eq("id", document_id).execute()

        return {"message": "Document deleted", "deleted_statements": deleted_statements}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.delete("/statements/{statement_id}")
async def delete_financial_statement(
    statement_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Delete a financial statement"""
    supabase = get_supabase()
    
    try:
        # Verify statement exists
        existing = supabase.table("financial_statements").select("id").eq("id", statement_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Financial statement not found")
        
        # Delete statement
        supabase.table("financial_statements").delete().eq("id", statement_id).execute()
        
        return {"message": "Financial statement deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting financial statement: {str(e)}")

@router.get("/companies/{company_id}/overview", response_model=Dict[str, Any])
async def get_financial_overview(
    company_id: str,
    current_user: Optional[Any] = Depends(optional_auth())
):
    """Get financial overview including statements, projections, and latest analysis"""
    supabase = get_supabase()
    
    try:
        # Get latest financial statements
        statements_result = supabase.table("financial_statements").select("*").eq("company_id", company_id).order("year", desc=True).limit(5).execute()
        
        # Get latest projections
        projections_result = supabase.table("financial_projections").select("*").eq("company_id", company_id).order("year").limit(5).execute()
        
        # Get latest analysis
        analysis_result = supabase.table("financial_analyses").select("*").eq("company_id", company_id).order("created_at", desc=True).limit(1).execute()
        
        # Get documents
        documents_result = supabase.table("financial_documents").select("filename, parsing_status, upload_date").eq("company_id", company_id).order("upload_date", desc=True).limit(5).execute()
        
        return {
            "company_id": company_id,
            "historical_statements": statements_result.data,
            "projections": projections_result.data,
            "latest_analysis": analysis_result.data[0] if analysis_result.data else None,
            "uploaded_documents": documents_result.data,
            "overview": {
                "years_available": len(statements_result.data),
                "has_projections": len(projections_result.data) > 0,
                "has_analysis": len(analysis_result.data) > 0,
                "latest_year": max(stmt["year"] for stmt in statements_result.data) if statements_result.data else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving financial overview: {str(e)}")
