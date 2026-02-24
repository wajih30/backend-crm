"""Audit service - handles audit log operations"""

from app.utils.supabase_client import get_supabase_client
from typing import Optional, List, Dict, Any

class AuditService:
    """Service for audit log management"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def get_audit_logs(
        self,
        action_type: Optional[str] = None,
        lead_id: Optional[str] = None,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filters"""
        query = self.client.table("status_history").select("*")
        
        if action_type:
            query = query.eq("action_type", action_type)
        if lead_id:
            query = query.eq("lead_id", lead_id)
        if user_id:
            query = query.eq("updated_by", user_id)
        
        response = query.order("updated_at", desc=True).range(skip, skip + limit - 1).execute()
        
        return response.data if response.data else []
    
    async def log_action(
        self,
        lead_id: str,
        action_type: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an action to audit trail"""
        self.client.table("status_history").insert({
            "lead_id": lead_id,
            "action_type": action_type,
            "updated_by": user_id,
            "metadata": metadata or {}
        }).execute()
