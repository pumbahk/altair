# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
import mock
from mock import sentinel as S

#boo
import altaircms.page.models
import altaircms.event.models
import altaircms.auth.models
import altaircms.models

def setup_organization(use_only_one_static_page_type):
    from altaircms.auth.models import Organization
    organization = Organization(use_only_one_static_page_type=use_only_one_static_page_type)
    return organization

def make_smartphone_request(request):
    from altair.mobile.interfaces import ISmartphoneRequest
    from zope.interface import directlyProvides
    directlyProvides(request, ISmartphoneRequest)
    return request

class Tests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

        from altairsite.fetcher import ICurrentPageFetcher
        self.current_fetcher = mock.Mock()
        self.config.registry.registerUtility(self.current_fetcher, ICurrentPageFetcher)

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from altairsite.front.resources import AccessControlPC
        return AccessControlPC
    
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeRequest(self, organization):
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        request.organization = organization
        request.registry = self.config.registry
        return request

    def test_pc__one__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=True)
        request = self._makeRequest(organization)
        target = self._makeOne(request)
        target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.current_fetcher.pc_static_page.called)

    def test_pc__two__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=False)
        request = self._makeRequest(organization)
        target = self._makeOne(request)
        target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.current_fetcher.pc_static_page.called)

    def test_smartphone__one__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=True)
        request = make_smartphone_request(self._makeRequest(organization))
        target = self._makeOne(request)
        target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.current_fetcher.pc_static_page.called)

    def test_smartphone__two__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=False)
        request = make_smartphone_request(self._makeRequest(organization))
        target = self._makeOne(request)
        target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertFalse(self.current_fetcher.pc_static_page.called)
        self.assertTrue(self.current_fetcher.smartphone_static_page.called)
