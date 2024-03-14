import asyncio
import logging
from src import dependencies
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from . import services
from . import schemes
from src import database
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

router = APIRouter(prefix="/curier")

logger = logging.getLogger("debug")

#TODO: add logging
@router.post(path="/")
async def registration(courier: schemes.CourierRegistration, session: AsyncSession = Depends(dependencies.get_async_session)):
    await services.register_courier(session, courier.name, courier.districts)
    
    await session.commit()
    
    return Response(status_code=status.HTTP_201_CREATED)


@router.get(path="/", response_model=list[schemes.CourierRead])
async def courieres(session: AsyncSession = Depends(dependencies.get_async_session)):
    courieres = await services.get_courieres(session)
    return courieres


@router.get(path="/{id}", response_model=schemes.CourierDetail)
async def courier_detail(id: UUID4):
    session1 = database.async_session_maker()
    session2 = database.async_session_maker()
    session3 = database.async_session_maker()
    
    courier, order, metrics = await asyncio.gather(
        services.get_courier(session1, id),
        services.get_active_order(session2, id),
        services.get_courier_metrics(session3, id)
    )
    
    [await s.close() for s in [session1, session2, session3]]
    
    return schemes.CourierDetail(
        id=courier.id, name=courier.name, active_order=schemes.ActiveOrder(
            id=order.id, name=order.name
        ) if order else None,
        metrics=metrics.model_dump()
    )