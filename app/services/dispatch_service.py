# File: app/services/dispatch_service.py
import uuid
import asyncio
from app.db.database import supabase
from app.utils.geo_calc import calculate_accurate_distance
from app.core.exceptions import ResourceNotFoundError
from app.services.email_service import dispatch_branch_email_notification 
from app.utils.timezone_helpers import get_current_utc_time

async def async_geocode(address: str):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="tmc_homecare_dispatch_system")
    return await asyncio.to_thread(geolocator.geocode, address, timeout=5)

async def process_auto_dispatch(order):
    """
    Core algorithmic engine for determining the optimal branch assignment.
    Fully synchronized with WGS-84 distance metrics and custom enterprise exceptions.
    """
    # --- STAGE 1: Geolocation Resolution ---
    search_query = f"{order.address}, Indonesia"
    patient_lat, patient_lon = order.patient_lat, order.patient_lon
    
    try:
        location = await async_geocode(search_query)
        if location:
            patient_lat = location.latitude
            patient_lon = location.longitude
    except Exception as e:
        print(f"⚠️ Geocoding resolution warning: {str(e)}")

    # --- STAGE 2: Fleet & Branch Analysis ---
    branches_res = supabase.table("branches").select("*").execute()
    branches = branches_res.data if branches_res.data else []
    
    if not branches:
        raise ValueError("No active branches available in the system for dispatch.")

    selected_branch = None
    shortest_distance = float('inf')

    for branch in branches:
        b_lat = branch.get("latitude")
        b_lon = branch.get("longitude")
        if b_lat and b_lon:
            distance = calculate_accurate_distance(patient_lat, patient_lon, b_lat, b_lon)
            if distance < shortest_distance:
                selected_branch = branch
                shortest_distance = distance
                
    if not selected_branch:
        selected_branch = branches[0]
        shortest_distance = 0.0

    # --- STAGE 3: Persistence & Notification Dispatch ---
    new_trx_id = f"TRX-{uuid.uuid4().hex[:8].upper()}"
    waktu_sekarang_utc = get_current_utc_time().isoformat()
    
    new_db_row = {
        "id": new_trx_id, 
        "patient": order.patient, 
        "phone": order.phone,
        "service": order.service, 
        "nurse": "Pending Assignment", 
        "time": str(order.time), 
        "order_status": "Scheduled", 
        "visit_status": "Waiting Assignment",
        "branch": selected_branch['name'], 
        "sla_total": "Pending",
        "timeline": [
            {
                "status": "Order Placed", 
                "time": waktu_sekarang_utc, 
                "done": True
            }
        ]
    }
    
    supabase.table("transactions").insert([new_db_row]).execute()

    # Dispatch email silently in the background
    branch_email = selected_branch.get('email', 'admin@tmc.com')
    asyncio.create_task(
        dispatch_branch_email_notification(
            target_email=branch_email,
            branch_name=selected_branch['name'],
            patient_name=order.patient,
            service_type=order.service,
            target_time=str(order.time),
            patient_address=order.address
        )
    )
    
    return selected_branch['name'], shortest_distance