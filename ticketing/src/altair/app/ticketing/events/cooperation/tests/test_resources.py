# -*- coding: utf-8 -*-
from unittest import TestCase
from pyramid import testing


class CooperationEventResourceTest(TestCase):

    def setUp(self):
        from altair.app.ticketing.core.models import (
            Event,
            Organization,
            )
        organization = Organization(id=1, short_name=u'', code=u'XX')
        event = Event(title=u'テスト', organization=organization)
        event.save()
        self.event_id = event.id

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
