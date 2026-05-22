# File: app/services/system_service.py
import asyncio
from app.db.database import supabase
from app.core.exceptions import ResourceNotFoundError

class SystemConfigService:
    """Encapsulates all business logic for System Configurations with synchronized exceptions."""

    @staticmethod
    async def fetch_all_configurations():
        """Fetches all system settings and formats them into a key-value dictionary."""
        response = await asyncio.to_thread(
            lambda: supabase.table("system_configs").select("*").execute()
        )
        configs = {row["config_key"]: row["config_value"] for row in response.data}
        return configs

    @staticmethod
    async def fetch_specific_configuration(config_key: str):
        """Fetches a specific configuration value by its key."""
        response = await asyncio.to_thread(
            lambda: supabase.table("system_configs").select("config_value").eq("config_key", config_key).execute()
        )
        
        if not response.data:
            raise ResourceNotFoundError(resource_name=f"Configuration Key '{config_key}'")
            
        return response.data[0]["config_value"]

    @staticmethod
    async def upsert_configuration(config_key: str, config_value: any):
        """Updates or creates a new configuration key-value pair."""
        update_data = {
            "config_value": config_value,
            "updated_at": "now()"
        }
        await asyncio.to_thread(
            lambda: supabase.table("system_configs").upsert(
                {"config_key": config_key, **update_data}
            ).execute()
        )
        return {"config_key": config_key, "config_value": config_value}