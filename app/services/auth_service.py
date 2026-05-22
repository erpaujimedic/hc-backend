import httpx
from fastapi import HTTPException, status
from app.core.config import settings 

async def authenticate_user_with_firebase(email: str, password: str) -> dict:
    """
    Exchanges email and password for a Firebase ID token using REST API.
    Silicon Valley Standard: Uses asynchronous httpx client to prevent blocking the FastAPI event loop.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_WEB_API_KEY}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        # Menggunakan httpx.AsyncClient agar tidak memblokir event loop
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response_data = response.json()
            
    except httpx.RequestError as e:
        # Penanganan error jika server Firebase sedang down atau jaringan server kita bermasalah
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Network error: Failed to communicate with authentication server. Detail: {str(e)}"
        )
    
    if "error" in response_data:
        error_message = response_data["error"]["message"]
        if error_message in ["EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_EMAIL"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Authentication failed: {error_message}"
        )
        
    return response_data