"""User management routes"""

import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.user import UserCreate, UserUpdate, UserResponse
from app.utils.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def list_users():
    """List all users (admin only)"""
    try:
        client = get_supabase_client()
        response = client.table("users").select("*").execute()
        return response.data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        client = get_supabase_client()
        response = client.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create a new user (admin only)"""
    try:
        client = get_supabase_client()
        
        response = client.table("users").insert({
            "id": str(uuid.uuid4()),
            "name": user_data.name,
            "email": user_data.email,
            "phone": user_data.phone,
            "role": user_data.role
        }).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate):
    """Update user by ID (admin only)"""
    try:
        client = get_supabase_client()
        
        update_dict = user_data.model_dump(exclude_unset=True)
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        response = client.table("users").update(update_dict).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete user by ID (admin only)"""
    try:
        client = get_supabase_client()
        response = client.table("users").delete().eq("id", user_id).execute()
        return {"message": "User deleted successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
