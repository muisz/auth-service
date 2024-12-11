import environ
from fastapi import FastAPI, Depends, status, Response
from typing import Annotated, Any

from app.dependencies import get_database_connection
from app.schema import (
    AuthRegister,
    AuthSignin,
    ErrorResponse,
    VerifyTokenRequest,
    TokenValidationResponse,
    VerifyAccount,
    OTPRequest,
)
from app.repository import DbAuthRepository
from app.service import AuthService, Jwt, OTPService
from app.exception import ClientError

environ.Env()
environ.Env.read_env('.env')

app = FastAPI()

DbDep = Annotated[Any, Depends(get_database_connection)]

@app.post('/signup', status_code=status.HTTP_201_CREATED)
def signup(db: DbDep, payload: AuthRegister, response: Response):
    try:
        repository = DbAuthRepository(db)
        service = AuthService(repository)
        service.register(payload)
        return

    except ClientError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(message=str(error))

@app.post('/signin')
def signin(db: DbDep, payload: AuthSignin, response: Response):
    try:
        repository = DbAuthRepository(db)
        service = AuthService(repository)
        auth = service.authenticate(payload.email, payload.password)
        
        jwt = Jwt()
        token_payload = {'id': auth.id}
        token = jwt.create_token_pair(token_payload)
        return token

    except ClientError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(message=str(error))

@app.post('/token/verify')
def verify_token(payload: VerifyTokenRequest):
    jwt = Jwt()
    return TokenValidationResponse(valid=jwt.verify(payload.token))

@app.post('/token/refresh')
def refresh_token(payload: VerifyTokenRequest, response: Response):
    try:
        jwt = Jwt()
        new_token = jwt.refresh(payload.token)
        return new_token
    
    except ClientError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(message=str(error))

@app.post('/verify')
def verify(db: DbDep, payload: VerifyAccount, response: Response):
    try:
        repository = DbAuthRepository(db)
        auth_service = AuthService(repository)
        otp_service = OTPService()

        auth = auth_service.get_auth_by_id(payload.id)
        if auth is None:
            raise ClientError('account not found')
        if auth.is_active:
            raise ClientError('account is already activated')
        otp = OTPRequest(code=payload.code, session_code=payload.session_code)
        if not otp_service.check(otp):
            raise ClientError('invalid OTP')
        
        auth_service.verify(auth)
        otp_service.invalidate(otp)
        return

    except ClientError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(message=str(error))
