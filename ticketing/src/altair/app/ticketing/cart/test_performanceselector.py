# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

class MatchUpPerformanceSelectorTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from .performanceselector import MatchUpPerformanceSelector
        return MatchUpPerformanceSelector


    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_iface(self):
        from zope.interface.verify import verifyObject
        from .interfaces import IPerformanceSelector
        request = testing.DummyRequest()
        request.context = testing.DummyResource(request=request,
                                                available_sales_segments=[])
        target = self._makeOne(request)
        
        verifyObject(IPerformanceSelector, target)
        self.assertEqual(target.request, request)
        self.assertEqual(target.context, request.context)

    def test_zero(self):
        request = testing.DummyRequest()
        request.context = testing.DummyResource(request=request,
                                                available_sales_segments=[])

        target = self._makeOne(request)
        result = target()

        self.assertEqual(len(result), 0)

    def test_a_sales_segment(self):
        self.config.add_route('cart.seat_types', '/testing/seat_types/{performance_id}/{sales_segment_id}/{event_id}')
        self.config.add_route('cart.order', '/testing/order/{sales_segment_id}')
        from datetime import datetime
        request = testing.DummyRequest()
        request.context = testing.DummyResource(
            request=request,
            event=DummyEvent(id=123),
            available_sales_segments=[
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance1',
                        id=1,
                        start_on=datetime(2013, 3, 31),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=1,
                        ),
                    name=u"前売券",
                    id=2,
                    upper_limit=3
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance1',
                        id=4,
                        start_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=3
                        ),
                    name=u"前売券",
                    id=5,
                    upper_limit=10
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance2',
                        id=6,
                        start_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=2
                        ),
                    name=u"前売券",
                    id=7,
                    upper_limit=10
                    ),
                ]
            )

        target = self._makeOne(request)
        result = target()

        self.assertEqual(len(result), 2)
        self.assertEqual([pair[0] for pair in result], [u'testing performance1', u'testing performance2'])
        self.assertEqual(result[0][1][0], 
                         {'seat_types_url': 'http://example.com/testing/seat_types/1/2/123',
                          'upper_limit': 3, 
                          'order_url': 'http://example.com/testing/order/2', 
                          'id': 2, 
                          'name': u'2013-03-31 00:00\u958b\u59cb \u30c6\u30b9\u30c8\u4f1a\u5834 \u524d\u58f2\u5238'})
        self.assertEqual(result[0][1][1],
                         {'seat_types_url': 'http://example.com/testing/seat_types/4/5/123', 
                          'upper_limit': 10, 
                          'order_url': 'http://example.com/testing/order/5', 
                          'name': u'2013-04-01 00:00\u958b\u59cb \u30c6\u30b9\u30c8\u4f1a\u5834 \u524d\u58f2\u5238', 
                          'id': 5})
        self.assertEqual(result[1][1][0],
                         {'id': 7,
                          'name': u'2013-04-01 00:00\u958b\u59cb \u30c6\u30b9\u30c8\u4f1a\u5834 \u524d\u58f2\u5238',
                          'order_url': 'http://example.com/testing/order/7',
                          'seat_types_url': 'http://example.com/testing/seat_types/6/7/123',
                          'upper_limit': 10})

class DatePerformanceSelectorTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from .performanceselector import DatePerformanceSelector
        return DatePerformanceSelector


    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_iface(self):
        from zope.interface.verify import verifyObject
        from .interfaces import IPerformanceSelector
        request = testing.DummyRequest()
        request.context = testing.DummyResource(request=request,
                                                available_sales_segments=[])
        target = self._makeOne(request)
        
        verifyObject(IPerformanceSelector, target)
        self.assertEqual(target.request, request)
        self.assertEqual(target.context, request.context)

    def test_zero(self):
        request = testing.DummyRequest()
        request.context = testing.DummyResource(request=request,
                                                available_sales_segments=[])

        target = self._makeOne(request)
        result = target()

        self.assertEqual(len(result), 0)

    def test_a_sales_segment(self):
        self.config.add_route('cart.seat_types', '/testing/seat_types/{performance_id}/{sales_segment_id}/{event_id}')
        self.config.add_route('cart.order', '/testing/order/{sales_segment_id}')
        from datetime import datetime
        request = testing.DummyRequest()
        request.context = testing.DummyResource(
            request=request,
            event=DummyEvent(id=123),
            available_sales_segments=[
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance1',
                        id=1,
                        start_on=datetime(2013, 3, 31),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=1
                        ),
                    name=u"前売券",
                    id=2,
                    upper_limit=3,
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance1',
                        id=4,
                        start_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=2
                        ),
                    name=u"前売券",
                    id=5,
                    upper_limit=10,
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance2',
                        id=6,
                        start_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=3
                        ),
                    name=u"前売券",
                    id=7,
                    upper_limit=10,
                    ),
                ]
            )

        target = self._makeOne(request)
        result = target()

        self.assertEqual(len(result), 2)
        self.assertEqual([pair[0] for pair in result], [u'2013年03月31日', u'2013年04月01日'])

        self.assertEqual(result[0][1][0], 
                         {'seat_types_url': 'http://example.com/testing/seat_types/1/2/123',
                          'upper_limit': 3, 
                          'order_url': 'http://example.com/testing/order/2', 
                          'id': 2, 
                          'name': u'2013-03-31 00:00\u958b\u59cb \u30c6\u30b9\u30c8\u4f1a\u5834 \u524d\u58f2\u5238'})
        self.assertEqual(result[1][1][0],
                         {'seat_types_url': 'http://example.com/testing/seat_types/4/5/123', 
                          'upper_limit': 10, 
                          'order_url': 'http://example.com/testing/order/5', 
                          'name': u'2013-04-01 00:00\u958b\u59cb \u30c6\u30b9\u30c8\u4f1a\u5834 \u524d\u58f2\u5238', 
                          'id': 5})
        self.assertEqual(result[1][1][1],
                         {'id': 7,
                          'name': u'2013-04-01 00:00\u958b\u59cb \u30c6\u30b9\u30c8\u4f1a\u5834 \u524d\u58f2\u5238',
                          'order_url': 'http://example.com/testing/order/7',
                          'seat_types_url': 'http://example.com/testing/seat_types/6/7/123',
                          'upper_limit': 10})
        
class DummyEvent(testing.DummyModel):
    pass

class DummyPerformance(testing.DummyModel):
    pass

class DummySalesSegment(testing.DummyModel):
    pass
