import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

class BuildSalesSegmentListForInnerSalesTest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(self):
        self.session = _setup_db(modules=['altair.app.ticketing.core.models'])

    @classmethod
    def tearDownClass(self):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _callFUT(self, *args, **kwargs):
        from .helpers import build_sales_segment_list_for_inner_sales
        return build_sales_segment_list_for_inner_sales(*args, **kwargs)

    def test_get_inner_sales_segments(self):
        from .models import SalesSegment, SalesSegmentGroup
        from datetime import datetime
        from ..models import DBSession
        sales_segments = [
            SalesSegment(
                sales_segment_group=SalesSegmentGroup(kind='normal'),
                start_at=datetime(2012, 1, 1, 0, 0, 0),
                end_at=datetime(2013, 3, 31, 23, 59, 59)
                ),
            SalesSegment(
                sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                start_at=datetime(2013, 4, 1, 0, 0, 0),
                end_at=None
                ),
            SalesSegment(
                sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                start_at=datetime(2013, 8, 1, 0, 0, 0),
                end_at=datetime(2013, 10, 31, 23, 59, 59)
                ),
            SalesSegment(
                sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                start_at=datetime(2013, 1, 1, 0, 0, 0),
                end_at=datetime(2013, 3, 31, 23, 59, 59)
                ),
            SalesSegment(
                sales_segment_group=SalesSegmentGroup(kind='normal'),
                start_at=datetime(2013, 1, 1, 0, 0, 0),
                end_at=datetime(2013, 8, 31, 23, 59, 59)
                ),
            SalesSegment(
                sales_segment_group=SalesSegmentGroup(kind='sales_counter'),
                start_at=datetime(2013, 5, 1, 0, 0, 0),
                end_at=datetime(2013, 7, 31, 23, 59, 59)
                ),
            ]
        for sales_segment in sales_segments:
            DBSession.add(sales_segment)
        DBSession.flush()
        result = self._callFUT(sales_segments, datetime(2013, 2, 1, 0, 0, 0))
        self.assertEqual(result, [sales_segments[3], sales_segments[1], sales_segments[5], sales_segments[2], sales_segments[0], sales_segments[4]])
        result = self._callFUT(sales_segments, datetime(2013, 4, 1, 0, 0, 0))
        self.assertEqual(result, [sales_segments[1], sales_segments[3], sales_segments[5], sales_segments[2], sales_segments[4], sales_segments[0]])

