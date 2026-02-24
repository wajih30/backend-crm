"""Lead service - business logic for leads"""

from app.utils.supabase_client import get_supabase_client
from app.models.lead import LeadCreate, LeadUpdate, LeadResponse
from app.services.sla_service import SLAService
from app.services.email_service import EmailService
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

sla_service = SLAService()
email_service = EmailService()


class LeadService:
    """Service for lead management"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def create_lead(self, lead_data: LeadCreate, user_id: str) -> Dict[str, Any]:
        """Create a new lead"""
        try:
            # Calculate SLA deadline
            sla_deadline = None
            if lead_data.deadline:
                sla_deadline = lead_data.deadline
            
            lead_record = {
                "name": lead_data.name,
                "website": lead_data.website,
                "source": lead_data.source,
                "status": lead_data.status,
                "deadline": lead_data.deadline.isoformat() if lead_data.deadline else None,
                "sla_deadline": sla_deadline.isoformat() if sla_deadline else None,
                "notes": lead_data.notes,
                "assignee_id": lead_data.assignee_id,
                "custom_fields": lead_data.custom_fields or {},
                "created_by": user_id
            }
            
            response = self.client.table("leads").insert(lead_record).execute()
            
            if not response.data:
                raise ValueError("Failed to create lead")
            
            lead = response.data[0]
            
            # Log to audit
            await self._log_action(
                lead_id=lead["id"],
                action_type="lead_created",
                user_id=user_id,
                metadata=lead_record
            )
            
            # Send assignment email if assignee is specified
            if lead_data.assignee_id:
                try:
                    await email_service.send_assignment_email(lead, lead_data.assignee_id)
                except Exception as e:
                    # Log email error but don't fail the lead creation
                    print(f"Warning: Failed to send assignment email: {str(e)}")
            
            return lead
        except Exception as e:
            raise ValueError(f"Failed to create lead: {str(e)}")
    
    async def update_lead(self, lead_id: str, lead_data: LeadUpdate, user_id: str) -> Dict[str, Any]:
        """Update an existing lead"""
        try:
            update_dict = lead_data.model_dump(exclude_unset=True)
            
            # Convert datetime to ISO format
            if "deadline" in update_dict and update_dict["deadline"]:
                update_dict["deadline"] = update_dict["deadline"].isoformat()
            
            response = self.client.table("leads").update(update_dict).eq("id", lead_id).execute()
            
            if not response.data:
                raise ValueError("Lead not found")
            
            # Log status change if status was updated
            if "status" in update_dict:
                await self._log_status_change(
                    lead_id=lead_id,
                    new_status=update_dict["status"],
                    user_id=user_id,
                    comment=None
                )
            
            return response.data[0]
        except Exception as e:
            raise ValueError(f"Failed to update lead: {str(e)}")
    
    async def assign_lead(self, lead_id: str, assignee_id: str, user_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """Assign a lead to a user"""
        update_data = {"assignee_id": assignee_id}
        response = self.client.table("leads").update(update_data).eq("id", lead_id).execute()
        
        # Log assignment
        await self._log_action(
            lead_id=lead_id,
            action_type="lead_assigned",
            user_id=user_id,
            metadata={
                "assigned_to": assignee_id,
                "assigned_by": user_id,
                "comment": comment
            }
        )
        
        # Log status change
        await self._log_status_change(
            lead_id=lead_id,
            new_status="assigned",
            user_id=user_id,
            comment=f"Assigned to {assignee_id}. {comment or ''}"
        )
        
        return response.data[0]
    
    async def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """Get lead details with status history and assignee name"""
        lead_response = self.client.table("leads").select("*").eq("id", lead_id).execute()
        
        if not lead_response.data:
            raise ValueError("Lead not found")
        
        lead = lead_response.data[0]
        
        # Initialize default
        lead["assignee_name"] = "Unassigned"
        
        # Batch fetch related data
        queries = []
        if lead.get("assignee_id"):
            queries.append(self.client.table("users").select("name").eq("id", lead["assignee_id"]).execute())
        
        # Fetch status history
        queries.append(self.client.table("status_history").select("*").eq("lead_id", lead_id).order("updated_at", desc=False).execute())
        
        # Wait for all (though currently executed sequentially in this client wrapper)
        results = [q for q in queries]
        
        # Process results
        if lead.get("assignee_id") and results:
            user_resp = results[0]
            if user_resp.data:
                lead["assignee_name"] = user_resp.data[0].get("name")
            
        lead["status_history"] = results[-1].data if results[-1].data else []
                
        return lead

    async def list_leads(
        self,
        source: Optional[str] = None,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
        sla_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List leads with filters and optimized assignee name enrichment"""
        leads = []
        try:
            # 1. Fetch leads
            query = self.client.table("leads").select("*")
            if source:
                query = query.eq("source", source)
            if status:
                query = query.eq("status", status)
            if assignee_id:
                query = query.eq("assignee_id", assignee_id)
            
            response = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
            leads = response.data or []
            
            if not leads:
                return []

            # 2. Collect unique assignee IDs
            assignee_ids = list(set(l["assignee_id"] for l in leads if l.get("assignee_id")))
            
            # 3. Bulk fetch assignee names
            user_map = {}
            if assignee_ids:
                try:
                    # Fetch multiple users in one query using 'in'
                    user_resp = self.client.table("users").select("id, name").in_("id", assignee_ids).execute()
                    if user_resp.data:
                        user_map = {u["id"]: u["name"] for u in user_resp.data}
                except Exception as e:
                    print(f"Error fetching users in bulk: {str(e)}")

            # 4. Enrich leads from map
            for lead in leads:
                lead_assignee_id = lead.get("assignee_id")
                if lead_assignee_id and lead_assignee_id in user_map:
                    lead["assignee_name"] = user_map[lead_assignee_id]
                else:
                    lead["assignee_name"] = "Unassigned"
            
            # 5. Filter by SLA status if provided
            if sla_status:
                from datetime import timezone
                now = datetime.now(timezone.utc)
                filtered_leads = []
                for lead in leads:
                    if sla_status == "breached" and lead.get("sla_deadline"):
                        try:
                            sla_deadline = datetime.fromisoformat(lead["sla_deadline"])
                            if sla_deadline.tzinfo is None:
                                sla_deadline = sla_deadline.replace(tzinfo=timezone.utc)
                            if sla_deadline < now:
                                filtered_leads.append(lead)
                        except:
                            pass
                    elif sla_status == "at_risk" and lead.get("deadline"):
                        try:
                            deadline = datetime.fromisoformat(lead["deadline"])
                            if deadline.tzinfo is None:
                                deadline = deadline.replace(tzinfo=timezone.utc)
                            if now < deadline < now + timedelta(hours=1):
                                filtered_leads.append(lead)
                        except:
                            pass
                return filtered_leads
            
            return leads
            
        except Exception as e:
            print(f"Error listing leads: {str(e)}")
            raise e

    async def _log_action(self, lead_id: str, action_type: str, user_id: str, metadata: Dict[str, Any]):
        """Log an action in status_history or audit"""
        # Get current lead status to include in history record
        lead_resp = self.client.table("leads").select("status").eq("id", lead_id).execute()
        current_status = lead_resp.data[0]["status"] if lead_resp.data else None
        
        self.client.table("status_history").insert({
            "lead_id": lead_id,
            "status": current_status,
            "action_type": action_type,
            "updated_by": user_id,
            "metadata": metadata
        }).execute()
    
    async def _log_status_change(self, lead_id: str, new_status: str, user_id: str, comment: Optional[str] = None):
        """Log a status change"""
        self.client.table("status_history").insert({
            "lead_id": lead_id,
            "status": new_status,
            "action_type": "status_change",
            "comment": comment,
            "updated_by": user_id
        }).execute()
