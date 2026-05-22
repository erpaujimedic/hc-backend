# File: app/api/v1/endpoints/employees.py
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from typing import List

from app.db.supabase import supabase
from app.api.v1.endpoints.auth import require_admin

router = APIRouter()

class ApprovalResponse(BaseModel):
    message: str
    employee_id: str

@router.get("/", status_code=status.HTTP_200_OK)
async def get_employees():
    try:
        response = supabase.table("employees").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending", status_code=status.HTTP_200_OK)
async def get_pending_employees():
    try:
        response = supabase.table("employees").select("*").eq("is_active", False).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roster", status_code=status.HTTP_200_OK)
async def get_medical_roster(request: Request):
    """
    Retrieves the active field staff roster along with their medical positions
    for clean frontend conditional mapping.
    """
    await require_admin(request)
    try:
        # 🔥 CRITICAL UPDATE: We now select 'position' alongside full_name and branch
        response = supabase.table("employees") \
            .select("id, full_name, role, branch, position") \
            .eq("is_active", True) \
            .execute()
            
        return {
            "status": "success",
            "message": "Medical roster retrieved successfully",
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve medical roster: {str(e)}"
        )

@router.get("/{employee_id}", status_code=status.HTTP_200_OK)
async def get_employee_detail(employee_id: str):
    try:
        response = supabase.table("employees").select("*").eq("id", employee_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{employee_id}/approve", response_model=ApprovalResponse)
async def approve_employee(employee_id: str):
    try:
        response = supabase.table("employees").update({"is_active": True}).eq("id", employee_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee not found or already active.")
        return ApprovalResponse(message="Success! Employee account is now active.", employee_id=employee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))