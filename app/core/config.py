# File: app/core/config.py
import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Silicon Valley Standard: Centralized Application Settings management.
    Loads environment variables from a look-up file (.env) with strict Pydantic type validation.
    """
    
    # --- PROJECT CONFIGURATIONS ---
    PROJECT_NAME: str = "Homecare Command Center API"
    ENVIRONMENT: str = "development" # e.g., 'development', 'production', 'testing'
    
    # --- DATABASE CONFIGURATIONS (SUPABASE) ---
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # --- SECURITY & AUTH CONFIGURATIONS ---
    # Kunci brankas utama (Fernet Key)
    FIELD_ENCRYPTION_KEY: str
    
    # Path to Firebase Admin SDK json credential file
    FIREBASE_CREDENTIALS_PATH: str = "serviceAccountKey.json"
    
    # INI DIA YANG BARU: Kunci API Web Firebase untuk otentikasi REST API (Login)
    FIREBASE_WEB_API_KEY: str 
    
    # --- NOTIFICATION CREDENTIALS ---
    EMAIL_SENDER: str = ""
    EMAIL_PASSWORD: str = ""

    # --- REDIS CONFIGURATION ---
    # Default fallback for local development if not provided in .env
    REDIS_URL: str = "redis://localhost:6379/0" 

    # --- SENTRY ERROR TRACKING CONFIGURATION ---
    # Data Source Name (DSN) for Sentry integration. Leave empty to disable in local dev.
    SENTRY_DSN: str = ""

    # Automatically load from the .env file located at the project root folder
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore" # Ignores extra variables in .env that are not defined here
    )

    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, value: str) -> str:
        """Ensures the injected database endpoint is a valid URL structure."""
        if not value.startswith("https://") and not value.startswith("http://"):
            raise ValueError("Environment configuration error: SUPABASE_URL must be a valid HTTP/HTTPS endpoint.")
        return value

# Instantiate the global settings object to be imported across the application
settings = Settings()