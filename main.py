from fastapi import FastAPI, Query
from services.delivery_fee_service import get_total_delivery_fee
from models.DeliveryFeeRequest import DeliveryFeeRequest
from datetime import datetime

app = FastAPI()


@app.post("/deliveryfee")
def get_delivery_fee(request: DeliveryFeeRequest):
    return {"delivery_fee": get_total_delivery_fee(request)}


@app.get("/deliveryfee")
def get_delivery_fee_get_method(
    cart_value: int = Query(..., gt=0),
    delivery_distance: int = Query(..., gt=0),
    number_of_items: int = Query(..., gt=0),
    time: datetime = Query(...),
):
    request = DeliveryFeeRequest(
        cart_value=cart_value,
        delivery_distance=delivery_distance,
        number_of_items=number_of_items,
        time=time,
    )
    return {"delivery_fee": get_total_delivery_fee(request)}
