"""SLA service - handles SLA calculations and tracking"""

from datetime import datetime, timedelta
from app.config import get_settings
from app.utils.supabase_client import get_supabase_client
from typing import Optional

settings = get_settings()


class SLAService:
    """Service for SLA management"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.sla_duration = timedelta(minutes=settings.default_sla_duration_minutes)
    
    async def calculate_sla_deadline(self, deadline: datetime) -> Optional[datetime]:
        """Calculate SLA deadline based on lead deadline"""
        if not deadline:
            return None
        
        # SLA deadline is the lead deadline
        return deadline
    
    async def check_sla_breach(self, lead_id: str) -> bool:
        """Check if a lead has breached SLA"""
        lead_response = self.client.table("leads").select("sla_deadline").eq("id", lead_id).execute()
        
        if not lead_response.data:
            return False
        
        lead = lead_response.data[0]
        sla_deadline = lead.get("sla_deadline")
        
        if not sla_deadline:
            return False
        
        from datetime import timezone
        sla_datetime = datetime.fromisoformat(sla_deadline)
        if sla_datetime.tzinfo is None:
            sla_datetime = sla_datetime.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > sla_datetime
    
    async def get_approaching_deadlines(self, minutes_window: int = 30):
        """Get leads with deadlines approaching in the next N minutes"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        window_start = now
        window_end = now + timedelta(minutes=minutes_window)
        
        response = self.client.table("leads").select("*").filter(
            "deadline",
            "gte",
            window_start.isoformat()
        ).filter(
            "deadline",
            "lte",
            window_end.isoformat()
        ).eq("status", "active").execute()
        
        return response.data if response.data else []
    
    async def get_breached_leads(self):
        """Get leads that have breached SLA"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        response = self.client.table("leads").select("*").filter(
            "sla_deadline",
            "lt",
            now.isoformat()
        ).eq("status", "active").execute()
        
        return response.data if response.data else []
    
    async def mark_sla_breached(self, lead_id: str):
        """Mark lead as SLA breached"""
        self.client.table("leads").update({
            "status": "sla_breached"
        }).eq("id", lead_id).execute()
