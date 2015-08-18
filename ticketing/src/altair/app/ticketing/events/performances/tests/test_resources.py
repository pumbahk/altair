import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

class BuildSalesSegmentListForInnerSalesTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(self):
        self.session = _setup_db(modules=[
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.users.models',
            'altair.app.ticketing.lots.models',
            ])

    @classmethod
    def tearDownClass(self):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from ..resources import SalesCounterResourceMixin
        return SalesCounterResourceMixin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get_inner_sales_segments(self):
        from altair.app.ticketing.core.models import Performance, SalesSegment, SalesSegmentGroup, SalesSegmentSetting
        from datetime import datetime
        from altair.app.ticketing.models import DBSession
        performance = Performance(
            sales_segments=[
                SalesSegment(
                    sales_segment_group=SalesSegmentGroup(kind='normal'),
                    start_at=datetime(2012, 1, 1, 0, 0, 0),
                    end_at=datetime(2013, 3, 31, 23, 59, 59),
                    setting=SalesSegmentSetting(
                        sales_counter_selectable=True
                        )
                    ),
                SalesSegment(
                    sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                    start_at=datetime(2013, 4, 1, 0, 0, 0),
                    end_at=None,
                    setting=SalesSegmentSetting(
                        sales_counter_selectable=True
                        )
                    ),
                SalesSegment(
                    sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                    start_at=datetime(2013, 8, 1, 0, 0, 0),
                    end_at=datetime(2013, 10, 31, 23, 59, 59),
                    setting=SalesSegmentSetting(
                        sales_counter_selectable=True
                        )
                    ),
                SalesSegment(
                    sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                    start_at=datetime(2013, 1, 1, 0, 0, 0),
                    end_at=datetime(2013, 3, 31, 23, 59, 59),
                    setting=SalesSegmentSetting(
                        sales_counter_selectable=True
                        )
                    ),
                SalesSegment(
                    sales_segment_group=SalesSegmentGroup(kind='normal'),
                    start_at=datetime(2013, 1, 1, 0, 0, 0),
                    end_at=datetime(2013, 8, 31, 23, 59, 59),
                    setting=SalesSegmentSetting(
                        sales_counter_selectable=True
                        )
                    ),
                SalesSegment(
                    sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                    start_at=datetime(2013, 5, 1, 0, 0, 0),
                    end_at=datetime(2013, 7, 31, 23, 59, 59),
                    setting=SalesSegmentSetting(
                        sales_counter_selectable=True
                        )
                    ),
                ]
            )
        DBSession.add(performance)
        DBSession.flush()
        sales_segments = performance.sales_segments
        target = self._makeOne()
        target.request = testing.DummyRequest()
        target.now = datetime(2013, 2, 1, 0, 0, 0)
        target.performance = performance
        result = target.available_sales_segments
        self.assertEqual(result, [sales_segments[3], sales_segments[1], sales_segments[5], sales_segments[2], sales_segments[0], sales_segments[4]])
        target = self._makeOne()
        target.request = testing.DummyRequest()
        target.now = datetime(2013, 4, 1, 0, 0, 0)
        target.performance = performance
        result = target.available_sales_segments
        self.assertEqual(result, [sales_segments[1], sales_segments[3], sales_segments[5], sales_segments[2], sales_segments[4], sales_segments[0]])

