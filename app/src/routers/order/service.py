from uuid import uuid4
from pydantic import UUID4
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import (
    Select,
    Update
)
from sqlalchemy.ext.asyncio import AsyncSession
from src import models

async def find_available_courieres(session: AsyncSession, district: str) -> models.Courier | None:
    active_orders = Select(models.Order).where(
        (models.Courier.id == models.Order.courier_id) & (models.Order.status == 1)
    )
    covered_districts = Select(models.CourierAreas).join(
        models.District, models.District.id == models.CourierAreas.district_id
    ).filter((models.Courier.id == models.CourierAreas.courier_id) & (models.District.name == district))
    
    query = Select(models.Courier).filter(
        ~active_orders.exists() & covered_districts.exists()
    )
    result = await session.execute(query)
    return result.scalar()


async def get_district(session: AsyncSession, district: str) -> models.District | None:
    query = Select(models.District).where(models.District.name == district).limit(1)
    result = await session.execute(query)
    return result.scalar()


async def make_order(session: AsyncSession, name: str, district_id: UUID4, courier_id: UUID4) -> models.Order:
    query = insert(models.Order).values(
        id=uuid4(),
        name=name,
        district_id=district_id,
        courier_id=courier_id,
        status=1
    ).returning(models.Order)
    result = await session.execute(query)
    return result.scalar()


async def get_order(session: AsyncSession, id: UUID4) -> models.Order | None:
    query = Select(models.Order).where(models.Order.id == id).limit(1)
    res = await session.execute(query)
    order = res.scalar()
    return order
    
    
async def close_order(session: AsyncSession, id: UUID4) -> UUID4 | None:
    query = Update(models.Order).where((models.Order.id == id) & (models.Order.status == 1)).values(status=2, completed_at=datetime.now()).returning(models.Order.id)
    res = await session.execute(query)
    return res.scalar()