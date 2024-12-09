from pydantic import BaseModel
from typing import Union
from datetime import datetime


class Auth(BaseModel):
    id: Union[int, None] = None
    name: str
    email: str
    password: str
    is_active: bool
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
