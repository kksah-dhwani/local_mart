from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.address import Address
from app.models.delivery_zone import DeliveryZone
from app.models.user import User
from app.schemas.schemas import AddressCreate, AddressOut

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("", response_model=List[AddressOut])
def get_addresses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Address).filter(Address.user_id == current_user.id).all()


@router.post("", response_model=AddressOut, status_code=201)
def create_address(
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate zone belongs to block
    zone = db.query(DeliveryZone).filter(
        DeliveryZone.id == data.zone_id, DeliveryZone.block_id == data.block_id
    ).first()
    if not zone:
        raise HTTPException(400, "Zone does not belong to selected block")

    # If setting as default, unset others
    if data.is_default:
        db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})

    address = Address(user_id=current_user.id, **data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(404, "Address not found")

    if data.is_default:
        db.query(Address).filter(Address.user_id == current_user.id, Address.id != address_id).update(
            {"is_default": False}
        )

    for k, v in data.model_dump().items():
        setattr(address, k, v)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(404, "Address not found")
    db.delete(address)
    db.commit()
    return {"message": "Address deleted"}


@router.patch("/{address_id}/set-default")
def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = db.query(Address).filter(
        Address.id == address_id, Address.user_id == current_user.id
    ).first()
    if not address:
        raise HTTPException(404, "Address not found")
    db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
    address.is_default = True
    db.commit()
    return {"message": "Default address updated"}
