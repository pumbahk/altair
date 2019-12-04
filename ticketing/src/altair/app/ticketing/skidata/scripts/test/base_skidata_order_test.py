#! /usr/bin/env python
# encoding:utf-8
from unittest import TestCase
from pyramid.testing import setUp, tearDown, DummyRequest
from sqlalchemy import MetaData

from altair.app.ticketing.skidata.models import SkidataBarcode
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.skidata.scripts.test.test_helper.import_resource_helper import importer_tables
from altair.app.ticketing.skidata.scripts.test.testing import _setup_db, _teardown_db


class BaseSkidataOrderTest(TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.sqlahelper = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.orders.models',
            ])
        self.tables_meta = MetaData()
        self.tables_meta.bind = self.sqlahelper.get_engine()
        self.tables_meta.reflect()
        self.session = self.sqlahelper.get_session()
        self.except_keys = None

    def tearDown(self):
        _teardown_db()
        tearDown()

    def importer_tables_with_file(self, file_name, except_keys=None):
        importer_tables(self.session, self.tables_meta, file_name, except_keys)

    @classmethod
    def mock_prepare_barcode_data(cls, barcode_ids, now_datetime):
        barcode_objs = DBSession().query(SkidataBarcode) \
            .filter(SkidataBarcode.id.in_(barcode_ids))
        for obj in barcode_objs:
            obj.sent_at = now_datetime

    def send_qr_objs_to_hsh(self, qr_objs):
        pass

    def mock_objects(self, sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                     prepare_barcode_data, bootstrap, transaction):
        sqlahelper.get_engine.return_value = EngineEx()
        db_session.return_value = self.session
        get_global_db_session.return_value = self.session
        send_qr_objs_to_hsh.side_effect = self.mock_prepare_barcode_data
        prepare_barcode_data.side_effect = self.mock_prepare_barcode_data
        bootstrap.return_value = {'registry': self.config.registry}


class EngineEx(object):
    def __call__(self):
        pass

    @classmethod
    def connect(cls):
        return ConnectionEx()


class ConnectionEx(object):
    @classmethod
    def scalar(cls, query, params):
        return 1

    def close(self):
        pass
