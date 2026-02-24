"""Notification-related Pydantic models"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    lead_id: str
    assignee_id: str
    channel: str  # "email"
    message: str
    message_type: str  # "assignment", "reminder", "sla_breach"


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: str
    lead_id: str
    assignee_id: str
    channel: str
    message_type: str
    status: str  # "pending", "sent", "failed"
    retry_count: int
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
