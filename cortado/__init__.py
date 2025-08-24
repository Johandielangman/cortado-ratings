# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
#      /\_/\
#     ( o.o )
#      > ^ <
#
# Author: Johan Hanekom
# Date: August 2025
#
# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~

# =============== // MODULE IMPORT // ===============

from cortado.db_utils import CortadoDB
import cortado.datastructures as DS
import cortado.input_dc as DC


class Cortado:
    def __init__(self):
        self.db = CortadoDB()

    def new_rating(
        self,
        restaurant=DC.Restaurant,
        user=DC.User,
        rating=DC.Rating
    ):
        with self.db.get_session() as session:
            try:
                db_restaurant = session.query(DS.Restaurant).filter_by(
                    google_place_id=restaurant.google_place_id
                ).first()
                if not db_restaurant:
                    db_restaurant = DS.Restaurant(
                        name=restaurant.name,
                        address=restaurant.address,
                        google_place_id=restaurant.google_place_id,
                        latitude=restaurant.latitude,
                        longitude=restaurant.longitude,
                        website=restaurant.website,
                        restaurant_rating=restaurant.restaurant_rating
                    )
                    session.add(db_restaurant)
                    session.commit()

                db_user = session.query(DS.User).filter_by(
                    name=user.name
                ).first()
                if not db_user:
                    db_user = DS.User(
                        name=user.name,
                        email=user.email
                    )
                    session.add(db_user)
                    session.commit()

                db_rating = DS.Rating(
                    stars=rating.stars,
                    price_zar=rating.price_zar,
                    notes=rating.notes,
                    cookie=rating.cookie,
                    take_away=rating.take_away,
                    num_shots=rating.num_shots,
                    restaurant_id=db_restaurant.id,
                    user_id=db_user.id
                )
                session.add(db_rating)
                session.commit()
            except Exception:
                session.rollback()
                raise

        return rating


__all__ = [
    "Cortado",
    "get_cortado_instance",
    "DS",
    "DC"
]
