# File: app/services/employee_service.py
import asyncio
from fastapi import HTTPException, status
from app.db.database import supabase
from app.core.exceptions import ResourceNotFoundError

class EmployeeService:
    """Business logic for Manpower / Employee management."""

    @staticmethod
    async def fetch_all_employees():
        response = await asyncio.to_thread(
            lambda: supabase.table("employees").select("*").execute()
        )
        return response.data if response.data else []

    @staticmethod
    async def fetch_employee_by_id(employee_id: str):
        response = await asyncio.to_thread(
            lambda: supabase.table("employees").select("*").eq("id", employee_id).execute()
        )
        if not response.data:
            raise ResourceNotFoundError(resource_name=f"Employee '{employee_id}'")
        return response.data[0]