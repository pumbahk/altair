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

def make_mobile_request(request):
    from altair.mobile.interfaces import IMobileRequest
    from zope.interface import directlyProvides
    directlyProvides(request, IMobileRequest)
    return request

def fake_static_pageset_query__found(request, url, dt, page_type):
    class QueryLike:
        @classmethod
        def first(self):
            return page_type
    return QueryLike

def fake_static_pageset_query__not_found(request, url, dt, page_type):
    class QueryLike:
        @classmethod
        def first(self):
            return None
    return QueryLike

def make_fake_control(pc, mobile, smartphone, fake_static_pageset_query):
    control = mock.Mock("*FakePageQueryControl*")
    control.pc_pagetype = pc
    control.mobile_pagetype = mobile
    control.smartphone_pagetype = smartphone

    control.static_pageset_query = mock.Mock()
    control.static_pageset_query.side_effect = fake_static_pageset_query
    return control

class TestBase(unittest.TestCase):
    def _setup_component(self, config, fake_static_pageset_query):
        from altairsite.fetcher import ICurrentPageFetcher
        from altair.mobile.interfaces import ISmartphoneRequest
        from altair.mobile.interfaces import IMobileRequest
        from pyramid.interfaces import IRequest
        from altairsite.fetcher import (
            PageFetcherForPC, 
            PageFetcherForSmartphone, 
            PageFetcherForMobile
        )
        self.control = control = make_fake_control(S.pc, S.mobile, S.smartphone, fake_static_pageset_query)

        config.registry.adapters.register([IRequest], ICurrentPageFetcher, "", PageFetcherForPC(control))
        config.registry.adapters.register([ISmartphoneRequest], ICurrentPageFetcher, "", PageFetcherForSmartphone(control))
        config.registry.adapters.register([IMobileRequest], ICurrentPageFetcher, "", PageFetcherForMobile(control))

        ## check
        self.assertTrue(isinstance(config.registry.adapters.lookup([IRequest], ICurrentPageFetcher), PageFetcherForPC))
        self.assertTrue(isinstance(config.registry.adapters.lookup([ISmartphoneRequest], ICurrentPageFetcher), PageFetcherForSmartphone))
        self.assertTrue(isinstance(config.registry.adapters.lookup([IMobileRequest], ICurrentPageFetcher), PageFetcherForMobile))


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


class StaticPageQueryNotFoundTests(TestBase):
    def setUp(self):
        self.config = testing.setUp()
        self._setup_component(self.config, fake_static_pageset_query=fake_static_pageset_query__not_found)

    def test_pc_notfound(self):
        organization = setup_organization(use_only_one_static_page_type=True)
        request = self._makeRequest(organization)

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, None)

    def test_smartphone_notfound(self):
        organization = setup_organization(use_only_one_static_page_type=True)
        request = make_smartphone_request(self._makeRequest(organization))

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, None)

    ## mobile request only, raise 404 immediately(this is not good. but...)
    def test_mobile_notfound(self):
        from pyramid.httpexceptions import HTTPNotFound

        organization = setup_organization(use_only_one_static_page_type=True)
        request = make_mobile_request(self._makeRequest(organization))

        target = self._makeOne(request)

        with self.assertRaises(HTTPNotFound):
            target.fetch_static_page_from_params(url="<url>", dt=S.dt)
            self.assertTrue(self.control.static_pageset_query.called)


class StaticPageQueryFoundTests(TestBase):
    def setUp(self):
        self.config = testing.setUp()
        self._setup_component(self.config, fake_static_pageset_query=fake_static_pageset_query__found)

    def test_pc__one__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=True)
        request = self._makeRequest(organization)

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, self.control.pc_pagetype)

    def test_pc__two__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=False)
        request = self._makeRequest(organization)

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, self.control.pc_pagetype)

    def test_smartphone__one__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=True)
        request = make_smartphone_request(self._makeRequest(organization))

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, self.control.pc_pagetype)

    def test_smartphone__two__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=False)
        request = make_smartphone_request(self._makeRequest(organization))

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, self.control.smartphone_pagetype)

    def test_mobile__one__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=True)
        request = make_mobile_request(self._makeRequest(organization))

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, self.control.pc_pagetype)

    def test_mobile__two__static_pagetype(self):
        organization = setup_organization(use_only_one_static_page_type=False)
        request = make_mobile_request(self._makeRequest(organization))

        target = self._makeOne(request)
        result = target.fetch_static_page_from_params(url="<url>", dt=S.dt)
        
        self.assertTrue(self.control.static_pageset_query.called)
        self.assertEquals(result, self.control.mobile_pagetype)
