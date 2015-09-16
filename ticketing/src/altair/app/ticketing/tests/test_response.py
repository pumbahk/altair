# -*- coding:utf-8 -*-
import unittest
from pyramid import testing

class DummyVenusian(object):
    def __init__(self, config):
        self.config = config

    def attach(self, fn, callback):
        self.fn = fn
        self.callback = callback

    def scan(self, module):
        self.callback(self, self.fn.__name__, self.fn)

class RefreshResponseTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.html')

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.response import static_renderer
        @static_renderer(*args, **kwargs)
        def response(request, kwargs, renderer):
            return "ok"
        return response

    def test__missing_template(self):
        venusian = DummyVenusian(self.config)
        self._callFUT("altair.app.ticketing:templates/missing__missing.html", venusian_=venusian)

        from pyramid.exceptions import ConfigurationError
        with self.assertRaises(ConfigurationError):
            venusian.scan(".")
            self.config.commit()

    def test__exists_template(self):
        venusian = DummyVenusian(self.config)
        response_function = self._callFUT("altair.app.ticketing:templates/refresh.html", venusian_=venusian)
        venusian.scan(".")
        self.config.commit()
        self.assertEquals(response_function(request=None, kwargs={}), "ok")
