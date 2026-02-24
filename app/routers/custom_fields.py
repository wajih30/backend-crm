"""Custom fields service and router"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.utils.supabase_client import get_supabase_client
from app.dependencies import get_current_user, require_sdr

router = APIRouter(prefix="/api/custom-fields", tags=["custom-fields"])

class CustomFieldCreate(BaseModel):
    """Request to create a custom field"""
    name: str
    field_type: str  # text, number, date, select, checkbox
    is_active: bool = True
    options: Optional[List[str]] = None  # for select type

class CustomFieldResponse(BaseModel):
    """Custom field response"""
    id: str
    name: str
    field_type: str
    is_active: bool
    options: Optional[List[str]]
    created_at: str


@router.get("", response_model=List[CustomFieldResponse])
async def list_custom_fields(current_user: dict = Depends(get_current_user)):
    """List all active custom fields"""
    try:
        client = get_supabase_client()
        response = client.table("custom_fields").select("*").eq("is_active", True).execute()
        return response.data or []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=CustomFieldResponse)
async def create_custom_field(
    field_data: CustomFieldCreate,
    current_user: dict = Depends(require_sdr)
):
    """Create a new custom field"""
    try:
        client = get_supabase_client()
        
        # Validate field_type
        valid_types = ["text", "number", "date", "select", "checkbox"]
        if field_data.field_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid field_type. Must be one of: {', '.join(valid_types)}"
            )
        
        # For select type, options is required
        if field_data.field_type == "select" and not field_data.options:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="options required for select field_type"
            )
        
        response = client.table("custom_fields").insert({
            "name": field_data.name,
            "field_type": field_data.field_type,
            "is_active": field_data.is_active,
            "options": field_data.options
        }).execute()
        
        if not response.data:
            raise ValueError("Failed to create custom field")
        
        return response.data[0]
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{field_id}", response_model=CustomFieldResponse)
async def update_custom_field(
    field_id: str,
    field_data: CustomFieldCreate,
    current_user: dict = Depends(require_sdr)
):
    """Update a custom field"""
    try:
        client = get_supabase_client()
        
        response = client.table("custom_fields").update({
            "name": field_data.name,
            "field_type": field_data.field_type,
            "is_active": field_data.is_active,
            "options": field_data.options
        }).eq("id", field_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom field not found"
            )
        
        return response.data[0]
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{field_id}")
async def delete_custom_field(
    field_id: str,
    current_user: dict = Depends(require_sdr)
):
    """Soft delete a custom field (mark as inactive)"""
    try:
        client = get_supabase_client()
        
        response = client.table("custom_fields").update({
            "is_active": False
        }).eq("id", field_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Custom field not found"
            )
        
        return {"message": "Custom field deleted successfully"}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
