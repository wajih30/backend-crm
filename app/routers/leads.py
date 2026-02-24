"""Lead management routes"""

from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status as http_status
from typing import List, Optional
from datetime import datetime
from app.models.lead import LeadCreate, LeadUpdate, LeadAssign, LeadResponse, LeadDetailResponse
from app.utils.supabase_client import get_supabase_client
from app.services.lead_service import LeadService
from app.services.email_service import EmailService
from app.dependencies import get_current_user, require_sdr

router = APIRouter(prefix="/api/leads", tags=["leads"])
lead_service = LeadService()
email_service = EmailService()


@router.get("", response_model=List[LeadResponse])
async def list_leads(
    source: Optional[str] = Query(None),
    lead_status: Optional[str] = Query(None, alias="status"),
    assignee_id: Optional[str] = Query(None),
    sla_status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List all leads with optional filters"""
    try:
        return await lead_service.list_leads(
            source=source,
            status=lead_status,
            assignee_id=assignee_id,
            sla_status=sla_status,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    """Get lead details by ID"""
    try:
        return await lead_service.get_lead_details(lead_id)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=LeadResponse)
async def create_lead(lead_data: LeadCreate, current_user: dict = Depends(require_sdr)):
    """Create a new lead"""
    try:
        return await lead_service.create_lead(lead_data, current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, lead_data: LeadUpdate, current_user: dict = Depends(require_sdr)):
    """Update lead by ID"""
    try:
        return await lead_service.update_lead(lead_id, lead_data, current_user["id"])
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{lead_id}/assign", response_model=LeadResponse)
async def assign_lead(lead_id: str, assignment: LeadAssign, current_user: dict = Depends(require_sdr)):
    """Assign lead to a user"""
    try:
        lead = await lead_service.assign_lead(
            lead_id,
            assignment.assignee_id,
            current_user["id"],
            assignment.comment
        )
        
        # Send assignment email (non-blocking, don't fail the request)
        try:
            await email_service.send_assignment_email(lead, assignment.assignee_id)
        except Exception:
            pass  # Email failure shouldn't block assignment
        
        return lead
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{lead_id}/resend-email")
async def resend_notification_email(lead_id: str, current_user: dict = Depends(require_sdr)):
    """Resend notification email for a lead"""
    try:
        lead = await lead_service.get_lead_details(lead_id)
        if not lead.get("assignee_id"):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Lead has no assignee"
            )
        await email_service.send_assignment_email(lead, lead["assignee_id"])
        return {"message": "Email resent successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, current_user: dict = Depends(require_sdr)):
    """Delete lead by ID"""
    try:
        client = get_supabase_client()
        # Delete related records first (since no CASCADE in schema)
        client.table("status_history").delete().eq("lead_id", lead_id).execute()
        client.table("notifications").delete().eq("lead_id", lead_id).execute()
        
        # Now delete the lead
        client.table("leads").delete().eq("id", lead_id).execute()
        return {"message": "Lead deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
