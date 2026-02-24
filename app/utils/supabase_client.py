"""Supabase client initialization and utilities"""

from supabase import create_client, Client
from app.config import get_settings


def get_supabase_client() -> Client:
    """Initialize and return Supabase client with service role key"""
    settings = get_settings()
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_role_key
    )


def get_supabase_anon_client() -> Client:
    """Initialize and return Supabase client with anon key (user-scoped)"""
    settings = get_settings()
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_anon_key
    )
