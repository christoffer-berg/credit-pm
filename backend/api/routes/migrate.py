from fastapi import APIRouter, HTTPException
from core.database import get_supabase

router = APIRouter()

@router.post("/company-fields")
async def migrate_company_fields():
    """Add contact info fields to companies table"""
    supabase = get_supabase()
    
    # Check if columns already exist by trying to select them
    try:
        result = supabase.table("companies").select("website, email, phone, address, contact_person").limit(1).execute()
        return {"message": "Columns already exist", "status": "success"}
    except Exception:
        # Columns don't exist, need to add them via database admin
        return {
            "message": "Database schema migration required. Please add these columns to the companies table in Supabase dashboard:",
            "sql": """
            ALTER TABLE companies 
            ADD COLUMN IF NOT EXISTS website VARCHAR(255),
            ADD COLUMN IF NOT EXISTS email VARCHAR(255),
            ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
            ADD COLUMN IF NOT EXISTS address TEXT,
            ADD COLUMN IF NOT EXISTS contact_person VARCHAR(255);
            """,
            "status": "manual_migration_required"
        }