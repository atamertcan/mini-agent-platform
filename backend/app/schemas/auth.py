from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    tenant_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
