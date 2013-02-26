# coding: utf-8
import unittest
import json
from pyramid import testing
from altaircms import testing as a_testing
from altaircms.event.api import EventRepositry
from altaircms.event.interfaces import IAPIKeyValidator, IEventRepository

def setUpModule():
    from altaircms.testing import setup_db
    setup_db(["altaircms.page.models", 
              "altaircms.tag.models", 
              "altaircms.layout.models", 
              "altaircms.widget.models", 
              "altaircms.event.models", 
              "altaircms.asset.models"])

def tearDown():
    from altaircms.testing import teardown_db
    teardown_db()

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

    def test_delete_cascade_for_performance_children(self):
        """
        cascade chain: Event -> Performance -> SalesSegment -> Ticket
        """
        from altaircms.models import Performance, SalesSegment, Ticket

        target = Performance()
        
        sale0 = SalesSegment(performance=target)
        sale1 = SalesSegment(performance=target)

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
        self.assertTrue(all(s in self.session.deleted for s in SalesSegment.query))
        self.assertTrue(all(t in self.session.deleted for t in Ticket.query))
        

class ParseAndSaveEventTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.event.api import parse_and_save_event
        return parse_and_save_event(*args, **kwargs)


    data = """
{"created_at": "2012-06-20T10:33:34",
 "updated_at": "2012-06-20T10:33:34", 
 "organization": {"id": 1000, "short_name": "demo"}, 
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
                               "sales": [{"end_on": "2012-01-22T10:00:00",
                                          "id": 39,
                                          "kind": "first_lottery",
                                          "name": "一般先行",
                                          "tickets": [{"id": 571,
                                                       "name": "B席右",
                                                       "price": 2000,
                                                       "seat_type": "B席"},
                                                      {"id": 572,
                                                       "name": "B席左",
                                                       "price": 2000.0,
                                                       "seat_type": "B席"},
                                                      {"id": 599,
                                                       "name": "S席大人",
                                                       "price": 20000.0,
                                                       "seat_type": "S席"},
                                                      {"id": 600,
                                                       "name": "A席大人",
                                                       "price": 8000.0,
                                                       "seat_type": "A席"}],
                                          "seat_choice": false,
                                          "start_on": "2012-01-12T10:00:00"}],
                               "venue": "まついZEROホール"},
                              {"end_on": "2012-03-26T21:00:00",
                               "id": 97,
                               "name": "マツイ・オン・アイス(大阪公演)",
                               "open_on": "2012-03-26T18:00:00",
                               "prefecture": "osaka",
                               "start_on": "2012-03-26T19:00:00",
                               "sales": [{"end_on": "2012-03-12T00:00:00",
                                          "id": 40,
                                          "kind": "normal",
                                          "name": "一般販売",
                                          "tickets": [{"id": 1571,
                                                       "name": "B席右",
                                                       "price": 1000,
                                                       "seat_type": "B席"},
                                                      {"id": 1572,
                                                       "name": "B席左",
                                                       "price": 1000.0,
                                                       "seat_type": "B席"},
                                                      {"id": 1599,
                                                       "name": "S席大人",
                                                       "price": 10000.0,
                                                       "seat_type": "S席"},
                                                      {"id": 1600,
                                                       "name": "A席大人",
                                                       "price": 4000.0,
                                                       "seat_type": "A席"}
                                                     ],
                                          "seat_choice": true,
                                          "start_on": "2012-01-23T10:00:00"}], 
                               "venue": "マツイ市民会館"}
                             ], 
             "start_on": "2012-03-15T10:00:00",
             "subtitle": "なし",
             "title": "マツイ・オン・アイス"}]}
    """

    data_for_delete = """
{"created_at": "2012-06-20T10:33:34",
 "updated_at": "2012-06-20T10:33:34", 
 "organization": {"id": 1000, "short_name": "demo"}, 
 "events": [{"deal_close": "2012-12-25T00:00:01",
             "deal_open": "2012-10-25T10:00:00",
             "end_on": "2012-03-15T13:00:00",
             "id": 20,
             "organization_id": 1000, 
             "performances": [{"deleted": true,
                               "id": 96}, 
                              {"end_on": "2012-03-26T21:00:00",
                               "id": 97,
                               "name": "マツイ・オン・アイス(大阪公演)",
                               "open_on": "2012-03-26T18:00:00",
                               "prefecture": "osaka",
                               "start_on": "2012-03-26T19:00:00",
                               "sales": [{"end_on": "2012-03-12T00:00:00",
                                          "id": 40,
                                          "kind": "normal",
                                          "name": "一般販売",
                                          "tickets": [{"id": 1571,
                                                       "deleted": true}, 
                                                      {"id": 1572,
                                                       "deleted": true}, 
                                                      {"id": 1599,
                                                       "name": "S席大人",
                                                       "price": 10000.0,
                                                       "seat_type": "S席"},
                                                      {"id": 1600,
                                                       "name": "A席大人",
                                                       "price": 4000.0,
                                                       "seat_type": "A席"}
                                                     ],
                                          "seat_choice": true,
                                          "start_on": "2012-01-23T10:00:00"}], 
                               "venue": "マツイ市民会館"}
                             ], 
             "start_on": "2012-03-15T10:00:00",
             "subtitle": "なし",
             "title": "マツイ・オン・アイス"}]}
    """

    def tearDown(self):
        import transaction
        transaction.abort()

    def test_it(self):
        from datetime import datetime
        from altaircms.auth.models import Organization
        from altaircms.models import Ticket
        request = testing.DummyRequest()
        result = self._callFUT(request, json.loads(self.data))

        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event.title, u"マツイ・オン・アイス")
        self.assertEqual(event.backend_id, 20) #backend id
        self.assertEqual(event.event_open, datetime(2012, 3, 15, 10))
        self.assertEqual(event.event_close, datetime(2012, 3, 15, 13))
        self.assertNotEqual(event.organization_id, 1000)
        self.assertEqual(event.organization_id, Organization.query.filter_by(backend_id=1000).one().id)
        self.assertEqual(len(event.performances), 2)

        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス(東京公演)")
        self.assertEqual(performance.backend_id, 96)
        self.assertEqual(performance.venue, u"まついZEROホール")
        self.assertEqual(performance.open_on, datetime(2012, 3, 15, 8))
        self.assertEqual(performance.start_on, datetime(2012, 3, 15, 10))
        self.assertEqual(performance.end_on, datetime(2012, 3, 15, 13))

        ## todo:change
        self.assertEqual(len(performance.sales), 1)
        
        sale = performance.sales[0]
        self.assertEqual(sale.group.name, u"一般先行")
        self.assertEqual(sale.backend_id, 39)
        self.assertEqual(sale.start_on, datetime(2012, 1, 12, 10))
        self.assertEqual(sale.end_on, datetime(2012, 1, 22, 10))

        self.assertEqual(Ticket.query.count(), 8)
        self.assertEqual(len(sale.tickets), 4)

        ticket = performance.sales[0].tickets[0]
        self.assertEqual(ticket.backend_id, 599)
        self.assertEqual(ticket.name, u"S席大人")
        self.assertEqual(ticket.seattype, u"S席")
        self.assertEqual(ticket.price, 20000)

    def test_create_and_delete(self):
        from datetime import datetime
        from altaircms.auth.models import Organization
        request = testing.DummyRequest()
        from altaircms.models import DBSession
        ## create
        result = self._callFUT(request, json.loads(self.data))
        ## delete
        result = self._callFUT(request, json.loads(self.data_for_delete))

        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event.title, u"マツイ・オン・アイス")
        self.assertEqual(event.backend_id, 20) #backend id
        self.assertEqual(event.event_open, datetime(2012, 3, 15, 10))
        self.assertEqual(event.event_close, datetime(2012, 3, 15, 13))
        self.assertNotEqual(event.organization_id, 1000)
        self.assertEqual(event.organization_id, Organization.query.filter_by(backend_id=1000).one().id)
        self.assertEqual(len(event.performances), 1)

        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス(大阪公演)")
        self.assertEqual(performance.backend_id, 97)
        self.assertEqual(performance.venue, u"マツイ市民会館")
        self.assertEqual(performance.open_on, datetime(2012, 3, 26, 18))
        self.assertEqual(performance.start_on, datetime(2012, 3, 26, 19))
        self.assertEqual(performance.end_on, datetime(2012, 3, 26, 21))

        ## todo:change
        self.assertEqual(len(performance.sales), 1)
        
        sale = performance.sales[0]
        self.assertEqual(sale.group.name, u"一般販売")
        self.assertEqual(sale.backend_id, 40)
        self.assertEqual(sale.start_on, datetime(2012, 1, 23, 10))
        self.assertEqual(sale.end_on, datetime(2012, 3, 12, 0))


        self.assertEqual(len(sale.tickets), 2)

        ticket = performance.sales[0].tickets[0]
        self.assertEqual(ticket.backend_id, 1599)
        self.assertEqual(ticket.name, u"S席大人")
        self.assertEqual(ticket.seattype, u"S席")
        self.assertEqual(ticket.price, 10000)

    def test_register_multiple(self):
        from altaircms.models import Ticket, Performance, SalesSegment

        request = testing.DummyRequest()
        result = self._callFUT(request, json.loads(self.data))
        fst_performance_count = Performance.query.count()
        fst_sale_count = SalesSegment.query.count()
        fst_ticket_count = Ticket.query.count()

        result = self._callFUT(request, json.loads(self.data))
        self.assertEquals(fst_performance_count, Performance.query.count())
        self.assertEquals(fst_sale_count, SalesSegment.query.count())
        self.assertEquals(fst_ticket_count, Ticket.query.count())


class ValidateAPIKeyTests(unittest.TestCase):
    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _callFUT(self, *args, **kwargs):
        from altaircms.event.api import validate_apikey
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
        import sqlahelper
        self.session = sqlahelper.get_session()
        self.validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(self.validator, IAPIKeyValidator)

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from altaircms.event.views import event_register
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
        
if __name__ == "__main__":
    unittest.main()
