import os
import sys
import pytest
from pydantic import ValidationError
from datetime import datetime

current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
os.chdir(root_dir)
sys.path.append(root_dir)

from services.delivery_fee_service import (
    get_small_order_surcharge,
    get_distance_fee,
    get_bulk_fee,
    is_rush_hour,
    get_total_delivery_fee,
)
from models.DeliveryFeeRequest import DeliveryFeeRequest


# If the cart value is less than 10€, a small order surcharge is added to the delivery price.
# The surcharge is the difference between the cart value and 10€.
# For example, if the cart value is 8.90€, the surcharge will be 1.10€.


def test_small_order_surcharge_gets_applied():
    assert get_small_order_surcharge(1000) == 0
    assert get_small_order_surcharge(155) == 845
    assert get_small_order_surcharge(1) == 999
    assert get_small_order_surcharge(1001) == 0

    with pytest.raises(ValidationError):
        get_small_order_surcharge(-1)

    with pytest.raises(ValidationError):
        get_small_order_surcharge(0)


# A delivery fee for the first 1000 meters (=1km) is 2€.
# If the delivery distance is longer than that, 1€ is added for every additional 500 meters
# that the courier needs to travel before reaching the destination.
# Even if the distance would be shorter than 500 meters, the minimum fee is always 1€.
# Example 1: If the delivery distance is 1499 meters, the delivery fee is:
# 2€ base fee + 1€ for the additional 500 m => 3€
# Example 2: If the delivery distance is 1500 meters, the delivery fee is:
# 2€ base fee + 1€ for the additional 500 m => 3€
# Example 3: If the delivery distance is 1501 meters, the delivery fee is:
# 2€ base fee + 1€ for the first 500 m + 1€ for the second 500 m => 4€


def test_get_distance_fee():
    assert get_distance_fee(1) == 200
    assert get_distance_fee(999) == 200
    assert get_distance_fee(1000) == 200
    assert get_distance_fee(1001) == 300
    assert get_distance_fee(1499) == 300
    assert get_distance_fee(1500) == 300
    assert get_distance_fee(1501) == 400

    with pytest.raises(ValidationError):
        get_distance_fee(-1)

    with pytest.raises(ValidationError):
        get_distance_fee(0)


# If the number of items is five or more, an additional 50 cent surcharge is added for each item above and including the fifth item.
# An extra "bulk" fee applies for more than 12 items of 1,20€
# Example 1: If the number of items is 4, no extra surcharge
# Example 2: If the number of items is 5, a 50 cent surcharge is added
# Example 3: If the number of items is 10, a 3€ surcharge (6 x 50 cents) is added
# Example 4: If the number of items is 13, a 5,70€ surcharge is added ((9 x 50 cents) + 1,20€)
# Example 5: If the number of items is 14, a 6,20€ surcharge is added ((10 x 50 cents) + 1,20€)


def test_get_bulk_fee():
    assert get_bulk_fee(1) == 0
    assert get_bulk_fee(4) == 0
    assert get_bulk_fee(5) == 50
    assert get_bulk_fee(10) == 300
    assert get_bulk_fee(13) == 570
    assert get_bulk_fee(14) == 620

    with pytest.raises(ValidationError):
        get_bulk_fee(-1)

    with pytest.raises(ValidationError):
        get_bulk_fee(0)


# Rush hour is 15.00 - 19.00 on Fridays.
def test_is_rush_hour():
    assert is_rush_hour(datetime(2024, 2, 5, 15, 0)) == False
    assert is_rush_hour(datetime(2024, 2, 2, 15, 0)) == True
    assert is_rush_hour(datetime(2024, 2, 2, 14, 59)) == False
    assert is_rush_hour(datetime(2024, 2, 2, 19, 0)) == False


def test_get_total_delivery_fee_with_rush_hour_should_apply_multiplier_of_1point2():
    assert (
        get_total_delivery_fee(
            DeliveryFeeRequest(
                cart_value=1000,
                delivery_distance=1000,
                number_of_items=1,
                time=datetime(2024, 2, 2, 15, 0),
            )
        )
        == 240
    )


def test_fee_cant_be_over_15000_even_on_rush_hour():
    assert (
        get_total_delivery_fee(
            DeliveryFeeRequest(
                cart_value=1000,
                delivery_distance=1000,
                number_of_items=100,
                time=datetime(2024, 2, 2, 15, 0),
            )
        )
        == 1500
    )


def test_cart_value_of_20000_should_have_free_delivery():
    assert (
        get_total_delivery_fee(
            DeliveryFeeRequest(
                cart_value=20000,
                delivery_distance=1000,
                number_of_items=1,
                time=datetime(2024, 2, 2, 15, 0),
            )
        )
        == 0
    )
