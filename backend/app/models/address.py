from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("delivery_zones.id"), nullable=False)
    label = Column(String(50), default="Home")
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    landmark = Column(String(150))
    pincode = Column(String(10))
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="addresses")
    block = relationship("Block", back_populates="addresses")
    zone = relationship("DeliveryZone", back_populates="addresses")
    orders = relationship("Order", back_populates="address")
