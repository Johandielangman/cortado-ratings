# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
#      /\_/\
#     ( o.o )
#      > ^ <
#
# Author: Johan Hanekom
# Date: August 2025
#
# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~

# =============== // STANDARD IMPORT // ===============

from dataclasses import dataclass, field


@dataclass
class Restaurant:
    name: str
    address: str | None = field(default=None)
    google_place_id: str | None = field(default=None)
    latitude: float | None = field(default=None)
    longitude: float | None = field(default=None)
    website: str | None = field(default=None)
    restaurant_rating: float | None = field(default=None)


@dataclass
class User:
    name: str
    email: str | None = field(default=None)


@dataclass
class Rating:
    stars: int
    price_zar: float
    notes: str | None = field(default=None)
    num_shots: str | None = field(default=None)
    cookie: bool = field(default=False)
    take_away: bool = field(default=False)
