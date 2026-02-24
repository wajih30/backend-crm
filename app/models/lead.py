"""Lead-related Pydantic models"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class LeadCreate(BaseModel):
    """Schema for creating a new lead"""
    name: str
    email: Optional[str] = None
    website: Optional[str] = None
    source: str = "manual"
    status: str = "active"
    deadline: Optional[datetime] = None
    notes: Optional[str] = None
    assignee_id: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    name: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None
    assignee_id: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadAssign(BaseModel):
    """Schema for assigning a lead"""
    assignee_id: str
    comment: Optional[str] = None


class StatusHistoryItem(BaseModel):
    """Schema for status history"""
    id: str
    status: Optional[str] = None
    comment: Optional[str]
    updated_by: str
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeadResponse(BaseModel):
    """Schema for lead response"""
    id: str
    name: str
    email: Optional[str]
    website: Optional[str]
    source: str
    status: str
    deadline: Optional[datetime]
    notes: Optional[str]
    sla_deadline: Optional[datetime]
    custom_fields: Optional[Dict[str, Any]]
    assignee_id: Optional[str]
    assignee_name: Optional[str] = "Unassigned"
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeadDetailResponse(LeadResponse):
    """Extended lead response with status history"""
    status_history: Optional[list[StatusHistoryItem]] = None
