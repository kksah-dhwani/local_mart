from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.address import Address
from app.models.delivery_zone import DeliveryZone


def calculate_delivery(address_id: int, cart_subtotal: Decimal, db: Session) -> dict:
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        return {
            "is_deliverable": False,
            "delivery_charge": Decimal("0"),
            "zone_name": None,
            "free_delivery_above": None,
            "message": "Address not found",
        }

    zone = db.query(DeliveryZone).filter(
        DeliveryZone.id == address.zone_id,
        DeliveryZone.block_id == address.block_id,
        DeliveryZone.is_active == True,
    ).first()

    if not zone:
        return {
            "is_deliverable": False,
            "delivery_charge": Decimal("0"),
            "zone_name": None,
            "free_delivery_above": None,
            "message": "Delivery not available in your area",
        }

    min_val = Decimal(str(zone.min_order_value or 0))
    charge = Decimal("0") if cart_subtotal >= min_val and min_val > 0 else Decimal(str(zone.delivery_charge))

    return {
        "is_deliverable": True,
        "delivery_charge": charge,
        "zone_name": zone.zone_name,
        "free_delivery_above": min_val if min_val > 0 else None,
        "message": (
            f"Free delivery applied! (Orders above ₹{min_val})"
            if cart_subtotal >= min_val and min_val > 0
            else f"Delivery charge: ₹{charge}"
        ),
    }
