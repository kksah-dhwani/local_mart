from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_admin
from app.models.block import Block
from app.models.delivery_zone import DeliveryZone
from app.schemas.schemas import BlockCreate, BlockOut, ZoneCreate, ZoneOut, ZoneUpdate

router = APIRouter(prefix="/blocks", tags=["Blocks"])


@router.get("", response_model=List[BlockOut])
def get_blocks(db: Session = Depends(get_db)):
    return db.query(Block).filter(Block.is_active == True).all()


@router.get("/{block_id}/zones", response_model=List[ZoneOut])
def get_zones(block_id: int, db: Session = Depends(get_db)):
    return db.query(DeliveryZone).filter(
        DeliveryZone.block_id == block_id, DeliveryZone.is_active == True
    ).all()


# ── ADMIN ────────────────────────────────────────────────
@router.post("", response_model=BlockOut, status_code=201)
def create_block(data: BlockCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    block = Block(**data.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


@router.put("/{block_id}", response_model=BlockOut)
def update_block(block_id: int, data: BlockCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(404, "Block not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(block, k, v)
    db.commit()
    db.refresh(block)
    return block


@router.delete("/{block_id}")
def delete_block(block_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(404, "Block not found")
    block.is_active = False
    db.commit()
    return {"message": "Block deactivated"}


# ── ZONES ────────────────────────────────────────────────
zone_router = APIRouter(prefix="/delivery-zones", tags=["Delivery Zones"])


@router.post("/zones", response_model=ZoneOut, status_code=201)
def create_zone(data: ZoneCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    zone = DeliveryZone(**data.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


@router.put("/zones/{zone_id}", response_model=ZoneOut)
def update_zone(zone_id: int, data: ZoneUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    zone = db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(zone, k, v)
    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/zones/{zone_id}")
def delete_zone(zone_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    zone = db.query(DeliveryZone).filter(DeliveryZone.id == zone_id).first()
    if not zone:
        raise HTTPException(404, "Zone not found")
    zone.is_active = False
    db.commit()
    return {"message": "Zone deactivated"}
