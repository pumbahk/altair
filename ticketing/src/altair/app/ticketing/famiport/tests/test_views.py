# -*- coding: utf-8 -*-
from unittest import TestCase
from altair.app.ticketing.testing import (
    _setup_db,
    _teardown_db,
    )


class SearchViewTest(TestCase):
    def setUp(self):

        from webtest import TestApp
        from pyramid.config import Configurator
        self.session = _setup_db()
        config = Configurator()
        config.include('altair.app.ticketing.famiport')

        extra_environ = {'HTTP_HOST': 'example.com:80'}
        self.app = TestApp(config.make_wsgi_app(), extra_environ=extra_environ)

    def test_it(self):
        self.app.post('/api/search/')
