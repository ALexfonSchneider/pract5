from pydantic import UUID4
from . import service
from . import schemes
from src import dependencies
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

router = APIRouter(prefix="/order", )


@router.get(path="/{id}", response_model=schemes.OrderRead, description='Получить заказ по его id')
async def get_order(id: UUID4, session: AsyncSession = Depends(dependencies.get_async_session)):
    order = await service.get_order(session, id)
    if not order:
        return Response(status_code=404)
    return order


@router.put(path="/{id}", description='Закрыть заказ по его id')
async def close_order(id: UUID4, session: AsyncSession = Depends(dependencies.get_async_session)):
    id = await service.close_order(session, id)
    if not id:
        raise HTTPException(status_code=404, detail='order does not exists')
    await session.commit()
    return Response(status_code=status.HTTP_200_OK)


@router.post(path="/", responses={
    200: {'model': schemes.NewOrderResponse},
    400: {}
}, description='Создать новый заказ')
async def make_order(new_order: schemes.NewOrder, session: AsyncSession = Depends(dependencies.get_async_session)):
    district = await service.get_district(session, new_order.district)
    courier = await service.find_available_courieres(session, new_order.district)
    
    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='district not found')
    
    if not courier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='available courier do not found')
    
    order = await service.make_order(session, new_order.name, district.id, courier.id)
    await session.commit()
    if order:
        return schemes.NewOrderResponse(
            courier_id=order.courier_id,
            order_id=order.id
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cannot find courier")