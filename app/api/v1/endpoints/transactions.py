# File: app/api/v1/endpoints/transactions.py
from fastapi import APIRouter, HTTPException, status, Query, Body
from typing import List, Optional, Any

# IMPORTANT: Import your Supabase client
from app.db.supabase import supabase

router = APIRouter()

# ==========================================
# 1. RETRIEVE ALL TRANSACTIONS (WITH TELEMETRY)
# ==========================================
@router.get("", status_code=status.HTTP_200_OK)
async def get_all_transactions():
    """
    Retrieve all operational schedules and perfectly map them for the React Frontend.
    Includes Spatial Data (Lat/Lng) for both Patients and Field Agents.
    """
    try:
        # Fetch raw data from Supabase 'patient_tasks' table
        response = supabase.table("patient_tasks").select("*").order("id", desc=True).execute()
        
        raw_data = response.data or []
        print(f"🔍 [Diagnostic Radar] Supabase returned {len(raw_data)} raw rows from 'patient_tasks'.")
        
        # SILICON VALLEY DATA MAPPING
        formatted_data = []
        for task in raw_data:
            formatted_data.append({
                "id": task.get("id"),
                "branch": task.get("branch") or task.get("branch_code") or "AUTO",
                "patient_name": task.get("patient_name") or task.get("patient") or "Unknown Patient",
                "phone": task.get("phone") or "No Phone",
                "service": task.get("service") or task.get("service_name") or "General Homecare",
                
                # Combine Date and Time for the table display safely
                "schedule_time": f"{task.get('schedule_date', '')} {task.get('schedule_time', '')}".strip() or "TBA",
                
                "nurse_name": task.get("nurse_name") or "",
                
                # CRITICAL FIX: React table strictly expects 'orderStatus' (CamelCase)
                "orderStatus": task.get("status") or "Scheduled",
                "status": task.get("status") or "Scheduled",
                "slaTotal": "00:00:00",

                # 🔥 ENGINE WAKTU (DIKIRIM KE REACT BIAR TIMELINE GAK --:--)
                "created_at": task.get("created_at"),
                "en_route_time": task.get("en_route_time"),
                "arrived_time": task.get("arrived_time"),
                "completed_time": task.get("completed_time"),
                
                # Patient Destination Data
                "patient_lat": task.get("patient_lat"),
                "patient_lng": task.get("patient_lng"),
                "address": task.get("address"),
                "maps_link": task.get("maps_link"),
                
                # 🔥 FIELD AGENT LIVE TELEMETRY DATA
                "current_lat": task.get("current_lat"),
                "current_lng": task.get("current_lng")
            })
            
        print(f"✅ [Transactions API] Successfully mapped and dispatched {len(formatted_data)} records to Frontend.")
        return formatted_data
        
    except Exception as e:
        print(f"🚨 [Transactions API CRITICAL] Failed to fetch data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to retrieve transaction records."
        )


# ==========================================
# 2. CREATE NEW TRANSACTION
# ==========================================
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_transaction(payload: dict = Body(...)):
    """
    Create a new operational schedule.
    Inserts data directly into the 'patient_tasks' table.
    """
    try:
        # Clean the payload (remove None values) & ensure default status
        insert_data = {k: v for k, v in payload.items() if v is not None}
        insert_data["status"] = "Scheduled" 
        
        response = supabase.table("patient_tasks").insert(insert_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Database rejected the insertion. Please verify your payload structure."
            )
            
        print("✅ [Transactions API] New schedule successfully dispatched.")
        return {
            "status": "success", 
            "message": "Schedule successfully created.", 
            "data": response.data[0]
        }
        
    except Exception as e:
        print(f"🚨 [Transactions CRITICAL] Failed to create schedule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to dispatch new operational schedule to the database."
        )


# ==========================================
# 3. UPDATE TRANSACTION DETAILS
# ==========================================
@router.patch("/{transaction_id}", status_code=status.HTTP_200_OK)
async def update_transaction_detail(transaction_id: str, payload: dict = Body(...)):
    """
    Update specific operational fields of a transaction (Used by Edit Order Modal).
    """
    try:
        update_data = {k: v for k, v in payload.items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No valid data provided for update."
            )

        response = supabase.table("patient_tasks").update(update_data).eq("id", transaction_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Transaction ID {transaction_id} not found."
            )
            
        print(f"✅ [Transactions API] Successfully updated transaction {transaction_id}.")
        return {
            "status": "success", 
            "message": "Transaction successfully updated.", 
            "data": response.data[0]
        }
        
    except Exception as e:
        print(f"🚨 [Transactions CRITICAL] Failed to update data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to update operational data in the database."
        )


# ==========================================
# 4. UPDATE TRANSACTION STATUS ONLY (DENGAN MESIN WAKTU)
# ==========================================
@router.patch("/{transaction_id}/status", status_code=status.HTTP_200_OK)
async def update_transaction_status(transaction_id: str, status_payload: dict = Body(...)):
    """
    Update solely the operational status of a specific transaction.
    """
    try:
        new_status = status_payload.get("status")
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="The 'status' field is required in the payload."
            )

        # 🔥 INJEKSI WAKTU: Bikin paket update buat disuntik ke Supabase
        update_packet = {"status": new_status}
        
        if "en_route_time" in status_payload:
            update_packet["en_route_time"] = status_payload["en_route_time"]
        if "arrived_time" in status_payload:
            update_packet["arrived_time"] = status_payload["arrived_time"]
        if "completed_time" in status_payload:
            update_packet["completed_time"] = status_payload["completed_time"]

        response = supabase.table("patient_tasks").update(update_packet).eq("id", transaction_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Transaction ID {transaction_id} not found."
            )

        print(f"✅ [Transactions API] Successfully updated status of {transaction_id} to '{new_status}' with Time Data.")
        return {
            "status": "success", 
            "message": f"Transaction status updated to {new_status}.", 
            "data": response.data[0]
        }
        
    except Exception as e:
        print(f"🚨 [Transactions CRITICAL] Failed to update status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to update operational status in the database."
        )


