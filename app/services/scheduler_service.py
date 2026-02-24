"""Scheduler service - handles background jobs"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.sla_service import SLAService
from app.services.email_service import EmailService
from app.utils.supabase_client import get_supabase_client
import asyncio

sla_service = SLAService()
email_service = EmailService()


class SchedulerService:
    """Service for background job scheduling"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.client = get_supabase_client()
    
    def start(self):
        """Start the scheduler"""
        # Check for approaching deadlines every 5 minutes
        self.scheduler.add_job(
            self._check_approaching_deadlines,
            IntervalTrigger(minutes=5),
            id="check_approaching_deadlines"
        )
        
        # Check for SLA breaches every 5 minutes
        self.scheduler.add_job(
            self._check_sla_breaches,
            IntervalTrigger(minutes=5),
            id="check_sla_breaches"
        )
        
        self.scheduler.start()
    
    async def _check_approaching_deadlines(self):
        """Check for leads with approaching deadlines"""
        try:
            approaching_leads = await sla_service.get_approaching_deadlines(minutes_window=30)
            
            for lead in approaching_leads:
                # Check if reminder already sent
                notification = self.client.table("notifications").select("*").eq(
                    "lead_id", lead["id"]
                ).eq("message_type", "reminder").execute()
                
                if not notification.data:
                    await email_service.send_reminder_email(lead)
        
        except Exception as e:
            print(f"Error checking approaching deadlines: {str(e)}")
    
    async def _check_sla_breaches(self):
        """Check for leads that have breached SLA"""
        try:
            breached_leads = await sla_service.get_breached_leads()
            
            for lead in breached_leads:
                # Mark as SLA breached
                await sla_service.mark_sla_breached(lead["id"])
                
                # Send notification to SDR
                await email_service.send_sla_breach_email(lead, lead["created_by"])
        
        except Exception as e:
            print(f"Error checking SLA breaches: {str(e)}")
