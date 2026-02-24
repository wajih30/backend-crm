
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

res = supabase.table("leads").select("id, name, assignee_id").execute()
print("LEADS DATA:")
for lead in res.data:
    print(f"ID: {lead['id']}, Name: {lead['name']}, Assignee ID: {lead['assignee_id']}")

users = supabase.table("users").select("id, name").execute()
print("\nUSERS DATA:")
for user in users.data:
    print(f"ID: {user['id']}, Name: {user['name']}")
