from supabase import create_client, Client
from app.core.config import settings
from typing import Optional

# Initialize Supabase clients only if configured
supabase: Optional[Client] = None
supabase_anon: Optional[Client] = None

if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
    try:
        # Service Role Client (Bypasses RLS - Server Side Only)
        supabase = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        print("✅ Supabase service client initialized")
    except Exception as e:
        print(f"⚠️ Supabase service client failed: {e}")
        supabase = None

if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
    try:
        # Standard Anon Client (Respects RLS if used)
        supabase_anon = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
        print("✅ Supabase anon client initialized")
    except Exception as e:
        print(f"⚠️ Supabase anon client failed: {e}")
        supabase_anon = None

if not supabase and not supabase_anon:
    print("⚠️ Supabase not configured - storage features will be limited")
