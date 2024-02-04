from models.DeliveryFeeRequest import DeliveryFeeRequest
from pydantic import validate_call
from datetime import datetime
import math

BASE_FEE = 200
ADDITIONAL_FEE = 100

BASE_DISTANCE = 1000
ADDITIONAL_DISTANCE = 500

BULK_ITEMS_THRESHOLD_1 = 4
BULK_ITEMS_THRESHOLD_2 = 12

BULK_ITEMS_THRESHOLD_1_FEE = 50
BULK_ITEMS_THRESHOLD_2_FEE = 120

MAX_FEE = 1500
CART_VALUE_THRESHOLD_FOR_SURCHARGE = 1000

RUSH_HOUR_DAY_OF_WEEK = 4
RUSH_HOUR_START_HOUR = 15
RUSH_HOUR_END_HOUR = 19
RUSH_HOUR_FEE_MULTIPLIER = 1.2


@validate_call
def _is_rush_hour(time: datetime):
    return (
        time.weekday() == RUSH_HOUR_DAY_OF_WEEK
        and RUSH_HOUR_START_HOUR <= time.hour < RUSH_HOUR_END_HOUR
    )


@validate_call
def _get_small_order_surcharge(cart_value: int) -> int:
    return max(CART_VALUE_THRESHOLD_FOR_SURCHARGE - cart_value, 0)


@validate_call
def _get_distance_fee(delivery_distance: int) -> int:
    if delivery_distance <= BASE_DISTANCE:
        return BASE_FEE

    distance_over_base = (
        math.ceil(delivery_distance - BASE_DISTANCE) / ADDITIONAL_DISTANCE
    )
    return BASE_FEE + (distance_over_base * ADDITIONAL_FEE)


@validate_call
def _get_bulk_fee(number_of_items: int) -> int:
    fee = 0
    if number_of_items > BULK_ITEMS_THRESHOLD_1:
        items_over_threshold_1 = number_of_items - BULK_ITEMS_THRESHOLD_1
        fee = items_over_threshold_1 * BULK_ITEMS_THRESHOLD_1_FEE

    if number_of_items > BULK_ITEMS_THRESHOLD_2:
        fee += BULK_ITEMS_THRESHOLD_2_FEE

    return fee


@validate_call
def get_total_delivery_fee(request: DeliveryFeeRequest):
    small_order_surcharge = _get_small_order_surcharge(request.cart_value)
    distance_fee = _get_distance_fee(request.delivery_distance)
    bulk_fee = _get_bulk_fee(request.number_of_items)

    fee = small_order_surcharge + distance_fee + bulk_fee

    if _is_rush_hour(request.time):
        fee *= RUSH_HOUR_FEE_MULTIPLIER

    return min(fee, MAX_FEE)
