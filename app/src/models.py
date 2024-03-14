from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import (
    Column,
    String,
    Uuid,
    ForeignKey,
    UniqueConstraint,
    Integer,
    DateTime,
)


class Base(DeclarativeBase):
    pass


class District(Base):
    __tablename__ = "districts"
    
    id = Column("id", Uuid, primary_key=True)
    name = Column("name", String, unique=True)
    
    areas = relationship("CourierAreas", uselist=True)
    orders = relationship("Order", uselist=True)


class CourierAreas(Base):
    __tablename__ = "courier_areas"
    
    id = Column("id", Uuid, primary_key=True)
    district_id = Column("district_id", ForeignKey("districts.id", ondelete="RESTRICT"), nullable=False) 
    courier_id = Column("courier_id", ForeignKey("couriers.id", ondelete="RESTRICT"), nullable=False)
    
    unique_together_constraint = UniqueConstraint("district_id", "courier_id")
    
    courier = relationship('Courier', viewonly=True)
    district = relationship("District", viewonly=True)


class Courier(Base):
    __tablename__ = "couriers" 
    
    id = Column("id", Uuid, primary_key=True)
    name = Column("name", String)
    
    areas = relationship("CourierAreas", uselist=True, viewonly=True)
    orders = relationship("Order", uselist=True, viewonly=True)
    order = relationship("Order", viewonly=True)
 
 
class CourierMetrics(BaseModel):
    avg_order_complete_time: float
    avg_day_orders: float


class Order(Base):
    __tablename__ = "orders"
    
    id = Column("id", Uuid, primary_key=True)
    name = Column("name", String)
    courier_id = Column("courier", ForeignKey("couriers.id", ondelete="RESTRICT"), nullable=False)
    district_id = Column("district", ForeignKey("districts.id", ondelete="RESTRICT"), nullable=False)
    status = Column("status", Integer)
    created_at = Column("created_at", DateTime, default=datetime.now)
    completed_at = Column("completed_at", DateTime, nullable=True)
    
    courier = relationship('Courier', viewonly=True)
    district = relationship('District', viewonly=True)