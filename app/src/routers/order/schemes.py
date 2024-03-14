from pydantic import BaseModel, UUID4

class OrderRead(BaseModel):
    courier_id: UUID4
    name: str
    status: int

class NewOrder(BaseModel):
    name: str
    district: str
    

class NewOrderResponse(BaseModel):
    order_id: UUID4
    courier_id: UUID4
    

class OrderStatus(BaseModel):
    courier_id: UUID4