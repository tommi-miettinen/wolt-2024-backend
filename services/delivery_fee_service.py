from models.DeliveryFeeRequest import DeliveryFeeRequest
from pydantic import validate_call, BaseModel, validator, Field
from datetime import datetime
from typing import Annotated, Any, Dict
import math


class DeliveryFeeConfig(BaseModel):
    BASE_FEE: Annotated[int, Field(gt=0, validate_default=True)] = 200
    ADDITIONAL_FEE: Annotated[int, Field(gt=0, validate_default=True)] = 100
    BASE_DISTANCE: Annotated[int, Field(gt=0, validate_default=True)] = 1000
    ADDITIONAL_DISTANCE: Annotated[int, Field(gt=0, validate_default=True)] = 500
    BULK_ITEMS_THRESHOLD_1: Annotated[int, Field(gt=0, validate_default=True)] = 4
    BULK_ITEMS_THRESHOLD_2: Annotated[int, Field(gt=0, validate_default=True)] = 12
    BULK_ITEMS_THRESHOLD_1_FEE: Annotated[int, Field(gt=0, validate_default=True)] = 50
    BULK_ITEMS_THRESHOLD_2_FEE: Annotated[int, Field(gt=0, validate_default=True)] = 120
    MAX_FEE: Annotated[int, Field(gt=0, validate_default=True)] = 1500
    CART_VALUE_THRESHOLD_FOR_SURCHARGE: Annotated[
        int, Field(gt=0, validate_default=True)
    ] = 1000
    RUSH_HOUR_DAY_OF_WEEK: Annotated[int, Field(ge=0, lt=7, validate_default=True)] = 4
    RUSH_HOUR_START_HOUR: Annotated[int, Field(ge=0, lt=24, validate_default=True)] = 15
    RUSH_HOUR_END_HOUR: Annotated[int, Field(ge=0, lt=24, validate_default=True)] = 19
    RUSH_HOUR_FEE_MULTIPLIER: Annotated[float, Field(gt=0, validate_default=True)] = 1.2

    @validator("RUSH_HOUR_END_HOUR")
    def validate_rush_hours(cls, value: int, values: Dict[str, Any]):
        if "RUSH_HOUR_START_HOUR" in values and value <= values["RUSH_HOUR_START_HOUR"]:
            raise ValueError(
                "RUSH_HOUR_END_HOUR must be greater than RUSH_HOUR_START_HOUR"
            )
        return value


config = DeliveryFeeConfig()


@validate_call
def _is_rush_hour(time: datetime):
    return (
        time.weekday() == config.RUSH_HOUR_DAY_OF_WEEK
        and config.RUSH_HOUR_START_HOUR <= time.hour < config.RUSH_HOUR_END_HOUR
    )


@validate_call
def _get_small_order_surcharge(cart_value: Annotated[float, Field(gt=0)]):
    return max(config.CART_VALUE_THRESHOLD_FOR_SURCHARGE - cart_value, 0)


@validate_call
def _get_distance_fee(delivery_distance: Annotated[int, Field(gt=0)]):
    if delivery_distance <= config.BASE_DISTANCE:
        return config.BASE_FEE

    distance_over_base = (
        math.ceil(delivery_distance - config.BASE_DISTANCE) / config.ADDITIONAL_DISTANCE
    )
    return int(config.BASE_FEE + (distance_over_base * config.ADDITIONAL_FEE))


@validate_call
def _get_bulk_fee(number_of_items: Annotated[int, Field(gt=0)]):
    fee = 0
    if number_of_items > config.BULK_ITEMS_THRESHOLD_1:
        items_over_threshold_1 = number_of_items - config.BULK_ITEMS_THRESHOLD_1
        fee = items_over_threshold_1 * config.BULK_ITEMS_THRESHOLD_1_FEE

    if number_of_items > config.BULK_ITEMS_THRESHOLD_2:
        fee += config.BULK_ITEMS_THRESHOLD_2_FEE

    return fee


@validate_call
def get_total_delivery_fee(request: DeliveryFeeRequest):
    small_order_surcharge = _get_small_order_surcharge(request.cart_value)
    distance_fee = _get_distance_fee(request.delivery_distance)
    bulk_fee = _get_bulk_fee(request.number_of_items)

    fee = small_order_surcharge + distance_fee + bulk_fee

    if _is_rush_hour(request.time):
        fee *= config.RUSH_HOUR_FEE_MULTIPLIER

    return round(min(fee, config.MAX_FEE), 2)
