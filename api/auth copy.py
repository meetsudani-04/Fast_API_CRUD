from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import random
import string
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.database import get_db
from db.models import User, OTP
from db.schema import UserCreate, UserLogin, ForgetPassword, ResetPassword

auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "change_this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session Timeout"
        )

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def create_jwt_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_otp(length: int = 6):
    return ''.join(random.choices(string.digits, k=length))

@auth_router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pw = pwd_context.hash(user.password)
    new_user = User(
        email=user.email, 
        hashed_password=hashed_pw
    )
    db.add(new_user)    
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "Sign up successful"}

@auth_router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(email=user.email).first()

    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):

        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_jwt_token({"sub": db_user.email})
    return {"status": "success", "message": "Login successful", "access_token": token}

@auth_router.post("/forgot-password")
def forgot_password(req: ForgetPassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(email=req.email).first()
    if not db_user:
        return {"status": "success", "message": "If the email exists, an OTP has been sent"}
    code = generate_otp()
    otp = OTP(user_id=db_user.id, otp_code=code, expires_at=datetime.utcnow() + timedelta(minutes=5))
    db.add(otp)
    db.commit()
    # Place your email-sending logic here (for demo purposes, we'll just print)
    print(f"OTP for {req.email}: {code}")
    return {"status": "success", "message": "OTP sent to your email address"}

@auth_router.post("/reset-password")
def reset_password(req: ResetPassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(email=req.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_obj = db.query(OTP).filter_by(user_id=db_user.id, otp_code=req.otp_code).first()
    if not otp_obj or otp_obj.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    db_user.hashed_password = pwd_context.hash(req.new_password)
    db.delete(otp_obj)
    db.commit()
    return {"status": "success", "message": "Password reset successful"}