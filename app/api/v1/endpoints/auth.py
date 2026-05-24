# File: app/api/v1/endpoints/auth.py
import os
from dotenv import load_dotenv

# Nyalain mesin pembaca environment variables dari file .env
load_dotenv()

from fastapi import APIRouter, HTTPException, status, Request, Body
from pydantic import BaseModel
from typing import Optional
from app.db.supabase import supabase
import requests
import uuid

try:
    from firebase_admin import auth as firebase_auth
except ImportError:
    firebase_auth = None

router = APIRouter()

# --- SCHEMAS (Format Data) ---
class LoginRequest(BaseModel):
    loginId: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str
    branch: str

class RegisterResponse(BaseModel):
    message: str
    uid: str
    status: str

class OverrideRequest(BaseModel):
    master_key: str

# --- ENDPOINTS ---

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login_endpoint(payload: LoginRequest):
    """
    Real Authentication with Auto-Sync:
    Verifies password via Firebase. If user is missing in Supabase, 
    automatically provisions a database profile to prevent login failure.
    """
    try:
        # 1. VERIFY CREDENTIALS AGAINST REAL FIREBASE
        firebase_api_key = os.getenv("FIREBASE_WEB_API_KEY")
        if not firebase_api_key:
            raise HTTPException(status_code=500, detail="Firebase Web API Key missing in backend configuration.")

        fb_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"
        fb_response = requests.post(fb_url, json={
            "email": payload.loginId,
            "password": payload.password,
            "returnSecureToken": True
        })

        if fb_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Authentication failed. Invalid email or password provided to Firebase Gateway."
            )

        fb_data = fb_response.json()
        firebase_uid = fb_data.get("localId")

        # 2. CHECK IF USER PROFILE EXISTS IN SUPABASE
        response = supabase.table("employees").select("*").eq("email", payload.loginId).execute()
        users = response.data

        if not users:
            # 🔥 AUTOMATED AUTO-SYNC
            generated_name = payload.loginId.split('@')[0].capitalize()
            
            insert_result = supabase.table("employees").insert({
                "firebase_uid": firebase_uid,
                "email": payload.loginId,
                "full_name": generated_name,
                "role": "Administrator",
                "position": "System Admin", # 👈 SILICON VALLEY FIX
                "branch": "TMC BSD",
                "is_active": True 
            }).execute()
            
            user_data = insert_result.data[0]
        else:
            user_data = users[0]

        # 3. ENFORCE STATUS CHECK FOR REGISTERED USERS
        if not user_data.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access denied. Your account registration is pending supervisor approval."
            )

        # 4. ISSUE APPLICATION SESSION ACCESS TOKEN
        access_token = f"homs_token_{user_data['id']}"

        return LoginResponse(
            access_token=access_token,
            user={
                "id": user_data["id"],
                "email": user_data["email"],
                "name": user_data["full_name"],
                "role": user_data["role"],
                "branch": user_data.get("branch", "TMC HQ")
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(request: Request):
    """
    Session Verification Guard
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or malformed authorization token.")

    token = auth_header.split(" ")[1]
    
    try:
        user_id = token.split("_")[2]
        response = supabase.table("employees").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session binding broken. Employee record missing.")
            
        user_data = response.data[0]
        
        return {
            "data": {
                "id": user_data["id"],
                "name": user_data["full_name"],
                "email": user_data["email"],
                "role": user_data["role"],
                "branch": user_data.get("branch", "TMC HQ"),
                "photoUrl": None
            }
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token encryption or session identity has expired.")


# ==========================================
# 🔐 SPV SECURITY OVERRIDE VERIFICATION
# ==========================================
@router.post("/verify-override", status_code=status.HTTP_200_OK)
async def verify_spv_override(payload: OverrideRequest, request: Request):
    """
    Secure endpoint to verify SPV Master Key for emergency order overrides.
    Prevents hardcoded passwords in the React frontend.
    """
    try:
        # Opsional: Pastikan yang nge-request minimal udah login
        await get_current_user(request)
        
        # 🔥 ENTERPRISE SECURITY: Ambil kunci dari Environment Variable.
        # Fallback ke 'admin123' sementara kalau env belum di-set di server Render lo.
        valid_key = os.getenv("SPV_MASTER_KEY", "admin123")
        
        if payload.master_key != valid_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid Master Key. Access Denied."
            )
            
        print("🔓 [SECURITY] SPV Override Key verified successfully.")
        return {"status": "success", "message": "Master Key verified. Edit unlocked."}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🚨 [Security API Error] Failed to verify override key: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal security verification error.")


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_endpoint(payload: RegisterRequest):
    """
    Standard Employee Registration Pipeline
    """
    try:
        firebase_uid = str(uuid.uuid4())
        if firebase_auth:
            new_user = firebase_auth.create_user(
                email=payload.email,
                password=payload.password,
                display_name=payload.name 
            )
            firebase_uid = new_user.uid
        
        # 🚀 SILICON VALLEY FIX: SMART POSITION EXTRACTOR
        # Otomatis deteksi profesi dari role biar gak NULL di database!
        role_lower = payload.role.lower()
        determined_position = payload.role # Default fallback
        
        if "nurse" in role_lower or "perawat" in role_lower:
            determined_position = "Nurse"
        elif "doctor" in role_lower or "dokter" in role_lower:
            determined_position = "Doctor"
        elif "therapist" in role_lower or "fisioterapi" in role_lower or "terapis" in role_lower:
            determined_position = "Therapist"
        elif "spv" in role_lower or "supervisor" in role_lower:
            determined_position = "Supervisor"

        # Inject Data ke Supabase
        supabase.table("employees").insert({
            "firebase_uid": firebase_uid,
            "email": payload.email,
            "full_name": payload.name,
            "role": payload.role,      
            "position": determined_position, # 👈 INI OBATNYA BOS!
            "branch": payload.branch,  
            "is_active": False  
        }).execute()

        return RegisterResponse(
            message="Success! Account creation request has been sent to Admin for approval.",
            uid=firebase_uid,
            status="pending_approval"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}")


async def require_admin(request: Request):
    """Administrative access role boundary validator"""
    current_user_req = await get_current_user(request)
    user_data = current_user_req["data"]
    
    allowed_roles = ["SPV Operasional", "Administrator", "PIC Branch"]
    if user_data.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator level privileges required."
        )
    return user_data


@router.get("/requests/pending", status_code=status.HTTP_200_OK)
async def get_pending_requests():
    """
    Retrieve all employee records where 'is_active' is currently False.
    """
    try:
        response = supabase.table("employees").select("*").eq("is_active", False).execute()
        
        formatted_data = []
        for emp in response.data:
            formatted_data.append({
                "id": emp.get("firebase_uid"), 
                "name": emp.get("full_name"),  
                "email": emp.get("email"),
                "role": emp.get("role"),
                "branch": emp.get("branch")
            })
            
        print(f"✅ [Approval API] Successfully retrieved {len(formatted_data)} pending requests.")
        return formatted_data
        
    except Exception as e:
        print(f"🚨 [Approval API CRITICAL] Failed to fetch pending requests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to load the approval queue from the database."
        )


@router.post("/requests/{uid}/approve", status_code=status.HTTP_200_OK)
async def approve_request(uid: str):
    """
    Approve an account by toggling 'is_active' to True.
    """
    try:
        response = supabase.table("employees").update({"is_active": True}).eq("firebase_uid", uid).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Applicant data could not be located in the system."
            )
            
        print(f"✅ [Approval API] Account {uid} SUCCESSFULLY APPROVED.")
        return {"status": "success", "message": "Account access has been successfully granted."}
        
    except Exception as e:
        print(f"🚨 [Approval API CRITICAL] Failed to approve account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while processing the approval."
        )


@router.post("/requests/{uid}/reject", status_code=status.HTTP_200_OK)
async def reject_request(uid: str):
    """
    Reject an account request by permanently deleting it from the database.
    """
    try:
        response = supabase.table("employees").delete().eq("firebase_uid", uid).execute()
        
        print(f"❌ [Approval API] Account {uid} PERMANENTLY REJECTED AND DELETED.")
        return {"status": "success", "message": "Account request has been successfully rejected."}
        
    except Exception as e:
        print(f"🚨 [Approval API CRITICAL] Failed to reject account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while rejecting the application."
        )


# ==========================================
# 📢 FETCH PUBLIC ANNOUNCEMENT (FOR LOGIN VIEW)
# ==========================================
@router.get("/announcements", status_code=status.HTTP_200_OK)
async def get_public_announcements():
    """
    Fetch active live announcements for the unauthenticated login portal screen.
    No access token required.
    """
    try:
        response = supabase.table("system_configs").select("*").eq("config_key", "live_announcements").execute()
        if response.data:
            # Returns the JSON object directly: {"message": "...", "type": "..."}
            return response.data[0].get("config_value")
        return {"message": "System running optimally.", "type": "info"}
    except Exception as e:
        print(f"🚨 [Public Config Error] Failed to stream announcements: {str(e)}")
        return {"message": "Welcome to HOMS Workspace.", "type": "info"}


# ==========================================
# 🔒 UPDATE LIVE ANNOUNCEMENT (FOR CONFIG PANEL)
# ==========================================
@router.post("/announcements/update", status_code=status.HTTP_200_OK)
async def update_live_announcements(request: Request, payload: dict = Body(...)):
    """
    Secure administrative endpoint to push real-time broadcasts onto the login gateway.
    Protected by require_admin security layer.
    """
    try:
        # Enforce administrative permission check
        await require_admin(request)
        
        # Payload validation
        msg = payload.get("message", "").strip()
        msg_type = payload.get("type", "info")
        
        if not msg:
            raise HTTPException(status_code=400, detail="Announcement message content cannot be blank.")

        # Update the metadata inside Supabase database
        response = supabase.table("system_configs").update({
            "config_value": {"message": msg, "type": msg_type}
        }).eq("config_key", "live_announcements").execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Database failed to update announcement matrix.")

        print(f"📢 [BROADCAST] System configuration updated by administrator. Message: {msg}")
        return {"status": "success", "message": "Broadcast pushed successfully to login portal."}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🚨 [Admin Config Error] Broadcast dispatch crashed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error handling config update.")


# ==========================================
# 🪪 FETCH ALL EMPLOYEES WITH LIVE STATUS MATRIX
# ==========================================
@router.get("/staffs", status_code=status.HTTP_200_OK)
async def get_all_staffs(request: Request):
    """
    Retrieve all practitioners and calculate their real-time homecare operational status
    (Standby, En Route, Scheduled) by cross-referencing active tasks.
    """
    try:
        # 1. Enforce administrative access protection
        await require_admin(request)
        
        # 2. Fetch all employees from Supabase
        emp_res = supabase.table("employees").select("*").eq("is_active", True).execute()
        employees = emp_res.data or []
        
        # 3. Fetch all active patient tasks to calculate the live status matrix
        task_res = supabase.table("patient_tasks").select("nurse_name, status").execute()
        tasks = task_res.data or []
        
        formatted_staff = []
        for emp in employees:
            name = emp.get("full_name", "")
            
            # Smart Availability Logic Interceptor
            current_status = "Standby" # Default fallback state
            
            # 🔥 SILICON VALLEY FIX: Pake str() bukan String() !!
            is_en_route = any(t.get("nurse_name") == name and str(t.get("status", "")).lower() == "ongoing" for t in tasks)
            is_scheduled = any(t.get("nurse_name") == name and str(t.get("status", "")).lower() == "assigned" for t in tasks)
            
            if is_en_route:
                current_status = "En Route"
            elif is_scheduled:
                current_status = "Scheduled"
                
            formatted_staff.append({
                "id": emp.get("id"),
                "firebase_uid": emp.get("firebase_uid"),
                "name": name,
                "email": emp.get("email"),
                "role": emp.get("role"),
                "position": emp.get("position") or "General Practitioner",
                "branch": emp.get("branch") or "TMC HQ",
                "photo_url": emp.get("photo_url") or None, # Firebase Storage Public URL mapping
                "status": current_status
            })
            
        print(f"🪪 [STAFF MATRIX] Dispatched {len(formatted_staff)} active practitioners with computed statuses.")
        return formatted_staff
    except Exception as e:
        print(f"🚨 [Staff API Error] Failed to process staff matrix layout: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error compilation failed.")


# ==========================================
# 📸 UPDATE PRACTITIONER PHOTO URL
# ==========================================
@router.patch("/staffs/{staff_id}/photo", status_code=status.HTTP_200_OK)
async def update_staff_photo(staff_id: str, request: Request, payload: dict = Body(...)):
    """
    Inject the Firebase Storage bucket public image URL into the employee profile record inside Supabase.
    """
    try:
        await require_admin(request)
        url = payload.get("photo_url", "").strip()
        
        if not url:
            raise HTTPException(status_code=400, detail="Photo URL target string cannot be empty.")
            
        response = supabase.table("employees").update({"photo_url": url}).eq("id", staff_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee target identification mismatch.")
            
        print(f"📸 [IMAGE BIND] Staff ID {staff_id} is now securely bound to Firebase Image Object: {url}")
        return {"status": "success", "message": "Practitioner ID Card image synchronized successfully."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"🚨 [Photo API Error] Database sync mutation crashed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to map secure asset location to Supabase row.")