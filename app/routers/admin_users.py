"""Admin user management routes - restricted to admins only"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.utils.supabase_client import get_supabase_client
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/admin/users", tags=["admin"])


class AdminCreateUserRequest(BaseModel):
    """Request to create a new user (admin only)"""
    name: str
    email: EmailStr
    password: str
    role: str  # admin, sdr, assignee
    phone: str = None


class AdminUpdateUserRequest(BaseModel):
    """Request to update user (admin only)"""
    name: str = None
    email: EmailStr = None
    role: str = None
    phone: str = None


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to ensure current user is admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return current_user


@router.post("/create", dependencies=[Depends(require_admin)])
async def create_user(user_data: AdminCreateUserRequest, current_user: dict = Depends(require_admin)):
    """Create a new user - ADMIN ONLY"""
    admin_client = get_supabase_client()
    auth_user_id = None
    profile_created = False
    
    try:
        # Validate role
        if user_data.role not in ["admin", "sdr", "assignee"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'admin', 'sdr', or 'assignee'"
            )
        
        # Create auth user via admin API
        auth_response = admin_client.auth.admin.create_user({
            "email": user_data.email,
            "password": user_data.password,
            "email_confirm": True,
            "user_metadata": {
                "name": user_data.name,
                "created_by_admin": current_user["id"]
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create auth user"
            )
        
        auth_user = auth_response.user
        auth_user_id = str(auth_user.id)
        
        # Create user profile
        user_profile = admin_client.table("users").insert({
            "id": auth_user_id,
            "name": user_data.name,
            "email": user_data.email,
            "phone": user_data.phone,
            "role": user_data.role
        }).execute()
        
        profile_created = True
        
        return {
            "message": "User created successfully",
            "user": user_profile.data[0] if user_profile.data else None
        }
    
    except Exception as e:
        # Cleanup on failure
        if auth_user_id:
            try:
                if profile_created:
                    admin_client.table("users").delete().eq("id", auth_user_id).execute()
                admin_client.auth.admin.delete_user(auth_user_id)
            except Exception as cleanup_err:
                print(f"Cleanup failed: {cleanup_err}")
        
        if isinstance(e, HTTPException):
            raise e
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", dependencies=[Depends(require_admin)])
async def update_user(
    user_id: str,
    user_data: AdminUpdateUserRequest,
    current_user: dict = Depends(require_admin)
):
    """Update a user - ADMIN ONLY"""
    admin_client = get_supabase_client()
    
    try:
        # Build update payload
        update_payload = {}
        if user_data.name:
            update_payload["name"] = user_data.name
        if user_data.email:
            update_payload["email"] = user_data.email
        if user_data.role:
            if user_data.role not in ["admin", "sdr", "assignee"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role"
                )
            update_payload["role"] = user_data.role
        if user_data.phone:
            update_payload["phone"] = user_data.phone
        
        if not update_payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update user profile
        result = admin_client.table("users").update(update_payload).eq("id", user_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "message": "User updated successfully",
            "user": result.data[0]
        }
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", dependencies=[Depends(require_admin)])
async def delete_user(user_id: str, current_user: dict = Depends(require_admin)):
    """Delete a user - ADMIN ONLY"""
    admin_client = get_supabase_client()
    
    try:
        # Prevent self-deletion
        if user_id == current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Delete from users table
        admin_client.table("users").delete().eq("id", user_id).execute()
        
        # Delete auth user
        admin_client.auth.admin.delete_user(user_id)
        
        return {"message": "User deleted successfully"}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
