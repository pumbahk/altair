#-*- coding: utf-8 -*-
from unittest import TestCase
import json
import StringIO as io

from pyramid import testing

from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.testing import _setup_db, _teardown_db

from .dump import OrderExporter

class OrderDownloadBetaTest(TestCase, CoreTestMixin):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.users.models',
                'altair.app.ticketing.operators.models',
                ]
            )
        CoreTestMixin.setUp(self)

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def test_options(self):
        from altair.app.ticketing.orders.dump import column_compiler
        data = json.dumps({
            'type': 'csv',
            'options': column_compiler.keys(),
            'filters': {},
            'limit': None,
            'page': 1,
            })
        fp = io.StringIO()
        exporter = OrderExporter(self.session, 1)
        exporter.exportfp(fp, json_=data)

    def test_filters(self):
        from altair.app.ticketing.orders.dump import column_compiler
        data = json.dumps({
            'type': 'csv',
            'options': ['order-no', 'ORDER_CREATED_AT'],
            'filters': {'ordered-at': ['2014-01-01T00:00:00', '2014-01-01T23:59:59']},
            'limit': None,
            'page': 1,
            })
        fp = io.StringIO()
        exporter = OrderExporter(self.session, 1)
        exporter.exportfp(fp, json_=data)
