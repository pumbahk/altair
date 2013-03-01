from altaircms.testing import setup_db
from altaircms.testing import teardown_db

def setUpModule():
    setup_db(models=[
            "altaircms.models", 
            "altaircms.tag.models", 
            "altaircms.event.models"
            ])

def tearDownModule():
    teardown_db()
