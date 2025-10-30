from itertools import product
from fastapi import APIRouter, Depends
from uuid import uuid4
from fastapi import status
from sqlalchemy.orm import Session
from api.auth import get_current_user
from fastapi import HTTPException
from db.schema import ProductCreate, ProductUpdate, ProductResponse
from api import crud
from db.database import get_db
from db.models import Product, User

admin = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@admin.get("/all", response_model=list[ProductResponse])
def list_all_products(db: Session = Depends(get_db)):
    """
    Public endpoint – shows all products from all users
    """
    return crud.get_products_all(db)



