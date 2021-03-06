# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta

import sqlahelper
import mock
import transaction

from altair.app.ticketing.skidata.exceptions import SkidataSendWhitelistError
from altair.app.ticketing.skidata.models import SkidataBarcodeErrorHistory
from altair.skidata.api import make_whitelist
from altair.skidata.interfaces import ISkidataSession
from altair.skidata.models import SkidataWebServiceResponse, Error, HSHErrorType, HSHErrorNumber, TSAction, TSOption
from altair.skidata.sessions import SkidataWebServiceSession
from pyramid.path import DottedNameResolver
from pyramid.testing import DummyModel, DummyRequest, tearDown


class CreateNewBarcodeTest(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import create_new_barcode
        return create_new_barcode(*args, **kwargs)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_create_new_barcode_success(self, find_all_by_order_no, insert_new_barcode):
        """ create_new_barcodeの正常系テスト """
        find_all_by_order_no.return_value = [DummyModel(id=1), DummyModel(id=2)]
        self.__call_test_target(order_no='TEST0000001')
        self.assertTrue(insert_new_barcode.called)


class UpdateBarcodeToRereshOrder(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import update_barcode_to_refresh_order
        return update_barcode_to_refresh_order(*args, **kwargs)

    @staticmethod
    def _create_token_with_quantity_only(token_id, item_name, serial):
        return DummyModel(
            id=token_id,
            serial=serial,
            item=DummyModel(
                product_item=DummyModel(
                    name=item_name,
                    product=DummyModel(
                        seat_stock_type=DummyModel(
                            quantity_only=True
                        )
                    )
                )
            )
        )

    @staticmethod
    def _create_token_with_seat(token_id, item_name, seat_name):
        return DummyModel(
            id=token_id,
            seat=DummyModel(name=seat_name),
            item=DummyModel(
                product_item=DummyModel(
                    name=item_name,
                    product=DummyModel(
                        seat_stock_type=DummyModel(
                            quantity_only=False
                        )
                    )
                )
            )
        )

    @staticmethod
    def _create_request():
        def mock_query_utility(arg):
            return DummyModel()
        request = DummyModel(
            registry=DummyModel(
                queryUtility=mock_query_utility
            )
        )
        return request

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_update_to_modify_with_quantity_only(self, find_all_by_order_no, update_token):
        """ 正常系テスト 数受けの予約更新　予約商品増減なし """
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)
            ),
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_quantity_only(2, u'テスト商品', 1)
            ),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0),
            self._create_token_with_quantity_only(11, u'テスト商品', 1)
        ]

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_update_to_add_with_quantity_only(self, find_all_by_order_no, insert_new_barcode, update_token):
        """ 正常系テスト 数受けの予約更新　予約商品を増やす """
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)
            ),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0),
            self._create_token_with_quantity_only(11, u'テスト商品', 1)
        ]

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(insert_new_barcode.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.cancel')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_cancel_with_quantity_only(self, find_all_by_order_no, cancel, update_token):
        """ 正常系テスト 数受けの予約更新　予約商品を減らす """
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)
            ),
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_quantity_only(2, u'テスト商品', 1)
            ),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0)
        ]

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(cancel.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.send_whitelist_to_skidata')
    @mock.patch('altair.app.ticketing.skidata.api.make_whitelist')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.find_by_barcode')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_delete_whitelist_with_quantity_only(self, find_all_by_order_no, find_by_barcode, make_whitelist,
                                                            send_whitelist_to_skidata, update_token):
        """ 正常系テスト 数受けの予約更新　予約商品を減らす Whitelist送信済 """
        from datetime import datetime
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=datetime.now(),
                data='test-barcode1',
                ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)
            ),
            DummyModel(
                id=1,
                sent_at=datetime.now(),
                data='test-barcode2',
                ordered_product_item_token=self._create_token_with_quantity_only(2, u'テスト商品', 1)
            ),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0)
        ]
        find_by_barcode.return_value = test_existing_barcode_list[0]
        make_whitelist.return_value = DummyModel()

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(find_by_barcode.called)
        self.assertTrue(make_whitelist.called)
        self.assertTrue(send_whitelist_to_skidata.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_modify_with_seat(self, find_all_by_order_no, update_token):
        """ 正常系テスト 席ありの予約更新　予約商品増減なし """
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')
            ),
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_seat(2, u'テスト商品', u'23番席')
            )
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席'),
            self._create_token_with_seat(11, u'テスト商品', u'23番席')
        ]

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_add_with_seat(self, find_all_by_order_no, insert_new_barcode, update_token):
        """ 正常系テスト 席ありの予約更新　予約商品を増やす """
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')
            )
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席'),
            self._create_token_with_seat(11, u'テスト商品', u'23番席')
        ]

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(insert_new_barcode.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.cancel')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_cancel_with_seat(self, find_all_by_order_no, cancel, update_token):
        """  refreshの正常系テスト 席ありの予約更新　予約商品を減らす """
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')
            ),
            DummyModel(
                id=1,
                sent_at=None,
                ordered_product_item_token=self._create_token_with_seat(2, u'テスト商品', u'23番席')
            ),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席')
        ]

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(cancel.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.skidata.api.send_whitelist_to_skidata')
    @mock.patch('altair.app.ticketing.skidata.api.make_whitelist')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.find_by_barcode')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_delete_whitelist_with_seat(self, find_all_by_order_no, find_by_barcode, make_whitelist,
                                                   send_whitelist_to_skidata, update_token):
        """  refreshの正常系テスト 席ありの予約更新　予約商品を減らす """
        from datetime import datetime
        test_request = self._create_request()
        test_existing_barcode_list = [
            DummyModel(
                id=1,
                sent_at=datetime.now(),
                data='test-barcode1',
                ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')
            ),
            DummyModel(
                id=1,
                sent_at=datetime.now(),
                data='test-barcode2',
                ordered_product_item_token=self._create_token_with_seat(2, u'テスト商品', u'23番席')
            ),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席')
        ]
        find_by_barcode.return_value = test_existing_barcode_list[0]
        make_whitelist.return_value = DummyModel()

        self.__call_test_target(test_request, u'TEST000001', test_existing_barcode_list)
        self.assertTrue(find_by_barcode.called)
        self.assertTrue(make_whitelist.called)
        self.assertTrue(send_whitelist_to_skidata.called)
        self.assertTrue(update_token.called)


