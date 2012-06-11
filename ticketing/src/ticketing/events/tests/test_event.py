# -*- coding:utf-8 -*-
import unittest
import datetime
import transaction
from ticketing.core.models import Event, Organization, DBSession
from pyramid import testing

def _setup_db():
    import sqlahelper
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    return sqlahelper.get_session()

def _teardown_db():
    import transaction
    transaction.abort()

def setUpModule():
    DBSession.remove()

def tearDownModule():
    pass

class EventBaseTest(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()
        
    def _createTestEvent(self):
        event = Event()
        event.start_on = datetime.datetime(2012, 2, 14, 15, 13, 26, 438062)
        event.end_on = datetime.datetime(2012, 3, 14, 15, 13, 26, 438062)
        event.publish_at = datetime.datetime(2012, 3, 1, 15, 13, 26, 438062)
        event.code = u'_test_code'
        event.title = u'_test_title'
        event.abbreviated_title= u'_test_ab_title'
        event.seats_and_prices = u'seats_and_prices'
        event.organization = Organization()
        return event
 
    def test_crud(self):
        DBSession.expire_on_commit = False
        event = self._createTestEvent()
        self.assertEquals(Event.add(event), None)
        DBSession.flush()
        insEvent = Event.get(code=event.code)
        self.assertEquals(insEvent.title, event.title)
        modTitle = u'_test_modified_title'
        insEvent.title = modTitle
        Event.update(insEvent)
        DBSession.refresh(insEvent)
        self.assertEquals(insEvent.title, modTitle)
        self.assertEquals(DBSession.delete(insEvent), None)
        DBSession.flush()
        insEvent = Event.get(code=event.code)
        self.assertEquals(insEvent, None)


if __name__ == "__main__":
    unittest.main()
