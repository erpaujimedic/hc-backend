# File: app/schemas/transaction.py
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

# ==========================================
# 1. BASE SCHEMA (Shared Attributes)
# ==========================================
class TransactionBase(BaseModel):
    # Original Financial/Basic Fields
    patient_id: Optional[str] = Field(None, description="Linked Patient ID")
    amount: Optional[float] = Field(0.0, description="Total transaction cost")
    description: Optional[str] = Field(None, description="Additional notes")

    # Operational & Assignment Fields (Matching Supabase 'patient_tasks')
    patient_name: Optional[str] = Field(None, description="Name of the patient")
    branch: Optional[str] = Field(None, description="Branch code (e.g., T01-BSD)")
    phone: Optional[str] = Field(None, description="Patient contact number")
    service: Optional[str] = Field(None, description="Medical service requested")
    
    # 🔥 NEW: Gerbang untuk B2B Partner / Order Source
    source: Optional[str] = Field(None, description="Order source like Halodoc, Mobile JKN, Internal")
    
    schedule_time: Optional[str] = Field(None, description="Time of visit (e.g., 22:30)")
    schedule_date: Optional[date] = Field(None, description="Date of visit")
    nurse_name: Optional[str] = Field(None, description="Assigned field agent/nurse")

    # Target Coordinates
    patient_lat: Optional[float] = Field(None, description="Target Latitude")
    patient_lng: Optional[float] = Field(None, description="Target Longitude")

class TransactionCreate(TransactionBase):
    """Schema for creating a new task/transaction from the HQ Dashboard"""
    patient_name: str = Field(..., description="Patient name is mandatory for creation")
    service: str = Field(..., description="Service type is mandatory")

# ==========================================
# 2. UPDATE SCHEMA (Crucial for Agent App & Admin Edit)
# ==========================================
class TransactionUpdate(BaseModel):
    """Schema strictly used for PATCH requests from the Agent Dashboard & Admin Edit"""
    status: Optional[str] = Field(None, description="Current protocol status (Scheduled, Ongoing, Arrived, Completed)")
    nurse_name: Optional[str] = Field(None, description="Used when agent claims a mission")
    
    # 🔥 NEW: Biar Admin bisa ngedit sumber order (Halodoc -> Internal, dll)
    source: Optional[str] = Field(None, description="Order source like Halodoc, Mobile JKN, Internal")
    
    patient_name: Optional[str] = Field(None, description="Name of the patient")
    phone: Optional[str] = Field(None, description="Patient contact number")
    branch: Optional[str] = Field(None, description="Branch code")
    service: Optional[str] = Field(None, description="Medical service requested")
    schedule_time: Optional[str] = Field(None, description="Time of visit")
    
    # Telemetry & Timestamp Updates
    current_lat: Optional[float] = Field(None, description="Agent's live latitude")
    current_lng: Optional[float] = Field(None, description="Agent's live longitude")
    en_route_time: Optional[datetime] = Field(None, description="Timestamp when departure initiated")
    arrived_time: Optional[datetime] = Field(None, description="Timestamp when agent arrived")
    completed_time: Optional[datetime] = Field(None, description="Timestamp when mission was completed")
    
    # Pre-Departure Audit Logs
    prep_photo: Optional[str] = Field(None, description="Base64 or URL of the medical kit photo")
    checklist_completed: Optional[bool] = Field(None, description="True if mandatory checklist is cleared")

    # 🔥 NEW: Emergency Override Flags
    is_manual_close: Optional[bool] = Field(None, description="Flag for emergency manual close")
    manual_close_reason: Optional[str] = Field(None, description="Reason for manual closing")

# ==========================================
# 3. RESPONSE SCHEMA (Sent back to Frontend)
# ==========================================
class TransactionResponse(TransactionBase):
    """Schema for returning data back to the Frontend apps"""
    id: str
    status: str = Field(default="Scheduled")
    
    # Include Telemetry and Audit in response so UI can react
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    en_route_time: Optional[datetime] = None
    arrived_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    prep_photo: Optional[str] = None
    checklist_completed: Optional[bool] = False
    
    # 🔥 NEW: Emergency Override Flags
    is_manual_close: Optional[bool] = False
    manual_close_reason: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True