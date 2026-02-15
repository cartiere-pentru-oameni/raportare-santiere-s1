# Technical Stack

## Authentication
Custom database authentication using bcrypt password hashing and Flask server-side sessions. Only internal users (admins, validators) need accounts - citizens remain fully anonymous.

## Database
Self-hosted PostgreSQL database with psycopg3 connection pooling. Two client aliases are used for backward compatibility:
- `supabase` - alias to DatabaseClient for public operations
- `supabase_admin` - alias to DatabaseClient for admin operations
Both now connect to the same PostgreSQL database (RLS removed for self-hosted setup).

## File Storage
Hetzner Object Storage (S3-compatible) using boto3 SDK. Private bucket with presigned URLs for access control.
- Storage operations: upload, download, delete, signed URL generation
- Security: Private bucket, 1-hour presigned URLs, server-side access control

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
