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


@pytest.fixture
def location_data() -> dict:
    return {
        "place_name": "Vovo Telo Bakery & Café",
        "formatted_address": "Corner Country Estate Drive and, Shop 2, Waterfall Wilds Waterfall Wilds, Waterfall Dr, Waterfall, Midrand, 1685, South Africa",
        "place_id": "ChIJ5ceK_tFzlR4RBOSyaD4YaHo",
        "latitude": -26.0195134,
        "longitude": 28.0892369,
        "website": "https://vovotelo.co.za",
        "rating": 3.9
    }
