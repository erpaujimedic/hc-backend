# File: app/api/v1/endpoints/transactions.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

# IMPORTANT: Import your Supabase client
from app.db.supabase import supabase

router = APIRouter()

# ==========================================
# 🛡️ PYDANTIC SCHEMAS (SILICON VALLEY STANDARD)
# Strict validation models to protect the database
# ==========================================

class TransactionCreate(BaseModel):
    order_source: str = Field(default="INTERNAL", description="B2B Source or Platform")
    patient_name: str
    phone: str
    address: str
    maps_link: Optional[str] = None
    service: str
    
    # 🔥 THE BULLETPROOF FIX: Izinkan menerima null (None) dari Frontend!
    schedule_date: Optional[str] = None
    schedule_time: Optional[str] = None
    branch: Optional[str] = None
    
    nurse_name: Optional[str] = None
    patient_lat: Optional[float] = None
    patient_lng: Optional[float] = None

class TransactionUpdate(BaseModel):
    order_source: Optional[str] = None
    patient_name: Optional[str] = None
    phone: Optional[str] = None
    branch: Optional[str] = None
    schedule_time: Optional[str] = None
    service: Optional[str] = None
    nurse_name: Optional[str] = None
    status: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str
    en_route_time: Optional[str] = None
    arrived_time: Optional[str] = None
    completed_time: Optional[str] = None
    prep_photo: Optional[str] = None
    checklist_completed: Optional[bool] = None
    is_manual_close: Optional[bool] = None
    manual_close_reason: Optional[str] = None
    
    # 🔥 TAMBAHAN WAJIB BIAR KOORDINAT AWAL GA DIBUANG FASTAPI
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None

class ClaimJob(BaseModel):
    nurse_name: str

class TelemetryUpdate(BaseModel):
    current_lat: float
    current_lng: float

class PatientReview(BaseModel):
    patient_name: str
    service_name: str
    rating: int
    answers: Dict[str, Any] = Field(default_factory=dict)
    feedback: Optional[str] = ""

# ==========================================
# 1. RETRIEVE ALL TRANSACTIONS (WITH TELEMETRY & AUDIT)
# ==========================================
@router.get("", status_code=status.HTTP_200_OK)
async def get_all_transactions():
    """
    Retrieve all operational schedules and perfectly map them for the React Frontend.
    Includes Spatial Data (Lat/Lng) and Pre-Departure Audit data.
    """
    try:
        response = supabase.table("patient_tasks").select("*").order("id", desc=True).execute()
        raw_data = response.data or []
        print(f"🔍 [Diagnostic Radar] Supabase returned {len(raw_data)} raw rows from 'patient_tasks'.")
        
        formatted_data = []
        for task in raw_data:
            formatted_data.append({
                "id": task.get("id"),
                "branch": task.get("branch") or task.get("branch_code") or "AUTO",
                "patient_name": task.get("patient_name") or task.get("patient") or "Unknown Patient",
                "phone": task.get("phone") or "No Phone",
                "service": task.get("service") or task.get("service_name") or "General Homecare",
                
                # 🔥 OMNI-CHANNEL SOURCE EXTRACTOR
                "source": task.get("order_source") or task.get("source") or task.get("platform") or task.get("channel") or "INTERNAL", 
                
                "schedule_time": f"{task.get('schedule_date', '')} {task.get('schedule_time', '')}".strip() or "TBA",
                "nurse_name": task.get("nurse_name") or "",
                
                "orderStatus": task.get("status") or "Scheduled",
                "status": task.get("status") or "Scheduled",

                "created_at": task.get("created_at"),
                "en_route_time": task.get("en_route_time"),
                "arrived_time": task.get("arrived_time"),
                "completed_time": task.get("completed_time"),
                
                "patient_lat": task.get("patient_lat"),
                "patient_lng": task.get("patient_lng"),
                "address": task.get("address"),
                "maps_link": task.get("maps_link"),
                
                "current_lat": task.get("current_lat"),
                "current_lng": task.get("current_lng"),

                "prep_photo": task.get("prep_photo"),
                "checklist_completed": task.get("checklist_completed") or False,
                "is_manual_close": task.get("is_manual_close") or False,
                "manual_close_reason": task.get("manual_close_reason")
            })
            
        return formatted_data
        
    except Exception as e:
        print(f"🚨 [Transactions API CRITICAL] Failed to fetch data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transaction records.")


