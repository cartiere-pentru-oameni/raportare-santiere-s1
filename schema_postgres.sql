-- PostgreSQL Schema for Raportare Santiere S1
-- Modified from schema.sql to remove Supabase-specific features (RLS)

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL CHECK (type IN ('no-paperwork', 'noise-violation', 'pollution-violation', 'others')),
    location_lat NUMERIC NOT NULL,
    location_lng NUMERIC NOT NULL,
    address TEXT,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in-review', 'validated', 'invalidated', 'resolved', 'not-allowed')),
    submitted_by_user_id UUID,
    submitted_by_username TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pictures table
CREATE TABLE IF NOT EXISTS pictures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    user_id UUID,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Official users table (for validators and admins)
CREATE TABLE IF NOT EXISTS official_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('validator', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reports history table
CREATE TABLE IF NOT EXISTS reports_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    changed_by UUID REFERENCES official_users(id),
    change_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contact messages table (anonymous contact form)
CREATE TABLE IF NOT EXISTS contact_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    admin_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permits table (scraped building permits)
CREATE TABLE IF NOT EXISTS permits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issuer TEXT NOT NULL,  -- 'ps1' or 'pmb'
    address TEXT NOT NULL,
    data JSONB NOT NULL,   -- all permit data as JSON
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permits metadata table (scraper status tracking)
CREATE TABLE IF NOT EXISTS permits_metadata (
    issuer TEXT PRIMARY KEY,  -- 'ps1' or 'pmb'
    total_count INTEGER NOT NULL DEFAULT 0,
    last_scraped_at TIMESTAMPTZ,
    scraped_by_user_id UUID REFERENCES official_users(id),
    scraped_by_username TEXT,
    status TEXT DEFAULT 'idle',  -- 'idle', 'running', 'error'
    error_message TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(type);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at);
CREATE INDEX IF NOT EXISTS idx_pictures_report_id ON pictures(report_id);
CREATE INDEX IF NOT EXISTS idx_comments_report_id ON comments(report_id);
CREATE INDEX IF NOT EXISTS idx_reports_history_report_id ON reports_history(report_id);
CREATE INDEX IF NOT EXISTS idx_permits_issuer ON permits(issuer);
CREATE INDEX IF NOT EXISTS idx_permits_address ON permits(address);

-- Initialize permits_metadata with default rows
INSERT INTO permits_metadata (issuer, total_count, status) VALUES ('ps1', 0, 'idle') ON CONFLICT (issuer) DO NOTHING;
INSERT INTO permits_metadata (issuer, total_count, status) VALUES ('pmb', 0, 'idle') ON CONFLICT (issuer) DO NOTHING;
