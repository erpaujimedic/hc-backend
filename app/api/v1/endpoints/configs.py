# File: app/api/v1/endpoints/configs.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Optional
from app.db.supabase import supabase # Sesuaikan path import supabase lu ya

router = APIRouter()

# Schema buat nangkep kiriman PATCH (Update aja)
class ConfigUpdate(BaseModel):
    config_value: Any  # Pake 'Any' karena isinya bisa Array atau Object JSON apa aja

# 🔥 SCHEMA BARU: Buat nangkep kiriman POST (Bikin baru/Auto-Inject)
class ConfigCreate(BaseModel):
    config_key: str
    config_value: Any
    description: Optional[str] = None

@router.get("")
async def get_all_configs():
    """
    Tarik semua data dari tabel system_configs
    """
    try:
        response = supabase.table("system_configs").select("*").order("config_key").execute()
        return response.data
    except Exception as e:
        print(f"🚨 [API Configs] Error GET: {str(e)}")
        raise HTTPException(status_code=500, detail="Gagal menarik data konfigurasi sistem.")

# 🔥 API BARU: POST (Buat nyuntikin data otomatis dari Web Frontend)
@router.post("")
async def create_or_upsert_config(payload: ConfigCreate):
    """
    Auto-Injector API: Bikin config baru kalau belum ada di database.
    Pake metode UPSERT (Update or Insert) biar aman anti-duplikat.
    """
    try:
        data = {
            "config_key": payload.config_key,
            "config_value": payload.config_value,
            "description": payload.description
        }
        # Upsert: Kalo config_key udah ada, timpa. Kalo belom, bikin baru!
        response = supabase.table("system_configs").upsert(data, on_conflict="config_key").execute()
        return {"status": "success", "message": "Config injected/updated successfully!", "data": response.data}
    except Exception as e:
        print(f"🚨 [API Configs] Error POST: {str(e)}")
        raise HTTPException(status_code=500, detail="Gagal menyuntikkan konfigurasi baru.")

@router.patch("/{config_key}")
async def update_config(config_key: str, payload: ConfigUpdate):
    """
    Update JSON config_value berdasarkan config_key (e.g., 'homecare_services')
    """
    try:
        response = supabase.table("system_configs").update({
            "config_value": payload.config_value
        }).eq("config_key", config_key).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Config dengan key '{config_key}' tidak ditemukan.")
            
        return {"status": "success", "message": "Config updated", "data": response.data[0]}
    except Exception as e:
        print(f"🚨 [API Configs] Error PATCH: {str(e)}")
        raise HTTPException(status_code=500, detail="Gagal menyimpan konfigurasi.")