# coding: utf-8

import unittest
from datetime import datetime


def setUpModule():
    import sqlahelper
    from sqlalchemy import create_engine
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.models

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()


class FindTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def test_it(self):
        import sqlahelper
        from altaircms.event.models import Event

        session = sqlahelper.get_session()

        target = Event(deal_open=datetime(1900, 1, 1), 
                       deal_close=datetime(1900, 1, 30))
        session.add(target)
        
        self.assertEquals(Event.near_the_deal_close_query(datetime(1900, 1, 28), 3).count(), 1)
        self.assertEquals(Event.near_the_deal_close_query(datetime(1900, 1, 28), 2).count(), 1)
        self.assertEquals(Event.near_the_deal_close_query(datetime(1900, 1, 28), 1).count(), 0)

        self.assertEquals(Event.near_the_deal_close_query(datetime(1900, 1, 30), 0).count(), 1)



        
if __name__ == "__main__":
    unittest.main()
