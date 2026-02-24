"""Email service - handles email notifications"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template, FileSystemLoader, Environment
from app.config import get_settings
from app.utils.supabase_client import get_supabase_client
from typing import Optional, Dict, Any
import asyncio
import os

settings = get_settings()


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
        
        # Load Jinja2 environment for templates
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def send_assignment_email(self, lead: Dict[str, Any], assignee_id: str, max_retries: int = 3):
        """Send assignment email to assignee"""
        try:
            # Get assignee details
            assignee_response = self.client.table("users").select("email, name").eq("id", assignee_id).execute()
            
            if not assignee_response.data:
                raise ValueError("Assignee not found")
            
            assignee = assignee_response.data[0]
            
            # Prepare email content
            subject = f"New Lead Assignment: {lead['name']}"
            template = self.jinja_env.get_template("assignment_email.html")
            html_content = template.render(
                assignee_name=assignee.get("name", "User"),
                lead_name=lead.get("name"),
                website=lead.get("website", "N/A"),
                source=lead.get("source", "N/A"),
                deadline=lead.get("deadline", "N/A"),
                notes=lead.get("notes", "N/A"),
                lead_url=f"{settings.app_url}/leads/{lead['id']}"
            )
            
            # Send email with retry
            success = await self._send_email_with_retry(
                to_email=assignee["email"],
                subject=subject,
                html_content=html_content,
                max_retries=max_retries
            )
            
            if success:
                # Log notification
                await self._log_notification(
                    lead_id=lead["id"],
                    assignee_id=assignee_id,
                    message_type="assignment",
                    status="sent"
                )
        
        except Exception as e:
            print(f"Error sending assignment email: {str(e)}")
    
    async def send_reminder_email(self, lead: Dict[str, Any]):
        """Send deadline reminder email"""
        try:
            assignee_id = lead.get("assignee_id")
            if not assignee_id:
                return
            
            assignee_response = self.client.table("users").select("email, name").eq("id", assignee_id).execute()
            
            if not assignee_response.data:
                return
            
            assignee = assignee_response.data[0]
            subject = f"Reminder: Lead {lead['name']} deadline approaching"
            
            template = self.jinja_env.get_template("reminder_email.html")
            html_content = template.render(
                assignee_name=assignee.get("name", "User"),
                lead_name=lead.get("name"),
                status=lead.get("status", "N/A"),
                deadline=lead.get("deadline", "N/A"),
                lead_url=f"{settings.app_url}/leads/{lead['id']}"
            )
            
            success = await self._send_email_with_retry(
                to_email=assignee["email"],
                subject=subject,
                html_content=html_content
            )
            
            if success:
                await self._log_notification(
                    lead_id=lead["id"],
                    assignee_id=assignee_id,
                    message_type="reminder",
                    status="sent"
                )
        
        except Exception as e:
            print(f"Error sending reminder email: {str(e)}")
    
    async def send_sla_breach_email(self, lead: Dict[str, Any], sdr_id: str):
        """Send SLA breach notification email"""
        try:
            sdr_response = self.client.table("users").select("email, name").eq("id", sdr_id).execute()
            
            if not sdr_response.data:
                return
            
            sdr = sdr_response.data[0]
            subject = f"SLA Breach Alert: Lead {lead['name']}"
            
            template = self.jinja_env.get_template("sla_breach_email.html")
            html_content = template.render(
                lead_name=lead.get("name"),
                source=lead.get("source", "N/A"),
                sla_deadline=lead.get("sla_deadline", "N/A"),
                lead_url=f"{settings.app_url}/leads/{lead['id']}"
            )
            
            success = await self._send_email_with_retry(
                to_email=sdr["email"],
                subject=subject,
                html_content=html_content
            )
            
            if success:
                await self._log_notification(
                    lead_id=lead["id"],
                    assignee_id=sdr_id,
                    message_type="sla_breach",
                    status="sent"
                )
        
        except Exception as e:
            print(f"Error sending SLA breach email: {str(e)}")
    
    async def _send_email_with_retry(self, to_email: str, subject: str, html_content: str, max_retries: int = 3) -> bool:
        """Send email with retry logic"""
        for attempt in range(max_retries):
            try:
                async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as smtp:
                    await smtp.login(self.smtp_username, self.smtp_password)
                    
                    message = MIMEMultipart("alternative")
                    message["Subject"] = subject
                    message["From"] = f"{self.from_name} <{self.from_email}>"
                    message["To"] = to_email
                    
                    html_part = MIMEText(html_content, "html")
                    message.attach(html_part)
                    
                    await smtp.send_message(message)
                
                return True
            
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to send email after {max_retries} attempts: {str(e)}")
                    return False
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return False
    
    async def _log_notification(self, lead_id: str, assignee_id: str, message_type: str, status: str):
        """Log notification to database"""
        self.client.table("notifications").insert({
            "lead_id": lead_id,
            "assignee_id": assignee_id,
            "channel": "email",
            "message_type": message_type,
            "status": status,
            "retry_count": 0
        }).execute()
