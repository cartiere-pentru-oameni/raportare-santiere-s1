from supabase import create_client, Client
from app.config import Config

# Public client (respects RLS)
supabase: Client = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_ANON_KEY
)

# Admin client (bypasses RLS)
supabase_admin: Client = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_SERVICE_KEY
)
