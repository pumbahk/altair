# -*- coding:utf-8 -*-
import unittest
from datetime import datetime

def setUpModule():
    from altair.app.ticketing.testing import _setup_db
    _setup_db(modules=[
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.lots.models",
            ])

def tearDownModule():
    from altair.app.ticketing.testing import _teardown_db
    _teardown_db()


def get_organization(*args, **kwargs):
    from altair.app.ticketing.core.models import Organization
    return Organization(*args, **kwargs)

def request():
    class Request:
        session = {}
    return Request

class EventCMSDataTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.core.models import Event
        return Event

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_data_include_organazation_id(self):
        organization = get_organization(id=10000)
        target = self._makeOne(organization=organization)
        result = target._get_self_cms_data()
        self.assertEqual(result["organization_id"], 10000)

    def test_data_include_deleted_performance(self):
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.core.models import Performance
        from pyramid.testing import DummyRequest

        organization = get_organization(id=10000, short_name="org")
        
        target = self._makeOne(organization=organization)
        performance = Performance(event=target,  deleted_at=datetime(1900, 1, 1), start_on=datetime(1900, 1, 1))
        DBSession.add(target)
        DBSession.add(performance)
        DBSession.flush()

        result = target.get_cms_data(request=DummyRequest(),now=datetime.now(),validation=False)

        self.assertEquals(len(result["performances"]), 1)
        self.assertTrue(result["performances"][0]["deleted"])

"""
todo: もっと丁寧なassertion.今はレンダリングできるかだけを見ている。
"""

class GenDataTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.events.api import get_cms_data
        return get_cms_data(*args, **kwargs)
        
    def _build_event(self, organization):
        from altair.app.ticketing.core.models import Event, Performance, Product, SalesSegment, SalesSegmentGroup, Site, Venue, StockType
        
        event0 = Event(id=40020, code="DM399", organization=organization, 
                       abbreviated_title=u"なし",
                       title=u"マツイ・オン・アイス")
        site0 = Site(prefecture="tokyo")
        venue0 = Venue(site=site0, name=u"まついZEROホール", organization=organization)
        performance0 = Performance(id=40096, 
                                   open_on=datetime(2013, 3, 15, 8), 
                                   start_on=datetime(2013, 3, 15, 10), 
                                   end_on=datetime(2013, 3, 15, 13), 
                                   name=u"マツイ・オン・アイス(東京公演)", 
                                   code="hehehhe", 
                                   event=event0, 
                                   venue=venue0)
        group0 = SalesSegmentGroup(name=u"一般先行", kind="first_lottery")
        sales_segment0 = SalesSegment(id=40039, 
                                     performance=performance0,
                                     sales_segment_group=group0,
                                     seat_choice=False, 
                                     start_at=datetime(2012, 1, 12, 10), 
                                     end_at=datetime(2012, 1, 22, 10))
        seat_stock_type0 = StockType(name=u"B席")
        seat_stock_type1 = StockType(name=u"S席")
        seat_stock_type2 = StockType(name=u"A席")
        product2 = Product(id=400599, 
                           sales_segment=sales_segment0, 
                           sales_segment_group=group0, 
                           seat_stock_type=seat_stock_type1, 
                           display_order=1, 
                           name=u"S席大人", 
                           price=20000)
        product3 = Product(id=400600, 
                           sales_segment=sales_segment0, 
                           sales_segment_group=group0, 
                           seat_stock_type=seat_stock_type2,  
                           display_order=2, 
                           name=u"A席大人", 
                           price=8000)
        product0 = Product(id=400571, 
                           sales_segment=sales_segment0, 
                           sales_segment_group=group0, 
                           seat_stock_type=seat_stock_type0, 
                           display_order=3, 
                           name=u"B席右", 
                           price=2000)
        product1 = Product(id=400572, 
                           sales_segment=sales_segment0, 
                           sales_segment_group=group0, 
                           seat_stock_type=seat_stock_type0, 
                           display_order=4, 
                           name=u"B席左", 
                           price=2000)
        ##
        site1 = Site(prefecture="osaka")
        venue1 = Venue(site=site1, name=u"まつい市民会館", organization=organization)
        performance1 = Performance(id=40097, 
                                   open_on=None, 
                                   start_on=datetime(2013, 3, 26, 19), 
                                   end_on=None, 
                                   name=u"マツイ・オン・アイス(大阪公演)", 
                                   event=event0, 
                                   venue=venue1)
        group1 = SalesSegmentGroup(name=u"一般販売", kind="normal")
        sales_segment1 = SalesSegment(id=40040, 
                                     performance=performance1,
                                     sales_segment_group=group1,
                                     seat_choice=False, 
                                     start_at=datetime(2012, 1, 23, 10), 
                                     end_at=None)
        seat_stock_type3 = StockType(name=u"B席")
        seat_stock_type4 = StockType(name=u"S席")
        seat_stock_type5 = StockType(name=u"A席")
        product6 = Product(id=401599, 
                           sales_segment=sales_segment1, 
                           sales_segment_group=group1, 
                           seat_stock_type=seat_stock_type4, 
                           display_order=1, 
                           name=u"S席大人", 
                           price=10000)
        product7 = Product(id=401600, 
                           sales_segment=sales_segment1, 
                           sales_segment_group=group1, 
                           seat_stock_type=seat_stock_type5, 
                           display_order=2, 
                           name=u"A席大人", 
                           price=4000)
        product4 = Product(id=401571, 
                           sales_segment=sales_segment1, 
                           sales_segment_group=group1, 
                           seat_stock_type=seat_stock_type3, 
                           display_order=3, 
                           name=u"B席右", 
                           price=1000)
        product5 = Product(id=401572, 
                           sales_segment=sales_segment1, 
                           sales_segment_group=group1, 
                           seat_stock_type=seat_stock_type3, 
                           display_order=4, 
                           name=u"B席左", 
                           price=1000)

        return event0

    def test_it(self):
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.core.models import Organization

        organization = Organization(id=1000, short_name="demo")
        event0 = self._build_event(organization)
        DBSession.add(event0)
        DBSession.flush()
        result = self._callFUT(request(), organization, event0, now=datetime(2012, 6, 20, 10, 33, 34))

        import json
        outputdata = json.dumps(result, indent=2, ensure_ascii=False)
        self.assertTrue(outputdata)
        # print outputdata # see: altaircms.events.tests

    def test_with_delete(self):
        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.core.models import Organization

        organization = Organization(id=1000, short_name="demo")
        event0 = self._build_event(organization)
        DBSession.add(event0)
        DBSession.flush()

        p1 = None
        for p in event0.performances:
            if p.id == 40096:
                p.venue.delete()
                for s in p.sales_segments:
                    for pr in s.products:
                        pr.delete()
                    s.delete()
                p.delete()
            if p.id == 40097:
                p1 = p
                

        sales_segment = p1.sales_segments[0]
        for p in sales_segment.products:
            if p.id == 401599:
                p.delete()
            if p.id == 401572:
                p.delete()
                

        result = self._callFUT(request(), organization, event0, now=datetime(2012, 6, 20, 10, 33, 34))

        import json
        outputdata = json.dumps(result, indent=2, ensure_ascii=False)
        self.assertTrue(outputdata)
        # print outputdata # see: altaircms.events.tests

        
        
        
if __name__ == "__main__":
    unittest.main()
