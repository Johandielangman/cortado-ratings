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

from streamlit.testing.v1 import AppTest

# =============== // MODULE IMPORT // ===============

import constants as c


def test_root_can_run():
    at = AppTest.from_file(str(c.MAIN_PATH))
    at.run()
    assert not at.exception


def test_pages_can_run():
    for page in c.PAGES_DIR.iterdir():
        if page.suffix == ".py":
            at = AppTest.from_file(str(page))
            at.run()
            assert not at.exception
