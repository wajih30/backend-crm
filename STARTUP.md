# 🚀 Backend Setup Complete - Next Steps

## ✅ What's Been Done

1. **Backend Structure** - Complete FastAPI project with all routers, services, and models
2. **Dependencies** - All 40+ packages installed in `venv`
3. **Database Schema** - 4-table schema with RLS, indexes, and triggers ready
4. **Email Templates** - 3 beautiful HTML templates for notifications
5. **Environment** - .env configured with your Supabase & Gmail credentials

---

## 📋 Steps to Launch Backend

### Step 1: Run Database Migration

The SQL migration script is ready. You need to run it in Supabase:

```bash
# Option A: Use the migration helper (shows the SQL)
python migrate.py

# Copy all the SQL output from the terminal
```

Then:
1. Go to https://supabase.com → Select your project `twwksglyjfqkrvyryais`
2. Click **SQL Editor** → **New Query**
3. Paste the entire SQL script from `python migrate.py` output
4. Click **Execute** button

✨ **Your database will be ready with:**
- ✅ users table (4 columns)
- ✅ leads table (13 columns + JSONB custom_fields)
- ✅ status_history table (audit trail)
- ✅ notifications table (email logs)
- ✅ Row Level Security policies
- ✅ Performance indexes
- ✅ Auto-timestamp triggers

---

### Step 2: Start the Backend Server

```bash
# Activate venv (if not already active)
venv\Scripts\Activate.ps1

# Start development server with auto-reload
uvicorn app.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

---

### Step 3: Test the Backend

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Interactive API Documentation:**
Visit: http://localhost:8000/docs

You'll see all available endpoints with try-it-out functionality!

---

## 📊 Available API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login with email
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Lead Management
- `GET /api/leads` - List all leads with filters
- `POST /api/leads` - Create new lead
- `GET /api/leads/{id}` - Get lead details
- `PATCH /api/leads/{id}` - Update lead
- `POST /api/leads/{id}/assign` - Assign to team member
- `POST /api/leads/{id}/resend-email` - Retry email notification

### Dashboard
- `GET /api/dashboard/metrics` - View all metrics
- `GET /api/dashboard/leads-per-assignee` - Leads by assignee

### Admin
- `GET /api/users` - List users (admin only)
- `POST /api/users` - Create user (admin only)
- `GET /api/audit-logs` - View audit logs (admin only)

---

## 🎯 Example API Calls

### 1. Create a Lead
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "website": "acme.com",
    "source": "email",
    "deadline": "2026-02-25T10:00:00Z",
    "notes": "Hot prospect"
  }'
```

### 2. List Leads
```bash
curl http://localhost:8000/api/leads?source=email&status=active
```

### 3. Get Dashboard Metrics
```bash
curl http://localhost:8000/api/dashboard/metrics
```

---

## 🔧 Configuration Reference

Your `.env` is already configured with:

```env
# Supabase (Your Project)
SUPABASE_URL=https://twwksglyjfqkrvyryais.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci... (configured)
SUPABASE_ANON_KEY=eyJhbGci... (configured)

# Email (Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=wajih.work2001@gmail.com
SMTP_PASSWORD=dchjovcqnnxiwuaq

# Application URLs
APP_URL=http://localhost:5173 (Frontend)
BACKEND_URL=http://localhost:8000 (Backend)

# SLA Settings
DEFAULT_SLA_DURATION_MINUTES=120
SCHEDULER_INTERVAL_MINUTES=5
REMINDER_BEFORE_DEADLINE_MINUTES=30
```

---

## 📁 Backend File Structure

```
backend/
├── app/
│   ├── main.py              ← FastAPI entry point
│   ├── config.py            ← Settings from .env
│   ├── dependencies.py      ← Auth & middleware
│   ├── models/              ← Pydantic schemas
│   │   ├── user.py
│   │   ├── lead.py
│   │   ├── dashboard.py
│   │   └── notification.py
│   ├── routers/             ← API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── leads.py
│   │   ├── dashboard.py
│   │   └── audit_logs.py
│   ├── services/            ← Business logic
│   │   ├── lead_service.py
│   │   ├── email_service.py
│   │   ├── sla_service.py
│   │   ├── audit_service.py
│   │   ├── dashboard_service.py
│   │   └── scheduler_service.py
│   ├── templates/           ← Email HTML templates
│   │   ├── assignment_email.html
│   │   ├── reminder_email.html
│   │   └── sla_breach_email.html
│   └── utils/
│       └── supabase_client.py
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
├── requirements.txt         ← All dependencies (frozen)
├── .env                     ← Your credentials ✅
├── migrate.py              ← Database migration helper
├── README.md               ← Full documentation
└── QUICKSTART.md           ← Quick setup guide
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| **ModuleNotFoundError** | Activate venv: `venv\Scripts\Activate.ps1` |
| **Connection to Supabase fails** | Check SUPABASE_URL and internet connection |
| **Email won't send** | Verify Gmail app password in .env (no spaces) |
| **Port 8000 already in use** | Kill process or use different port: `--port 8001` |
| **Database schema error** | Make sure SQL migration ran successfully in Supabase |

---

## 📝 Important Notes

1. **Database Migration**: Must run the SQL script in Supabase SQL Editor first
2. **Background Jobs**: Scheduler starts automatically when backend starts
3. **Email Retry**: Emails retry up to 3 times with exponential backoff
4. **RLS Policies**: Enforce access control - no manual permission management needed
5. **Audit Logs**: All actions are automatically logged to `status_history` table

---

## 🎉 Next Steps

After backend is running:

1. ✅ **Backend Running** - `http://localhost:8000`
2. ⏭️ **Create Frontend** - React/Vite app (Phase 9)
3. ⏭️ **Connect Frontend** - API integration
4. ⏭️ **Deploy** - Production setup

---

## 📞 Support

If you encounter issues:

1. Check logs in terminal for detailed errors
2. Verify .env file has correct credentials
3. Test connection: `curl http://localhost:8000/health`
4. Check Supabase dashboard for database status
5. Review [FastAPI docs](https://fastapi.tiangolo.com)

---

**Backend Status:** 🟢 **READY TO RUN**

**Last Updated:** February 24, 2026

---

**Command to start:** 
```bash
uvicorn app.main:app --reload --port 8000
```
