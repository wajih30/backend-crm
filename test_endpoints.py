"""Test script for API endpoints with Supabase Auth + Email"""

import httpx
import json
import time

BASE_URL = "http://localhost:8000"
# Use existing confirmed user for login test
TEST_EMAIL = "wajihurrehman2001@gmail.com"
TEST_PASSWORD = "TestPass123!"

# Second user for assignment email target
ASSIGNEE_EMAIL = "wajih_rehman@icloud.com"


def req(method, path, expected_status=200, json_data=None, headers=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        response = httpx.request(method, url, json=json_data, headers=headers, timeout=30)
        icon = "PASS" if response.status_code == expected_status else "FAIL"
        print(f"[{icon}] {method} {path} -> {response.status_code}")
        try:
            data = response.json()
            print(f"   {json.dumps(data, indent=2, default=str)[:600]}")
        except Exception:
            print(f"   {response.text[:300]}")
        print()
        return response
    except Exception as e:
        print(f"[ERROR] {method} {path} -> {e}\n")
        return None


def main():
    print("=" * 60)
    print("Lead Management CRM - Full API + Email Test")
    print("=" * 60 + "\n")

    # 1. Health
    print("=== 1. Health ===")
    req("GET", "/health")

    # 2. Login with existing confirmed user
    print("=== 2. Login ===")
    resp = req("POST", "/api/auth/login", json_data={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    token = None
    user_id = None
    if resp and resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token")
        user_id = data.get("user", {}).get("id")

    print(f"   >> Token: {'YES' if token else 'NO'}")
    print(f"   >> User ID: {user_id}\n")

    if not token:
        print("CANNOT PROCEED WITHOUT TOKEN. Exiting.")
        return

    auth = {"Authorization": f"Bearer {token}"}

    # 3. Get Me
    print("=== 3. Get Me ===")
    req("GET", "/api/auth/me", headers=auth)

    # 4. List Users (find assignee)
    print("=== 4. List Users ===")
    resp = req("GET", "/api/users")
    assignee_id = None
    if resp and resp.status_code == 200:
        for u in resp.json():
            if u["email"] == ASSIGNEE_EMAIL:
                assignee_id = u["id"]
                print(f"   >> Found assignee: {assignee_id}\n")

    # 5. Create Lead
    print("=== 5. Create Lead ===")
    resp = req("POST", "/api/leads", headers=auth, json_data={
        "name": "Acme Corp Enterprise Lead",
        "website": "https://acme.com",
        "source": "website",
        "status": "active",
        "deadline": "2026-02-25T18:00:00+05:00",
        "notes": "Enterprise plan inquiry - high priority",
        "custom_fields": {"industry": "Technology", "company_size": "500+", "budget": "$50k"}
    })

    lead_id = None
    if resp and resp.status_code == 200:
        lead_id = resp.json().get("id")
        print(f"   >> Lead ID: {lead_id}\n")

    # 6. List Leads
    print("=== 6. List Leads ===")
    req("GET", "/api/leads", headers=auth)

    # 7. Get Lead Detail
    if lead_id:
        print("=== 7. Get Lead Detail ===")
        req("GET", f"/api/leads/{lead_id}", headers=auth)

    # 8. Assign Lead (TRIGGERS EMAIL to assignee!)
    if lead_id and assignee_id:
        print("=== 8. Assign Lead (triggers email) ===")
        resp = req("POST", f"/api/leads/{lead_id}/assign", headers=auth, json_data={
            "assignee_id": assignee_id,
            "comment": "Please follow up on this lead ASAP"
        })
        if resp and resp.status_code == 200:
            print(f"   >> Assignment email should be sent to: {ASSIGNEE_EMAIL}\n")

    # 9. Update Lead Status
    if lead_id:
        print("=== 9. Update Status ===")
        req("PATCH", f"/api/leads/{lead_id}", headers=auth, json_data={
            "status": "in_progress"
        })

    # 10. Resend Email
    if lead_id:
        print("=== 10. Resend Notification Email ===")
        resp = req("POST", f"/api/leads/{lead_id}/resend-email", headers=auth)

    # 11. Get Lead Detail (with history)
    if lead_id:
        print("=== 11. Lead Detail (with status history) ===")
        req("GET", f"/api/leads/{lead_id}", headers=auth)

    # 12. Dashboard
    print("=== 12. Dashboard Metrics ===")
    req("GET", "/api/dashboard/metrics")
    req("GET", "/api/dashboard/leads-per-assignee")

    # 13. Audit Logs
    print("=== 13. Audit Logs ===")
    req("GET", "/api/audit-logs")

    print("=" * 60)
    print("DONE! Check inbox for assignment emails.")
    print("=" * 60)


if __name__ == "__main__":
    main()