class SkidataWhitelistBaseTest(unittest.TestCase):
    @staticmethod
    def _create_order(order_no, start_on, is_paid=True, enable_skidata=True):
        return DummyModel(
            order_no=order_no,
            paid_at=(start_on - timedelta(days=7)) if is_paid else None,
            canceled_at=None,
            refunded_at=None,
            refund_id=None,
            performance=DummyModel(
                start_on=start_on,
                event=DummyModel(
                    setting=DummyModel(enable_skidata=enable_skidata),
                    organization=DummyModel(
                        setting=DummyModel(enable_skidata=enable_skidata)
                    )
                )
            )
        )

    @staticmethod
    def _create_skidata_barcode(order_no, barcode_id, qr_code, start_on, is_sent=False):
        return DummyModel(
            id=barcode_id,
            data=qr_code,
            sent_at=(start_on - timedelta(days=1)) if is_sent else None,
            canceled_at=None,
            ordered_product_item_token=DummyModel(
                seat=DummyModel(name=u'テスト座席'),
                item=DummyModel(
                    ordered_product=DummyModel(
                        order=DummyModel(order_no=order_no)
                    ),
                    product_item=DummyModel(
                        name=u'テスト商品明細',
                        skidata_property=DummyModel(value=u'テストチケット種別'),
                        product=DummyModel(
                            name=u'テスト商品',
                            sales_segment=DummyModel(
                                name=u'テスト販売区分',
                                sales_segment_group=DummyModel(
                                    skidata_property=DummyModel(value=u'テスト大人子供プロパティ')
                                )
                            )
                        ),
                        performance=DummyModel(
                            name=u'テスト公演',
                            start_on=start_on,
                            open_on=start_on - timedelta(hours=1),
                            event=DummyModel(organization=DummyModel(code=u'RE'))
                        ),
                        stock=DummyModel(
                            stock_type=DummyModel(
                                name='テスト席種',
                                attribute=u'テストゲート'
                            )
                        )
                    )
                )
            )
        )


