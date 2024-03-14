from pydantic import BaseModel, UUID4

class CourierRegistration(BaseModel):
    name: str
    districts: list[str]
    

class CourierRead(BaseModel):
    id: UUID4
    name: str


class ActiveOrder(BaseModel):
    id: UUID4
    name: str


class CourierMetrics(BaseModel):
    avg_order_complete_time: float
    avg_day_orders: float


class CourierDetail(CourierRead):
    active_order: ActiveOrder | None
    metrics: CourierMetrics
    
    
class District(BaseModel):
    id: UUID4
    name: str
   
    
class Order(BaseModel):
    id: UUID4
    name: str
    district: District

    