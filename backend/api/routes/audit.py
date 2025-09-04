from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from services.auth import verify_token
from services.audit_service import AuditService, VersionManager
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/cases/{case_id}/trail")
async def get_case_audit_trail(
    case_id: str,
    current_user = Depends(verify_token)
):
    """Get the complete audit trail for a specific case."""
    try:
        trail = await AuditService.get_case_audit_trail(case_id)
        return {"case_id": case_id, "trail": trail}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sections/{section_id}/history")
async def get_section_history(
    section_id: str,
    current_user = Depends(verify_token)
):
    """Get the edit history for a specific section."""
    try:
        history = await AuditService.get_section_history(section_id)
        return {"section_id": section_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sections/{section_id}/versions")
async def get_section_versions(
    section_id: str,
    current_user = Depends(verify_token)
):
    """Get all versions of a section."""
    try:
        versions = await VersionManager.get_section_versions(section_id)
        return {"section_id": section_id, "versions": versions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sections/{section_id}/versions/compare")
async def compare_section_versions(
    section_id: str,
    version1: int = Query(..., description="First version to compare"),
    version2: int = Query(..., description="Second version to compare"),
    current_user = Depends(verify_token)
):
    """Compare two versions of a section."""
    try:
        comparison = await VersionManager.compare_versions(section_id, version1, version2)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    limit: int = Query(50, le=200, description="Maximum number of activities to return"),
    current_user = Depends(verify_token)
):
    """Get recent activity for a specific user."""
    # Verify user can access this data (self or admin)
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only view own activity")
    
    try:
        activity = await AuditService.get_user_activity(user_id, limit)
        return {"user_id": user_id, "activity": activity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/ai-usage")
async def get_ai_usage_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user = Depends(verify_token)
):
    """Get AI usage statistics."""
    try:
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        stats = await AuditService.get_ai_usage_stats(start_date, end_date)
        return {
            "period": {"start": start_date, "end": end_date},
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/system")
async def get_system_stats(
    current_user = Depends(verify_token)
):
    """Get overall system usage statistics."""
    try:
        from core.database import get_supabase
        supabase = get_supabase()
        
        # Get basic counts
        cases_result = supabase.table("pm_cases").select("id", count="exact").execute()
        companies_result = supabase.table("companies").select("id", count="exact").execute()
        sections_result = supabase.table("pm_sections").select("id", count="exact").execute()
        
        # Get recent activity (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_activity = supabase.table("audit_log") \
            .select("action") \
            .gte("created_at", week_ago) \
            .execute()
        
        activity_counts = {}
        for log in recent_activity.data or []:
            action = log.get("action", "unknown")
            activity_counts[action] = activity_counts.get(action, 0) + 1
        
        return {
            "totals": {
                "cases": cases_result.count,
                "companies": companies_result.count,
                "sections": sections_result.count
            },
            "recent_activity": activity_counts,
            "period": "Last 7 days"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))