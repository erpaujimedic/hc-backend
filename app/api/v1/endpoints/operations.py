# File: app/api/v1/endpoints/operations.py
import json
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request, WebSocket, WebSocketDisconnect, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from redis import asyncio as aioredis
from typing import List

# Security & Config
from app.core.config import settings
from app.api.v1.endpoints.auth import get_current_user, require_admin
from app.db.supabase import supabase

# Schemas
from app.schemas.ops import VisitStatusUpdate, EmergencyAlert, StaffLocationUpdate, OrderRequest

# Services
from app.services.ops_service import HomecareOpsService
from app.services.dispatch_service import process_auto_dispatch

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# --- FLEET TRACKING MANAGER ---
class EnterpriseFleetTrackingManager:
    """
    Silicon Valley Standard: Distributed WebSocket Manager using Redis Pub/Sub.
    Manages live geographical tracking for mobile nurses.
    """
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, visit_id: str, websocket: WebSocket):
        await websocket.accept()
        if visit_id not in self.active_connections:
            self.active_connections[visit_id] = []
        self.active_connections[visit_id].append(websocket)

    def disconnect(self, visit_id: str, websocket: WebSocket):
        if visit_id in self.active_connections and websocket in self.active_connections[visit_id]:
            self.active_connections[visit_id].remove(websocket)

    async def broadcast_location(self, visit_id: str, payload: dict):
        await self.redis.publish(f"fleet_{visit_id}", json.dumps(payload))

tracking_manager = EnterpriseFleetTrackingManager()

# --- ROUTES DISPATCH ---
@router.post("/dispatch/auto", tags=["Dispatch"])
async def auto_assign_schedule(order: OrderRequest, current_user: dict = Depends(get_current_user)):
    """Automatically assigns the nearest available branch based on patient coordinates."""
    try:
        branch_name, distance = await process_auto_dispatch(order)
        return {
            "status": "success", 
            "message": "Auto-dispatch successful. Nearest branch assigned.",
            "data": {
                "assigned_branch": branch_name, 
                "distance_km": round(distance, 2),
                "estimated_time_mins": round(distance * 3) 
            }
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))

# --- ROUTES FIELD OPS & TRACKING ---
@router.get("/active-visits", tags=["Operations"])
async def get_active_fleet_operations(limit: int = 50, offset: int = 0, current_user: dict = Depends(get_current_user)):
    """Fetch all currently active homecare visits."""
    data = await HomecareOpsService.fetch_active_visits(limit, offset)
    return {"status": "success", "data": data}

@router.post("/sos", tags=["Operations"])
@limiter.limit("3/minute")
async def trigger_field_emergency(request: Request, alert: EmergencyAlert, bg_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Handles critical SOS signals from field nurses."""
    emergency_log = await HomecareOpsService.trigger_emergency_alert(alert)
    bg_tasks.add_task(HomecareOpsService.dispatch_critical_alerts, emergency_log)
    return {"status": "critical", "message": "SOS Alert dispatched."}

@router.websocket("/ws/location/{visit_id}")
async def live_location(websocket: WebSocket, visit_id: str):
    """Duplex WebSocket stream for live staff GPS tracking."""
    await tracking_manager.connect(visit_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            location_frame = StaffLocationUpdate(**data)
            await HomecareOpsService.save_telemetry_frame(visit_id, location_frame)
            
            broadcast_payload = {
                "visit_id": visit_id,
                "staff_id": location_frame.staff_id,
                "coordinates": {"lat": location_frame.latitude, "lon": location_frame.longitude},
                "role": location_frame.role
            }
            await tracking_manager.broadcast_location(visit_id, broadcast_payload)
            
    except WebSocketDisconnect:
        tracking_manager.disconnect(visit_id, websocket)
        await HomecareOpsService.finalize_telemetry_session(visit_id)
    except Exception:
        tracking_manager.disconnect(visit_id, websocket)

# --- ANALYTICS & TRANSACTIONS (The new missing piece!) ---
@router.get("/transactions", status_code=status.HTTP_200_OK, tags=["Operations"])
async def get_all_transactions(request: Request):
    """
    Retrieve all patient transaction data for the Analytics table/charts.
    Protected endpoint: Requires Administrator or Supervisor privileges.
    """
    await require_admin(request)
    
    try:
        response = supabase.table("patient_tasks").select("*").execute()
        
        return {
            "status": "success",
            "message": "Transactions retrieved successfully",
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve transactions: {str(e)}"
        )