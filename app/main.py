# File: app/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

# Firebase Authentication Engine
import firebase_admin
from firebase_admin import credentials

# Cache Engine Initialization
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Configuration & Master Router
from app.core.config import settings
from app.api.v1.router import api_router
from app.api.v1.endpoints import configs # 👈 Import lu udah bener di sini

# ==========================================
# FIREBASE ENGINE INITIALIZATION
# ==========================================
# Mencegah Firebase di-initialize 2 kali (yang bikin error)
if not firebase_admin._apps:
    try:
        # File JSON ditaruh di root folder (sejajar dengan folder app)
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        print("✅ [Firebase Engine] Successfully Initialized!")
    except Exception as e:
        print(f"🚨 [Firebase CRITICAL] Failed to start: {str(e)}")

# ==========================================
# SENTRY ERROR TRACKING INITIALIZATION
# ==========================================
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )
    print("✅ Sentry Error Tracking Radar Activated.")

# ==========================================
# LIFESPAN EVENTS (STARTUP & SHUTDOWN)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Redis Cache Engine
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="homs-cache")
    print("✅ Redis Cache Engine Initialized.")
    
    yield # Application runs here
    
    # Shutdown sequence (Close connections gracefully if needed)

# ==========================================
# APP INITIALIZATION
# ==========================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc"      # ReDoc UI
)

# CORS Middleware Setup (Enable Cross-Origin for Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# GLOBAL EXCEPTION HANDLER
# ==========================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches all unhandled exceptions to prevent sensitive data leaks."""
    print(f"🚨 [CRITICAL UNHANDLED ERROR] {request.method} {request.url} - Error: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected internal server error occurred. Our engineering team has been notified.",
            "error_type": "UnhandledSystemException"
        }
    )

# ==========================================
# ROOT ENDPOINT (HEALTH CHECK)
# ==========================================
@app.get("/", tags=["System Health"])
def system_health_check():
    """Root endpoint to verify server operational status."""
    return {
        "status": "online",
        "message": "HOMS: Homecare Management System API is fully operational.",
        "environment": settings.ENVIRONMENT
    }

# ==========================================
# ROUTER REGISTRATION (The Silicon Valley Way)
# ==========================================
# Registers ALL v1 endpoints under a single master router
app.include_router(api_router, prefix="/api/v1")

# 🔥 FIX: COLOKIN KABEL API CONFIGS KESINI BIAR 404 ILANG!
app.include_router(configs.router, prefix="/api/v1/configs", tags=["System Configs"])