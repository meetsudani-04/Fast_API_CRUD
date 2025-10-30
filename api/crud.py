from sqlalchemy.orm import Session
from db.models import Product
from db.schema import ProductCreate

def create_product(
    db: Session,
    product: ProductCreate,
    user_id : int,
    image_path: str = None,
    ):
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_path=image_path,
        user_id=user_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(
    db: Session,
    product_id: int
    ):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(
    db: Session,
    user_id: int,
    ):
    return (
        db.query(Product)
        .filter(Product.user_id == user_id)
        .all()
    )

def update_product(db: Session, product_id: int, product: ProductCreate, image_path: str = None):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    for attr, value in product.dict().items():
        setattr(db_product, attr, value)
    if image_path:
        db_product.image_path = image_path
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

# admin
def get_products_all(db: Session):
    return db.query(Product).all()


