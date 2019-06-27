# -*- coding:utf-8 -*-
import unittest
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db


class MiniAdminLotResourceTest(unittest.TestCase):
    def setUp(self):
        self.__session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.operators.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models'
            ]
        )

    def tearDown(self):
        _teardown_db()

    @staticmethod
    def __make_test_target(*args, **kwargs):
        from altair.app.ticketing.mini_admin.resources import MiniAdminLotResource
        return MiniAdminLotResource(*args, **kwargs)

    def __make_base_test_data(self):
        from altair.app.ticketing.core.models import Event, Organization
        from altair.app.ticketing.operators.models import Operator
        from altair.app.ticketing.lots.models import Lot
        organization = Organization(
            id=1,
            code=u'TS',
            short_name=u'testing'
        )
        event = Event(
            id=1,
            display_order=1,
            organization_id=organization.id
        )
        operator = Operator(
            id=1,
            organization_id=organization.id
        )
        lot = Lot(
            id=1,
            organization_id=organization.id,
            event_id=event.id
        )
        self.__session.add_all([organization, event, operator, lot])
        self.__session.flush()

        self.__organization = organization
        self.__event = event
        self.__operator = operator
        self.__lot = lot

    def test_lot(self):
        """
        property: lotの正常系テスト
        """
        self.__make_base_test_data()
        test_request = DummyRequest(matchdict={u'lot_id': self.__lot.id})

        test_resource = self.__make_test_target(test_request)
        test_resource.user = self.__operator
        lot_value = test_resource.lot
        self.assertEqual(lot_value, self.__lot)

    def test_invalid_param_lot_id(self):
        """
        異常系のテスト リクエストパラーメータが不正
        """
        from pyramid.httpexceptions import HTTPNotFound
        self.__make_base_test_data()
        test_request = DummyRequest(matchdict={u'lot_id': u'invalid_value'})


        with self.assertRaises(HTTPNotFound):
            self.__make_test_target(test_request)
