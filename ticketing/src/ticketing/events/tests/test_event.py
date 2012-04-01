# -*- coding:utf-8 -*-
import unittest
import datetime
import transaction
from ticketing.events.models import Event, session as DBSession

def setUpModule():
    DBSession.remove()

def tearDownModule():
    pass

class EventBaseTest(unittest.TestCase):
                    
    def setUp(self):
        from ticketing import main
        app = main({}, **{"sqlalchemy.url": "mysql://ticketing:ticketing@127.0.0.1/ticketing?use_unicode=true&charset=utf8", 
                          "mako.directories": "ticketing:templates", 
                          "auth.secret": "SDQGxGIhVqSr3zJWV8KvHqHtJujhJj", 
                          "session.secret": "B7gzHVRUqErB1TFgSeLCHH3Ux6ShtI"}) 
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        transaction.abort()
        DBSession.remove()
        
    def _getTestEvent(self):
        event = Event()
        event.start_on = datetime.datetime(2012, 2, 14, 15, 13, 26, 438062)
        event.end_on = datetime.datetime(2012, 3, 14, 15, 13, 26, 438062)
        event.publish_at = datetime.datetime(2012, 3, 1, 15, 13, 26, 438062)
        event.code = u'_test_code'
        event.title = u'_test_title'
        event.abbreviated_title= u'_test_ab_title'
        event.seats_and_prices = u'seats_and_prices'
        return event
 
    def test_crud(self):
        DBSession.expire_on_commit = False
        event = self._getTestEvent()
        self.assertEquals(Event.add(event), None)
        DBSession.flush()
        insEvent = Event.get_by_code(event.code)
        self.assertEquals(insEvent.title, event.title)
        modTitle = u'_test_modified_title'
        insEvent.title = modTitle
        Event.update(insEvent)
        DBSession.refresh(insEvent)
        self.assertEquals(insEvent.title, modTitle)
        self.assertEquals(DBSession.delete(insEvent), None)
        DBSession.flush()
        insEvent = Event.get_by_code(event.code)
        self.assertEquals(insEvent, None)


if __name__ == "__main__":
    unittest.main()
