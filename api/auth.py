from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
import random, string, os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.schema import UserCreate, UserLogin, ForgetPassword, ResetPassword  # keep your Pydantic input models

auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# In-memory stores
@dataclass
class MemUser:
    id: int
    email: str
    hashed_password: str

@dataclass
class MemOTP:
    user_id: int
    otp_code: str
    expires_at: datetime

users_by_email: Dict[str, MemUser] = {}
users_by_id: Dict[int, MemUser] = {}
otps: Dict[str, MemOTP] = {}  # key by f"{user_id}:{otp_code}"
_next_user_id = 1

bearer_scheme = HTTPBearer(auto_error=False)

def _create_user(email: str, password: str) -> MemUser:
    global _next_user_id
    hashed_pw = pwd_context.hash(password)
    user = MemUser(id=_next_user_id, email=email, hashed_password=hashed_pw)
    users_by_email[email] = user
    users_by_id[user.id] = user
    _next_user_id += 1
    return user

def _get_user_by_email(email: str) -> Optional[MemUser]:
    return users_by_email.get(email)

def _store_otp(user_id: int, code: str, minutes: int = 5) -> MemOTP:
    otp = MemOTP(user_id=user_id, otp_code=code, expires_at=datetime.utcnow() + timedelta(minutes=minutes))
    otps[f"{user_id}:{code}"] = otp
    return otp

def _get_otp(user_id: int, code: str) -> Optional[MemOTP]:
    return otps.get(f"{user_id}:{code}")

def _delete_otp(user_id: int, code: str) -> None:
    otps.pop(f"{user_id}:{code}", None)

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session Timeout")

    user = _get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def create_jwt_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_otp(length: int = 6):
    return ''.join(random.choices(string.digits, k=length))

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate):
    if _get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    _create_user(user.email, user.password)
    return {"status": "success", "message": "Sign up successful"}

@auth_router.post("/login")
def login(user: UserLogin):
    db_user = _get_user_by_email(user.email)
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_jwt_token({"sub": db_user.email})
    return {"status": "success", "message": "Login successful", "access_token": token}

@auth_router.post("/forgot-password")
def forgot_password(req: ForgetPassword):
    db_user = _get_user_by_email(req.email)
    # Always return success to avoid user enumeration
    if not db_user:
        return {"status": "success", "message": "If the email exists, an OTP has been sent"}
    # Optionally clear existing OTPs for this user
    for key in list(otps.keys()):
        if key.startswith(f"{db_user.id}:"):
            otps.pop(key, None)
    code = generate_otp()
    _store_otp(db_user.id, code, minutes=5)
    print(f"OTP for {req.email}: {code}")  # replace with email/SMS sending in real apps
    return {"status": "success", "message": "OTP sent to your email address"}

@auth_router.post("/reset-password")
def reset_password(req: ResetPassword):
    db_user = _get_user_by_email(req.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_obj = _get_otp(db_user.id, req.otp_code)
    if not otp_obj or otp_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    db_user.hashed_password = pwd_context.hash(req.new_password)
    _delete_otp(db_user.id, req.otp_code)
    return {"status": "success", "message": "Password reset successful"}