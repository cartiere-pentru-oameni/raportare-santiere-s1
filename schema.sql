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

-- Enable Row Level Security (RLS)
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE pictures ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE official_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE permits ENABLE ROW LEVEL SECURITY;
ALTER TABLE permits_metadata ENABLE ROW LEVEL SECURITY;

-- RLS Policies for reports
CREATE POLICY "Public can view all reports" ON reports
    FOR SELECT USING (true);

CREATE POLICY "Anyone can insert reports" ON reports
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Service role can do everything on reports" ON reports
    FOR ALL USING (auth.role() = 'service_role');

-- RLS Policies for pictures
CREATE POLICY "Public can view pictures of reviewed reports" ON pictures
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM reports
            WHERE reports.id = pictures.report_id
            AND reports.status IN ('in-review', 'validated', 'resolved')
        )
    );

CREATE POLICY "Anyone can insert pictures" ON pictures
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Service role can do everything on pictures" ON pictures
    FOR ALL USING (auth.role() = 'service_role');

-- RLS Policies for comments
CREATE POLICY "Public can view comments" ON comments
    FOR SELECT USING (true);

CREATE POLICY "Service role can do everything on comments" ON comments
    FOR ALL USING (auth.role() = 'service_role');

-- RLS Policies for official_users
CREATE POLICY "Service role can do everything on official_users" ON official_users
    FOR ALL USING (auth.role() = 'service_role');

-- RLS Policies for reports_history
CREATE POLICY "Service role can do everything on reports_history" ON reports_history
    FOR ALL USING (auth.role() = 'service_role');

-- RLS Policies for contact_messages
CREATE POLICY "Anyone can submit contact messages" ON contact_messages
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Service role has full access to contact messages" ON contact_messages
    FOR ALL USING (auth.role() = 'service_role');

-- RLS Policies for permits
CREATE POLICY "Public can read permits" ON permits
    FOR SELECT USING (true);

CREATE POLICY "Service role can do everything on permits" ON permits
    FOR ALL USING (auth.role() = 'service_role');

-- RLS Policies for permits_metadata
CREATE POLICY "Public can read permits_metadata" ON permits_metadata
    FOR SELECT USING (true);

CREATE POLICY "Service role can do everything on permits_metadata" ON permits_metadata
    FOR ALL USING (auth.role() = 'service_role');

-- Initialize permits_metadata with default rows
INSERT INTO permits_metadata (issuer, total_count, status) VALUES ('ps1', 0, 'idle') ON CONFLICT DO NOTHING;
INSERT INTO permits_metadata (issuer, total_count, status) VALUES ('pmb', 0, 'idle') ON CONFLICT DO NOTHING;
