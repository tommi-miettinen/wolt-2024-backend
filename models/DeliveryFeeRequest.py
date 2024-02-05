from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime


class DeliveryFeeRequest(BaseModel):
    cart_value: Annotated[int, Field(gt=0)]
    delivery_distance: Annotated[int, Field(gt=0)]
    number_of_items: Annotated[int, Field(gt=0)]
    time: datetime
