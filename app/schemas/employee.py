# File: app/schemas/employee.py
import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

# --- 1. CORE EMPLOYEE SCHEMAS ---
class EmployeeBase(BaseModel):
    full_name: str = Field(..., description="The full legal name of the homecare employee/nurse.")
    email: EmailStr = Field(..., description="Professional email address.")
    phone_number: str = Field(..., description="Contact number for operational dispatch.")
    role: str = Field(..., description="Job classification (e.g., 'Admin', 'Nurse', 'Branch Staff').")
    is_active: bool = Field(default=True, description="Active status flag.")

class EmployeeCreate(EmployeeBase):
    firebase_uid: str = Field(..., description="Firebase UID upon registration.")

class EmployeeResponse(EmployeeBase):
    id: str = Field(..., description="Unique UUID assigned by Supabase.")
    created_at: datetime = Field(..., description="Record creation timestamp.")
    model_config = {"from_attributes": True}

# --- 2. UTILITY SCHEMAS ---
class BarcodeData(BaseModel):
    """Payload schema for ID card barcode scanning via Base64 image."""
    image_base64: str = Field(..., description="Base64 encoded string.", min_length=50)

    @field_validator('image_base64')
    @classmethod
    def validate_base64_format(cls, value: str) -> str:
        clean_value = value.split(',')[-1] if ',' in value else value
        if not re.match(r'^[A-Za-z0-9+/]+={0,2}$', clean_value):
            raise ValueError("Invalid Base64 format.")
        return value