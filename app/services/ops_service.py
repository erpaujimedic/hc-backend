# File: app/services/ops_service.py
import asyncio
from app.db.database import supabase
from app.schemas.ops import VisitStatusUpdate, EmergencyAlert, StaffLocationUpdate
from app.core.security import DataSecurityManager
from app.core.exceptions import ResourceNotFoundError
from app.utils.timezone_helpers import get_current_utc_time

class HomecareOpsService:
    """
    Silicon Valley Standard: Encapsulates all business logic for Homecare Operations & Transactions.
    """

    # --- TRANSACTIONS LOGIC ---
    @staticmethod
    async def fetch_all_transactions():
        """Fetch all operational transactions (merged from old transactions.py)"""
        response = await asyncio.to_thread(
            lambda: supabase.table("transactions").select("*").order("id", desc=True).execute()
        )
        return response.data if response.data else []

    @staticmethod
    async def fetch_transaction_by_id(transaction_id: str):
        """Fetch single transaction by ID"""
        response = await asyncio.to_thread(
            lambda: supabase.table("transactions").select("*").eq("id", transaction_id).execute()
        )
        if not response.data:
            raise ResourceNotFoundError(resource_name=f"Transaction '{transaction_id}'")
        return response.data[0]

    # --- FIELD OPS & TRACKING LOGIC ---
    @staticmethod
    async def fetch_active_visits(limit: int, offset: int):
        """Asynchronously fetches active operations data and decrypts clinical payload safely."""
        response = await asyncio.to_thread(
            lambda: supabase.table("transactions")\
                .select("*", count="exact")\
                .neq("visit_status", "Completed")\
                .range(offset, offset + limit - 1)\
                .execute()
        )
        
        clean_data = []
        if response.data:
            for record in response.data:
                if record.get("notes"):
                    try:
                        record["notes"] = DataSecurityManager.decrypt_sensitive_data(record["notes"])
                    except Exception:
                        record["notes"] = "[Decryption Failure: Corrupted or Compromised Data]"
                clean_data.append(record)
        return clean_data

    @staticmethod
    async def trigger_emergency_alert(alert: EmergencyAlert):
        """Logs SOS data and triggers immediate background dispatch routines."""
        emergency_data = {
            "visit_id": alert.visit_id,
            "staff_id": alert.nurse_id,
            "emergency_type": alert.emergency_type,
            "latitude": alert.location_lat,
            "longitude": alert.location_lon,
            "status": "Unresolved"
        }
        await asyncio.to_thread(
            lambda: supabase.table("emergencies").insert(emergency_data).execute()
        )
        return emergency_data

    @staticmethod
    async def dispatch_critical_alerts(emergency_log: dict):
        """Background worker to notify Command Center."""
        print(f"[URGENT DISPATCH] SOS Triggered by Staff {emergency_log['staff_id']} at coords {emergency_log['latitude']}, {emergency_log['longitude']}")
        # Simulasi nunggu third party / proses email
        await asyncio.sleep(1)

    @staticmethod
    async def save_telemetry_frame(visit_id: str, frame: StaffLocationUpdate):
        """Persists streaming GPS telemetry into database via Upsert."""
        location_data = {
            "visit_id": visit_id,
            "staff_id": frame.staff_id,
            "role": frame.role,
            "latitude": frame.latitude,
            "longitude": frame.longitude,
            "updated_at": get_current_utc_time().isoformat() 
        }
        await asyncio.to_thread(
            lambda: supabase.table("staff_locations").upsert(location_data).execute()
        )

    @staticmethod
    async def finalize_telemetry_session(visit_id: str):
        """Cleans up GPS tracking cache when operation concludes."""
        await asyncio.to_thread(
            lambda: supabase.table("staff_locations").delete().eq("visit_id", visit_id).execute()
        )