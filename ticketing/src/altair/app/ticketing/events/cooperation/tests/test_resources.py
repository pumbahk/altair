# -*- coding: utf-8 -*-
from unittest import TestCase
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

class CooperationEventResourceTest(TestCase):

    def setUp(self):
        from altair.app.ticketing.core.models import (
            Event,
            Organization,
            )
        self.session = _setup_db([
            'altair.app.ticketing.core.models'
            ])
        organization = Organization(id=1, short_name=u'', code=u'XX')
        event = Event(title=u'テスト', organization=organization)
        self.session.add(event)
        self.session.flush()
        self.event_id = event.id

    def tearDown(self):
        _teardown_db()

    def test_create(self):
        from ..resources import CooperationEventResource
        request = testing.DummyRequest()
        request.matchdict = {
            'event_id': self.event_id,
            }
        CooperationEventResource(request)


class RequestAccessorTest(TestCase):

    def _makeOne(self):
        from ..resources import _RequestAccessor
        request = testing.DummyRequest()
        request.matchdict['event_id'] = 1
        request.params['performance_id'] = 2
        accessor = _RequestAccessor(request)
        return accessor

    def test_get_matchdict(self):
        accessor = self._makeOne()
        self.assertEqual(1, accessor._get_matchdict('event_id'))
