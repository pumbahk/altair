# -*- coding:utf-8 -*-
import unittest
import datetime
import transaction
from altair.app.ticketing.core.models import Event, Organization, DBSession
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

def setUpModule():
    DBSession.remove()

def tearDownModule():
    pass

class EventBaseTest(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.orders.models",
            ])

    def tearDown(self):
        _teardown_db()

    def _createTestEvent(self):
        event = Event()
        event.start_on = datetime.datetime(2012, 2, 14, 15, 13, 26, 438062)
        event.end_on = datetime.datetime(2012, 3, 14, 15, 13, 26, 438062)
        event.publish_at = datetime.datetime(2012, 3, 1, 15, 13, 26, 438062)
        event.code = u'_test_code'
        event.title = u'_test_title'
        event.abbreviated_title= u'_test_ab_title'
        event.seats_and_prices = u'seats_and_prices'
        event.organization = Organization(short_name='XX', code='XX')
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