class InsertWhitelistTest(SkidataWhitelistBaseTest):
    def setUp(self):
        self.request = DummyRequest()
        self.request.registry.registerUtility(mock.Mock(), ISkidataSession)

    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import send_whitelist_if_necessary
        send_whitelist_if_necessary(*args, **kwargs)

    @mock.patch('altair.app.ticketing.skidata.api.date')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.skidata.api.send_whitelist_to_skidata')
    def test_insert_whitelist(self, mock_send_whitelist_to_skidata, mock_find_all_by_order_no, mock_date):
        """正常系テスト　入金済みで今日開演の公演の予約に紐づくSkidataBarcodeからWhitelistから作成して送信"""
        order_no = 'RE0000000001'
        today = datetime(2020, 8, 1, 13, 0, 0)
        # 入金済みで今日開演の公演の予約
        order = self._create_order(order_no, today)

        barcode = self._create_skidata_barcode(order_no=order_no, barcode_id=1,
                                               qr_code='97XXXXXXXXXXXXXXXX01', start_on=today)
        mock_date.today.return_value = today.date()
        mock_find_all_by_order_no.return_value = [barcode]

        self.__call_test_target(request=self.request, order=order)
        self.assertTrue(mock_send_whitelist_to_skidata.called)

    @mock.patch('altair.app.ticketing.skidata.api.date')
    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.skidata.api.send_whitelist_to_skidata')
    def test_not_insert_whitelist(self, mock_send_whitelist_to_skidata, mock_find_all_by_order_no, mock_date):
        """正常系テスト　条件に合わない場合はWhitelistを送信しない"""
        order_no = 'RE0000000001'
        today = datetime(2020, 8, 1, 13, 0, 0)
        mock_date.today.return_value = today.date()

        # 未入金の予約
        order = self._create_order(order_no, today, is_paid=False)
        self.__call_test_target(request=self.request, order=order)
        self.assertFalse(mock_send_whitelist_to_skidata.called)

        # Skidata連携OFFのイベントの予約
        order = self._create_order(order_no, today, enable_skidata=False)
        self.__call_test_target(request=self.request, order=order)
        self.assertFalse(mock_send_whitelist_to_skidata.called)

        # 昨日開演の公演の予約
        yesterday = today - timedelta(days=1)
        order = self._create_order(order_no, yesterday)
        self.__call_test_target(request=self.request, order=order)
        self.assertFalse(mock_send_whitelist_to_skidata.called)

        # SkidataBarcodeが連携済み
        order = self._create_order(order_no, today)
        barcode = self._create_skidata_barcode(order_no=order_no, barcode_id=1, qr_code='97XXXXXXXXXXXXXXXX01',
                                               start_on=today, is_sent=True)
        mock_find_all_by_order_no.return_value = [barcode]

        mock_date.today.return_value = today.date()
        self.__call_test_target(request=self.request, order=order)
        self.assertFalse(mock_send_whitelist_to_skidata.called)


class DeleteWhitelistTest(SkidataWhitelistBaseTest):
    def setUp(self):
        self.request = DummyRequest()
        self.request.registry.registerUtility(mock.Mock(), ISkidataSession)

    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import delete_whitelist_if_necessary
        delete_whitelist_if_necessary(*args, **kwargs)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.skidata.api.send_whitelist_to_skidata')
    def test_delete_whitelist(self, mock_send_whitelist_to_skidata, mock_find_all_by_order_no):
        """正常系テスト　予約に紐づく連携済みのSkidataBarcodeからWhitelistから作成して送信"""
        order_no = 'RE0000000001'
        barcode = self._create_skidata_barcode(order_no=order_no, barcode_id=1, qr_code='97XXXXXXXXXXXXXXXX01',
                                               start_on=datetime.now(), is_sent=True)
        mock_find_all_by_order_no.return_value = [barcode]

        self.__call_test_target(request=self.request, order_no=order_no)
        self.assertTrue(mock_send_whitelist_to_skidata.called)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.skidata.api.send_whitelist_to_skidata')
    def test_not_delete_whitelist(self, mock_send_whitelist_to_skidata, mock_find_all_by_order_no):
        """正常系テスト　予約に紐づくSkidataBarcodeが未連携の場合はWhitelistを削除しない"""
        order_no = 'RE0000000001'
        barcode = self._create_skidata_barcode(order_no=order_no, barcode_id=1, qr_code='97XXXXXXXXXXXXXXXX01',
                                               start_on=datetime.now(), is_sent=False)
        mock_find_all_by_order_no.return_value = [barcode]

        self.__call_test_target(request=self.request, order_no=order_no)
        self.assertFalse(mock_send_whitelist_to_skidata.called)


