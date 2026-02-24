"""Application configuration and settings"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Lead Management CRM"
    app_version: str = "1.0.0"
    app_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    debug: bool = False
    
    # Supabase
    supabase_url: str = "https://placeholder.supabase.co"
    supabase_anon_key: str = "placeholder-anon-key"
    supabase_service_role_key: str = "placeholder-service-role-key"
    
    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = "placeholder@gmail.com"
    smtp_password: str = "placeholder-password"
    smtp_from_email: str = "placeholder@gmail.com"
    smtp_from_name: str = "Lead Management CRM"
    
    # SLA Configuration
    default_sla_duration_minutes: int = 120
    scheduler_interval_minutes: int = 5
    reminder_before_deadline_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
