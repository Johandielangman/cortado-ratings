# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
#      /\_/\
#     ( o.o )
#      > ^ <
#
# Author: Johan Hanekom
# Date: August 2025
#
# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~

# =============== // LIBRARY IMPORT // ===============

import pytest

# =============== // MODULE IMPORT // ===============

from cortado import Cortado, DC


def test_init():
    try:
        Cortado()
    except Exception as e:
        pytest.fail(f"Initialization of Cortado failed with error: {e}")


def test_new_rating(location_data):
    c = Cortado()

    c.new_rating(
        restaurant=DC.Restaurant(
            name=location_data["place_name"],
            address=location_data["formatted_address"],
            google_place_id=location_data["place_id"],
            latitude=location_data["latitude"],
            longitude=location_data["longitude"],
            website=location_data["website"],
            restaurant_rating=location_data["rating"]
        ),
        user=DC.User(
            name="johan",
        ),
        rating=DC.Rating(
            stars=2,
            price_zar=10.3,
            notes="Very lekker",
            cookie=True
        )
    )
