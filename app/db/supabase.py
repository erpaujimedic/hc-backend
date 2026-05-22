# File: app/db/supabase.py
import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    # Initialize Supabase client using credentials from the environment
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.info("✅ Supabase connection pool established successfully.")
except Exception as e:
    logger.error(f"❌ Failed to connect to Supabase: {e}")
    raise e