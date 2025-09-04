from typing import Dict, List, Optional, Any
from datetime import datetime
from core.database import get_supabase
import json
from enum import Enum

class AuditAction(str, Enum):
    CASE_CREATED = "case_created"
    CASE_UPDATED = "case_updated"
    SECTION_GENERATED = "section_generated"
    SECTION_UPDATED = "section_updated"
    SECTION_REGENERATED = "section_regenerated"
    DOCUMENT_EXPORTED = "document_exported"
    FINANCIAL_UPLOADED = "financial_uploaded"
    LOGIN = "user_login"
    LOGOUT = "user_logout"

class AuditService:
    """Service for handling audit logging and version control."""
    
    @staticmethod
    async def log_action(
        action: AuditAction,
        user_id: Optional[str] = None,
        case_id: Optional[str] = None,
        section_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        ai_response: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log an audit action to the database.
        """
        try:
            supabase = get_supabase()
            
            audit_data = {
                "action": action.value,
                "user_id": user_id,
                "case_id": case_id,
                "section_id": section_id,
                "prompt": prompt,
                "ai_response": ai_response,
                "model_version": model_version,
                "created_at": datetime.now().isoformat()
            }
            
            # Add details as JSON if provided
            if details:
                audit_data["details"] = json.dumps(details)
            
            result = supabase.table("audit_log").insert(audit_data).execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            print(f"Failed to log audit action: {e}")
            return {}
    
    @staticmethod
    async def get_case_audit_trail(case_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete audit trail for a specific case.
        """
        try:
            supabase = get_supabase()
            
            result = supabase.table("audit_log") \
                .select("*") \
                .eq("case_id", case_id) \
                .order("created_at", desc=False) \
                .execute()
            
            return result.data or []
            
        except Exception as e:
            print(f"Failed to get audit trail: {e}")
            return []
    
    @staticmethod
    async def get_section_history(section_id: str) -> List[Dict[str, Any]]:
        """
        Get the edit history for a specific section.
        """
        try:
            supabase = get_supabase()
            
            result = supabase.table("audit_log") \
                .select("*") \
                .eq("section_id", section_id) \
                .order("created_at", desc=False) \
                .execute()
            
            return result.data or []
            
        except Exception as e:
            print(f"Failed to get section history: {e}")
            return []
    
    @staticmethod
    async def get_user_activity(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent activity for a specific user.
        """
        try:
            supabase = get_supabase()
            
            result = supabase.table("audit_log") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return result.data or []
            
        except Exception as e:
            print(f"Failed to get user activity: {e}")
            return []
    
    @staticmethod
    async def get_ai_usage_stats(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get AI usage statistics for analysis.
        """
        try:
            supabase = get_supabase()
            
            query = supabase.table("audit_log") \
                .select("action, model_version, created_at") \
                .like("action", "%generate%")
            
            if start_date:
                query = query.gte("created_at", start_date)
            if end_date:
                query = query.lte("created_at", end_date)
            
            result = query.execute()
            logs = result.data or []
            
            stats = {
                "total_generations": len(logs),
                "by_model": {},
                "by_action": {},
                "by_date": {}
            }
            
            for log in logs:
                # Count by model
                model = log.get("model_version", "unknown")
                stats["by_model"][model] = stats["by_model"].get(model, 0) + 1
                
                # Count by action
                action = log.get("action", "unknown")
                stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
                
                # Count by date
                date = log.get("created_at", "")[:10]  # Extract date part
                stats["by_date"][date] = stats["by_date"].get(date, 0) + 1
            
            return stats
            
        except Exception as e:
            print(f"Failed to get AI usage stats: {e}")
            return {}

class VersionManager:
    """Service for managing document versions."""
    
    @staticmethod
    async def create_section_version(section_id: str, content: str, user_id: str) -> Dict[str, Any]:
        """
        Create a new version of a section.
        """
        try:
            supabase = get_supabase()
            
            # Get current section
            section_result = supabase.table("pm_sections") \
                .select("*") \
                .eq("id", section_id) \
                .execute()
            
            if not section_result.data:
                raise ValueError("Section not found")
            
            section = section_result.data[0]
            current_version = section.get("version", 1)
            
            # Update section with new version and content
            update_result = supabase.table("pm_sections") \
                .update({
                    "user_content": content,
                    "version": current_version + 1,
                    "updated_at": datetime.now().isoformat()
                }) \
                .eq("id", section_id) \
                .execute()
            
            # Log the version change
            await AuditService.log_action(
                action=AuditAction.SECTION_UPDATED,
                user_id=user_id,
                case_id=section["case_id"],
                section_id=section_id,
                details={
                    "old_version": current_version,
                    "new_version": current_version + 1,
                    "content_length": len(content)
                }
            )
            
            return update_result.data[0] if update_result.data else {}
            
        except Exception as e:
            print(f"Failed to create section version: {e}")
            return {}
    
    @staticmethod
    async def get_section_versions(section_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a section from audit log.
        """
        try:
            audit_trail = await AuditService.get_section_history(section_id)
            
            versions = []
            for entry in audit_trail:
                if entry.get("action") in ["section_generated", "section_updated", "section_regenerated"]:
                    version_info = {
                        "timestamp": entry.get("created_at"),
                        "action": entry.get("action"),
                        "user_id": entry.get("user_id"),
                        "model_version": entry.get("model_version"),
                        "content_preview": (entry.get("ai_response", "")[:100] + "...") 
                                         if entry.get("ai_response") and len(entry.get("ai_response", "")) > 100 
                                         else entry.get("ai_response", "")
                    }
                    versions.append(version_info)
            
            return versions
            
        except Exception as e:
            print(f"Failed to get section versions: {e}")
            return []
    
    @staticmethod
    async def compare_versions(section_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """
        Compare two versions of a section (basic implementation).
        """
        try:
            # This is a simplified version comparison
            # In a full implementation, you'd store actual version content
            # and use a proper diff algorithm
            
            versions = await VersionManager.get_section_versions(section_id)
            
            if len(versions) < max(version1, version2):
                return {"error": "Version not found"}
            
            v1_data = versions[version1 - 1] if version1 <= len(versions) else None
            v2_data = versions[version2 - 1] if version2 <= len(versions) else None
            
            return {
                "version1": v1_data,
                "version2": v2_data,
                "comparison": "Detailed diff not implemented in MVP"
            }
            
        except Exception as e:
            return {"error": f"Failed to compare versions: {str(e)}"}

# Middleware function to automatically log certain actions
async def audit_middleware(action: AuditAction, context: Dict[str, Any]):
    """
    Middleware to automatically log actions based on context.
    """
    await AuditService.log_action(
        action=action,
        user_id=context.get("user_id"),
        case_id=context.get("case_id"),
        section_id=context.get("section_id"),
        details=context.get("details"),
        prompt=context.get("prompt"),
        ai_response=context.get("ai_response"),
        model_version=context.get("model_version")
    )