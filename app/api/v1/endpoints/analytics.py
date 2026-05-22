# File: app/api/v1/endpoints/analytics.py
from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional
from app.db.supabase import supabase
from app.api.v1.endpoints.auth import require_admin

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    request: Request,
    branch: Optional[str] = Query(None, description="Filter by branch matrix"),
    month: Optional[str] = Query(None, description="Filter by operational month"),
    start_date: Optional[str] = Query(None, description="Filter by start date"),
    end_date: Optional[str] = Query(None, description="Filter by end date")
):
    """
    Dynamically calculate KPI summary directly from Supabase tables.
    Retrieves transaction metrics (Orders, SLA) and manpower statistics.
    Restricted to Admin / Supervisor roles.
    """
    # 1. Security Check: Ensure only authorized personnel can view metrics
    await require_admin(request)
    
    try:
        # =========================================================
        # 🟢 PART 1: TRANSACTION KPI METRICS (For the 4 Main Cards)
        # =========================================================
        txn_query = supabase.table("transactions").select("status")
        
        # Apply dynamic filters if provided by the frontend
        if branch:
            txn_query = txn_query.eq("branch_code", branch)
        if start_date:
            txn_query = txn_query.gte("created_at", start_date)
        if end_date:
            txn_query = txn_query.lte("created_at", end_date)
            
        txn_response = txn_query.execute()
        txn_data = txn_response.data or []
        
        total_orders = len(txn_data)
        
        # Calculate statuses (Case-insensitive matching to prevent data mismatch)
        completed_visits = sum(1 for t in txn_data if str(t.get("status")).lower() == "completed")
        cancelled_orders = sum(1 for t in txn_data if str(t.get("status")).lower() == "cancelled")
        
        # Calculate SLA Achievement
        valid_orders = total_orders - cancelled_orders
        sla_percentage = 0.0
        if valid_orders > 0:
            sla_percentage = round((completed_visits / valid_orders) * 100, 1)

        # =========================================================
        # 🔵 PART 2: MANPOWER & TASK METRICS (Your Original Code)
        # =========================================================
        try:
            nurses_res = supabase.table("employees").select("id").eq("role", "Staff Homecare").eq("is_active", True).execute()
            total_active_nurses = len(nurses_res.data or [])
            
            pending_res = supabase.table("employees").select("id").eq("is_active", False).execute()
            total_pending = len(pending_res.data or [])
            
            tasks_res = supabase.table("patient_tasks").select("id").eq("status", "ongoing").execute()
            total_ongoing = len(tasks_res.data or [])
        except Exception as inner_e:
            print(f"⚠️ [Analytics Warning] Failed to fetch secondary manpower stats: {str(inner_e)}")
            total_active_nurses = 0
            total_pending = 0
            total_ongoing = 0

        # =========================================================
        # 🚀 PART 3: RETURN UNIFIED PAYLOAD TO REACT
        # =========================================================
        return {
            # Core Dashboard KPIs
            "totalOrders": total_orders,
            "completedVisits": completed_visits,
            "slaAchievement": f"{sla_percentage}%",
            "cancelledOrders": cancelled_orders,
            
            # Secondary Manpower KPIs
            "activeNurses": total_active_nurses,
            "ongoingTreatments": total_ongoing,
            "pendingApprovals": total_pending
        }

    except Exception as e:
        print(f"🚨 [Analytics CRITICAL] Failed to compute dashboard summary: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An internal server error occurred while calculating dashboard metrics."
        )