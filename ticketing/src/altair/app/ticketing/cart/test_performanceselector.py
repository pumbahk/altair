# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

class MatchUpPerformanceSelectorTests(unittest.TestCase):
    maxDiff = None

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
        self.config.add_route('cart.seat_types2', '/testing/seat_types2/{performance_id}/{sales_segment_id}')
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
                        end_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=1,
                        ),
                    name=u"前売券",
                    start_at=datetime(2013, 1, 1),
                    id=2,
                    max_quantity=3
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance1',
                        id=3,
                        start_on=datetime(2013, 4, 1),
                        end_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=3
                        ),
                    name=u"前売券",
                    start_at=datetime(2013, 1, 1),
                    id=4,
                    max_quantity=10
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance2',
                        id=5,
                        start_on=datetime(2013, 4, 1),
                        end_on=datetime(2013, 4, 2),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=2
                        ),
                    name=u"前売券",
                    start_at=datetime(2013, 1, 1),
                    id=6,
                    max_quantity=10
                    ),
                ]
            )

        target = self._makeOne(request)
        result = target()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], u'testing performance1')
        self.assertEqual(result[0][1][0], 
                         {'id': 2, 
                          'seat_types_url': 'http://example.com/testing/seat_types2/1/2',
                          'max_quantity': 3, 
                          'order_url': 'http://example.com/testing/order/2', 
                          'name': u'2013年3月31日(日) - 4月1日(月) テスト会場 前売券',
                          'name_pc': u'2013年3月31日(日) - 4月1日(月) テスト会場 前売券',
                          'name_smartphone': u'2013年3月31日(日) - 4月1日(月) テスト会場 前売券',
                          'name_mobile': u'2013年3月31日(日) - 4月1日(月) テスト会場 前売券',
                          })
        self.assertEqual(result[0][1][1],
                         {'id': 4,
                          'seat_types_url': 'http://example.com/testing/seat_types2/3/4', 
                          'max_quantity': 10, 
                          'order_url': 'http://example.com/testing/order/4', 
                          'name': u'2013年4月1日(月) 00:00 テスト会場 前売券',
                          'name_pc': u'2013年4月1日(月) 00:00 テスト会場 前売券', 
                          'name_smartphone': u'2013年4月1日(月) 00:00 テスト会場 前売券', 
                          'name_mobile': u'2013年4月1日(月) 00:00 テスト会場 前売券', 
                          })
        self.assertEqual(result[1][0], u'testing performance2')
        self.assertEqual(result[1][1][0],
                         {'id': 6,
                          'seat_types_url': 'http://example.com/testing/seat_types2/5/6',
                          'max_quantity': 10,
                          'order_url': 'http://example.com/testing/order/6',
                          'name': u'2013年4月1日(月) - 4月2日(火) テスト会場 前売券',
                          'name_pc': u'2013年4月1日(月) - 4月2日(火) テスト会場 前売券',
                          'name_smartphone': u'2013年4月1日(月) - 4月2日(火) テスト会場 前売券',
                          'name_mobile': u'2013年4月1日(月) - 4月2日(火) テスト会場 前売券',
                          })

class DatePerformanceSelectorTests(unittest.TestCase):
    maxDiff = None

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
        self.config.add_route('cart.seat_types2', '/testing/seat_types2/{performance_id}/{sales_segment_id}')
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
                        id=2,
                        start_on=datetime(2013, 3, 31),
                        end_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=1
                        ),
                    name=u"前売券",
                    start_at=datetime(2013, 1, 1),
                    id=1,
                    max_quantity=3,
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance2',
                        id=4,
                        start_on=datetime(2013, 4, 1),
                        end_on=datetime(2013, 4, 2),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=2
                        ),
                    name=u"前売券",
                    start_at=datetime(2013, 1, 1),
                    id=3,
                    max_quantity=10,
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance3',
                        id=6,
                        start_on=datetime(2013, 4, 1),
                        end_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=3
                        ),
                    name=u"前売券",
                    start_at=datetime(2013, 1, 1),
                    id=5,
                    max_quantity=10,
                    ),
                DummySalesSegment(
                    performance=DummyPerformance(
                        name=u'testing performance4',
                        id=8,
                        start_on=datetime(2013, 4, 1),
                        end_on=datetime(2013, 4, 1),
                        venue=testing.DummyModel(name=u"テスト会場"),
                        display_order=3
                        ),
                    name=u"前売券",
                    start_at=datetime(2013, 1, 2),
                    id=7,
                    max_quantity=10,
                    ),
                ]
            )

        target = self._makeOne(request)
        result = target()

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0][0], u'2013年3月31日 - 4月1日')
        self.assertEqual(result[0][1][0], 
                         {'id': 1,
                          'seat_types_url': 'http://example.com/testing/seat_types2/2/1',
                          'order_url': 'http://example.com/testing/order/1', 
                          'max_quantity': 3, 
                          'name': u'2013年3月31日(日) - 4月1日(月) テスト会場 前売券',
                          'name_pc': u'テスト会場 前売券',
                          'name_smartphone': u'テスト会場 前売券',
                          'name_mobile': u'2013年3月31日(日) - 4月1日(月) テスト会場 前売券',
                          })
        self.assertEqual(result[1][0], u'2013年4月1日 - 4月2日')
        self.assertEqual(result[1][1][0],
                         {'id': 3,
                          'seat_types_url': 'http://example.com/testing/seat_types2/4/3', 
                          'order_url': 'http://example.com/testing/order/3',
                          'max_quantity': 10, 
                          'name': u'2013年4月1日(月) - 4月2日(火) テスト会場 前売券',
                          'name_pc': u'テスト会場 前売券',
                          'name_smartphone': u'テスト会場 前売券',
                          'name_mobile': u'2013年4月1日(月) - 4月2日(火) テスト会場 前売券',
                         })
        self.assertEqual(result[2][0], u'2013年4月1日')
        self.assertEqual(result[2][1][0],
                         {'id': 5,
                          'seat_types_url': 'http://example.com/testing/seat_types2/6/5',
                          'order_url': 'http://example.com/testing/order/5',
                          'max_quantity': 10,
                          'name': u'2013年4月1日(月) 00:00 テスト会場 前売券',
                          'name_pc': u'00:00 テスト会場 前売券',
                          'name_smartphone': u'00:00 テスト会場 前売券',
                          'name_mobile': u'2013年4月1日(月) 00:00 テスト会場 前売券',
                          })
        self.assertEqual(result[2][1][1],
                         {'id': 7,
                          'order_url': 'http://example.com/testing/order/7',
                          'seat_types_url': 'http://example.com/testing/seat_types2/8/7',
                          'max_quantity': 10,
                          'name': u'2013年4月1日(月) 00:00 テスト会場 前売券',
                          'name_pc': u'00:00 テスト会場 前売券',
                          'name_smartphone': u'00:00 テスト会場 前売券',
                          'name_mobile': u'2013年4月1日(月) 00:00 テスト会場 前売券',
                          })
        
class DummyEvent(testing.DummyModel):
    pass

class DummyPerformance(testing.DummyModel):
    pass

class DummySalesSegment(testing.DummyModel):
    pass
