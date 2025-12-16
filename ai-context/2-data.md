# Inputs & Outputs
1. Report data from citizens, including:
    - Type of violation
    - Location (coordinates, optional address)
    - Pictures (with EXIF data stripped)
    - Description (optional)
2. Official users data (validators and admins):
    - Usernames
    - Passwords (hashed with bcrypt)
    - Roles (validator, admin)
3. Report status updates from validators:
    - Status changes (pending, in_review, validated, rejected, resolved)
    - Comments on reports
4. Building permits data (scraped from official sources):
    - PS1 permits from primariasector1.ro
    - PMB permits from urbanism.pmb.ro
5. Contact messages from anonymous users
6. Statistics data for citizens

# Data modelling

## reports
- id (UUID, primary key)
- type (string: no-paperwork, noise-violation, pollution-violation, others)
- location_lat, location_lng (numeric, coordinates)
- address (text, nullable)
- description (text, nullable)
- status (string: pending, in-review, validated, invalidated, resolved, not-allowed)
- submitted_by_user_id (UUID, nullable)
- submitted_by_username (text, nullable)
- created_at (timestamp)
- updated_at (timestamp)

## pictures
- id (UUID, primary key)
- report_id (UUID, foreign key)
- storage_path (text) - path in Supabase Storage
- created_at (timestamp)

## comments
- id (UUID, primary key)
- report_id (UUID, foreign key)
- user_id (UUID, nullable)
- text (text)
- created_at (timestamp)

## official_users
- id (UUID, primary key)
- username (text, unique)
- password_hash (text, bcrypt)
- role (text: validator, admin)
- created_at (timestamp)
- updated_at (timestamp)

## reports_history
- id (UUID, primary key)
- report_id (UUID, foreign key)
- changed_by (UUID, nullable, foreign key to official_users)
- change_type (text)
- old_value (text, nullable)
- new_value (text, nullable)
- created_at (timestamp)

## permits
- id (UUID, primary key)
- issuer (text: ps1, pmb)
- address (text)
- data (jsonb) - all permit data as JSON
- source_url (text, nullable)
- created_at (timestamp)
- updated_at (timestamp)

## permits_metadata
- issuer (text, primary key: ps1, pmb)
- total_count (integer)
- last_scraped_at (timestamp, nullable)
- scraped_by_user_id (UUID, nullable)
- scraped_by_username (text, nullable)
- status (text: idle, running, error)
- error_message (text, nullable)
- updated_at (timestamp)

## contact_messages
- id (UUID, primary key)
- email (text, nullable)
- message (text)
- read (boolean, default false)
- admin_notes (text, nullable)
- created_at (timestamp)

# Storage
- Supabase Storage bucket `report-pictures` (private) for citizen-uploaded photos
- Supabase Postgres for all structured data

# No personal data logging policy
To protect the anonymity of the citizens using the platform, the logs will not store any personal data or data that can be used to identify a user. The following data will not be logged:
- IP addresses
- User agents
- Cookies (except for session management for admins and validators)
- Screen resolution
- Browser type
- Operating system
- Referrer URLs