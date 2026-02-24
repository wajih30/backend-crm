"""Dashboard and metrics routes"""

from fastapi import APIRouter, HTTPException, status
from app.models.dashboard import MetricsResponse, LeadsPerAssigneeResponse
from app.services.dashboard_service import DashboardService
from typing import List

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
dashboard_service = DashboardService()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get dashboard metrics"""
    try:
        return await dashboard_service.get_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/leads-per-assignee", response_model=List[LeadsPerAssigneeResponse])
async def get_leads_per_assignee():
    """Get leads grouped by assignee"""
    try:
        return await dashboard_service.get_leads_per_assignee()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
