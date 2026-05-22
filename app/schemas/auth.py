from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    loginId: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class RegisterResponse(BaseModel):
    message: str
    uid: str
    status: str