# ==========================================
# 2. CREATE NEW TRANSACTION
# ==========================================
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_transaction(payload: TransactionCreate):
    try:
        insert_data = payload.model_dump(exclude_unset=True)
        insert_data["status"] = "Scheduled" 
        
        # Menerjemahkan key dari Frontend menjadi nama kolom asli di Supabase
        if "order_source" in insert_data:
            insert_data["source"] = insert_data.pop("order_source")

        response = supabase.table("patient_tasks").insert(insert_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Database rejected the insertion.")
            
        print("✅ [Transactions API] New schedule successfully dispatched.")
        return {"status": "success", "message": "Schedule created.", "data": response.data[0]}
        
    except Exception as e:
        error_detail = str(e)
        if hasattr(e, 'details'):
            error_detail = f"{e.message} - {e.details}"
        elif hasattr(e, 'message'):
            error_detail = e.message
            
        print(f"🚨 [DB REJECTION CRITICAL] {error_detail}")
        raise HTTPException(status_code=422, detail=f"Data Integrity Error: {error_detail}")


# ==========================================
# 3. UPDATE TRANSACTION DETAILS
# ==========================================
@router.patch("/{transaction_id}", status_code=status.HTTP_200_OK)
async def update_transaction_detail(transaction_id: str, payload: TransactionUpdate):
    try:
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid data provided for update.")

        response = supabase.table("patient_tasks").update(update_data).eq("id", transaction_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found.")
            
        return {"status": "success", "message": "Transaction updated.", "data": response.data[0]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 4. UPDATE TRANSACTION STATUS ONLY (WITH DB UPDATE)
# ==========================================
@router.patch("/{transaction_id}/status", status_code=status.HTTP_200_OK)
async def update_transaction_status(transaction_id: str, payload: StatusUpdate):
    try:
        update_packet = payload.model_dump(exclude_unset=True)

        # 1. Update ke PostgreSQL Database (Ini otomatis akan nge-trigger event postgres_changes di Frontend lu)
        response = supabase.table("patient_tasks").update(update_packet).eq("id", transaction_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found.")

        # 2. Opsional: Lempar sinyal realtime ekstra (Kalau sewaktu-waktu lu butuh custom event)
        try:
            supabase.channel('hq-dashboard-metrics').send(
                "broadcast",
                {
                    "event": "status_update",
                    "payload": {
                        "transaction_id": transaction_id,
                        "status": payload.status
                    }
                }
            )
        except Exception as e:
            print(f"⚠️ [Broadcast Warning] Could not broadcast status: {e}")

        return {"status": "success", "message": f"Status updated to {payload.status}.", "data": response.data[0]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 5. ATOMIC LOCKING (CLAIM JOB)
# ==========================================
@router.patch("/{transaction_id}/claim", status_code=status.HTTP_200_OK)
async def claim_transaction(transaction_id: str, payload: ClaimJob):
    try:
        check_query = supabase.table("patient_tasks").select("nurse_name").eq("id", transaction_id).execute()
        
        if not check_query.data:
            raise HTTPException(status_code=404, detail="Task not found.")
            
        current_nurse = check_query.data[0].get("nurse_name")
        
        if current_nurse and current_nurse.strip() != "":
            raise HTTPException(status_code=409, detail="This order has already been claimed.")

        supabase.table("patient_tasks").update({
            "nurse_name": payload.nurse_name,
            "status": "Assigned" 
        }).eq("id", transaction_id).execute()

        return {"status": "success", "message": "Order successfully locked and claimed."}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 6. 🛰️ LIVE GPS TELEMETRY TRACKER (BROADCAST ONLY - NO DB WRITE!)
# ==========================================
@router.patch("/{transaction_id}/tracking", status_code=status.HTTP_200_OK)
async def update_live_tracking(transaction_id: str, payload: TelemetryUpdate):
    """
    🔥 SILICON VALLEY ARCHITECTURE 🔥
    Endpoint ini TIDAK menyentuh database sama sekali. 
    Ia hanya berfungsi sebagai stasiun relay untuk melempar koordinat ke memori browser Command Center.
    Hemat kuota, hemat CPU server, 0 delay!
    """
    try:
        # Mengirim data langsung ke channel "live-radar" untuk ditangkap oleh OverviewTab.jsx di Frontend
        supabase.channel('live-radar').send(
            "broadcast",
            {
                "event": "location_update",
                "payload": {
                    "transaction_id": transaction_id,
                    "lat": payload.current_lat,
                    "lng": payload.current_lng
                }
            }
        )

        # Mengembalikan response seolah-olah sukses disimpan biar aplikasi perawat tidak error
        return {"status": "success", "message": "GPS telemetry broadcasted to command center."}
        
    except Exception as e:
        print(f"🚨 [Telemetry Broadcast Error] {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to broadcast telemetry")


# ==========================================
# 7. 📋 GET DYNAMIC SURVEY TEMPLATE FOR PATIENT
# ==========================================
@router.get("/{transaction_id}/survey", status_code=status.HTTP_200_OK)
async def get_patient_survey(transaction_id: str):
    try:
        task_query = supabase.table("patient_tasks").select("service, patient_name").eq("id", transaction_id).execute()
        if not task_query.data:
            raise HTTPException(status_code=404, detail="Transaction not found.")
            
        service_name = task_query.data[0].get("service", "").lower()
        patient_name = task_query.data[0].get("patient_name", "")

        config_key = 'SURVEY_TEMPLATE_VAKSIN' 
        if 'wound' in service_name or 'luka' in service_name:
            config_key = 'SURVEY_TEMPLATE_WOUND_CARE'

        config_query = supabase.table("system_configs").select("config_value").eq("config_key", config_key).execute()
        questions = config_query.data[0].get("config_value", []) if config_query.data else []

        return {
            "status": "success",
            "patient_name": patient_name,
            "service_name": task_query.data[0].get("service"),
            "questions": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 8. ⭐ SUBMIT PATIENT REVIEW & AUTO-COMPLETE MISSION
# ==========================================
@router.post("/{transaction_id}/review", status_code=status.HTTP_200_OK)
async def submit_patient_review(transaction_id: str, payload: PatientReview):
    try:
        review_data = payload.model_dump()
        review_data["transaction_id"] = transaction_id
        
        supabase.table("patient_reviews").insert(review_data).execute()

        now_utc = datetime.now(timezone.utc).isoformat()
        
        # Trigger event postgres_changes ke Frontend
        supabase.table("patient_tasks").update({
            "status": "Completed",
            "completed_time": now_utc
        }).eq("id", transaction_id).execute()

        return {"status": "success", "message": "Review submitted and mission completed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))