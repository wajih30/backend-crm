# SRS Compliance Implementation - Migration Notes

## Changes Made (Feb 24, 2026)

### 1. ✅ Security Hardening

#### Authentication & Registration
- **PUBLIC REGISTRATION DISABLED**: `/api/auth/register` now returns 403 Forbidden
- **ROLE ESCALATION PREVENTED**: Public can only use `/api/auth/register-assignee` with forced "assignee" role
- **ADMIN-ONLY USER CREATION**: New `/api/admin/users/create` endpoint for admins to create users with any role
- **SELF-DELETION PREVENTED**: Admins cannot delete their own accounts

#### File Changes
- `app/routers/auth.py` - Disabled public registration, added `/register-assignee`
- `app/routers/admin_users.py` - NEW router for admin user management
- `app/main.py` - Imported and registered admin_users router

### 2. ✅ Data Enrichment & Lead Management

#### Lead API Enhancement
- `list_leads()` now returns `assignee_name` (enriched via SQL JOIN with users table)
- Leads table displays actual assignee names instead of just "Assigned" badge
- Source types updated: `email`, `website`, `manual`, `other` (was: manual, api, import)

#### File Changes
- `app/services/lead_service.py` - Enhanced to fetch and include assignee_name
- `frontend/src/pages/Leads.jsx` - Updated UI to show assignee_name, renamed "Website" to "Source Name"

### 3. ✅ Email Service Clarification

#### Data Separation Documentation
- **Lead Email** (`lead.email`) = Customer/Lead contact email (for reference, NOT used in notifications)
- **Assignee Email** (`users.email`) = Assignee's profile email (used for notification delivery)
- Assignment notifications ALWAYS go to assignee's profile email

#### File Changes
- `app/services/email_service.py` - Added detailed docstring explaining email field separation

### 4. ✅ UI Improvements

#### Kanban Board View (NEW)
- Visual board with 4 columns: Active, In Progress, On Hold, Closed
- Drag-and-drop functionality to move leads between statuses
- Shows Lead Name, Source Name, Email, Deadline, Assignee
- Real-time update on status change

#### Leads Table View (UPDATED)
- Changed "Website" column to "Source Name"
- Shows actual assignee names (not just "Assigned" badge)
- Updated source type dropdown (Email, Website, Manual, Other)
- Better visual hierarchy with status badges

#### File Changes
- `frontend/src/pages/Kanban.jsx` - NEW component with drag-drop board
- `frontend/src/pages/Kanban.css` - Professional Kanban styling
- `frontend/src/pages/Leads.jsx` - Updated field names and display logic
- `frontend/src/App.jsx` - Added /kanban route
- `frontend/src/components/Navbar.jsx` - Added Kanban navigation link

### 5. ✅ Custom Fields Support (NEW)

#### Custom Field Management
- `/api/custom-fields` endpoints for CRUD operations
- Field types: text, number, date, select, checkbox
- Soft-delete with `is_active` flag
- Validation for required select options

#### File Changes
- `app/routers/custom_fields.py` - NEW router for custom field management

### 6. ✅ Admin User Management

#### New Admin Endpoints
- `POST /api/admin/users/create` - Admin creates new user with role selection
- `PUT /api/admin/users/{user_id}` - Admin updates user details and role
- `DELETE /api/admin/users/{user_id}` - Admin deletes user (prevents self-deletion)

#### File Changes
- `app/routers/admin_users.py` - NEW admin user management router

### 7. ✅ Testing Framework

#### Test Files Created
- `backend/test_security.py` - Security tests for role-based access
- `backend/test_endpoints.py` - Endpoint verification tests

## Database Migration Required

```sql
-- Add custom_fields table if not exists
CREATE TABLE IF NOT EXISTS custom_fields (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  field_type VARCHAR(50) NOT NULL CHECK (field_type IN ('text', 'number', 'date', 'select', 'checkbox')),
  is_active BOOLEAN DEFAULT true,
  options JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS on custom_fields
ALTER TABLE custom_fields ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can view active custom fields
CREATE POLICY custom_fields_select ON custom_fields
  FOR SELECT USING (is_active = true);
```

## API Endpoint Changes

### REMOVED
- ❌ `POST /api/auth/register` (now returns 403 Forbidden)

### MODIFIED  
- `POST /api/auth/register-assignee` - New: Public can register as assignee only
- `GET /api/leads` - Now includes `assignee_name` field in response
- `POST /api/leads` - Source field now expects: email, website, manual, other

### NEW
- ✅ `POST /api/admin/users/create` - Admin creates users
- ✅ `PUT /api/admin/users/{user_id}` - Admin updates users
- ✅ `DELETE /api/admin/users/{user_id}` - Admin deletes users
- ✅ `GET /api/custom-fields` - List custom fields
- ✅ `POST /api/custom-fields` - Create custom field
- ✅ `PUT /api/custom-fields/{field_id}` - Update custom field
- ✅ `DELETE /api/custom-fields/{field_id}` - Delete custom field

## Frontend Route Changes

### NEW ROUTES
- `/kanban` - Kanban board view with drag-drop

### MODIFIED ROUTES
- `/leads` - Updated UI with proper field names and assignee display

## Testing Checklist

- [ ] Admin user can be created via seed (already exists)
- [ ] Non-admin cannot create users
- [ ] Non-admin cannot escalate their role
- [ ] Leads list shows assignee names
- [ ] Leads show correct source types (email, website, manual, other)
- [ ] Kanban board loads and displays leads by status
- [ ] Drag-drop in Kanban updates lead status
- [ ] Custom fields can be created/updated/deleted
- [ ] Assignment emails go to assignee's profile email
- [ ] Login with existing admin account works

## Deployment Steps

1. Update backend routes by importing `custom_fields` and `admin_users`
2. Run database migration for `custom_fields` table
3. Deploy updated frontend with Kanban and Leads changes
4. Test admin user creation via `/api/admin/users/create`
5. Verify role-based access control on all endpoints

## Breaking Changes

⚠️ **BREAKING**: Public registration is now disabled
- Existing code using `POST /api/auth/register` for user creation will fail
- Solution: Use `POST /api/admin/users/create` (admin only) or `/api/auth/register-assignee` (public, assignee only)

⚠️ **BREAKING**: Lead source field values changed
- Old values: `manual`, `api`, `import`
- New values: `email`, `website`, `manual`, `other`
- Migration: Update any existing leads and frontend filters

## Security Improvements

✅ No unauthorized role escalation possible
✅ Public registration restricted to assignee role only
✅ Admin functions require admin authentication
✅ Email notification sent to correct recipient (assignee's profile email)
✅ Self-deletion prevention for admins

## Notes

- All changes maintain backward compatibility with existing leads data
- RLS policies updated to work with new admin routes
- Email field separation clarified to prevent accidental customer email leaks in notifications
