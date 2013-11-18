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
        from ..views import candidates_sales_segment_group
        return candidates_sales_segment_group(*args, **kwargs)

    def test_no_set(self):
        context = testing.DummyResource()
        request = testing.DummyRequest(
            matchdict=dict(event_id='*'),
        )

        result = self._callFUT(context, request)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['sales_segment_groups'], [])

    def test_it(self):
        from altair.app.ticketing.core.models import (
            Event,
            SalesSegmentGroup,
        )

        event = Event()
        sales_segment_group = SalesSegmentGroup(event=event,
                                                name='testing')
        self.session.add(event)
        self.session.add(sales_segment_group)
        self.session.flush()

        context = testing.DummyResource()
        request = testing.DummyRequest(
            matchdict=dict(event_id=str(event.id)),
        )

        result = self._callFUT(context, request)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['sales_segment_groups'],
                         [{'id': sales_segment_group.id,
                           'name': 'testing'}])
