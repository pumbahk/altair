from altaircms.testing import setup_db
from altaircms.testing import teardown_db

def setUpModule():
    setup_db(models=[
            "altaircms.models", 
            "altaircms.topic.models", 
            "altaircms.event.models", 
            "altaircms.widget.models", 
            "altaircms.page.models", 
            ])

def tearDownModule():
    teardown_db()
