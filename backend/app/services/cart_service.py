from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.cart import Cart, CartItem
from app.models.product import Product


def get_or_create_cart(user_id: int, db: Session) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def get_cart_subtotal(cart: Cart) -> Decimal:
    total = Decimal("0")
    for item in cart.items:
        total += Decimal(str(item.product.price)) * item.quantity
    return total
