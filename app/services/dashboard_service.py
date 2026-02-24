"""Dashboard service - handles dashboard metrics and aggregations"""

from app.utils.supabase_client import get_supabase_client
from typing import Dict, List, Any
from datetime import datetime, timezone

class DashboardService:
    """Service for dashboard operations"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics"""
        # Get all leads
        leads_response = self.client.table("leads").select("*").execute()
        leads = leads_response.data if leads_response.data else []
        
        # Calculate metrics
        total_leads = len(leads)
        active_leads = sum(1 for lead in leads if lead.get("status") in ["active", "in_progress"])
        closed_leads = sum(1 for lead in leads if lead.get("status") == "closed")
        
        # Use UTC aware datetime for comparison
        now = datetime.now(timezone.utc)
        sla_breaches = 0
        for lead in leads:
            if lead.get("sla_deadline"):
                deadline = datetime.fromisoformat(lead["sla_deadline"])
                # Ensure deadline is aware (usually it is from Supabase, but safety first)
                if deadline.tzinfo is None:
                    deadline = deadline.replace(tzinfo=timezone.utc)
                if deadline < now:
                    sla_breaches += 1
        
        # Leads per assignee
        leads_per_assignee = {}
        for lead in leads:
            assignee_id = lead.get("assignee_id")
            if assignee_id:
                leads_per_assignee[assignee_id] = leads_per_assignee.get(assignee_id, 0) + 1
        
        # Average response time
        status_history = self.client.table("status_history").select("*").execute()
        avg_response_time = self._calculate_avg_response_time(status_history.data if status_history.data else [])
        
        return {
            "total_leads": total_leads,
            "active_leads": active_leads,
            "closed_leads": closed_leads,
            "sla_breaches": sla_breaches,
            "leads_per_assignee": leads_per_assignee,
            "average_response_time_minutes": avg_response_time
        }
    
    async def get_leads_per_assignee(self) -> List[Dict[str, Any]]:
        """Get leads grouped by assignee"""
        leads_response = self.client.table("leads").select("*").execute()
        leads = leads_response.data if leads_response.data else []
        
        users_response = self.client.table("users").select("id, name").execute()
        users = {user["id"]: user["name"] for user in (users_response.data if users_response.data else [])}
        
        assignee_stats = {}
        for lead in leads:
            assignee_id = lead.get("assignee_id")
            if assignee_id:
                if assignee_id not in assignee_stats:
                    assignee_stats[assignee_id] = {
                        "assignee_id": assignee_id,
                        "assignee_name": users.get(assignee_id, "Unknown"),
                        "total_leads": 0,
                        "active_leads": 0,
                        "closed_leads": 0
                    }
                
                assignee_stats[assignee_id]["total_leads"] += 1
                if lead.get("status") == "active":
                    assignee_stats[assignee_id]["active_leads"] += 1
                elif lead.get("status") == "closed":
                    assignee_stats[assignee_id]["closed_leads"] += 1
        
        return list(assignee_stats.values())
    
    def _calculate_avg_response_time(self, status_history: List[Dict[str, Any]]) -> float:
        """Calculate average response time from status history"""
        response_times = []
        now = datetime.now(timezone.utc)
        
        for record in status_history:
            if record.get("status") == "in_progress" and record.get("created_at"):
                # Simple calculation: time from creation to now for active responsiveness
                created = datetime.fromisoformat(record["created_at"])
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                response_times.append((now - created).total_seconds() / 60)
        
        return sum(response_times) / len(response_times) if response_times else 0.0
