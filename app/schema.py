from pydantic import BaseModel


class AuthRegister(BaseModel):
    name: str
    email: str
    password: str

class AuthSignin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access: str
    refresh: str

class ErrorResponse(BaseModel):
    message: str

class VerifyTokenRequest(BaseModel):
    token: str

class TokenValidationResponse(BaseModel):
    valid: bool

class OTPRequest(BaseModel):
    code: str
    session_code: str

class VerifyAccount(BaseModel):
    id: int
    code: str
    session_code: str
