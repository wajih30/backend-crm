#!/usr/bin/env python
"""
Direct PostgreSQL Migration Script
Connects directly to Supabase PostgreSQL and executes the schema migration
"""

import psycopg2
from psycopg2 import sql
from app.config import get_settings
import os

settings = get_settings()

def extract_connection_params(supabase_url: str) -> dict:
    """Extract connection parameters from Supabase URL"""
    # Parse URL: https://project-id.supabase.co
    # Connection: postgres://postgres:password@db.project-id.supabase.co:5432/postgres
    
    project_id = supabase_url.split("//")[1].split(".")[0]
    
    return {
        "host": f"db.{project_id}.supabase.co",
        "database": "postgres",
        "user": "postgres",
        "port": 5432
    }


def run_migration():
    """Execute the database migration"""
    
    print("🚀 Starting Database Migration...")
    print("=" * 80)
    
    # Read the migration SQL
    migration_path = os.path.join(
        os.path.dirname(__file__), 
        "supabase", 
        "migrations", 
        "001_initial_schema.sql"
    )
    
    with open(migration_path, "r") as f:
        migration_sql = f.read()
    
    # Extract connection parameters
    conn_params = extract_connection_params(settings.supabase_url)
    
    try:
        # Get password from .env - for Supabase it's typically the service role key used as password
        # However, we'll need the actual database password
        print("\n⚠️  DATABASE PASSWORD REQUIRED")
        print("-" * 80)
        print("\nTo connect to Supabase PostgreSQL, you need your database password.")
        print("\n📌 How to find your Supabase database password:")
        print("   1. Go to https://supabase.com → Select project")
        print("   2. Click Settings → Database")
        print("   3. Find 'Connection string' or scroll to password section")
        print("   4. Copy your database password")
        
        password = input("\n🔑 Enter your Supabase database password: ")
        
        if not password:
            print("❌ Password is required!")
            return False
        
        conn_params["password"] = password
        
        print("\n🔗 Connecting to Supabase PostgreSQL...")
        print(f"   Host: {conn_params['host']}")
        print(f"   Database: {conn_params['database']}")
        print(f"   User: {conn_params['user']}")
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("✅ Connected!")
        print("\n📝 Executing migration SQL...")
        print("-" * 80)
        
        # Execute the migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("\n📊 Created tables:")
        print("   ✅ users")
        print("   ✅ leads")
        print("   ✅ status_history")
        print("   ✅ notifications")
        print("\n🔒 Enabled Row Level Security (RLS) policies")
        print("📈 Created performance indexes")
        print("⏰ Set up auto-timestamp triggers")
        print("📊 Created dashboard views")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✨ Database migration successful!")
        print("\n🎉 Your database is ready!")
        print("\n📌 Next step: Start the backend server")
        print("   uvicorn app.main:app --reload --port 8000")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection Error: {str(e)}")
        print("\n💡 Possible issues:")
        print("   - Wrong password")
        print("   - Network connectivity issue")
        print("   - Firewall blocking connection")
        print("\n📌 Solution:")
        print("   - Verify password is correct")
        print("   - Check internet connection")
        print("   - Ensure IP is whitelisted in Supabase (optional)")
        return False
        
    except psycopg2.Error as e:
        print(f"\n❌ Database Error: {str(e)}")
        print("\n💡 This might be a SQL syntax issue or RLS policy conflict")
        print("\n📌 Alternative: Run SQL manually in Supabase SQL Editor")
        print("   1. Go to https://supabase.com")
        print("   2. SQL Editor → New Query")
        print("   3. Copy contents of: supabase/migrations/001_initial_schema.sql")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    success = run_migration()
    sys.exit(0 if success else 1)
