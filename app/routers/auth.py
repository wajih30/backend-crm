"""Authentication routes - Supabase Auth based"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserLoginRequest, UserRegisterRequest
from app.utils.supabase_client import get_supabase_client, get_supabase_anon_client
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(user_data: UserRegisterRequest):
    """Register a new user - DISABLED FOR SECURITY. Use admin endpoints to create users."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Public registration is disabled. Contact your administrator to create an account."
    )


@router.post("/register-assignee")
async def register_assignee(user_data: UserRegisterRequest):
    """Register as an Assignee only - no role selection allowed"""
    auth_user_id = None
    profile_created = False
    
    try:
        # Service role client for admin.create_user + table insert
        admin_client = get_supabase_client()
        
        # Force role to assignee, ignore any role in request
        assigned_role = "assignee"
        
        # Create user via admin API (auto-confirms email)
        auth_response = admin_client.auth.admin.create_user({
            "email": user_data.email,
            "password": user_data.password,
            "email_confirm": True,
            "user_metadata": {
                "name": user_data.name
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create auth user"
            )
        
        auth_user = auth_response.user
        auth_user_id = str(auth_user.id)
        
        # Create profile in users table with default assignee role
        user_profile = admin_client.table("users").insert({
            "id": auth_user_id,
            "name": user_data.name,
            "email": user_data.email,
            "role": assigned_role
        }).execute()
        
        profile_created = True
        
        # Sign in with anon client to get tokens
        anon_client = get_supabase_anon_client()
        login_response = anon_client.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        return {
            "message": "Account created successfully",
            "user": user_profile.data[0] if user_profile.data else None,
            "access_token": login_response.session.access_token if login_response.session else None,
            "refresh_token": login_response.session.refresh_token if login_response.session else None,
            "token_type": "bearer"
        }
    
    except Exception as e:
        # Cleanup if something failed mid-way
        if auth_user_id:
            try:
                admin_client = get_supabase_client()
                if profile_created:
                    admin_client.table("users").delete().eq("id", auth_user_id).execute()
                admin_client.auth.admin.delete_user(auth_user_id)
            except Exception as cleanup_err:
                print(f"Cleanup failed for user {auth_user_id}: {cleanup_err}")

        if isinstance(e, HTTPException):
            raise e
            
        error_msg = str(e)
        if "already been registered" in error_msg or "already exists" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {error_msg}"
        )


@router.post("/login")
async def login(credentials: UserLoginRequest):
    """Login user via Supabase Auth"""
    try:
        # Anon client for sign_in_with_password
        anon_client = get_supabase_anon_client()
        
        auth_response = anon_client.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Get user profile with service role client (bypasses RLS)
        admin_client = get_supabase_client()
        user_profile = admin_client.table("users").select("*").eq(
            "id", str(auth_response.user.id)
        ).execute()
        
        user_data = user_profile.data[0] if user_profile.data else {
            "id": str(auth_response.user.id),
            "email": auth_response.user.email,
            "role": "assignee"
        }
        
        return {
            "message": "Login successful",
            "user": user_data,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "token_type": "bearer"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        client = get_supabase_client()
        response = client.table("users").select("*").eq("id", current_user["id"]).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}
