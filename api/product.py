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

product_router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@product_router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = crud.create_product(db, product, user_id=current_user.id)
    return db_product
    
@product_router.get("/", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

):
    return crud.get_products(db,user_id=current_user.id)

@product_router.get("/all", response_model=list[ProductResponse])
def list_all_products(db: Session = Depends(get_db)):
    """
    Public endpoint – shows all products from all users
    """
    return crud.get_products_all(db)


@product_router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = crud.get_product(db, product_id)
    if not product or product.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@product_router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = crud.get_product(db, product_id)
    if not db_product or db_product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")

    updated = crud.update_product(db, product_id, product)
    return updated



@product_router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_product = crud.get_product(db, product_id)
    if not db_product or db_product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    crud.delete_product(db, product_id)
    return {"detail": "Product deleted successfully"}


