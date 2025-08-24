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

import os

# =============== // LIBRARY IMPORT // ===============

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

# =============== // MODULE IMPORT // ===============

import cortado.datastructures as ds


class CortadoDB:
    def __init__(self):
        self._engine = create_engine(self.object_url, echo=False)
        ds.Base.metadata.create_all(self._engine)

    def get_session(self):
        Session = sessionmaker(bind=self._engine)
        return Session()

    @property
    def object_url(self):
        return URL.create(
            "postgresql+psycopg2",
            username=os.environ["PSQL_USERNAME"],
            password=os.environ["PSQL_PASSWORD"],
            host=os.environ["PSQL_HOST"],
            database=os.environ["PSQL_DB"],
            query={
                "sslmode": "require",
                "channel_binding": "require"
            },
        )
