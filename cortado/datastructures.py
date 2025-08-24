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

import time
from sqlalchemy import String, Float, Numeric, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from ulid import ULID

# =============== // LIBRARY IMPORT // ===============


class Base(DeclarativeBase):
    pass


class TimeStampedModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(ULID()), index=True)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    last_updated_at: Mapped[float] = mapped_column(Float, default=time.time, onupdate=time.time)


class User(TimeStampedModel):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)

    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="user")


class Restaurant(TimeStampedModel):
    __tablename__ = "restaurant"

    # The obvious
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=True)

    # Location data
    google_place_id: Mapped[str] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(Numeric(precision=10, scale=8), nullable=True)
    longitude: Mapped[float] = mapped_column(Numeric(precision=11, scale=8), nullable=True)

    # Additional data
    website: Mapped[str] = mapped_column(String(500), nullable=True)
    restaurant_rating: Mapped[float] = mapped_column(Numeric(precision=2, scale=1), nullable=True)

    # Relationships
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="restaurant")


class Rating(TimeStampedModel):
    __tablename__ = "rating"

    # Foreign keys
    user_id: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    restaurant_id: Mapped[str] = mapped_column(String, ForeignKey("restaurant.id"), nullable=False)

    # Rating data
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    price_zar: Mapped[float] = mapped_column(Numeric(precision=8, scale=2), nullable=True)
    num_shots: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., single, double
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Optional interesting fields
    cookie: Mapped[bool] = mapped_column(Boolean, default=False)
    take_away: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ratings")
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="ratings")
