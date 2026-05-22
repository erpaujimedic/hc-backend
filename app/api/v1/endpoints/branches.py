# File: app/api/v1/endpoints/branches.py
from fastapi import APIRouter, HTTPException
from app.db.supabase import supabase

router = APIRouter()

@router.get("")
async def get_all_branches():
    """
    Fetch all active branches from the Supabase database.
    Sorted automatically by branch_code (T01, T02, ...) for frontend matrix filters.
    """
    try:
        # 🔥 SILICON VALLEY FIX: Added .order("branch_code") to sort alphanumeric codes ascendingly
        response = supabase.table("branches").select("*").order("branch_code").execute()
        
        # Return an empty list if no data is found to prevent frontend mapping errors
        if not response.data:
            print("⚠️ [Branches API] No branch records found in the database.")
            return []
            
        print(f"✅ [Branches API] Successfully fetched and sorted {len(response.data)} branch records.")
        return response.data
        
    except Exception as e:
        print(f"🚨 [Supabase CRITICAL] Failed to fetch branch records: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve branch matrices from the database. Please verify the database connection."
        )