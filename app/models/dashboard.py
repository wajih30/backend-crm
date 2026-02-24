"""Dashboard-related Pydantic models"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class MetricsResponse(BaseModel):
    """Schema for dashboard metrics"""
    total_leads: int
    active_leads: int
    closed_leads: int
    sla_breaches: int
    leads_per_assignee: Dict[str, int]
    average_response_time_minutes: Optional[float]
    
    class Config:
        from_attributes = True


class LeadsPerAssigneeResponse(BaseModel):
    """Schema for leads grouped by assignee"""
    assignee_id: str
    assignee_name: str
    total_leads: int
    active_leads: int
    closed_leads: int