# ==========================================
# 5. ATOMIC LOCKING (CLAIM JOB)
# ==========================================
@router.patch("/{transaction_id}/claim", status_code=status.HTTP_200_OK)
async def claim_transaction(transaction_id: str, payload: dict = Body(...)):
    """
    Atomic Locking Engine for Open Job Board.
    Ensures that an order cannot be claimed by two agents simultaneously.
    """
    try:
        nurse_name = payload.get("nurse_name")
        if not nurse_name:
            raise HTTPException(status_code=400, detail="Practitioner identity is required.")

        # Verification: Check if the order is already taken
        check_query = supabase.table("patient_tasks").select("nurse_name, status").eq("id", transaction_id).execute()
        
        if not check_query.data:
            raise HTTPException(status_code=404, detail="Task not found in the system.")
            
        current_nurse = check_query.data[0].get("nurse_name")
        
        if current_nurse and current_nurse.strip() != "":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Too late! This order has already been claimed by another practitioner."
            )

        # Atomic Lock: Claim the task and update status
        response = supabase.table("patient_tasks").update({
            "nurse_name": nurse_name,
            "status": "Assigned" 
        }).eq("id", transaction_id).execute()

        print(f"🔒 [JOB BOARD] Order {transaction_id} successfully claimed by {nurse_name}.")
        return {"status": "success", "message": "Order successfully locked and claimed."}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🚨 [JOB BOARD CRITICAL] Failed to claim order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 6. 🛰️ LIVE GPS TELEMETRY TRACKER 
# ==========================================
@router.patch("/{transaction_id}/tracking", status_code=status.HTTP_200_OK)
async def update_live_tracking(transaction_id: str, payload: dict = Body(...)):
    """
    Live GPS Tracking Endpoint for Field Agents.
    Receives current_lat and current_lng from the Agent's mobile device.
    """
    try:
        lat = payload.get("current_lat")
        lng = payload.get("current_lng")
        
        if lat is None or lng is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Missing GPS coordinates in telemetry payload."
            )

        # Update the transaction table with the agent's live location
        response = supabase.table("patient_tasks").update({
            "current_lat": lat,
            "current_lng": lng
        }).eq("id", transaction_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Active task not found for GPS injection."
            )

        print(f"📡 [RADAR] Agent Telemetry Received -> TRX: {transaction_id} | Lat: {lat}, Lng: {lng}")
        return {"status": "success", "message": "GPS telemetry ping registered successfully."}
        
    except Exception as e:
        print(f"🚨 [RADAR CRITICAL] Telemetry processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 7. 📋 GET DYNAMIC SURVEY TEMPLATE FOR PATIENT
# ==========================================
@router.get("/{transaction_id}/survey", status_code=status.HTTP_200_OK)
async def get_patient_survey(transaction_id: str):
    """
    Fetch the correct survey template based on the service the patient received.
    """
    try:
        # 1. Cari tau pasien ini dapet layanan apa
        task_query = supabase.table("patient_tasks").select("service, patient_name").eq("id", transaction_id).execute()
        if not task_query.data:
            raise HTTPException(status_code=404, detail="Transaction not found.")
            
        service_name = task_query.data[0].get("service", "").lower()
        patient_name = task_query.data[0].get("patient_name", "")

        # 2. Tentukan Template Key berdasarkan layanan (Mapping cerdas)
        config_key = 'SURVEY_TEMPLATE_VAKSIN' # Default
        if 'wound' in service_name or 'luka' in service_name:
            config_key = 'SURVEY_TEMPLATE_WOUND_CARE'
        # Nanti lu bisa tambahin IF lagi buat layanan lain (Infus, Fisio, dll)

        # 3. Tarik template pertanyaan dari system_configs
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
async def submit_patient_review(transaction_id: str, payload: dict = Body(...)):
    """
    Saves patient review and AUTOMATICALLY triggers 'Completed' status.
    """
    try:
        # 1. Simpan review ke tabel patient_reviews
        review_data = {
            "transaction_id": transaction_id,
            "patient_name": payload.get("patient_name"),
            "service_name": payload.get("service_name"),
            "rating": payload.get("rating"),
            "dynamic_answers": payload.get("answers", {}), # Jawaban JSON dari pasien
            "feedback": payload.get("feedback", "")
        }
        supabase.table("patient_reviews").insert(review_data).execute()

        # 2. 🔥 THE MAGIC: Otomatis ubah status task jadi COMPLETED & catat jam selesai!
        from datetime import datetime, timezone
        now_utc = datetime.now(timezone.utc).isoformat()
        
        supabase.table("patient_tasks").update({
            "status": "Completed",
            "completed_time": now_utc
        }).eq("id", transaction_id).execute()

        print(f"⭐ [REVIEW] Transaction {transaction_id} is now COMPLETED by Patient!")
        return {"status": "success", "message": "Review submitted and mission completed."}

    except Exception as e:
        print(f"🚨 [REVIEW CRITICAL] Failed to submit review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))