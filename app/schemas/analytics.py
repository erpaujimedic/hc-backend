# File: app/schemas/analytics.py
from pydantic import BaseModel

class KPISummaryResponse(BaseModel):
    total_orders: int
    completed_orders: int
    active_orders: int
    completion_rate: float