# File: app/schemas/ops.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from app.utils.formatter import standardize_phone_number

# --- 1. TRANSACTIONS SCHEMAS ---
class TransactionCreate(BaseModel):
    patient_id: str
    nurse_id: str
    service_type: str
    scheduled_time: datetime
    
class TransactionResponse(BaseModel):
    id: str
    patient: str
    service: str
    order_status: str
    visit_status: str
    branch: str
    model_config = {"extra": "allow"}

# --- 2. DISPATCH / ORDER SCHEMAS ---
class OrderRequest(BaseModel):
    """Core payload schema for ingesting new Homecare service orders."""
    patient: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(...)
    service: str = Field(..., min_length=3)
    time: datetime = Field(...)
    address: str = Field(..., min_length=10)
    manual_branch: str = Field(default="AUTO")
    patient_lat: float = Field(..., ge=-90.0, le=90.0)
    patient_lon: float = Field(..., ge=-180.0, le=180.0)

    @field_validator("phone")
    @classmethod
    def validate_and_format_phone(cls, value: str) -> str:
        return standardize_phone_number(value, default_region="ID")

# --- 3. FIELD OPERATIONS SCHEMAS ---
class VisitStatusUpdate(BaseModel):
    status: str = Field(..., min_length=2)
    notes: Optional[str] = Field(None, max_length=500)

class EmergencyAlert(BaseModel):
    visit_id: str = Field(...)
    nurse_id: str = Field(...)
    emergency_type: str = Field(...)
    location_lat: float = Field(..., ge=-90.0, le=90.0)
    location_lon: float = Field(..., ge=-180.0, le=180.0)

class StaffLocationUpdate(BaseModel):
    staff_id: str = Field(...)
    role: str = Field(...)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)