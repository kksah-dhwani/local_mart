import razorpay
import hmac
import hashlib
import json
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.address import Address
from app.models.user import User
from app.services.cart_service import get_or_create_cart, get_cart_subtotal
from app.services.delivery_service import calculate_delivery
from app.services.whatsapp_service import notify_new_order

router = APIRouter(prefix="/payments", tags=["Payments"])

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


class CreatePaymentRequest(BaseModel):
    address_id: int
    notes: str = ""


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    address_id: int
    notes: str = ""


@router.post("/create-order")
def create_razorpay_order(
    data: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = db.query(Address).filter(
        Address.id == data.address_id,
        Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(404, "Address not found")

    cart = get_or_create_cart(current_user.id, db)
    if not cart.items:
        raise HTTPException(400, "Cart is empty")

    subtotal = get_cart_subtotal(cart)
    delivery_info = calculate_delivery(data.address_id, subtotal, db)

    if not delivery_info["is_deliverable"]:
        raise HTTPException(400, delivery_info["message"])

    total = subtotal + Decimal(str(delivery_info["delivery_charge"]))

    razorpay_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "receipt": f"order_user_{current_user.id}",
        "notes": {
            "user_id": str(current_user.id),
            "address_id": str(data.address_id),
        }
    })

    return {
        "razorpay_order_id": razorpay_order["id"],
        "amount": int(total * 100),
        "currency": "INR",
        "key_id": settings.RAZORPAY_KEY_ID,
        "subtotal": float(subtotal),
        "delivery_charge": float(delivery_info["delivery_charge"]),
        "total": float(total),
        "user_name": current_user.name,
        "user_email": current_user.email,
        "user_phone": current_user.phone,
    }


@router.post("/verify")
async def verify_payment(
    data: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Signature verify
    body = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected != data.razorpay_signature:
        raise HTTPException(400, "Payment verification failed. Invalid signature.")

    # 2. Address validate
    address = db.query(Address).filter(
        Address.id == data.address_id,
        Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(404, "Address not found")

    # 3. Cart se order banao
    cart = get_or_create_cart(current_user.id, db)
    if not cart.items:
        raise HTTPException(400, "Cart is empty")

    subtotal = get_cart_subtotal(cart)
    delivery_info = calculate_delivery(data.address_id, subtotal, db)
    delivery_charge = Decimal(str(delivery_info["delivery_charge"]))
    total = subtotal + delivery_charge

    snap = {
        "label": address.label,
        "address_line1": address.address_line1,
        "address_line2": address.address_line2,
        "landmark": address.landmark,
        "pincode": address.pincode,
    }

    order = Order(
        user_id=current_user.id,
        address_id=address.id,
        status="confirmed",
        payment_method="online",
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total_amount=total,
        snap_address=json.dumps(snap),
        snap_block_name=address.block.name if address.block else None,
        snap_zone_name=address.zone.zone_name if address.zone else None,
        notes=data.notes,
        razorpay_order_id=data.razorpay_order_id,
        razorpay_payment_id=data.razorpay_payment_id,
    )
    db.add(order)
    db.flush()

    item_count = 0
    for item in cart.items:
        oi = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product.name,
            product_image=item.product.image_url,
            unit_price=item.product.price,
            quantity=item.quantity,
            line_total=Decimal(str(item.product.price)) * item.quantity,
        )
        item.product.stock_qty = max(0, item.product.stock_qty - item.quantity)
        db.add(oi)
        item_count += 1

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    db.refresh(order)

    # WhatsApp notification
    try:
        await notify_new_order(
            order_id=order.id,
            customer_name=current_user.name,
            total=float(order.total_amount),
            block=order.snap_block_name or "N/A",
            zone=order.snap_zone_name or "N/A",
            item_count=item_count,
            payment_method="online",
        )
    except Exception:
        pass

    return {"message": "Payment successful! Order placed.", "order_id": order.id}
