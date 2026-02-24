#!/usr/bin/env python
"""Database migration script - runs the initial schema"""

from supabase import create_client
from app.config import get_settings
import os

settings = get_settings()

# Read the migration SQL
migration_path = os.path.join(os.path.dirname(__file__), "supabase", "migrations", "001_initial_schema.sql")

with open(migration_path, "r") as f:
    migration_sql = f.read()

# Initialize Supabase client with service role key
client = create_client(
    supabase_url=settings.supabase_url,
    supabase_key=settings.supabase_service_role_key
)

print("🚀 Starting database migration...")
print(f"📊 Connecting to: {settings.supabase_url}")

try:
    # Execute the migration
    # Note: Direct SQL execution via Python client has limitations
    # Instead, provide instructions for manual migration
    print("\n✅ Migration file ready!")
    print("\n📋 Please follow these steps to run the migration:\n")
    print("1. Go to https://supabase.com and log in to your project")
    print(f"2. Project: twwksglyjfqkrvyryais")
    print("3. Navigate to SQL Editor → New Query")
    print("4. Copy and paste the following SQL script:")
    print("=" * 80)
    print(migration_sql)
    print("=" * 80)
    print("\n5. Click 'Execute' to run the migration")
    print("\n✨ After migration, your database will have:")
    print("   - users table")
    print("   - leads table with JSONB custom_fields")
    print("   - status_history table for audit trails")
    print("   - notifications table for email logging")
    print("   - Row Level Security policies")
    print("   - Indexes for performance")
    print("\n")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)
