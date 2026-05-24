# File: app/main.py
import os
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
import json

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
from app.api.v1.endpoints import configs

# ==========================================
# FIREBASE ENGINE INITIALIZATION
# ==========================================
if not firebase_admin._apps:
    try:
        firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if firebase_json:
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            print("☁️ [Firebase Engine] Initializing with Environment Variable...")
        else:
            cred = credentials.Certificate("serviceAccountKey.json")
            print("💻 [Firebase Engine] Initializing with local JSON file...")
            
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
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="homs-cache")
    print("✅ Redis Cache Engine Initialized.")
    yield 

# ==========================================
# APP INITIALIZATION
# ==========================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",      
    redoc_url="/redoc"      
)

# ==========================================
# 🛡️ ENTERPRISE CORS CONFIGURATION
# ==========================================
# Dilarang pakai ["*"] jika allow_credentials=True. Harus explicit!
ALLOWED_ORIGINS = [
    "http://localhost:5173",          # Local Development
    "http://127.0.0.1:5173",          # Local Development (Fallback)
    "https://tmchcsystem.web.app",    # Production Firebase
    "https://tmchcsystem.firebaseapp.com" # Production Firebase Alternate
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua method (GET, POST, PATCH, dll)
    allow_headers=["*"],  # Izinkan semua header (Authorization, Content-Type, dll)
    expose_headers=["*"]  # Penting agar frontend bisa baca custom response headers
)

# ==========================================
# 🚨 GLOBAL EXCEPTION HANDLER (DEBUG MODE ENHANCED)
# ==========================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Menangkap error 500 dan mencegah crash, 
    sekaligus mengirim traceback ke log Render biar gampang di-debug.
    """
    print(f"🔥 [CRITICAL 500] Method: {request.method} | URL: {request.url}")
    print("🛑 Traceback Detail:")
    traceback.print_exc() # Print full error ke log Render bos!
    
    # Render error feedback ke Frontend
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal Server Error occurred. Check Backend Logs (Render).",
            "detail": str(exc), # Kirim pesan aslinya biar frontend tau
            "error_type": type(exc).__name__
        }
    )

# ==========================================
# ROOT ENDPOINT (HEALTH CHECK)
# ==========================================
@app.get("/", tags=["System Health"])
def system_health_check():
    return {
        "status": "online",
        "message": "HOMS: Homecare Management System API is fully operational.",
        "environment": settings.ENVIRONMENT,
        "cors_origins": ALLOWED_ORIGINS
    }

# ==========================================
# ROUTER REGISTRATION
# ==========================================
app.include_router(api_router, prefix="/api/v1")
app.include_router(configs.router, prefix="/api/v1/configs", tags=["System Configs"])