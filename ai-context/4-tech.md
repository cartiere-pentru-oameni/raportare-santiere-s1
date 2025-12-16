# Technical Stack

## Authentication
Custom database authentication using bcrypt password hashing and Flask server-side sessions. Only internal users (admins, validators) need accounts - citizens remain fully anonymous.

## Database
Supabase Postgres database with Row-Level Security (RLS). Two clients are used:
- `supabase` (anon key) - for public operations, respects RLS
- `supabase_admin` (service key) - for admin operations, bypasses RLS

## File Storage
Supabase Storage (S3-compatible) for report pictures. Bucket: `report-pictures` (private).

## Backend
Python Flask 3.1 with Blueprints architecture:
- `app/routes/public.py` - public routes (home, reports, map)
- `app/routes/auth.py` - login/logout
- `app/routes/admin.py` - admin dashboard, user management
- `app/routes/validator.py` - validator dashboard, report review
- `app/routes/permits.py` - permits search and scraper triggers
- `app/routes/api.py` - API endpoints
- `app/scrapers/pmb.py` - PMB permits scraper (urbanism.pmb.ro)
- `app/scrapers/ps1.py` - PS1 permits scraper (primariasector1.ro)

## Frontend
AdminLTE 3.2 template with jQuery and Bootstrap. Minimalistic, boomer-friendly UI.

## Maps
OpenStreetMap with Leaflet.js for interactive map functionality.

## Configuration
Environment variables via `.env` file (python-dotenv). See `.env.example` for required variables. 
