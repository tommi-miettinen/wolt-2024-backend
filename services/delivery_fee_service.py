from models.DeliveryFeeRequest import DeliveryFeeRequest

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


def get_small_order_surcharge(cart_value: int) -> int:
    return max(CART_VALUE_THRESHOLD_FOR_SURCHARGE - cart_value, 0)


def get_distance_fee(delivery_distance: int) -> int:
    if delivery_distance <= BASE_DISTANCE:
        return BASE_FEE

    distance_over_base = (
        math.ceil(delivery_distance - BASE_DISTANCE) / ADDITIONAL_DISTANCE
    )
    return BASE_FEE + (distance_over_base * ADDITIONAL_FEE)


def get_bulk_fee(number_of_items: int) -> int:
    fee = 0
    if number_of_items > BULK_ITEMS_THRESHOLD_1:
        items_over_threshold_1 = number_of_items - BULK_ITEMS_THRESHOLD_1
        fee = items_over_threshold_1 * BULK_ITEMS_THRESHOLD_1_FEE

    if number_of_items > BULK_ITEMS_THRESHOLD_2:
        fee += BULK_ITEMS_THRESHOLD_2_FEE

    return fee


def get_total_delivery_fee(request: DeliveryFeeRequest):
    small_order_surcharge = get_small_order_surcharge(request.cart_value)
    distance_fee = get_distance_fee(request.delivery_distance)
    bulk_fee = get_bulk_fee(request.number_of_items)

    return min(small_order_surcharge + distance_fee + bulk_fee, MAX_FEE)
