# File: app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, 
    employees, 
    operations, 
    analytics, 
    system, 
    transactions,
    branches # 🔥 IMPORT BRANCHES ENDPOINT BARU KITA
)

# Initialize the main API router for version 1
api_router = APIRouter()

# Register all module endpoints with appropriate prefixes and OpenAPI tags
# Silicon Valley Standard: Strict separation of concerns across endpoint domains
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(employees.router, prefix="/employees", tags=["Manpower Management"])
api_router.include_router(operations.router, prefix="/ops", tags=["Operations Center"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transaction Management"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Dashboard & Analytics"])
api_router.include_router(system.router, prefix="/system", tags=["Configuration"])

# 🔥 NEW: BRANCHES MATRIX REGISTRATION
api_router.include_router(branches.router, prefix="/branches", tags=["Branch Management"])