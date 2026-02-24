# Quick Start Guide

## Prerequisites

You need:
1. **Python 3.9+** installed on your machine
2. **Supabase Project** - Create free at https://supabase.com
3. **SMTP Credentials** - SendGrid, Resend, or Gmail

## Step-by-Step Setup

### 1. Activate Virtual Environment

Open PowerShell/Terminal in `c:\Users\LENOVO\wajih\custom crm\backend` and run:

```powershell
# Windows
venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit `.env` file with your actual credentials:

```env
# REQUIRED: Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# REQUIRED: SMTP Configuration (choose one provider)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use app-specific password for Gmail
SMTP_FROM_EMAIL=your-email@gmail.com

# Optional: Adjust if needed
DEFAULT_SLA_DURATION_MINUTES=120
```

**Where to find Supabase keys:**
1. Go to https://supabase.com and sign in
2. Create a new project or select existing
3. Go to **Settings** → **API**
4. Copy `Project URL`, `anon public key`, and `service_role key`

### 4. Set Up Database Schema

**Via Supabase Dashboard (Easiest):**
1. Log in to Supabase
2. Go to **SQL Editor**
3. Click **New Query**
4. Copy and paste contents of `supabase/migrations/001_initial_schema.sql`
5. Click **Execute**

**Via psql (Alternative):**
```bash
psql postgresql://postgres:password@db.supabase.co/postgres < supabase\migrations\001_initial_schema.sql
```

### 5. Start the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

### 6. Test the Backend

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Interactive API Documentation:**
Visit: http://localhost:8000/docs

You'll see Swagger UI with all available endpoints.

## Project Structure Summary

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings from .env
│   ├── dependencies.py      # Auth middleware
│   ├── models/              # Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   └── utils/               # Helper functions
├── supabase/
│   └── migrations/          # Database schema
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (secrets)
└── README.md               # Full documentation
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py -v
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'app'` | Make sure venv is activated and you're in `backend/` directory |
| `Connection refused` to Supabase | Check SUPABASE_URL and internet connection |
| `Authentication failed` | Verify API keys are correct in .env |
| Email not sending | Check SMTP credentials and try Gmail/SendGrid/Resend |
| RLS policy errors | Ensure database schema is properly migrated |

## Next Steps

1. **Create a user** via `/api/auth/register` endpoint
2. **Create a lead** via `/api/leads` endpoint
3. **Assign lead** via `/api/leads/{id}/assign` endpoint
4. **Check dashboard** metrics via `/api/dashboard/metrics`

## Endpoints Overview

| Feature | Endpoint | Method |
|---------|----------|--------|
| Health Check | `/health` | GET |
| API Docs | `/docs` | GET |
| Register | `/api/auth/register` | POST |
| Login | `/api/auth/login` | POST |
| Create Lead | `/api/leads` | POST |
| List Leads | `/api/leads` | GET |
| Assign Lead | `/api/leads/{id}/assign` | POST |
| Dashboard | `/api/dashboard/metrics` | GET |

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPABASE_URL` | - | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | - | Supabase anonymous key |
| `SUPABASE_SERVICE_ROLE_KEY` | - | Supabase service role key |
| `SMTP_HOST` | `smtp.gmail.com` | Email SMTP server |
| `SMTP_PORT` | `587` | SMTP port (usually 587) |
| `DEFAULT_SLA_DURATION_MINUTES` | `120` | SLA deadline in minutes |
| `APP_URL` | `http://localhost:5173` | Frontend URL |
| `BACKEND_URL` | `http://localhost:8000` | Backend URL |

## Support Resources

- FastAPI docs: https://fastapi.tiangolo.com
- Supabase docs: https://supabase.com/docs
- Python async: https://docs.python.org/3/library/asyncio.html
- Pydantic: https://docs.pydantic.dev

---

**Backend Status:** ✅ Ready to run after configuration

**Next: Create the Frontend (React/Vite)**
