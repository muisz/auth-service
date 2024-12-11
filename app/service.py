import bcrypt
import jwt
import os
import requests
from datetime import datetime, timedelta
from typing import Union

from app.repository import AuthRepository
from app.schema import AuthRegister, Token, OTPRequest
from app.models import Auth
from app.exception import ClientError


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository
    
    def register(self, auth: AuthRegister) -> Auth:
        email = auth.email.lower()
        if self.is_email_exist(email):
            raise ClientError("email already exist")

        password = PasswordHasherService.hash(auth.password)
        new_auth = Auth(
            name=auth.name,
            email=email,
            password=password,
            is_active=False,
        )
        return self.repository.create(new_auth)
    
    def is_email_exist(self, email: str) -> bool:
        auth = self.repository.get_by_email(email)
        return auth is not None
    
    def authenticate(self, email: str, password: str):
        auth = self.repository.get_by_email(email.lower())
        if auth is None or not PasswordHasherService.is_valid(password, auth.password):
            raise ClientError('account not found')
        if not auth.is_active:
            raise ClientError('inactive account')
        return auth
    
    def verify(self, auth: Auth):
        auth.is_active = True
        self.repository.update(auth)

    def get_auth_by_id(self, id: int) -> Union[Auth, None]:
        return self.repository.get_by_id(id)

class PasswordHasherService:
    @staticmethod
    def hash(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    @staticmethod
    def is_valid(password: str, hash: str):
        return bcrypt.checkpw(password.encode(), hash.encode())

class Jwt:
    def __init__(self):
        self.key = os.environ.get('JWT_KEY')
        self.refresh_key = self.key + "-refresh"
        self.algorithm = "HS256"
    
    def create_token_pair(self, payload: dict) -> Token:
        access = self.create_access_token(payload)
        refresh = self.create_refresh_token(payload)
        return Token(access=access, refresh=refresh)

    def create_access_token(self, payload: dict):
        now = datetime.now()
        expired_at = now + timedelta(hours=1)
        payload['exp'] = expired_at
        token = jwt.encode(payload, self.key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, payload: dict):
        now = datetime.now()
        expired_at = now + timedelta(hours=12)
        payload['exp'] = expired_at
        token = jwt.encode(payload, self.refresh_key, algorithm=self.algorithm)
        return token
    
    def refresh(self, token: str) -> Token:
        try:
            payload = jwt.decode(token, self.refresh_key, algorithms=[self.algorithm])
            return self.create_token_pair(payload)
        except Exception:
            raise ClientError("Invalid token")
    
    def verify(self, token: str) -> Token:
        try:
            jwt.decode(token, self.key, algorithms=[self.algorithm])
            return True
        except Exception:
            return False


class OTPServiceBase:
    def check(self, otp: OTPRequest) -> bool:
        raise NotImplementedError()
    
    def invalidate(self, otp: OTPRequest):
        raise NotImplementedError()


class OTPService(OTPServiceBase):
    def __init__(self):
        self.host = os.environ.get('OTP_SERVICE')
    
    def check(self, otp: OTPRequest) -> bool:
        url = f'{self.host}/check'
        payload = {'code': otp.code, 'session_code': otp.session_code}
        response = requests.post(url, json=payload)
        return response.status_code == 200 and response.json().get('valid') is True
    
    def invalidate(self, otp: OTPRequest):
        url = f'{self.host}/invalidate'
        payload = {'code': otp.code, 'session_code': otp.session_code}
        requests.post(url, json=payload)
