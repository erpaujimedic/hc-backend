# File: app/api/v1/endpoints/system.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from app.schemas.system import ConfigUpdate
from app.api.v1.endpoints.auth import get_current_user, require_admin
from app.services.system_service import SystemConfigService # Dulu namanya config_srv

router = APIRouter()

@router.get("/settings", tags=["Configuration"])
@cache(expire=3600, namespace="homs-cache")
async def get_all_settings(current_user: dict = Depends(get_current_user)):
    """Retrieves all system configurations and service catalogs."""
    try:
        configs = await SystemConfigService.fetch_all_configurations()
        return {
            "status": "success",
            "message": "System configurations retrieved successfully.",
            "data": configs
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration retrieval failed: {str(e)}"
        )

@router.put("/settings/{config_key}", tags=["Configuration"])
async def update_setting(config_key: str, payload: ConfigUpdate, admin_user: dict = Depends(require_admin)):
    """Updates or creates a new system configuration."""
    try:
        updated_value = await SystemConfigService.upsert_configuration(config_key, payload.config_value)
        await FastAPICache.clear(namespace="homs-cache")
        
        return {
            "status": "success",
            "message": f"Configuration '{config_key}' successfully updated. Cache invalidated.",
            "data": updated_value
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration and invalidate cache: {str(e)}"
        )