-- =============================================
-- Lead Management & Assignment Tool Database Schema
-- Supabase PostgreSQL
-- Version: 1.0
-- =============================================

-- =============================================
-- TABLE: users
-- Description: User profiles (managed by Supabase Auth)
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'sdr', 'assignee')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for role-based queries
CREATE INDEX idx_users_role ON users(role);

-- =============================================
-- TABLE: leads
-- Description: Central lead records with flexible JSONB custom fields
-- =============================================
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    website VARCHAR(255),
    source VARCHAR(100) NOT NULL DEFAULT 'manual',
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'in_progress', 'not_active', 'closed', 'on_hold', 'sla_breached')),
    deadline TIMESTAMP WITH TIME ZONE,
    sla_deadline TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    custom_fields JSONB DEFAULT '{}',
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_leads_assignee_id ON leads(assignee_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_deadline ON leads(deadline);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_created_by ON leads(created_by);
CREATE INDEX idx_leads_created_at ON leads(created_at);

-- =============================================
-- TABLE: status_history
-- Description: Audit trail for status changes and actions
-- =============================================
CREATE TABLE IF NOT EXISTS status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    status VARCHAR(50),
    action_type VARCHAR(100),
    comment TEXT,
    updated_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for audit queries
CREATE INDEX idx_status_history_lead_id ON status_history(lead_id);
CREATE INDEX idx_status_history_updated_by ON status_history(updated_by);
CREATE INDEX idx_status_history_action_type ON status_history(action_type);
CREATE INDEX idx_status_history_created_at ON status_history(created_at);

-- =============================================
-- TABLE: notifications
-- Description: Email notification log for SLA tracking and retry
-- =============================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    assignee_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    channel VARCHAR(50) NOT NULL DEFAULT 'email',
    message_type VARCHAR(100) NOT NULL CHECK (message_type IN ('assignment', 'reminder', 'sla_breach')),
    message TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    retry_count INTEGER DEFAULT 0,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for notification queries
CREATE INDEX idx_notifications_lead_id ON notifications(lead_id);
CREATE INDEX idx_notifications_assignee_id ON notifications(assignee_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_message_type ON notifications(message_type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- =============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Users table policies
-- Allow users to see their own profile
CREATE POLICY users_select_self ON users
    FOR SELECT USING (auth.uid() = id);

-- Allow admin to see all users
CREATE POLICY users_select_admin ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = auth.uid() AND u.role = 'admin'
        )
    );

-- Leads table policies
-- Allow users to see leads assigned to them
CREATE POLICY leads_select_assigned ON leads
    FOR SELECT USING (
        assignee_id = auth.uid()
    );

-- Allow SDR/Admin to see all leads
CREATE POLICY leads_select_sdr ON leads
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = auth.uid() AND u.role IN ('admin', 'sdr')
        )
    );

-- Allow SDR/Admin to insert leads
CREATE POLICY leads_insert_sdr ON leads
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = auth.uid() AND u.role IN ('admin', 'sdr')
        ) AND created_by = auth.uid()
    );

-- Allow SDR/Admin to update leads
CREATE POLICY leads_update_sdr ON leads
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = auth.uid() AND u.role IN ('admin', 'sdr')
        )
    );

-- Status history table policies
-- Allow users to see status history for leads they can access
CREATE POLICY status_history_select ON status_history
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM leads l 
            WHERE l.id = lead_id AND (
                l.assignee_id = auth.uid() OR
                EXISTS (
                    SELECT 1 FROM users u 
                    WHERE u.id = auth.uid() AND u.role IN ('admin', 'sdr')
                )
            )
        )
    );

-- Notifications table policies
-- Allow users to see notifications for leads assigned to them
CREATE POLICY notifications_select ON notifications
    FOR SELECT USING (
        assignee_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM users u 
            WHERE u.id = auth.uid() AND u.role = 'admin'
        )
    );

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- View for lead metrics
CREATE OR REPLACE VIEW v_lead_metrics AS
SELECT 
    COUNT(*) as total_leads,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_leads,
    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_leads,
    SUM(CASE WHEN status = 'sla_breached' THEN 1 ELSE 0 END) as sla_breaches
FROM leads;

-- View for leads per assignee
CREATE OR REPLACE VIEW v_leads_per_assignee AS
SELECT 
    l.assignee_id,
    u.name as assignee_name,
    COUNT(*) as total_leads,
    SUM(CASE WHEN l.status = 'active' THEN 1 ELSE 0 END) as active_leads,
    SUM(CASE WHEN l.status = 'closed' THEN 1 ELSE 0 END) as closed_leads
FROM leads l
LEFT JOIN users u ON l.assignee_id = u.id
WHERE l.assignee_id IS NOT NULL
GROUP BY l.assignee_id, u.name;

-- =============================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- =============================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER users_update_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Trigger for leads table
CREATE TRIGGER leads_update_timestamp
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Trigger for status_history table
CREATE TRIGGER status_history_update_timestamp
    BEFORE UPDATE ON status_history
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Trigger for notifications table
CREATE TRIGGER notifications_update_timestamp
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- =============================================
-- END OF SCHEMA
-- =============================================
