# coding: utf-8
import unittest
from pyramid import testing
from altaircms import testing as a_testing

def _to_utc(d):
    return d.replace(tzinfo=None) - d.utcoffset()

class EventFromDictTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .api import event_from_dict
        return event_from_dict(*args, **kwargs)

    def test_it(self):
        from datetime import datetime
        data = {
            "id": u"this-is-id",
            "name": u"this-is-name",
            "start_on": u"1970-01-01T12:34:56+09:00",
            "end_on": u"2038-01-01T01:23:45+09:00",
            }

        event = self._callFUT(data)
        
        self.assertEqual(event.backend_event_id, u"this-is-id")
        self.assertEqual(event.name, u"this-is-name")
        self.assertEqual(_to_utc(event.event_on), datetime(1970, 1, 1, 3, 34, 56))


class PerformanceFromDict(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .api import performance_from_dict
        return performance_from_dict(*args, **kwargs)

    def test_it(self):
        from datetime import datetime
        data = {
            "id": "this-is-id",
            "name": "this-is-name",
            "venue": u"this-is-venue",
            "open_on": u"1970-01-01T12:34:56+09:00",
            "start_on": u"2012-01-01T12:34:56+09:00",
            "close_on": u"2038-01-01T23:34:45+09:00",
            }
        performance = self._callFUT(data)

        self.assertEqual(performance.backend_performance_id, "this-is-id")
        self.assertEqual(performance.title, "this-is-name")
        self.assertEqual(performance.venue, "this-is-venue")
        self.assertEqual(_to_utc(performance.open_on), datetime(1970, 1, 1, 3, 34, 56))
        self.assertEqual(_to_utc(performance.start_on), datetime(2012, 1, 1, 3, 34, 56))
        self.assertEqual(_to_utc(performance.close_on), datetime(2038, 1, 1, 14, 34, 45))
        
class SaleFromDictTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .api import sale_from_dict
        return sale_from_dict(*args, **kwargs)

    def test_it(self):
        from datetime import datetime

        data = {
            "name": u"this-is-name",
            "start_on": u"2012-01-01T12:34:56+09:00",
            "end_on": u"2038-01-01T23:34:45+09:00",
            }

        sale = self._callFUT(data)

        self.assertEqual(sale.name, "this-is-name")
        self.assertEqual(_to_utc(sale.start_on), datetime(2012, 1, 1, 3, 34, 56))
        self.assertEqual(_to_utc(sale.end_on), datetime(2038, 1, 1, 14, 34, 45))


class TicketFromDictTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .api import ticket_from_dict
        return ticket_from_dict(*args, **kwargs)

    def test_it(self):
        from datetime import datetime

        data = {
            'name': u'this-is-name',
            'price': 9876,
            'seat_type': u'this-is-seat',
            }

        ticket = self._callFUT(data)

        self.assertEqual(ticket.name, 'this-is-name')
        self.assertEqual(ticket.price, 9876)
        self.assertEqual(ticket.seat_type, 'this-is-seat')

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
        result = self._callFUT(json.loads(self.data))

        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event.name, u"マツイ・オン・アイス")
        self.assertEqual(_to_utc(event.event_on), datetime(2012, 3, 15, 10))
        self.assertEqual(_to_utc(event.event_close), datetime(2012, 3, 15, 13))

        self.assertEqual(len(event.performances), 2)
        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス 東京公演")
        self.assertEqual(performance.venue, u"まついZEROホール")
        self.assertEqual(_to_utc(performance.open_on), datetime(2012, 3, 15, 8))
        self.assertEqual(_to_utc(performance.start_on), datetime(2012, 3, 15, 10))
        self.assertEqual(_to_utc(performance.close_on), datetime(2012, 3, 15, 13))

        self.assertEqual(len(performance.sales), 2)
        
        sale = performance.sales[0]
        self.assertEqual(sale.name, u"presale")
        self.assertEqual(_to_utc(sale.start_on), datetime(2012, 1, 12, 10))
        self.assertEqual(_to_utc(sale.end_on), datetime(2012, 1, 22, 10))

        self.assertEqual(len(sale.tickets), 3)

        ticket = sale.tickets[0]
        self.assertEqual(ticket.name, u"A席大人")
        self.assertEqual(ticket.seat_type, u"A席")
        self.assertEqual(ticket.price, 5000)

    data = """
{
 "created_at": "2012-01-10T13:42:00+09:00",
 "updated_at": "2012-01-11T15:32:00+09:00",
 "events": [
   {
     "id": 1,
     "name": "マツイ・オン・アイス",
     "start_on": "2012-03-15T19:00:00+09:00",
     "end_on": "2012-03-15T22:00:00+09:00",
     "performances": [
       {
         "id": 2,
         "name": "マツイ・オン・アイス 東京公演",
         "venue": "まついZEROホール",
         "open_on": "2012-03-15T17:00:00+09:00",
         "start_on": "2012-03-15T19:00:00+09:00",
         "close_on": "2012-03-15T22:00:00+09:00",
         "sales": [
           {
             "name": "presale",
             "start_on": "2012-01-12T19:00:00+09:00",
             "end_on": "2012-01-22T19:00:00+09:00",
             "tickets": [
               {
                 "name": "A席大人",
                 "seat_type": "A席",
                 "price": 5000
               },
               {
                 "name": "A席子供",
                 "seat_type": "A席",
                 "price": 3000
               },
               {
                 "name": "B席",
                 "seat_type": "B席",
                 "price": 3000
               }
             ]
           },
           {
             "name": "normal",
             "start_on": "2012-01-23T19:00:00+09:00",
             "end_on": "2012-01-31T19:00:00+09:00",
             "tickets": [
               {
                 "name": "A席大人",
                 "seat_type": "A席",
                 "price": 5000
               },
               {
                 "name": "A席子供",
                 "seat_type": "A席",
                 "price": 3000
               },
               {
                 "name": "B席",
                 "seat_type": "B席",
                 "price": 3000
               }
             ]
           }
         ]
       },
       {
         "id": 3,
         "name": "マツイ・オン・アイス 大阪公演",
         "venue": "心斎橋まつい会館",
         "open_on": "2012-03-16T17:00:00+09:00",
         "start_on": "2012-03-16T19:00:00+09:00",
         "close_on": "2012-03-16T22:00:00+09:00",
         "sales": [
           {
             "name": "presale",
             "start_on": "2012-01-12T19:00:00+09:00",
             "end_on": "2012-01-22T19:00:00+09:00",
             "tickets": [
               {
                 "name": "A席大人",
                 "seat_type": "A席",
                 "price": 5000
               },
               {
                 "name": "A席子供",
                 "seat_type": "A席",
                 "price": 3000
               },
               {
                 "name": "B席",
                 "seat_type": "B席",
                 "price": 3000
               }
             ]
           },
           {
             "name": "normal",
             "start_on": "2012-01-23T19:00:00+09:00",
             "end_on": "2012-01-31T19:00:00+09:00",
             "tickets": [
               {
                 "name": "A席大人",
                 "seat_type": "A席",
                 "price": 5000
               },
               {
                 "name": "A席子供",
                 "seat_type": "A席",
                 "price": 3000
               },
               {
                 "name": "B席",
                 "seat_type": "B席",
                 "price": 3000
               }
             ]
           }
         ]
       }
     ]
   }
 ]
}
"""

