from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import (
    Float,
    Select,
    func
)
from src import models
from uuid import uuid4

async def upsert_districts(session: AsyncSession, districts: list[str]):
    query = insert(models.District).values([
        {"id": uuid4(), "name": district} for district in districts
    ]).on_conflict_do_nothing().returning(models.District.id)
    res = await session.execute(query)


async def create_areas(session: AsyncSession, courier_id: UUID4, districts: list[str]):
    query = insert(models.CourierAreas).values([
        {"id": uuid4(), "district_id": Select(models.District.id).where(models.District.name == district), "courier_id": courier_id} for district in districts
    ]).on_conflict_do_nothing().returning(models.CourierAreas.id)
    res = await session.execute(query)
    return res.scalars().all()


async def register_courier(session: AsyncSession, name: str, districts: list[str]) -> UUID4:
    courier_id = uuid4()
    
    query = insert(models.Courier).values(
        id=courier_id,
        name=name,
    )
    await session.execute(query)
    
    await upsert_districts(session, districts)
    await create_areas(session, courier_id, districts)
    
    return courier_id


async def get_courier(session: AsyncSession, id: UUID4 | str) -> models.Courier | None:
    query = Select(models.Courier).where(models.Courier.id == id)
    result = await session.execute(query)
    courier = result.scalar()
    return courier


async def get_active_order(session: AsyncSession, courier_id: UUID4 | str) -> models.Order | None:
    query = Select(models.Order).where((models.Order.courier_id == courier_id) & (models.Order.status == 1))
    result = await session.execute(query)
    order = result.scalar()
    return order


async def get_courier_metrics(session: AsyncSession, courier_id: UUID4 | str) -> models.CourierMetrics:
    avg_processing_time = Select(func.round(func.avg(func.extract('hour', models.Order.completed_at - models.Order.created_at)), 3).cast(Float)).where(models.Order.courier_id == courier_id)
    
    date_trunc_day = func.date_trunc('day', models.Order.completed_at).label('date')
    daily_orders = Select(
            date_trunc_day, func.count("*").label('count')
        ).group_by(
            date_trunc_day
        ).where(models.Order.courier_id == courier_id)
    avg_day_orders = Select(func.round(func.avg(daily_orders.c.count), 2).cast(Float))
    
    avg_processing_time = await session.execute(avg_processing_time)
    avg_day_orders = await session.execute(avg_day_orders)
    
    avg_day_orders = avg_day_orders.scalar()
    avg_processing_time = avg_processing_time.scalar()
    
    if not avg_day_orders:
        avg_day_orders = 0.0
    if not avg_processing_time:
        avg_processing_time = 0.0
        
    return models.CourierMetrics(
        avg_day_orders=avg_day_orders,
        avg_order_complete_time=avg_processing_time,
    )
    

async def get_courieres(session: AsyncSession, limit: int = -1, offset: int = 0) -> list[models.Courier]:
    query = Select(models.Courier).offset(offset)
    if limit >= 0:
        query = query.limit(limit)

    result = await session.execute(query)
    courieres = result.scalars().all()
    return courieres