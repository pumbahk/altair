import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

class candidates_sales_segmentTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
        ])

    def tearDown(self):
        _teardown_db()

    def _callFUT(self, *args, **kwargs):
        from ..views import candidates_sales_segment
        return candidates_sales_segment(*args, **kwargs)

    def test_no_set(self):
        context = testing.DummyResource()
        request = testing.DummyRequest(
            matchdict=dict(event_id='*'),
        )

        result = self._callFUT(context, request)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['salessegments'], [])

    def test_it(self):
        from altair.app.ticketing.core.models import (
            Event,
            SalesSegment,
            SalesSegmentGroup,
        )

        event = Event()
        sales_segment = SalesSegment(event=event,
                                     sales_segment_group=SalesSegmentGroup(name='testing'))
        self.session.add(event)
        self.session.flush()

        context = testing.DummyResource()
        request = testing.DummyRequest(
            matchdict=dict(event_id=str(event.id)),
        )

        result = self._callFUT(context, request)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['salessegments'],
                         [{'id': sales_segment.id,
                           'name': 'testing'}])
