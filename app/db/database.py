import logging
from supabase import create_client, Client
from supabase.client import ClientOptions
from app.core.config import settings

# ==========================================
# 1. PROFESSIONAL LOGGER INITIALIZATION
# ==========================================
# Silicon Valley Standard: Never use print() in production.
logger = logging.getLogger("homecare_database")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# ==========================================
# 2. SINGLETON DATABASE MANAGER
# ==========================================
class SupabaseDatabase:
    """
    Singleton Database Manager for Supabase.
    Ensures only one persistent connection instance is created for the entire FastAPI lifecycle,
    preventing memory leaks and connection exhaustion.
    """
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                logger.error("CRITICAL: Supabase URL or Key is missing from environment variables.")
                raise ValueError("Database initialization failed: Missing credentials.")

            # Enterprise configuration: Explicit timeouts prevent server hanging
            options = ClientOptions(
                postgrest_client_timeout=15, # Maksimal nunggu data DB 15 detik
                storage_client_timeout=15,   # Maksimal nunggu upload file 15 detik
                schema="public"              # Skema default
            )

            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY,
                    options=options
                )
                logger.info("✅ Supabase connection pool established successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {str(e)}")
                raise e
                
        return cls._instance

# ==========================================
# 3. GLOBAL INSTANCE EXPORT
# ==========================================
# Variabel inilah yang nanti di-import oleh semua file di folder 'services/'
supabase: Client = SupabaseDatabase.get_client()