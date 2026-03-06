from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.cart_service import get_or_create_cart, get_cart_subtotal
from app.services.delivery_service import calculate_delivery

router = APIRouter(prefix="/delivery", tags=["Delivery"])


@router.get("/calculate")
def calc_delivery(
    address_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = get_or_create_cart(current_user.id, db)
    subtotal = get_cart_subtotal(cart)
    result = calculate_delivery(address_id, subtotal, db)
    return result
