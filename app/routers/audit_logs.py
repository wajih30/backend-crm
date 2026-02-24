"""Audit logs routes"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])
audit_service = AuditService()


@router.get("")
async def get_audit_logs(
    action_type: Optional[str] = Query(None),
    lead_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get audit logs with optional filters (admin only)"""
    try:
        return await audit_service.get_audit_logs(
            action_type=action_type,
            lead_id=lead_id,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