class SendWhitelistTest(SkidataWhitelistBaseTest):
    def setUp(self):
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine

        self.engine = create_engine('sqlite://')
        sqlahelper.add_engine(self.engine)

        resolver = DottedNameResolver()
        resolver.resolve('altair.app.ticketing.core.models')
        resolver.resolve('altair.app.ticketing.orders.models')
        resolver.resolve('altair.app.ticketing.skidata.models')

        base = sqlahelper.get_base()
        base.metadata.bind = self.engine
        base.metadata.create_all(bind=self.engine)
        self.scoped_session = sessionmaker(bind=self.engine, autocommit=True)

    def tearDown(self):
        transaction.abort()
        session = sqlahelper.get_session()
        session.remove()
        tearDown()

    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import send_whitelist_to_skidata
        send_whitelist_to_skidata(*args, **kwargs)

    @staticmethod
    def _make_skidata_session(errors=None):
        skidata_resp = SkidataWebServiceResponse(status_code=200, text='')
        success_prop = mock.PropertyMock(return_value=errors in (None, []))
        errors_prop = mock.PropertyMock(return_value=errors or [])
        type(skidata_resp).success = success_prop
        type(skidata_resp).errors = errors_prop

        skidata_session = SkidataWebServiceSession(
            url='http://localhost/ImporterWebService', timeout=20,
            version='HSHIF25', issuer='1', receiver='1'
        )
        skidata_session.send = mock.MagicMock(return_value=skidata_resp)
        return skidata_session

    def assert_error_history_inserted(self, *skidata_barcode):
        for barcode_list in skidata_barcode:
            barcode_list = SkidataBarcodeErrorHistory.find_all_by_barcode_id(barcode_list.id,
                                                                             session=sqlahelper.get_session())
            self.assertTrue(len(barcode_list) == 1)
            barcode_list[0].delete()

    def test_send_whitelist_for_insert(self):
        """正常系テスト　成功レスポンス: Whitelist追加リクエストを送信する"""
        qr_code = '97XXXXXXXXXXXXXXXX01'
        start_on = datetime(2020, 8, 1, 13, 0, 0)
        barcode = self._create_skidata_barcode(order_no='RE0000000001', barcode_id=1,
                                               qr_code=qr_code, start_on=start_on)
        expire = datetime(year=start_on.year, month=12, day=31, hour=23, minute=59, second=59)
        whitelist = make_whitelist(action=TSAction.INSERT, qr_code=qr_code, ts_option=TSOption(), expire=expire)

        self.assertIsNone(barcode.sent_at)

        session = self._make_skidata_session()
        self.__call_test_target(skidata_session=session, whitelist=whitelist, barcode_list=[barcode])

        # Whitelist追加成功の場合は sent_at を更新
        self.assertIsNotNone(barcode.sent_at)

    def test_send_whitelist_for_delete(self):
        """正常系テスト　成功レスポンス: Whitelist削除リクエストを送信する"""
        qr_code = '97XXXXXXXXXXXXXXXX01'
        start_on = datetime(2020, 8, 1, 13, 0, 0)
        barcode = self._create_skidata_barcode(order_no='RE0000000001', barcode_id=1,
                                               qr_code=qr_code, start_on=start_on)
        whitelist = make_whitelist(action=TSAction.DELETE, qr_code=qr_code)

        self.assertIsNone(barcode.canceled_at)

        session = self._make_skidata_session()
        self.__call_test_target(skidata_session=session, whitelist=whitelist, barcode_list=[barcode])

        # Whitelist削除成功の場合は canceled_at を更新
        self.assertIsNotNone(barcode.canceled_at)

    @mock.patch('altair.app.ticketing.skidata.api.sessionmaker')
    def test_send_whitelist_for_insert_and_handle_error(self, mock_sessionmaker):
        """
        正常系テスト　エラー要素を含むケース: インポート成功 or Warning エラーのWhitelistに一致するSkidataBarcode.sent_atを更新する
        """
        start_on = datetime(2020, 8, 1, 13, 0, 0)
        expire = datetime(year=start_on.year, month=12, day=31, hour=23, minute=59, second=59)

        warning_qr_code_for_insert = '97XXXXXXXXXXXXXXXX01'
        warning_barcode_for_insert = self._create_skidata_barcode(order_no='RE0000000001', barcode_id=1,
                                                                  qr_code=warning_qr_code_for_insert, start_on=start_on)
        warning_whitelist_for_insert = make_whitelist(action=TSAction.INSERT, qr_code=warning_qr_code_for_insert,
                                                      ts_option=TSOption(), expire=expire)

        error_qr_code_for_insert = '97XXXXXXXXXXXXXXXX02'
        error_barcode_for_insert = self._create_skidata_barcode(order_no='RE0000000001', barcode_id=2,
                                                                qr_code=error_qr_code_for_insert, start_on=start_on)
        error_whitelist_for_insert = make_whitelist(action=TSAction.INSERT, qr_code=error_qr_code_for_insert,
                                                    ts_option=TSOption(), expire=expire)

        success_qr_code_for_insert = '97XXXXXXXXXXXXXXXX03'
        success_barcode_for_insert = self._create_skidata_barcode(order_no='RE0000000001', barcode_id=3,
                                                                  qr_code=success_qr_code_for_insert, start_on=start_on)
        success_whitelist_for_insert = make_whitelist(action=TSAction.INSERT, qr_code=success_qr_code_for_insert,
                                                      ts_option=TSOption(), expire=expire)

        # Warningタイプのエラー
        warning_for_insert = Error(type_=HSHErrorType.WARNING, number=HSHErrorNumber.ALREADY_EXISTING_TS_PROPERTY,
                                   description='Already Existing TSProperty',
                                   whitelist=warning_whitelist_for_insert)
        # Errorタイプのエラー
        error_for_insert = Error(type_=HSHErrorType.ERROR, number=HSHErrorNumber.INVALID_DATA_TYPE,
                                 description='Invalid Data Type',
                                 whitelist=error_whitelist_for_insert)

        self.assertIsNone(success_barcode_for_insert.sent_at)
        self.assertIsNone(warning_barcode_for_insert.sent_at)
        self.assertIsNone(error_barcode_for_insert.sent_at)

        mock_sessionmaker.return_value = self.scoped_session
        session = self._make_skidata_session(errors=[warning_for_insert, error_for_insert])

        # fail_silentlyがFalseの場合はExceptionをraiseする
        self.assertRaises(SkidataSendWhitelistError, self.__call_test_target,
                          skidata_session=session,
                          whitelist=[warning_whitelist_for_insert, error_whitelist_for_insert,
                                     success_whitelist_for_insert],
                          barcode_list=[warning_barcode_for_insert, error_barcode_for_insert,
                                        success_barcode_for_insert],
                          fail_silently=False)
        # 連携エラーのデータが登録されている
        self.assert_error_history_inserted(warning_barcode_for_insert, error_barcode_for_insert)

        # Exceptionをraiseしない場合
        self.__call_test_target(skidata_session=session,
                                whitelist=[warning_whitelist_for_insert, error_whitelist_for_insert,
                                           success_whitelist_for_insert],
                                barcode_list=[warning_barcode_for_insert, error_barcode_for_insert,
                                              success_barcode_for_insert],
                                fail_silently=True)
        # インポート成功とWarningタイプのエラーのWhitelistに一致するSkidataBarcodeのみsent_atが更新されている
        self.assertIsNotNone(success_barcode_for_insert.sent_at)
        self.assertIsNotNone(warning_barcode_for_insert.sent_at)
        self.assertIsNone(error_barcode_for_insert.sent_at)
        # 連携エラーのデータが登録されている
        self.assert_error_history_inserted(warning_barcode_for_insert, error_barcode_for_insert)

    @mock.patch('altair.app.ticketing.skidata.api.sessionmaker')
    def test_send_whitelist_for_delete_and_handle_error(self, mock_sessionmaker):
        """
        正常系テスト　エラー要素を含むケース: インポート成功 or Warning エラーのWhitelistに一致するSkidataBarcode.canceled_atを更新する
        """
        start_on = datetime(2020, 8, 1, 13, 0, 0)

        warning_qr_code_for_delete = '97XXXXXXXXXXXXXXXX04'
        warning_barcode_for_delete = self._create_skidata_barcode(order_no='RE0000000002', barcode_id=4,
                                                                  qr_code=warning_qr_code_for_delete, start_on=start_on)
        warning_whitelist_for_delete = make_whitelist(action=TSAction.DELETE, qr_code=warning_qr_code_for_delete)

        error_qr_code_for_delete = '97XXXXXXXXXXXXXXXX05'
        error_barcode_for_delete = self._create_skidata_barcode(order_no='RE0000000002', barcode_id=5,
                                                                qr_code=error_qr_code_for_delete, start_on=start_on)
        error_whitelist_for_delete = make_whitelist(action=TSAction.DELETE, qr_code=error_qr_code_for_delete)

        success_qr_code_for_delete = '97XXXXXXXXXXXXXXXX06'
        success_barcode_for_delete = self._create_skidata_barcode(order_no='RE0000000002', barcode_id=6,
                                                                  qr_code=success_qr_code_for_delete, start_on=start_on)
        success_whitelist_for_delete = make_whitelist(action=TSAction.DELETE, qr_code=success_qr_code_for_delete)

        # Warningタイプのエラー
        warning_for_delete = Error(type_=HSHErrorType.WARNING, number=HSHErrorNumber.RECORD_DOES_NOT_EXIST,
                                   description='Delete, record does not exist',
                                   whitelist=warning_whitelist_for_delete)
        # Errorタイプのエラー
        error_for_delete = Error(type_=HSHErrorType.ERROR, number=HSHErrorNumber.NON_EXISTING_PERMISSION,
                                 description='Non Existing Permission',
                                 whitelist=error_whitelist_for_delete)

        self.assertIsNone(success_barcode_for_delete.canceled_at)
        self.assertIsNone(warning_barcode_for_delete.canceled_at)
        self.assertIsNone(error_barcode_for_delete.canceled_at)

        mock_sessionmaker.return_value = self.scoped_session
        session = self._make_skidata_session(errors=[warning_for_delete, error_for_delete])

        # fail_silentlyがFalseの場合はExceptionをraiseする
        self.assertRaises(SkidataSendWhitelistError, self.__call_test_target,
                          skidata_session=session,
                          whitelist=[warning_whitelist_for_delete, error_whitelist_for_delete,
                                     success_whitelist_for_delete],
                          barcode_list=[warning_barcode_for_delete, error_barcode_for_delete,
                                        success_barcode_for_delete],
                          fail_silently=False)
        # 連携エラーのデータが登録されている
        self.assert_error_history_inserted(warning_barcode_for_delete, error_barcode_for_delete)

        # Exceptionをraiseしない場合
        self.__call_test_target(skidata_session=session,
                                whitelist=[warning_whitelist_for_delete, error_whitelist_for_delete,
                                           success_whitelist_for_delete],
                                barcode_list=[warning_barcode_for_delete, error_barcode_for_delete,
                                              success_barcode_for_delete],
                                fail_silently=True)
        # インポート成功とWarningタイプのエラーのWhitelistに一致するSkidataBarcodeのみcanceled_atが更新されている
        self.assertIsNotNone(success_barcode_for_delete.canceled_at)
        self.assertIsNotNone(warning_barcode_for_delete.canceled_at)
        self.assertIsNone(error_barcode_for_delete.canceled_at)
        # 連携エラーのデータが登録されている
        self.assert_error_history_inserted(warning_barcode_for_delete, error_barcode_for_delete)

    def test_send_whitelist_and_handle_stop_error(self):
        """
        正常系テスト　エラー要素を含むケース: Stop エラー
        """
        start_on = datetime(2020, 8, 1, 13, 0, 0)

        qr_code = '97XXXXXXXXXXXXXXXX01'
        barcode = self._create_skidata_barcode(order_no='RE0000000001', barcode_id=1,
                                               qr_code=qr_code, start_on=start_on)
        whitelist = make_whitelist(action=TSAction.DELETE, qr_code=qr_code)

        # Stopタイプのエラー
        stop_error = Error(type_=HSHErrorType.STOP, number=HSHErrorNumber.HSH_INTERNAL_ERROR,
                           description='HSH internal error')

        self.assertIsNone(barcode.canceled_at)

        session = self._make_skidata_session(errors=[stop_error])

        # fail_silentlyがFalseの場合はExceptionをraiseする
        self.assertRaises(SkidataSendWhitelistError, self.__call_test_target,
                          skidata_session=session,
                          whitelist=whitelist,
                          barcode_list=[barcode],
                          fail_silently=False)

        # Exceptionをraiseしない場合
        self.__call_test_target(skidata_session=session,
                                whitelist=whitelist,
                                barcode_list=[barcode],
                                fail_silently=True)
        # 全インポート処理失敗なので、SkidataBarcodeのみcanceled_atは更新されていない
        self.assertIsNone(barcode.canceled_at)
