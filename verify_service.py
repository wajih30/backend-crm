
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

from app.services.lead_service import LeadService

async def test():
    load_dotenv()
    service = LeadService()
    try:
        leads = await service.list_leads()
        print(f"FETCHED {len(leads)} LEADS")
        for lead in leads:
            print(f"Lead: {lead['name']}, ID: {lead['id']}, Assignee ID: {lead.get('assignee_id')}, Assignee Name: {lead.get('assignee_name')}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
