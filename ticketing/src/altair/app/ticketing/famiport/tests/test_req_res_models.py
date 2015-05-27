# -*- coding: utf-8 -*-
from unittest import TestCase
import datetime
from pyramid.testing import (
    setUp,
    tearDown,
    DummyRequest,
    )
from altair.app.ticketing.testing import (
    _setup_db,
    _teardown_db,
    )


class FamiPortModelTestCase(TestCase):
    def setUp(self):
        self.now = datetime.datetime.now()
        self.session = _setup_db([
            'altair.app.ticketing.famiport.models',
            ])
        self.request = DummyRequest()
        self.config = setUp(
            request=self.request,
            settings={},
            )
        # self.config.include('altair.app.ticketing.faimport')  # mm

    def tearDown(self):
        tearDown()
        self.session.remove()
        _teardown_db()

    def _target(self):
        return None

    def _makeOne(self, *args, **kwds):
        target = self._target()
        return target(*args, **kwds)

    def _callFUT(self, func, *args, **kwds):
        return func(*args, **kwds)


class FamiPortReservationInquiryRequestTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortReservationInquiryRequest as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'storeCode': '0123',
            'ticketingDate': '20150530010203',
            'reserveNumber': u'112345678',
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortPaymentTicketingRequestTest(FamiPortModelTestCase):

    def _target(self):
        from ..communication import FamiPortPaymentTicketingRequest as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'storeCode': '0123',
            'mmkNo': '0123',
            'ticketingDate': '20150530010203',
            'sequenceNo': '1234',
            'playGuideId': '0234783428',
            'barCodeNo': '58315793859',
            'customerName': u'楽天太郎',
            'phoneNumber': u'07011112222',
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortPaymentTicketingCompletionRequestTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortPaymentTicketingRequest as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'storeCode': '0123',
            'mmkNo': '0123',
            'ticketingDate': '20150530010203',
            'sequenceNo': '1234',
            'playGuideId': '0234783428',
            'barCodeNo': '58315793859',
            'customerName': u'楽天太郎',
            'phoneNumber': u'07011112222',
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortPaymentTicketingCancelRequestTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortPaymentTicketingCancelRequest as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'storeCode': '0123',
            'mmkNo': '0123',
            'ticketingDate': '20150530010203',
            'sequenceNo': '1234',
            'playGuideId': '0234783428',
            'barCodeNo': '58315793859',
            'orderId': u'07011112222',
            'cancelCode': u'1',
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortInformationRequestTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortInformationRequest as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'infoKubun': '123456',  # 案内種別
            'storeCode': '3352',  # 店舗コード
            'kogyoCode': '1234',  # 興行コード
            'kogyoSubCode': 'FIREHFRE',  # 興行サブコード
            'koenCode': 'HGREIHGE',  # 公演コード
            'uketsukeCode': 'HIGROEIHGR',  # 受付コード
            'playGuideId': 'HGREH',  # クライアントID
            'authCode': '1289rh',  # 認証コード
            'reserveNumber': 'XX000001234',  # 予約照会番号
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortCustomerInformationRequestTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortCustomerInformationRequest as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'storeCode': '1234',  # 店舗コード
            'mmkNo': '01824',  # 発券Famiポート番号
            'ticketingDate': '20150101000000',  # 利用日時
            'sequenceNo': '1',  # 処理通番
            'barCodeNo': '124',  # バーコード情報
            'playGuideId': '12345',  # クライアントID
            'orderId': '012',  # 注文ID
            'totalAmount': '100',  # 入金金額
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortTicketResponseTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortTicketResponse as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'barCodeNo': '104y38q',  # チケットバーコード番号
            'ticketClass': '12345',  # チケット区分
            'templateCode': '12345',  # テンプレートコード
            'ticketData': u'9tty8grheg9hrg0h093h0q9hg0q439h',  # 券面データ
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortReservationInquiryResponseTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortReservationInquiryResponse as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'resultCode': '1245',  # 処理結果
            'replyClass': '3289',  # 応答結果区分
            'replyCode': '9714',  # 応答結果
            'playGuideId': '021942',  # クライアントID
            'barCodeNo': '12974',  # 支払番号
            'totalAmount': '100',  # 合計金額
            'ticketPayment': '80',  # チケット料金
            'systemFee': '10',  # システム利用料
            'ticketingFee': '10',  # 店頭発券手数料
            'ticketCountTotal': '5',  # チケット枚数
            'ticketCount': '3',  # 本券購入枚数
            'kogyoName': u'興行名',  # 興行名
            'koenDate': '20150101000000',  # 公園日時
            'name': u'楽天太郎',  # お客様氏名
            'nameInput': '1',  # 氏名要求フラグ
            'phoneInput': '1',  # 電話番号要求フラグ
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortPaymentTicketingResponseTest(FamiPortModelTestCase):

    def _target(self):
        from ..communication import FamiPortPaymentTicketingResponse as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'resultCode': '123',  # 処理結果
            'storeCode': '2147',  # 店舗コード
            'sequenceNo': '82398',  # 処理通番
            'barCodeNo': 't439qtq309',  # 支払番号
            'orderId': '65431',  # 注文ID
            'replyClass': '912742',  # 応答結果区分
            'replyCode': '194',  # 応答結果
            'playGuideId': '105',  # クライアントID
            'playGuideName': '018',  # クライアント漢字名称
            'orderTicketNo': '91',  # 払込票番号
            'exchangeTicketNo': '1',  # 引換票番号
            'ticketingStart': '2',  # 発券開始日時
            'ticketingEnd': '3',  # 発券期限日時
            'totalAmount': '4',  # 合計金額
            'ticketPayment': '5',  # チケット料金
            'systemFee': '6',  # システム利用料
            'ticketingFee': '7',  # 店頭発券手数料
            'ticketCountTotal': '8',  # チケット枚数
            'ticketCount': '9',  # 本券購入枚数
            'kogyoName': '10',  # 興行名
            'koenDate': '11',  # 公演日時
            'barCodeNo': '12',  # チケットバーコード番号
            'ticketClass': '13',  # チケット区分
            'templateCode': '14',  # テンプレートコード
            'ticketData': '15',  # 券面データ
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortPaymentTicketingCompletionResponseTest(FamiPortModelTestCase):

    def _target(self):
        from ..communication import FamiPortPaymentTicketingCompletionResponse as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'resultCode': '123456',  # 処理結果
            'storeCode': '837',  # 店舗コード
            'sequenceNo': '3',  # 処理通番
            'barCodeNo': '2',  # 支払番号
            'orderId': '4',  # 注文ID
            'replyCode': '5',  # 応答結果
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortPaymentTicketingCancelResponseTest(FamiPortModelTestCase):

    def _target(self):
        from ..communication import FamiPortPaymentTicketingCancelResponse as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'resultCode': '1',  # 処理結果
            'storeCode': '2',  # 店舗コード
            'sequenceNo': '3',  # 処理通番
            'barCodeNo': '4',  # 支払番号
            'orderId': '5',  # 注文ID
            'replyCode': '6',  # 応答結果
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortInformationResponseTest(FamiPortModelTestCase):

    def _target(self):
        from ..communication import FamiPortInformationResponse as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'resultCode': '1',  # 処理結果
            'infoKubun': '6',  # 案内区分
            'infoMessage': u'メッセージメッセージメッセージ',  # 内容文言
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)


class FamiPortCustomerInformationResponseTest(FamiPortModelTestCase):
    def _target(self):
        from ..communication import FamiPortCustomerInformationResponse as klass
        return klass

    def test_it(self):
        target = self._target()
        kwds = {
            'resultCode': '1',  # 処理結果
            'replyCode': '2',  # 応答結果
            'name': u'楽天太郎',  # 氏名
            'memberId': '3',  # 会員ID
            'address1': '4',  # 住所1
            'address2': '5',  # 住所2
            'identifyNo': '6',  # 半券個人識別番号
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)