class ValidateAPIKeyTests(unittest.TestCase):
    def setUp(self):
        from altaircms.lib.testutils import _initTestingDB
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

        

# class TestEventView(unittest.TestCase):
#     def setUp(self):
#         self.config = testing.setUp()
        
#     def tearDown(self):
#         testing.tearDown()
#         import transaction
#         transaction.abort()

#     def _getTarget(self):
#         from .views import EventRESTAPIView
#         return EventRESTAPIView

#     def _makeOne(self, request):
#         return self._getTarget()(request)

#     def test_create_invalid(self):
#         # null post
#         request = testing.DummyRequest()

#         target = self._makeOne(request)
#         result = target.create()

#         self.assertEqual(result.status_int, 400)

#     def test_create_valid(self):
#         self._fill_request_post()
#         request = testing.DummyRequest(POST=self._fill_request_post())

#         target = self._makeOne(request)
#         result = target.create()

#         self.assertEqual(result.status_int, 201)
#         self.assertEqual(result.message, None)

#     def test_read(self):
#         self._insert_event()

#         # list object
#         resp = EventRESTAPIView(self.request).read()
#         self.assertTrue(str(resp).startswith("{'events': ["))

#         # read object
#         resp = EventRESTAPIView(self.request, '1').read()
#         self.assertTrue(str(resp).startswith("{'inquiry_for':"))

