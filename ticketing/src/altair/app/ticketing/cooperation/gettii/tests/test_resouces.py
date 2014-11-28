# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock
from pyramid import testing


class VenueResourceTest(TestCase):
    def _makeOne(self):
        from ..resources import VenueResource
        request = testing.DummyRequest()
        request.matchdict['venue_id'] = 1
        resource = VenueResource(request)
        resource.organization = Mock()
        resource.organization.id = 1
        return resource

    def test_venue_no_venue(self):
        from pyramid.httpexceptions import HTTPNotFound
        resource = self._makeOne()
        with self.assertRaises(HTTPNotFound):
            resource.venue

    def test_external_venues(self):
        from pyramid.httpexceptions import HTTPNotFound
        resource = self._makeOne()
        with self.assertRaises(HTTPNotFound):
            resource.external_venues
