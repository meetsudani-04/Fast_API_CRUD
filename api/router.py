from fastapi import APIRouter, Depends
from uuid import uuid4
from fastapi import status
from sqlalchemy.orm import Session
from api.auth import get_current_user


from db.database import get_db
from db.models import User

router = APIRouter()

@router.get("/get-all-users", tags=["Users"] , status_code=status.HTTP_200_OK)
async def get_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
    
):
    users = db.query(User).all()
    return {"status": "success", "message": "users fetched successfully", "data": users}