# -*- coding: utf-8 -*-
from unittest import TestCase
from pyramid.testing import DummyResource
from altair.app.ticketing.testing import DummyRequest
from altair.app.ticketing.testing import _setup_db, _teardown_db


class AugusTicketViewTest(TestCase):
    def setUp(self):
        self.__session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
            ]
        )

    def tearDown(self):
        _teardown_db()

    @staticmethod
    def __get_test_target():
        from ..views import AugusTicketView
        return AugusTicketView

    def __make_test_target(self, *args, **kwargs):
        return self.__get_test_target()(*args, **kwargs)

    def __make_base_test_data(self):
        from altair.app.ticketing.core.models import (
            Event,
            Performance,
            AugusPerformance
        )
        base_event = Event(
            id=1,
            display_order=1
        )
        base_performance = Performance(
            id=1,
            event_id=1,
            public=1,
            display_order=1
        )
        base_augus_performance = AugusPerformance(
            id=1,
            augus_event_code=1,
            augus_performance_code=1,
            augus_venue_code=1,
            augus_venue_name=u'テスト会場',
            augus_event_name=u'テストイベント',
            augus_performance_name=u'テスト公演',
            augus_venue_version=0,
            performance_id=1
        )
        self.__session.add_all([base_event,
                                base_performance,
                                base_augus_performance])
        self.__session.flush()
        return base_event, base_augus_performance

    def test_save_to_update(self):
        """
        Test AugusTicketView.save
        オーガスデータとAltairの席種を紐付けるケース
        """
        from altair.app.ticketing.core.models import AugusTicket, StockType
        event, augus_performance = self.__make_base_test_data()
        augus_tickets = [
            AugusTicket(
                id=1,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券1',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1000,
                augus_performance_id=augus_performance.id
            ),
            AugusTicket(
                id=2,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券2',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1500,
                augus_performance_id=augus_performance.id
            ),
            AugusTicket(
                id=3,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券3',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=2000,
                augus_performance_id=augus_performance.id
            )
        ]
        stock_types = [
            StockType(
                id=1,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            ),
            StockType(
                id=2,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            ),
            StockType(
                id=3,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            )
        ]
        self.__session.add_all(augus_tickets)
        self.__session.add_all(stock_types)
        self.__session.flush()

        def mock_route_path(arg1, event_id=None):
            return 'http://dummy_route_path'

        def mock_route_url(arg1, event_id=None):
            return 'http://dummy_route_url'

        request = DummyRequest(
            params={u"stock_type-1": u"1", u"stock_type-2": u"2", u"stock_type-3": u"3"},
            route_path=mock_route_path,
            route_url=mock_route_url
        )
        context = DummyResource(
            event=DummyResource(id=1)
        )

        self.__make_test_target(context, request).save()

        self.assertEqual(augus_tickets[0].stock_type_id, stock_types[0].id)
        self.assertEqual(augus_tickets[1].stock_type_id, stock_types[1].id)
        self.assertEqual(augus_tickets[2].stock_type_id, stock_types[2].id)

    def test_save_to_delete(self):
        """
        Test AugusTicketView.save
        オーガスデータとAltairの席種を紐付を削除するケース
        """
        from altair.app.ticketing.core.models import AugusTicket, StockType
        event, augus_performance = self.__make_base_test_data()
        stock_types = [
            StockType(
                id=1,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            ),
            StockType(
                id=2,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            ),
            StockType(
                id=3,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            )
        ]
        augus_tickets = [
            AugusTicket(
                id=1,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券1',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1000,
                augus_performance_id=augus_performance.id,
                stock_type_id=1
            ),
            AugusTicket(
                id=2,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券2',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1500,
                augus_performance_id=augus_performance.id,
                stock_type_id=2
            ),
            AugusTicket(
                id=3,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券3',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=2000,
                augus_performance_id=augus_performance.id,
                stock_type_id=3
            )
        ]
        self.__session.add_all(stock_types)
        self.__session.add_all(augus_tickets)
        self.__session.flush()

        def mock_route_path(arg1, event_id=None):
            return 'http://dummy_route_path'

        def mock_route_url(arg1, event_id=None):
            return 'http://dummy_route_url'

        request = DummyRequest(
            params={u"stock_type-1": None, u"stock_type-2": None, u"stock_type-3": None},
            route_path=mock_route_path,
            route_url=mock_route_url
        )
        context = DummyResource(
            event=DummyResource(id=1)
        )

        self.__make_test_target(context, request).save()

        self.assertIsNone(augus_tickets[0].stock_type_id)
        self.assertIsNone(augus_tickets[1].stock_type_id)
        self.assertIsNone(augus_tickets[2].stock_type_id)

    def test_save_with_invalid_select_prefix(self):
        """
        Test AugusTicketView.save
        オーガスデータとAltairの席種を紐付けを試みるが、パラメータプレフィックス不正により紐付け失敗するケース
        """
        from altair.app.ticketing.core.models import AugusTicket, StockType
        event, augus_performance = self.__make_base_test_data()
        augus_tickets = [
            AugusTicket(
                id=1,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券1',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1000,
                augus_performance_id=augus_performance.id
            ),
            AugusTicket(
                id=2,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券2',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1500,
                augus_performance_id=augus_performance.id
            ),
            AugusTicket(
                id=3,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'テスト券3',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=2000,
                augus_performance_id=augus_performance.id
            )
        ]
        stock_types = [
            StockType(
                id=1,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            ),
            StockType(
                id=2,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            ),
            StockType(
                id=3,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1
            )
        ]
        self.__session.add_all(augus_tickets)
        self.__session.add_all(stock_types)
        self.__session.flush()

        def mock_route_path(arg1, event_id=None):
            return 'http://dummy_route_path'

        def mock_route_url(arg1, event_id=None):
            return 'http://dummy_route_url'

        request = DummyRequest(
            params={u"invalid_prefix-1": u"1", u"invalid_prefix-2": u"2", u"invalid_prefix-3": u"3"},
            route_path=mock_route_path,
            route_url=mock_route_url
        )
        context = DummyResource(
            event=DummyResource(id=1)
        )

        self.__make_test_target(context, request).save()

        # 紐付け失敗につきNoneのまま
        self.assertIsNone(augus_tickets[0].stock_type_id)
        self.assertIsNone(augus_tickets[1].stock_type_id)
        self.assertIsNone(augus_tickets[2].stock_type_id)

    def test_save_with_value_error(self):
        """
        Test AugusTicketView.save
        オーガスデータが紐づく公演と、Altair席種が紐づく公演のアンマッチによりエラーとなるケース
        """
        from altair.app.ticketing.core.models import AugusTicket, StockType, Event, Performance
        from pyramid.httpexceptions import HTTPBadRequest
        _, augus_performance = self.__make_base_test_data()
        augus_ticket = AugusTicket(
            id=1,
            augus_venue_code=augus_performance.augus_venue_code,
            augus_seat_type_code=1,
            augus_seat_type_name=u'テスト券1',
            augus_seat_type_classif=u'1',
            unit_value_code=0,
            unit_value_name=u'定価',
            value=1000,
            augus_performance_id=augus_performance.id
        )
        mismatch_event = Event(
            id=2,
            display_order=2
        )
        mismatch_performance = Performance(
            id=2,
            event_id=mismatch_event.id,
            public=1,
            display_order=2
        )
        stock_type = StockType(
            id=1,
            event_id=mismatch_event.id,
            display_order=1,
            display=1,
            disp_reports=1
        )
        self.__session.add_all([augus_ticket,
                                mismatch_event,
                                mismatch_performance,
                                stock_type])
        def mock_route_path(arg1, event_id=None):
            return 'http://dummy_route_path'

        def mock_route_url(arg1, event_id=None):
            return 'http://dummy_route_url'

        request = DummyRequest(
            params={u"stock_type-1": u"1"},
            route_path=mock_route_path,
            route_url=mock_route_url
        )
        context = DummyResource(
            event=DummyResource(id=1)
        )

        with self.assertRaises(HTTPBadRequest):
            self.__make_test_target(context, request).save()

    def test_save_with_validation_error(self):
        """
        Test AugusTicketView.save
        オーガスデータとAltairの席種でバリデーションエラーとなるケース
        """
        from altair.app.ticketing.core.models import AugusTicket, StockType
        event, augus_performance = self.__make_base_test_data()
        augus_tickets = [
            AugusTicket(
                id=1,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'指定席チケット',
                augus_seat_type_classif=u'1',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1000,
                augus_performance_id=augus_performance.id
            ),
            AugusTicket(
                id=2,
                augus_venue_code=augus_performance.augus_venue_code,
                augus_seat_type_code=1,
                augus_seat_type_name=u'自由席チケット',
                augus_seat_type_classif=u'2',
                unit_value_code=0,
                unit_value_name=u'定価',
                value=1500,
                augus_performance_id=augus_performance.id
            )
        ]
        stock_types = [
            StockType(
                id=1,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1,
                quantity_only=True
            ),
            StockType(
                id=2,
                event_id=event.id,
                display_order=1,
                display=1,
                disp_reports=1,
                quantity_only=False
            )
        ]
        self.__session.add_all(augus_tickets)
        self.__session.add_all(stock_types)
        self.__session.flush()

        def mock_route_path(arg1, event_id=None):
            return 'http://dummy_route_path'

        def mock_route_url(arg1, event_id=None):
            return 'http://dummy_route_url'

        flash_msg_list = list()

        def mock_flash(flash_msg):
            flash_msg_list.append(flash_msg)

        request = DummyRequest(
            params={u"stock_type-1": u"1", u"stock_type-2": u"2"},
            route_path=mock_route_path,
            route_url=mock_route_url,
            session=DummyResource(
                flash=mock_flash
            )
        )
        context = DummyResource(
            event=DummyResource(id=1)
        )

        self.__make_test_target(context, request).save()

        # 指定席のAugusTicketと自由席のStockType連携、自由席のAugusTicketと指定席のStockType連携の2つ分のエラーとなるはず
        self.assertEqual(len(flash_msg_list), 2)
