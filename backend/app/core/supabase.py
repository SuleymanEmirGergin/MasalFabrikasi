from supabase import create_client, Client
from app.core.config import settings

# Service Role Client (Bypasses RLS - Server Side Only)
# CRITICAL: Never expose SUPABASE_SERVICE_KEY to the client
supabase: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_SERVICE_KEY
)

# Standard Anon Client (Respects RLS if used)
supabase_anon: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY
)
