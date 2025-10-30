from datetime import datetime
import uuid
from pydantic import BaseModel, Field, constr
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]

class ForgetPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    otp_code: str
    email: str
    new_password: str

# product schemas
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image_path: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_path: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_path: Optional[str] = None
    created_at: datetime
    user_id: int