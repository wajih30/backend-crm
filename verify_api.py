
import requests
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# We need a token to call the endpoint
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

# Sign in as a test user or just use service role to get a token? 
# The endpoint requires auth. Let's try to sign in with the test user.
email = "wajih.work2001@gmail.com"
password = "placeholder-password" # I hope this works or I'll use a direct token

try:
    auth_resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
    token = auth_resp.session.access_token
except:
    print("Sign in failed, trying to get a user directly from DB to use their ID if possible, but we need a JWT.")
    # Fallback: maybe the dev server is running without strict validation or I can bypass it for the test?
    # No, let's just try to call it and see if we get 401.
    token = "invalid"

headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("http://localhost:8000/api/leads", headers=headers)

print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    for lead in data:
        print(f"Lead: {lead['name']}, Assignee ID: {lead.get('assignee_id')}, Assignee Name: {lead.get('assignee_name')}")
else:
    print(resp.text)
