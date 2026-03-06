from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.schemas import CartItemAdd, CartItemUpdate
from app.services.cart_service import get_or_create_cart, get_cart_subtotal

router = APIRouter(prefix="/cart", tags=["Cart"])


def serialize_cart(cart):
    items = []
    for item in cart.items:
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "slug": item.product.slug,
                "price": float(item.product.price),
                "mrp": float(item.product.mrp) if item.product.mrp else None,
                "image_url": item.product.image_url,
                "unit": item.product.unit,
                "stock_qty": item.product.stock_qty,
            },
        })
    return {
        "id": cart.id,
        "items": items,
        "subtotal": float(get_cart_subtotal(cart)),
        "item_count": len(items),
    }


@router.get("")
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(current_user.id, db)
    return serialize_cart(cart)


@router.post("/items", status_code=201)
def add_to_cart(
    data: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == data.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if product.stock_qty < data.quantity:
        raise HTTPException(400, f"Only {product.stock_qty} items in stock")

    cart = get_or_create_cart(current_user.id, db)
    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.id, CartItem.product_id == data.product_id
    ).first()

    if existing:
        new_qty = existing.quantity + data.quantity
        if product.stock_qty < new_qty:
            raise HTTPException(400, f"Cannot add more. Only {product.stock_qty} in stock")
        existing.quantity = new_qty
    else:
        item = CartItem(cart_id=cart.id, product_id=data.product_id, quantity=data.quantity)
        db.add(item)

    db.commit()
    db.refresh(cart)
    return serialize_cart(cart)


@router.put("/items/{product_id}")
def update_cart_item(
    product_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = get_or_create_cart(current_user.id, db)
    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    ).first()
    if not item:
        raise HTTPException(404, "Item not in cart")
    if data.quantity <= 0:
        db.delete(item)
    else:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product.stock_qty < data.quantity:
            raise HTTPException(400, f"Only {product.stock_qty} in stock")
        item.quantity = data.quantity
    db.commit()
    db.refresh(cart)
    return serialize_cart(cart)


@router.delete("/items/{product_id}")
def remove_cart_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = get_or_create_cart(current_user.id, db)
    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id, CartItem.product_id == product_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
    db.refresh(cart)
    return serialize_cart(cart)


@router.delete("/clear")
def clear_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = get_or_create_cart(current_user.id, db)
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
