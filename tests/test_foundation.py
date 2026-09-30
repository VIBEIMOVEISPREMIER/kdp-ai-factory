from kdp_factory.db import init_db
from kdp_factory.config import DATA_DIR

def test_foundation():
    init_db()
    assert DATA_DIR.exists()