#     def test_delete(self):
#         self._insert_event()

#         resp = EventRESTAPIView(self.request, '1').delete()
#         self.assertEqual(resp.status_int, 200)

#         resp = EventRESTAPIView(self.request, '999').delete()
#         self.assertEqual(resp.status_int, 400)

#     def _insert_event(self):


#     def _fill_request_post(self):
#         return dict(
#             (u'title', u'たいとる'),
#             (u'subtitle', u'サブタイトル'),
#             (u'description', u'説明'),
#             (u'event_open', u'2011-1-1 00:00:00'),
#             (u'event_close', u'2011-12-31 23:59:59'),
#             (u'deal_open', u'2011-12-31 23:59:59'),
#             (u'deal_close', u'2011-12-31 23:59:59'),
#             (u'is_searchable', u'y'),
#             )

class DummyValidator(object):
    def __init__(self, apikey):
        self.apikey = apikey
        self.called = []

    def __call__(self, apikey):
        self.called.append(('__call__', apikey))
        return self.apikey == apikey

class DummyEventRepositry(testing.DummyResource):
    def parse_and_save_event(self, data):
        self.called_data = data

class TestEventRegister(unittest.TestCase):
    
    def setUp(self):
        self.config = testing.setUp()


    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from .views import event_register
        return event_register(request)


    def test_event_register_ok(self):
        from .interfaces import IAPIKEYValidator, IEventRepositiry
        validator = DummyValidator('hogehoge')
        repository = DummyEventRepositry()
        self.config.registry.registerUtility(validator, IAPIKEYValidator)
        self.config.registry.registerUtility(repository, IEventRepositiry)

        headers = {'X-Altair-Authorization': 'hogehoge'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                         headers=headers,
                                         POST={'jsonstring': '{}'},
                                         )

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 201)
        self.assertEqual(repository.called_data, {})


    def test_event_register_ng(self):
        from .interfaces import IAPIKEYValidator
        validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(validator, IAPIKEYValidator)
        # 認証パラメタなし
        request = a_testing.DummyRequest(POST={})

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 403)

    def test_event_register_ng2(self):
        from .interfaces import IAPIKEYValidator
        validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(validator, IAPIKEYValidator)

        # 認証通過、必須パラメタなし
        headers = {'X-Altair-Authorization': 'hogehoge'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                       POST={}, 
                                       headers=headers)

        response = self._callFUT(request)

        self.assertEqual(response.status_int, 400)

    def test_event_register_ng3(self):
        from .interfaces import IAPIKEYValidator
        validator = DummyValidator('hogehoge')
        self.config.registry.registerUtility(validator, IAPIKEYValidator)

        # パースできないJSON
        headers = {'X-Altair-Authorization': 'hogehoge'}
        POST = {'jsonstring': 'aaaaaaaaaaa'}
        request = a_testing.DummyRequest(registry=self.config.registry,
                                         headers=headers,
                                         POST=POST)
        response = self._callFUT(request)

        self.assertEqual(response.status_int, 400)
