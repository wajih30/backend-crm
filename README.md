# Lead Management & Assignment Tool - Backend

A FastAPI-based backend for the Lead Management & Assignment Tool with Supabase PostgreSQL database integration.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings & environment config
│   ├── dependencies.py         # Auth and dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User Pydantic models
│   │   ├── lead.py             # Lead Pydantic models
│   │   ├── dashboard.py        # Dashboard Pydantic models
│   │   └── notification.py     # Notification Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── users.py            # User management endpoints
│   │   ├── leads.py            # Lead management endpoints
│   │   ├── dashboard.py        # Dashboard endpoints
│   │   └── audit_logs.py       # Audit log endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── lead_service.py     # Lead business logic
│   │   ├── email_service.py    # Email notifications
│   │   ├── sla_service.py      # SLA calculations
│   │   ├── audit_service.py    # Audit trail
│   │   ├── dashboard_service.py # Dashboard metrics
│   │   └── scheduler_service.py # Background jobs
│   ├── utils/
│   │   ├── __init__.py
│   │   └── supabase_client.py  # Supabase client
│   └── templates/
│       └── [email templates]
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
├── tests/
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- Supabase project (get from https://supabase.com)
- SMTP credentials (SendGrid, Resend, or SES)

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# SMTP / Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Application Settings
APP_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# SLA Configuration
DEFAULT_SLA_DURATION_MINUTES=120
```

### 4. Set Up Database Schema

Run the migration in Supabase:

1. Go to your Supabase dashboard
2. Navigate to SQL Editor
3. Run the contents of `supabase/migrations/001_initial_schema.sql`

### 5. Run the Backend

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/logout` - Logout user

### Users
- `GET /api/users` - List all users (admin only)
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users` - Create new user (admin only)
- `PATCH /api/users/{id}` - Update user (admin only)
- `DELETE /api/users/{id}` - Delete user (admin only)

### Leads
- `GET /api/leads` - List leads with filters
- `GET /api/leads/{id}` - Get lead details
- `POST /api/leads` - Create new lead
- `PATCH /api/leads/{id}` - Update lead
- `POST /api/leads/{id}/assign` - Assign lead
- `POST /api/leads/{id}/resend-email` - Resend notification email

### Dashboard
- `GET /api/dashboard/metrics` - Get dashboard metrics
- `GET /api/dashboard/leads-per-assignee` - Get leads by assignee

### Audit Logs
- `GET /api/audit-logs` - Get audit logs (admin only)

## Features

### Lead Management
- Create, read, update leads
- Support for custom JSONB fields
- Flexible status management
- Multi-source lead tracking

### Assignment & Notifications
- Assign leads to team members
- Automatic email notifications
- Notification retry logic (3 attempts)
- Assignment history tracking

### SLA & Deadline Management
- Configure SLA duration
- Automatic deadline reminders (30 min before)
- SLA breach detection and notification
- Background cron jobs every 5 minutes

### Dashboard & Metrics
- Real-time lead metrics
- Leads per assignee breakdown
- SLA performance tracking
- Status distribution

### Audit & Compliance
- Immutable audit logs
- Action tracking (creation, assignment, updates)
- User activity history
- Metadata logging for all operations

### Security
- Supabase Auth integration
- Row Level Security (RLS) policies
- Role-based access control
- JWT token validation
- CORS support

## Background Jobs

The scheduler runs the following background tasks:

1. **Deadline Reminder Check** (every 5 minutes)
   - Finds leads with deadlines in the next 30 minutes
   - Sends reminder emails to assignees

2. **SLA Breach Check** (every 5 minutes)
   - Detects leads that have exceeded SLA deadline
   - Notifies SDR/creator
   - Marks lead as SLA breached

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Troubleshooting

### Environment Variables Not Loading
- Ensure `.env` file is in the `backend/` directory
- Reload the application after editing `.env`

### Email Not Sending
- Check SMTP credentials in `.env`
- Verify SMTP host/port are correct
- Check firewall/network settings
- Look for errors in application logs

### Database Connection Issues
- Verify Supabase URL and keys are correct
- Ensure database schema is migrated
- Check network connectivity to Supabase

### RLS Policy Errors
- Verify user role in `users` table
- Check RLS policies in Supabase dashboard
- Ensure auth token is valid

## Deployment

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t lead-management-backend .
docker run -p 8000:8000 --env-file .env lead-management-backend
```

### Environment Variables for Production
- Set `DEBUG=false`
- Use strong `JWT_SECRET_KEY`
- Use production SMTP credentials
- Update `CORS_ORIGINS` with your frontend URL

## Performance Optimization

- Database indexes on `assignee_id`, `status`, `deadline`, `source`
- Connection pooling via Supabase
- Async/await for non-blocking operations
- Caching strategies for frequently accessed data

## Support

For issues or questions:
1. Check the logs for error messages
2. Review Supabase documentation
3. Check API documentation at `/docs`
4. Review the implementation plan document

## License

Proprietary - Lead Management & Assignment Tool v1.0
