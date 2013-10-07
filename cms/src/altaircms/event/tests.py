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
{
  "organization": {
    "id": 1000, 
    "code": "RT", 
    "short_name": "demo"
  }, 
  "created_at": "2012-06-20T10:33:34", 
  "events": [
    {
      "organization_id": 1000, 
      "code": "DM399", 
      "subtitle": "なし", 
      "title": "マツイ・オン・アイス", 
      "performances": [
        {
          "end_on": "2013-03-15T13:00:00", 
          "start_on": "2013-03-15T10:00:00", 
          "name": "マツイ・オン・アイス(東京公演)", 
          "open_on": "2013-03-15T08:00:00", 
          "prefecture": "tokyo", 
          "venue": "まついZEROホール", 
          "code": "this-is-code", 
          "id": 40096, 
          "sales": [
            {
              "tickets": [
                {
                  "display_order": 3, 
                  "price": 2000.0, 
                  "seat_type": "B席", 
                  "id": 400571, 
                  "name": "B席右"
                }, 
                {
                  "display_order": 4, 
                  "price": 2000.0, 
                  "seat_type": "B席", 
                  "id": 400572, 
                  "name": "B席左"
                }, 
                {
                  "display_order": 1, 
                  "price": 20000.0, 
                  "seat_type": "S席", 
                  "id": 400599, 
                  "name": "S席大人"
                }, 
                {
                  "display_order": 2, 
                  "price": 8000.0, 
                  "seat_type": "A席", 
                  "id": 400600, 
                  "name": "A席大人"
                }
              ], 
              "group_id": 1, 
              "start_on": "2012-01-12T10:00:00", 
              "kind_name": "first_lottery", 
              "name": "一般先行", 
              "seat_choice": "false", 
              "end_on": "2012-01-22T10:00:00", 
              "id": 40039, 
              "kind_label": "最速抽選"
            }
          ]
        }, 
        {
          "end_on": "", 
          "start_on": "2013-03-26T19:00:00", 
          "name": "マツイ・オン・アイス(大阪公演)", 
          "open_on": "", 
          "prefecture": "osaka", 
          "venue": "まつい市民会館", 
          "id": 40097, 
          "sales": [
            {
              "tickets": [
                {
                  "display_order": 3, 
                  "price": 1000.0, 
                  "seat_type": "B席", 
                  "id": 401571, 
                  "name": "B席右"
                }, 
                {
                  "display_order": 4, 
                  "price": 1000.0, 
                  "seat_type": "B席", 
                  "id": 401572, 
                  "name": "B席左"
                }, 
                {
                  "display_order": 1, 
                  "price": 10000.0, 
                  "seat_type": "S席", 
                  "id": 401599, 
                  "name": "S席大人"
                }, 
                {
                  "display_order": 2, 
                  "price": 4000.0, 
                  "seat_type": "A席", 
                  "id": 401600, 
                  "name": "A席大人"
                }
              ], 
              "group_id": 2, 
              "start_on": "2012-01-23T10:00:00", 
              "kind_name": "normal", 
              "name": "一般販売", 
              "seat_choice": "false", 
              "end_on": "", 
              "id": 40040, 
              "kind_label": "一般販売"
            }
          ]
        }
      ], 
      "id": 40020
    }
  ], 
  "updated_at": "2012-06-20T10:33:34"
}
    """

    data_for_delete = """
{
  "organization": {
    "id": 1000, 
    "code": "RT", 
    "short_name": "demo"
  }, 
  "created_at": "2012-06-20T10:33:34", 
  "events": [
    {
      "organization_id": 1000, 
      "code": "DM399", 
      "subtitle": "なし", 
      "title": "マツイ・オン・アイス", 
      "performances": [
        {
          "end_on": "2013-03-15T13:00:00", 
          "start_on": "2013-03-15T10:00:00", 
          "name": "マツイ・オン・アイス(東京公演)", 
          "open_on": "2013-03-15T08:00:00", 
          "deleted": "true", 
          "prefecture": "tokyo", 
          "venue": "まついZEROホール", 
          "id": 40096, 
          "sales": [
            {
              "tickets": [
                {
                  "name": "B席右", 
                  "deleted": "true", 
                  "display_order": 3, 
                  "id": 400571, 
                  "seat_type": "B席", 
                  "price": 2000.0
                }, 
                {
                  "name": "B席左", 
                  "deleted": "true", 
                  "display_order": 4, 
                  "id": 400572, 
                  "seat_type": "B席", 
                  "price": 2000.0
                }, 
                {
                  "name": "S席大人", 
                  "deleted": "true", 
                  "display_order": 1, 
                  "id": 400599, 
                  "seat_type": "S席", 
                  "price": 20000.0
                }, 
                {
                  "name": "A席大人", 
                  "deleted": "true", 
                  "display_order": 2, 
                  "id": 400600, 
                  "seat_type": "A席", 
                  "price": 8000.0
                }
              ], 
              "deleted": "true", 
              "group_id": 1, 
              "start_on": "2012-01-12T10:00:00", 
              "kind_name": "first_lottery", 
              "name": "一般先行", 
              "seat_choice": "false", 
              "end_on": "2012-01-22T10:00:00", 
              "id": 40039, 
              "kind_label": "最速抽選"
            }
          ]
        }, 
        {
          "end_on": "", 
          "start_on": "2013-03-26T19:00:00", 
          "name": "マツイ・オン・アイス(大阪公演)", 
          "open_on": "", 
          "prefecture": "osaka", 
          "venue": "まつい市民会館", 
          "id": 40097, 
          "sales": [
            {
              "tickets": [
                {
                  "display_order": 3, 
                  "price": 1000.0, 
                  "seat_type": "B席", 
                  "id": 401571, 
                  "name": "B席右"
                }, 
                {
                  "name": "B席左", 
                  "deleted": "true", 
                  "display_order": 4, 
                  "id": 401572, 
                  "seat_type": "B席", 
                  "price": 1000.0
                }, 
                {
                  "name": "S席大人", 
                  "deleted": "true", 
                  "display_order": 1, 
                  "id": 401599, 
                  "seat_type": "S席", 
                  "price": 10000.0
                }, 
                {
                  "display_order": 2, 
                  "price": 4000.0, 
                  "seat_type": "A席", 
                  "id": 401600, 
                  "name": "A席大人"
                }
              ], 
              "group_id": 2, 
              "start_on": "2012-01-23T10:00:00", 
              "kind_name": "normal", 
              "name": "一般販売", 
              "seat_choice": "false", 
              "end_on": "", 
              "id": 40040, 
              "kind_label": "一般販売"
            }
          ]
        }
      ], 
      "id": 40020
    }
  ], 
  "updated_at": "2012-06-20T10:33:34"
}
    """

    def tearDown(self):
        import transaction
        transaction.abort()

    @unittest.skip ("* #5609: must fix")
    def test_it(self):
        from datetime import datetime
        from altaircms.auth.models import Organization
        from altaircms.models import Ticket
        request = testing.DummyRequest()
        result = self._callFUT(request, json.loads(self.data))

        organization = Organization.query.filter_by(backend_id=1000).one()
        self.assertEqual(organization.short_name, "demo")
        self.assertEqual(organization.code, "RT")
        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event.title, u"マツイ・オン・アイス")
        self.assertEqual(event.backend_id, 40020) #backend id
        self.assertEqual(event.event_open, datetime(2013, 3, 15, 10))
        self.assertEqual(event.event_close, datetime(2013, 3, 26, 19))
        self.assertNotEqual(event.organization_id, 1000)
        self.assertEqual(event.organization_id, organization.id)
        self.assertEqual(len(event.performances), 2)

        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス(東京公演)")
        self.assertEqual(performance.backend_id, 40096)
        self.assertEqual(performance.code, u"this-is-code")
        self.assertEqual(performance.venue, u"まついZEROホール")
        self.assertEqual(performance.open_on, datetime(2013, 3, 15, 8))
        self.assertEqual(performance.start_on, datetime(2013, 3, 15, 10))
        self.assertEqual(performance.display_order, 50)
        self.assertEqual(performance.end_on, datetime(2013, 3, 15, 13))

        ## todo:change
        self.assertEqual(len(performance.sales), 1)
        
        sale = performance.sales[0]
        self.assertEqual(sale.group.name, u"一般先行")
        self.assertEqual(sale.group.backend_id, 1)
        self.assertEqual(sale.backend_id, 40039)
        self.assertEqual(sale.start_on, datetime(2012, 1, 12, 10))
        self.assertEqual(sale.end_on, datetime(2012, 1, 22, 10))

        self.assertEqual(Ticket.query.count(), 8)
        self.assertEqual(len(sale.tickets), 4)

        ticket = performance.sales[0].tickets[0]
        self.assertEqual(ticket.backend_id, 400599)
        self.assertEqual(ticket.name, u"S席大人")
        self.assertEqual(ticket.seattype, u"S席")
        self.assertEqual(ticket.display_order, 1)
        self.assertEqual(ticket.price, 20000)

        ## todo: refactoring
        from altaircms.models import SalesSegmentGroup, SalesSegmentKind
        self.assertEqual(SalesSegmentGroup.query.count(), 2)
        self.assertEqual(SalesSegmentKind.query.count(), 2)

    @unittest.skip ("* #5609: must fix")
    def test_create_and_delete(self):
        from datetime import datetime
        from altaircms.auth.models import Organization
        request = testing.DummyRequest()
        ## create
        result = self._callFUT(request, json.loads(self.data))
        ## delete indclude
        result = self._callFUT(request, json.loads(self.data_for_delete))

        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event.title, u"マツイ・オン・アイス")
        self.assertEqual(event.backend_id, 40020) #backend id
        self.assertEqual(event.event_open, datetime(2013, 3, 26, 19))
        self.assertEqual(event.event_close, datetime(2013, 3, 26, 19))
        self.assertNotEqual(event.organization_id, 1000)
        self.assertEqual(event.organization_id, Organization.query.filter_by(backend_id=1000).one().id)

        self.assertEqual(len(event.performances), 1)

        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス(大阪公演)")
        self.assertEqual(performance.backend_id, 40097)
        self.assertEqual(performance.venue, u"まつい市民会館")
        self.assertEqual(performance.open_on, None)
        self.assertEqual(performance.start_on, datetime(2013, 3, 26, 19))
        self.assertEqual(performance.end_on, None)

        ## todo:change
        self.assertEqual(len(performance.sales), 1)
        
        sale = performance.sales[0]
        self.assertEqual(sale.group.name, u"一般販売")
        self.assertEqual(sale.backend_id, 40040)
        self.assertEqual(sale.start_on, datetime(2012, 1, 23, 10))
        self.assertEqual(sale.end_on, None)


        ## todo: refactoring
        from altaircms.models import SalesSegmentGroup, SalesSegmentKind
        self.assertEqual(SalesSegmentGroup.query.count(), 2)
        self.assertEqual(SalesSegmentKind.query.count(), 2)

        self.assertEqual(len(sale.tickets), 2)

        ticket = performance.sales[0].tickets[0]
        self.assertEqual(ticket.backend_id, 401600)
        self.assertEqual(ticket.name, u"A席大人")
        self.assertEqual(ticket.seattype, u"A席")
        self.assertEqual(ticket.price, 4000)



    @unittest.skip ("* #5609: must fix")
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

    @unittest.skip ("* #5609: must fix")
    def test_first_deleted_include(self):
        from datetime import datetime
        from altaircms.auth.models import Organization
        request = testing.DummyRequest()
        ## delete indclude
        result = self._callFUT(request, json.loads(self.data_for_delete))

        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event.title, u"マツイ・オン・アイス")
        self.assertEqual(event.backend_id, 40020) #backend id
        self.assertEqual(event.event_open, datetime(2013, 3, 26, 19))
        self.assertEqual(event.event_close, datetime(2013, 3, 26, 19))
        self.assertNotEqual(event.organization_id, 1000)
        self.assertEqual(event.organization_id, Organization.query.filter_by(backend_id=1000).one().id)

        self.assertEqual(len(event.performances), 1)

        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス(大阪公演)")
        self.assertEqual(performance.backend_id, 40097)
        self.assertEqual(performance.venue, u"まつい市民会館")
        self.assertEqual(performance.open_on, None)
        self.assertEqual(performance.start_on, datetime(2013, 3, 26, 19))
        self.assertEqual(performance.end_on, None)

        ## todo:change
        self.assertEqual(len(performance.sales), 1)
        
        sale = performance.sales[0]
        self.assertEqual(sale.group.name, u"一般販売")
        self.assertEqual(sale.backend_id, 40040)
        self.assertEqual(sale.start_on, datetime(2012, 1, 23, 10))
        self.assertEqual(sale.end_on, None)


        ## todo: refactoring
        from altaircms.models import SalesSegmentGroup, SalesSegmentKind
        self.assertEqual(SalesSegmentGroup.query.count(), 1)
        self.assertEqual(SalesSegmentKind.query.count(), 1)

        self.assertEqual(len(sale.tickets), 2)

        ticket = performance.sales[0].tickets[0]
        self.assertEqual(ticket.backend_id, 401600)
        self.assertEqual(ticket.name, u"A席大人")
        self.assertEqual(ticket.seattype, u"A席")
        self.assertEqual(ticket.price, 4000)

    def test_parent_is_deleted_children_are_also_deleted(self):
        backend_data = u"""
{
    "created_at": "2013-03-15T18:46:37", 
    "events": [
        {
            "code": "89BZ9", 
            "id": 152, 
            "organization_id": 1, 
            "performances": [
                {
                    "end_on": "2012-01-10T22:00:00", 
                    "id": 547, 
                    "name": "test", 
                    "open_on": "2012-01-10T18:10:00", 
                    "prefecture": null, 
                    "sales": [
                        {
                            "deleted": "true", 
                            "end_on": "2012-12-24T00:00:00", 
                            "group_id": 551, 
                            "id": 1722, 
                            "kind_label": "\u5148\u884c\u5148\u7740", 
                            "kind_name": "early_firstcome", 
                            "name": "\u30b4\u30fc\u30eb\u30c9\u30fb\u30d7\u30e9\u30c1\u30ca\u30fb\u6cd5\u4eba\u5148\u884c\u767a\u58f2\uff08\u65e9\u5272\uff09", 
                            "seat_choice": "true", 
                            "start_on": "2012-12-21T10:00:00", 
                            "tickets": [
                                {
                                    "display_order": 1, 
                                    "id": 25346, 
                                    "name": "\u30d7\u30ec\u30df\u30a2\u30e0", 
                                    "price": 999999.0, 
                                    "seat_type": "\u30d7\u30ec\u30df\u30a2\u30e0"
                                }
                            ]
                        }
                    ], 
                    "start_on": "2012-01-10T19:10:00", 
                    "venue": "\u4ed9\u53f0\u5e02\u9752\u8449\u4f53\u80b2\u9928"
                }
            ], 
            "subtitle": "\u524a\u9664\u4f7f\u7528\u4e0d\u53ef", 
            "title": "\u524a\u9664\u4f7f\u7528\u4e0d\u53ef"
        }
    ], 
    "organization": {
        "id": 1, 
        "short_name": "89ers"
    }, 
    "updated_at": "2013-03-15T18:46:37"
}
"""
        request = testing.DummyRequest()
        self._callFUT(request, json.loads(backend_data))
        from altaircms.event.models import Event
        from altaircms.models import Performance, SalesSegment, Ticket

        self.assertEquals(Event.query.count(), 1)
        self.assertEquals(Performance.query.count(), 1)
        self.assertEquals(SalesSegment.query.count(), 0)
        self.assertEquals(Ticket.query.count(), 0)

class ValidateAPIKeyTests(unittest.TestCase):
    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _callFUT(self, *args, **kwargs):
        from altaircms.auth.api import validate_apikey
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
