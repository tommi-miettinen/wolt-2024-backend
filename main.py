from fastapi import FastAPI
from services.delivery_fee_service import get_total_delivery_fee
from models.DeliveryFeeRequest import DeliveryFeeRequest

app = FastAPI()


@app.post("/deliveryfee")
def get_delivery_fee(request: DeliveryFeeRequest):
    return {"delivery_fee": get_total_delivery_fee(request)}
