from pydantic import BaseModel, conint
from datetime import datetime


class DeliveryFeeRequest(BaseModel):
    cart_value: conint(gt=0)
    delivery_distance: conint(gt=0)
    number_of_items: conint(gt=0)
    time: datetime
