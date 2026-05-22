# File: app/services/analytics_service.py
import io
import pandas as pd
from fastapi import HTTPException, status
from app.db.database import supabase

class AnalyticsService:
    """
    Service Layer khusus untuk menangani logika bisnis Dashboard & KPI.
    Tidak ada urusan dengan HTTP Request/Response di sini.
    """

    @staticmethod
    async def get_recent_transactions(limit: int = 100):
        try:
            # Tarik data asli dari Supabase
            response = supabase.table("transactions").select("*").order("id", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database query failed: {str(e)}"
            )

    @staticmethod
    async def get_kpi_summary():
        try:
            # Hitung menggunakan Supabase aggregate agar hemat RAM
            res_total = supabase.table("transactions").select("id", count="exact").execute()
            res_completed = supabase.table("transactions").select("id", count="exact").eq("visit_status", "Completed").execute()
            
            total_orders = res_total.count if res_total.count else 0
            completed_orders = res_completed.count if res_completed.count else 0
            active_orders = total_orders - completed_orders
            
            completion_rate = round((completed_orders / total_orders) * 100, 2) if total_orders > 0 else 0.0

            return {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "active_orders": active_orders,
                "completion_rate": completion_rate
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Failed to calculate KPI summary: {str(e)}"
            )

    @staticmethod
    async def export_transactions_to_excel():
        try:
            trx_res = supabase.table("transactions").select("*").execute()
            
            if not trx_res.data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transaction data available to export.")
                
            df = pd.DataFrame(trx_res.data)
            
            # Bersihkan data (contoh: hapus kolom timeline yang berbentuk JSON)
            if 'timeline' in df.columns:
                df = df.drop(columns=['timeline'])
                
            # Stream ke memory, jangan save file ke hardisk server
            stream = io.BytesIO()
            with pd.ExcelWriter(stream, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='All_Transactions')
                
            stream.seek(0)
            return stream
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Failed to generate Excel report: {str(e)}"
            )