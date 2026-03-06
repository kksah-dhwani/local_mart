from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base


class DeliveryZone(Base):
    __tablename__ = "delivery_zones"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    zone_name = Column(String(100), nullable=False)
    delivery_charge = Column(Numeric(8, 2), nullable=False)
    min_order_value = Column(Numeric(8, 2), default=0)
    is_active = Column(Boolean, default=True)

    block = relationship("Block", back_populates="zones")
    addresses = relationship("Address", back_populates="zone")
