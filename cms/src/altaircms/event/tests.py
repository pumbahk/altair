# coding: utf-8
import unittest
from pyramid import testing
from altaircms import testing as a_testing
from altaircms.lib.testutils import _initTestingDB
from .api import EventRepositry
from .interfaces import IAPIKeyValidator, IEventRepository

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

def _to_utc(d):
    return d.replace(tzinfo=None) - d.utcoffset()

class CascadeDeleteTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()

    def test_delete_event_cascade_performance(self):
        from altaircms.event.models import Event
        from altaircms.models import Performance

        target = Event()
        per = Performance(event=target, backend_id=1)
        self.session.add(per)


        self.session.flush()
        self.session.delete(target)

        self.assertTrue(all(p in self.session.deleted for p in target.performances))
        self.assertEquals(Performance.query.count(), 0)

    def test_delete_performance_not_cascade_event(self):
        from altaircms.event.models import Event
        from altaircms.models import Performance

        target = Event()
        per = Performance(event=target, backend_id=1)
        self.session.add(per)


        self.session.flush()
        self.session.delete(per)

        self.assertTrue(target not in self.session.deleted)
        self.assertEquals(Performance.query.count(), 0)
        self.assertEquals(Event.query.count(), 1)

    def test_delete_cascade_for_event_children(self):
        """
        cascade chain: Event -> Performance -> Sale -> Ticket
        """
        from altaircms.event.models import Event
        from altaircms.models import Performance, Sale, Ticket

        target = Event()
        sale0 = Sale(name="a", kind=u"normal", event=target)
        sale1 = Sale(name="b", kind=u"normal", event=target)

        self.session.add_all([Ticket(sale=sale0, price=i) for i in [100, 200, 300, 400, 500]])
        self.session.add_all([Ticket(sale=sale1, price=i) for i in [100, 200, 300, 400, 500]])
        self.session.add(target)


        ## before delete target event instance check
        self.assertFalse(target in self.session.deleted)

        ## delete event
        self.session.flush()
        self.session.delete(target)

        ## after delete target event instance check
        self.assertTrue(target in self.session.deleted)
        self.assertTrue(all(p in self.session.deleted for p in Performance.query))
        self.assertTrue(all(s in self.session.deleted for s in Sale.query))
        self.assertTrue(all(t in self.session.deleted for t in Ticket.query))
        
        
class ParseAndSaveEventTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _callFUT(self, *args, **kwargs):
        from .api import parse_and_save_event
        return parse_and_save_event(*args, **kwargs)

    def test_it(self):
        from datetime import datetime
        import json
        request = testing.DummyRequest()
        result = self._callFUT(request, json.loads(self.data))

        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event.title, u"マツイ・オン・アイス")
        self.assertEqual(event.backend_id, 20) #backend id
        self.assertEqual(event.event_open, datetime(2012, 3, 15, 10))
        self.assertEqual(event.event_close, datetime(2012, 3, 15, 13))
        self.assertEqual(event.organization_id, 1000)
        self.assertEqual(len(event.performances), 2)

        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス(東京公演)")
        self.assertEqual(performance.backend_id, 96)
        self.assertEqual(performance.venue, u"まついZEROホール")
        self.assertEqual(performance.open_on, datetime(2012, 3, 15, 8))
        self.assertEqual(performance.start_on, datetime(2012, 3, 15, 10))
        self.assertEqual(performance.end_on, datetime(2012, 3, 15, 13))

        ## todo:change
        self.assertEqual(len(event.sales), 2)
        
        sale = event.sales[0]
        self.assertEqual(sale.name, u"一般先行")
        self.assertEqual(sale.backend_id, 39)
        self.assertEqual(sale.start_on, datetime(2012, 1, 12, 10))
        self.assertEqual(sale.end_on, datetime(2012, 1, 22, 10))


        self.assertEqual(len(performance.tickets), 4)

        ticket = sale.tickets[0]
        self.assertEqual(ticket.backend_id, 571)
        self.assertEqual(ticket.name, u"B席右")
        self.assertEqual(ticket.seattype, u"B席")
        self.assertEqual(ticket.price, 1000)

        ### check bound performance to ticket relation
        self.assertEquals(len(performance.tickets), 4)
        self.assertIn(ticket, performance.tickets)



    data = """
{"created_at": "2012-06-20T10:33:34",
 "events": [{"deal_close": "2012-12-25T00:00:01",
              "deal_open": "2012-10-25T10:00:00",
              "end_on": "2012-03-15T13:00:00",
              "id": 20,
              "organization_id": 1000, 
              "performances": [{"end_on": "2012-03-15T13:00:00",
                                 "id": 96,
                                 "name": "マツイ・オン・アイス(東京公演)",
                                 "open_on": "2012-03-15T08:00:00",
                                 "prefecture": "tokyo",
                                 "start_on": "2012-03-15T10:00:00",
                                 "tickets": [571,
                                              572,
                                              599,
                                              600],
                                 "venue": "まついZEROホール"},
                                {"end_on": "2012-03-26T21:00:00",
                                 "id": 97,
                                 "name": "マツイ・オン・アイス(大阪公演)",
                                 "open_on": "2012-03-26T18:00:00",
                                 "prefecture": "osaka",
                                 "start_on": "2012-03-26T19:00:00",
                                 "tickets": [571,
                                              572,
                                              599,
                                              600],
                                 "venue": "マツイ市民会館"}],
              "sales": [{"end_on": "2012-01-22T10:00:00",
                          "id": 39,
                          "kind": "first_lottery",
                          "name": "一般先行",
                          "seat_choice": false,
                          "start_on": "2012-01-12T10:00:00"},
                         {"end_on": "2012-03-12T00:00:00",
                          "id": 40,
                          "kind": "normal",
                          "name": "一般販売",
                          "seat_choice": true,
                          "start_on": "2012-01-23T10:00:00"}],
              "start_on": "2012-03-15T10:00:00",
              "subtitle": "なし",
              "tickets": [{"id": 571,
                            "name": "B席右",
                            "price": 1000,
                            "sale_id": 39,
                            "seat_type": "B席"},
                           {"id": 572,
                            "name": "B席左",
                            "price": 1000.0,
                            "sale_id": 39,
                            "seat_type": "B席"},
                           {"id": 599,
                            "name": "S席大人",
                            "price": 10000.0,
                            "sale_id": 40,
                            "seat_type": "S席"},
                           {"id": 600,
                            "name": "A席大人",
                            "price": 4000.0,
                            "sale_id": 40,
                            "seat_type": "A席"}],
              "title": "マツイ・オン・アイス"}],
 "updated_at": "2012-06-20T10:33:34"}
    """

    def test_register_multiple(self):
        import json
        from ..models import Ticket, Performance, Sale

        request = testing.DummyRequest()
        result = self._callFUT(request, json.loads(self.data))
        fst_performance_count = Performance.query.count()
        fst_sale_count = Sale.query.count()
        fst_ticket_count = Ticket.query.count()

        result = self._callFUT(request, json.loads(self.data))
        self.assertEquals(fst_performance_count, Performance.query.count())
        self.assertEquals(fst_sale_count, Sale.query.count())
        self.assertEquals(fst_ticket_count, Ticket.query.count())



class ValidateAPIKeyTests(unittest.TestCase):
    def setUp(self):
        self.session = _initTestingDB()

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _callFUT(self, *args, **kwargs):
        from .api import validate_apikey
        return validate_apikey(*args, **kwargs)

    def test_ok(self):
        from altaircms.auth.models import APIKey

        apikey = "hogehoge"
        d = APIKey(apikey=apikey)
        self.session.add(d)

        result = self._callFUT(apikey)

        self.assertTrue(result)

    def test_ng(self):
        apikey = "hogehoge"
        result = self._callFUT(apikey)

        self.assertFalse(result)

class DummyValidator(object):
    def __init__(self, apikey):
        self.apikey = apikey
        self.called = []

    def __call__(self, apikey):
        self.called.append(('__call__', apikey))
        return self.apikey == apikey

class DummyEventRepositry(testing.DummyResource):
    def parse_and_save_event(self, request, data):
        self.request = request
        self.called_data = data

class TestEventRegister(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()
        self.validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(self.validator, IAPIKeyValidator)

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from .views import event_register
        return event_register(request)

    def test_event_register_ok(self):
        repository = DummyEventRepositry()
        self.config.registry.registerUtility(repository, IEventRepository)
        headers = {'X-Altair-Authorization': 'hogehoge'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                         headers=headers,
                                         json_body={}
                                         )
        response = self._callFUT(request)

        self.assertEqual(response.status_int, 201)
        self.assertEqual(repository.called_data, {})

    def test_event_register_ng(self):
        # 認証パラメタなし
        repository = DummyEventRepositry()
        self.config.registry.registerUtility(repository, IEventRepository)
        request = a_testing.DummyRequest(json_body={})

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 403)

    def test_event_register_ng2(self):
        # 認証通過、必須パラメタなし
        self.config.registry.registerUtility(EventRepositry(), IEventRepository)
        headers = {'X-Altair-Authorization': 'hogehoge'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                         json_body={}, 
                                         headers=headers)

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 400)
        
