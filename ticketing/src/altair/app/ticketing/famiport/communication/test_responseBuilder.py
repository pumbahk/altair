# -*- coding: utf-8 -*-
import unittest
from unittest import skip
from datetime import (
    date,
    datetime,
    timedelta,
)
from decimal import Decimal
import mock
from pyramid.testing import DummyRequest, setUp, tearDown
from altair.sqlahelper import get_global_db_session

from ..api import get_response_builder
from .builders import FamiPortRequestFactory
from .models import (
    FamiPortRequestType,
    InformationResultCodeEnum,
    FamiPortReservationInquiryRequest,
    FamiPortPaymentTicketingRequest,
    FamiPortPaymentTicketingCompletionRequest,
    FamiPortPaymentTicketingCancelRequest,
    FamiPortInformationRequest,
    FamiPortCustomerInformationRequest,
    )
from ..models import FamiPortInformationMessage
from ..testing import _setup_db, _teardown_db


class FamiPortResponseBuilderTestBase(object):
    barcode_no_cash_on_delivery = u'01234012340123'
    barcode_no_payment = u'01234012340124'
    barcode_no_payment_ticketing = u'01234012340125'
    barcode_no_payment_only = u'01234012340126'
    barcode_no_ticketing_only = u'01234012340127'
    barcode_no_name = u'01234012340128'

    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.config.include('.')
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                'altair.app.ticketing.famiport.communication.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')
        from ..models import (
            FamiPortPrefecture,
            FamiPortPlayguide,
            FamiPortClient,
            FamiPortVenue,
            FamiPortGenre1,
            FamiPortGenre2,
            FamiPortSalesChannel,
            FamiPortPerformanceType,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortSalesSegment,
            FamiPortInformationMessage,
            FamiPortPrefecture,
            FamiPortOrder,
            FamiPortReceipt,
            FamiPortOrderType,
            FamiPortReceiptType,
            FamiPortTicketType,
            FamiPortTicket,
            FamiPortShop,
            )
        self.famiport_shop = FamiPortShop(
            code=u'000009',
            company_code=u'TEST',
            company_name=u'TEST',
            district_code=u'TEST',
            district_name=u'TEST',
            district_valid_from=date(2015, 6, 1),
            branch_code=u'TEST',
            branch_name=u'TEST',
            branch_valid_from=date(2015, 6, 1),
            name=u'TEST',
            name_kana=u'TEST',
            tel=u'070111122222',
            prefecture=1,
            prefecture_name=u'東京都',
            address=u'東京都品川区西五反田',
            open_from=date(2015, 6, 1),
            zip=u'1410000',
            business_run_from=date(2015, 6, 1),
            )
        self.session.add(self.famiport_shop)
        self.famiport_playguide = FamiPortPlayguide(
            discrimination_code=5,
            discrimination_code_2=4
            )
        self.famiport_client = FamiPortClient(
            playguide=self.famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        self.famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        self.famiport_genre_2 = FamiPortGenre2(
            genre_1=self.famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        self.famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        self.famiport_event = FamiPortEvent(
            client=self.famiport_client,
            venue=self.famiport_venue,
            genre_1=self.famiport_genre_1,
            genre_2=self.famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=u'000000',
            code_2=u'1111',
            name_1=u'テスト公演',
            name_2=u'テスト公演副題',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        self.famiport_performance = FamiPortPerformance(
            famiport_event=self.famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        self.famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=self.famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 10, 0, 0),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )
        self.famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000000',
            famiport_order_identifier=u'000011112222',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    barcode_no=self.barcode_no_cash_on_delivery,
                    famiport_order_identifier=u'000011112223',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000001',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000002',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    )
                ],
            customer_name_input=True,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )
        self.session.add(self.famiport_order_cash_on_delivery)
        self.famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112225',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 22, 00, 00, 00),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 21, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    barcode_no=self.barcode_no_payment,
                    famiport_order_identifier=u'000011112224',
                    shop_code=u'00009',
                    reserve_number=u'4321043210433',
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    barcode_no=self.barcode_no_payment_ticketing,
                    famiport_order_identifier=u'000011112225',
                    shop_code=u'00009',
                    reserve_number=u'4321043210434',
                    )
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000004',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    )
                ],
            customer_name_input=True,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )
        self.session.add(self.famiport_order_payment)
        self.famiport_order_payment_only = FamiPortOrder(
            type=FamiPortOrderType.PaymentOnly.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112226',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=None,
            ticketing_end_at=None,
            payment_start_at=datetime(2015, 5, 22, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'000011112227',
                    barcode_no=self.barcode_no_payment_only,
                    shop_code=u'00009',
                    reserve_number=u'4321043210435'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000005',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000006',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    )
                ],
            customer_name_input=True,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 22, 12, 34, 56)
            )
        self.session.add(self.famiport_order_payment_only)

        self.famiport_order_ticketing_only = FamiPortOrder(
            type=FamiPortOrderType.Ticketing.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112228',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 22, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=None,
            payment_due_at=None,
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'000011112229',
                    barcode_no=self.barcode_no_ticketing_only,
                    shop_code=u'00009',
                    reserve_number=u'4321043210436'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000007',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000008',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    )
                ],
            customer_name_input=True,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 22, 12, 34, 56)
            )
        self.session.add(self.famiport_order_ticketing_only)

        self.famiport_order_no_name = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112230',
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'000011112231',
                    barcode_no=self.barcode_no_name,
                    shop_code=u'00009',
                    reserve_number=u'4321043210437'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000009',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000010',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    price=5000,
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 22, 12, 34, 56)
            )
        self.session.add(self.famiport_order_no_name)
        self.session.commit()
        self.now = datetime(2015, 5, 21, 10, 0, 0)

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()


class FamiPortInformationMessageResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    """FamiPort案内通信で返すためのデータの作成

    リクエストからInformationMessageのデータを検索して
    その中から最もふさわしい内容のメッセージを返す。

    検索の優先度
    ============

    1. サービス不可エラー -> 無条件に返す
    2. その他メッセージ

       1. 予約用のメッセージ
       2. 受付コード (この受付コードからFamiPortOrderを引くことができることを仮定する)
       3. 販売区分用のメッセージ
       4. 公演
       5. イベントサブコード
       6. イベントコード
       7. クライアントコード

    3. メッセージなし

    同じ階層のメッセージがある場合はエラーコードが大きいものを返すようにする。
    (エラーコードを優先させるため)

    インプット分析
    --------------

    infoKubun: 1, 2, ブランク
    storeCode: 000001, アルファベットが入っている, ブランク
    kogyoCode: 000001, 存在しない, アルファベットが入っている, ブランク
    kogyoSubCode: 000a, 存在しない, ブランク
    koenCode: 00a, 存在しない, ブランク
    uketsukeCode: 00a, 存在しない, ブランク
    playGuideId: 00000000000000000000000a, 存在しない, ブランク
    authCode: '0' * 100, ブランク
    reserveNumber: 000000000000a, 存在しない, ブランク

    状況分析
    --------

    FamiPortInformationMessage: あり, なし
    storeCode: 存在する, 存在しない
    kogyoCode: 存在する, 存在しない
    kogyoSubCode: 存在する, 存在しない
    koenCode: 存在する, 存在しない
    uketsukeCode: 存在する, 存在しない
    playGuideId: 存在する, 存在しない
    authCode: 存在する, 存在しない, 認証エラー
    reserveNumber: 存在する, 存在しない


    共通正常系
    ----------

    infoKubun: 1
    storeCode: 000001 (存在する)
    kogyoCode: 000001 (存在しない)
    kogyoSubCode: 000a (存在しない)
    koenCode: 00a (存在しない)
    uketsukeCode: 00a  (存在しない)
    playGuideId: 00000000000000000000000a  (存在する)
    authCode: ''
    reserveNumber: 000000000000a (存在する)

    次のようなデータがある場合を考える。

    - result_code: 1  # 案内あり
      message: 'この予約は払い戻しになりました。'
      reserve_number: 'RSV00001'
      event_code_1: 'EVENT1'
      event_code_2: 'ESB1'
      performance_code: 'PF1'
      sales_segment_code: 'UK1'
      client_code: 'FAMIPORT_CLIENT_CODE_001'
      famiport_sales_segment_id: 1
    - result_code: 90  # サービス不可時案内
      message: 'メンテナンス中です。ご迷惑をおかけします。'
      reserve_number: 'RSV00001'
      event_code_1: 'EVENT1'
      event_code_2: 'ESB1'
      performance_code: 'PF1'
      sales_segment_code: 'UK1'
      client_code: 'FAMIPORT_CLIENT_CODE_001'
      famiport_sales_segment_id: 1
    - result_code: 90  # サービス不可時案内
      message: 'メンテナンス中です。ご迷惑をおかけします。'
      reserve_number: 'RSV00001'
      event_code_1: 'EVENT1'
      event_code_2: 'ESB1'
      performance_code: 'PF1'
      sales_segment_code: 'UK1'
      client_code: 'FAMIPORT_CLIENT_CODE_001'
      famiport_sales_segment_id: 1
    """

    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def _create_famiport_request(self, *args, **kwds):
        from .models import FamiPortInformationRequest as klass
        return klass(*args, **kwds)

    def _get_target(self, *args, **kwds):
        from .builders import FamiPortInformationResponseBuilder as klass
        return klass(*args, **kwds)

    def _callFUT(self, *args, **kwds):
        target = self._get_target(self.request.registry)
        return target.build_response(*args, **kwds)

    def test_it(self):
        args = []
        kwds = {
            'infoKubun': '1',
            'storeCode': '000001',  # (存在する)
            'kogyoCode': '000001',  # (存在しない)
            'kogyoSubCode': '000a',  # (存在しない)
            'koenCode': '00a',  # (存在しない)
            'uketsukeCode': '00a',  # (存在しない)
            'playGuideId': '00000000000000000000000a',  # (存在する),
            'authCode': '',
            'reserveNumber': '000000000000a',  # (存在する)
            }

        session = None
        now = None

        famiport_request = self._create_famiport_request(*args, **kwds)
        res = self._callFUT(famiport_request, session, now, self.request)
        from .models import FamiPortInformationResponse
        self.assertTrue(type(res), FamiPortInformationResponse)

    def test_with_sales_segment(self):
        from .models import FamiPortInformationRequest
        from ..models import FamiPortInformationMessage
        self.session.add(
            FamiPortInformationMessage(
                result_code=u'01',
                event_code_1=self.famiport_order_cash_on_delivery.famiport_sales_segment.famiport_performance.famiport_event.code_1,
                event_code_2=self.famiport_order_cash_on_delivery.famiport_sales_segment.famiport_performance.famiport_event.code_2,
                performance_code=self.famiport_order_cash_on_delivery.famiport_sales_segment.famiport_performance.code,
                sales_segment_code=self.famiport_order_cash_on_delivery.famiport_sales_segment.code,
                client_code=self.famiport_order_cash_on_delivery.client_code,
                message=u'メッセージ'
                )
            )
        self.session.flush()
        famiport_request = FamiPortInformationRequest(
            infoKubun='1',
            storeCode=u'00001',
            kogyoCode=u'000000',
            kogyoSubCode=u'1111',
            koenCode=u'001',
            uketsukeCode=u'001',
            playGuideId=u'012340123401234012340123'
            )
        now = datetime(2015, 1, 1)
        res = self._callFUT(famiport_request, self.session, now, self.request)
        self.assertEqual(res.resultCode, u'01')
        self.assertEqual(res.infoKubun, u'1')
        self.assertEqual(res.infoMessage, u'メッセージ')


    def test_no_reserve_number_no_uketsuke_no(self):
        args = []
        kwds = {
            'infoKubun': '1',
            'storeCode': '000001',  # (存在する)
            'kogyoCode': '000001',  # (存在しない)
            'kogyoSubCode': '000a',  # (存在しない)
            'koenCode': '00a',  # (存在しない)
            'uketsukeCode': '',  # (存在しない)
            'playGuideId': '00000000000000000000000a',  # (存在する),
            'authCode': '',
            'reserveNumber': '',  # (存在しない)
            }

        session = mock.MagicMock()
        now = None

        famiport_request = self._create_famiport_request(*args, **kwds)
        res = self._callFUT(famiport_request, session, now, self.request)
        self.assertEqual(res.infoMessage, u'')
        self.assertEqual(res.resultCode, u'00')

    def test_reserve_number_no_famiport_order(self):
        """reserveNumberは指定されていたがその予約はない"""
        args = []
        kwds = {
            'infoKubun': '1',
            'storeCode': '000001',  # (存在する)
            'kogyoCode': '000001',  # (存在しない)
            'kogyoSubCode': '000a',  # (存在しない)
            'koenCode': '00a',  # (存在しない)
            'uketsukeCode': '',  # (存在しない)
            'playGuideId': '00000000000000000000000a',  # (存在する),
            'authCode': '',
            'reserveNumber': 'IHGREOHGOREIGHOE',  # (存在しない)
            }

        session = self.session
        now = None

        from ..models import FamiPortInformationMessage
        info_msg = FamiPortInformationMessage(
            result_code=1, message='test', reserve_number='', event_code_1='1', )
        self.session.add(info_msg)
        self.session.commit()

        famiport_request = self._create_famiport_request(*args, **kwds)
        res = self._callFUT(famiport_request, session, now, self.request)
        self.assertEqual(res.infoMessage, u'')
        self.assertEqual(res.resultCode, u'00')

    def test_direct_sales(self):
        args = []
        kwds = {
            'infoKubun': '2',
            'storeCode': '000001',
            'kogyoCode': '000001',
            'kogyoSubCode': '000a',
            'koenCode': '00a',
            'uketsukeCode': '00a',
            'playGuideId': '00000000000000000000000a',
            'authCode': '',
            'reserveNumber': '000000000000a',
            }

        session = None
        now = None

        famiport_request = self._create_famiport_request(*args, **kwds)
        res = self._callFUT(famiport_request, session, now, self.request)
        self.assertTrue(res.infoMessage, u'現在お取り扱いしておりません。')

    # 案内
    @skip('old')
    def test_with_information(self):
        famiport_information_with_information_message = FamiPortInformationMessage(
            result_code=InformationResultCodeEnum.WithInformation.value,
            message=u'WithInformation メッセージ',
            )
        self.session.add(famiport_information_with_information_message)
        self.session.commit()
        from .models import ResultCodeEnum, ReplyCodeEnum
        f_request = FamiPortRequestFactory.create_request(
            {
                'infoKubun':     u'1',
                'storeCode':     u'000009',
                'kogyoCode':     u'',
                'kogyoSubCode':  u'',
                'koenCode':      u'',
                'uketsukeCode':  u'',
                'playGuideId':   u'',
                'authCode':      u'',
                'reserveNumber': u'4000000000001',
                },
            FamiPortRequestType.Information
            )

        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, InformationResultCodeEnum.WithInformation.value)
        self.assertEqual(result.infoKubun, u'1')
        self.assertEqual(result.infoMessage, u'WithInformation メッセージ')

    # 案内
    @skip('old')
    def test_service_unavail(self):
        famiport_information_service_unavailable_message = FamiPortInformationMessage(
            result_code=InformationResultCodeEnum.ServiceUnavailable.value,
            message=u'Service Unavailableメッセージ',
            )
        self.session.add(famiport_information_service_unavailable_message)
        self.session.commit()
        f_request = FamiPortRequestFactory.create_request(
            {
                'infoKubun':     u'1',
                'storeCode':     u'000009',
                'kogyoCode':     u'',
                'kogyoSubCode':  u'',
                'koenCode':      u'',
                'uketsukeCode':  u'',
                'playGuideId':   u'',
                'authCode':      u'',
                'reserveNumber': u'4000000000001',
                },
            FamiPortRequestType.Information
            )

        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, InformationResultCodeEnum.ServiceUnavailable.value)
        self.assertEqual(result.infoKubun, u'1')
        self.assertEqual(result.infoMessage, u'Service Unavailableメッセージ')


class FamiPortCustomerInformationResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 顧客情報照会
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def _payment_receipt(self, barcode_no, minutes=15):
        from ..models import FamiPortReceipt
        receipt = self.session \
                      .query(FamiPortReceipt) \
                      .filter_by(barcode_no=barcode_no) \
                      .one()
        time_point = datetime.now() - timedelta(minutes=minutes)
        receipt.inquired_at = time_point
        receipt.payment_request_received_at = time_point
        receipt._at = time_point
        self.session.add(receipt)
        self.session.commit()

    def test_ok(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 0)
        f_request = FamiPortCustomerInformationRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100001',
            barCodeNo=self.barcode_no_cash_on_delivery,
            playGuideId=self.famiport_client.code,
            orderId=u'000011112222',
            totalAmount=u'10540'
            )
        self._payment_receipt(self.barcode_no_cash_on_delivery)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.name, u'チケット　太郎')
        self.assertEqual(result.memberId, u'')
        self.assertEqual(result.address1, u'東京都品川区西五反田7-1-9')
        self.assertEqual(result.address2, u'五反田HSビル9F')
        self.assertEqual(result.identifyNo, u'')

    def test_not_found(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        f_request = FamiPortCustomerInformationRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100001',
            barCodeNo=u'0123401234012X',
            playGuideId=self.famiport_client.code,
            orderId=u'00001111222X',
            totalAmount=u'10540'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.CustomerNamePrintInformationError.value)
        self.assertEqual(result.name, None)
        self.assertEqual(result.memberId, None)
        self.assertEqual(result.address1, None)
        self.assertEqual(result.address2, None)
        self.assertEqual(result.identifyNo, None)


class FamiPortReservationInquiryResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 予約照会
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def test_ok(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=u'4321043210432',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演') # 興行名なので、「テスト公演」であるべきでは? 確認
        self.assertEqual(result.koenDate, u'201507011900')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'1')
        self.assertEqual(result.phoneInput, u'0')

    def test_too_early(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150520000000',
            reserveNumber=u'4321043210432',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.SearchKeyError.value)
        self.assertEqual(result.playGuideId, u'')
        self.assertEqual(result.barCodeNo, u'')
        self.assertEqual(result.totalAmount, u'')
        self.assertEqual(result.ticketPayment, u'')
        self.assertEqual(result.systemFee, u'')
        self.assertEqual(result.ticketingFee, u'')
        self.assertEqual(result.ticketCountTotal, u'')
        self.assertEqual(result.ticketCount, u'')
        self.assertEqual(result.kogyoName, u'')
        self.assertEqual(result.koenDate, u'')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_too_late_ticketing(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150524000000',
            reserveNumber=self.famiport_order_ticketing_only.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.TicketingDueError.value)
        self.assertEqual(result.playGuideId, u'')
        self.assertEqual(result.barCodeNo, u'')
        self.assertEqual(result.totalAmount, u'')
        self.assertEqual(result.ticketPayment, u'')
        self.assertEqual(result.systemFee, u'')
        self.assertEqual(result.ticketingFee, u'')
        self.assertEqual(result.ticketCountTotal, u'')
        self.assertEqual(result.ticketCount, u'')
        self.assertEqual(result.kogyoName, u'')
        self.assertEqual(result.koenDate, u'')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_too_late_payment(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150524000000',
            reserveNumber=self.famiport_order_payment.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.PaymentDueError.value)
        self.assertEqual(result.playGuideId, u'')
        self.assertEqual(result.barCodeNo, u'')
        self.assertEqual(result.totalAmount, u'')
        self.assertEqual(result.ticketPayment, u'')
        self.assertEqual(result.systemFee, u'')
        self.assertEqual(result.ticketingFee, u'')
        self.assertEqual(result.ticketCountTotal, u'')
        self.assertEqual(result.ticketCount, u'')
        self.assertEqual(result.kogyoName, u'')
        self.assertEqual(result.koenDate, u'')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_too_late_cash_on_delivery(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150524000000',
            reserveNumber=self.famiport_order_cash_on_delivery.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.PaymentDueError.value)
        self.assertEqual(result.playGuideId, u'')
        self.assertEqual(result.barCodeNo, u'')
        self.assertEqual(result.totalAmount, u'')
        self.assertEqual(result.ticketPayment, u'')
        self.assertEqual(result.systemFee, u'')
        self.assertEqual(result.ticketingFee, u'')
        self.assertEqual(result.ticketCountTotal, u'')
        self.assertEqual(result.ticketCount, u'')
        self.assertEqual(result.kogyoName, u'')
        self.assertEqual(result.koenDate, u'')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_invalid_ticket_date(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20XX0521134001',
            reserveNumber=u'4321043210432',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyClass, None)
        self.assertEqual(result.replyCode, ReplyCodeEnum.OtherError.value)
        self.assertEqual(result.barCodeNo, None)
        self.assertEqual(result.totalAmount, None)
        self.assertEqual(result.ticketPayment, None)
        self.assertEqual(result.systemFee, None)
        self.assertEqual(result.ticketingFee, None)
        self.assertEqual(result.ticketCountTotal, None)
        self.assertEqual(result.ticketCount, None)
        self.assertEqual(result.kogyoName, None)
        self.assertEqual(result.koenDate, None)
        self.assertEqual(result.name, None)
        self.assertEqual(result.nameInput, None)
        self.assertEqual(result.phoneInput, None)

    def test_not_found(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=u'432104321043X',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, None)
        self.assertEqual(result.replyCode, ReplyCodeEnum.SearchKeyError.value)
        self.assertEqual(result.barCodeNo, u'')
        self.assertEqual(result.totalAmount, u'')
        self.assertEqual(result.ticketPayment, u'')
        self.assertEqual(result.systemFee, u'')
        self.assertEqual(result.ticketingFee, u'')
        self.assertEqual(result.ticketCountTotal, u'')
        self.assertEqual(result.ticketCount, u'')
        self.assertEqual(result.kogyoName, u'')
        self.assertEqual(result.koenDate, u'')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_no_name_input(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=u'4321043210437',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')  # 興行名なので、「テスト公演」であるべきでは? 確認
        self.assertEqual(result.koenDate, u'201507011900')
        self.assertEqual(result.name, u'チケット　太郎')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_regression_fifty_five(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=self.famiport_order_cash_on_delivery.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)
        barcode_no = result.barCodeNo

        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100002',
            playGuideId=u'012340123401234012340123',
            barCodeNo=barcode_no,
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100002')
        self.assertEqual(result.barCodeNo, barcode_no)
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=self.famiport_order_cash_on_delivery.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, None)
        self.assertEqual(result.replyCode, ReplyCodeEnum.TicketAlreadyIssuedError.value)
        self.assertEqual(result.playGuideId, u'')
        self.assertEqual(result.barCodeNo, u'')

    def test_reissuing(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=self.famiport_order_cash_on_delivery.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)
        barcode_no = result.barCodeNo

        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100002',
            playGuideId=u'012340123401234012340123',
            barCodeNo=barcode_no,
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100002')
        self.assertEqual(result.barCodeNo, barcode_no)
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=barcode_no,
            orderId=u'000011112223',
            totalAmount=u'00010540'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, barcode_no)
        self.assertEqual(result.orderId, u'000011112223')

        self.famiport_order_cash_on_delivery.make_reissueable(self.now, self.request)

        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=self.famiport_order_cash_on_delivery.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)


class FamiPortCancelResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 30分VOID処理

    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def _get_target_class(self):
        from .builders import FamiPortPaymentTicketingCancelResponseBuilder as klass
        return klass

    def _get_target(self, *args, **kwds):
        klass = self._get_target_class()
        return klass(*args, **kwds)

    def _callFUT(self, *args, **kwds):
        target = self._get_target(self.request.registry)
        return target.build_response(*args, **kwds)

    def _create_famiport_request(self, *args, **kwds):
        from .models import FamiPortPaymentTicketingCancelRequest as klass
        return klass(*args, **kwds)

    def test_ok(self):
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now, self.request)

    def test_illigal(self):
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now, self.request)

    def test_already_payment(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now, self.request)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_already_issued(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now, self.request)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_cannot_cancel(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now, self.request)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_no_receipt(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now, self.request)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_no_famport_order(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now, self.request)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)


class FamiPortPaymentTicketingResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 入金発券
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def test_cash_on_delivery(self):
        """代引"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100002',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100002')
        self.assertEqual(result.barCodeNo, u'01234012340123')
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340123')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_payment_valid_date(self):
        u"""前払後日の支払"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Prepayment.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112224')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340124')
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')  # reserve number
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_payment_earlier_date(self):
        u"""前払後日の支払、支払期間前"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150520100000',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.SearchKeyError.value)

    def test_payment_later_date(self):
        u"""前払後日の支払、支払期限切れ"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522003000',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.PaymentDueError.value)

    def test_payment_later_date_but_within_moratorium(self):
        u"""前払後日の支払"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522000000',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Prepayment.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112224')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340124')
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')  # reserve number
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_ticketing_for_paid_order(self):
        u"""前払後日の発券"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        self.famiport_order_payment.paid_at = datetime(2015, 5, 21, 13, 40, 1)
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522211234',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[1].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Paid.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112225')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')  # reserve number
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00000000')
        self.assertEqual(result.ticketPayment, u'00000000')
        self.assertEqual(result.systemFee, u'00000000')
        self.assertEqual(result.ticketingFee, u'00000000')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_ticketing_yet_unpaid(self):
        u"""前払後日の発券で未払"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522211234',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.SearchKeyError.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, None)
        self.assertEqual(result.playGuideId, None)
        self.assertEqual(result.playGuideName, None)
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, None)
        self.assertEqual(result.ticketingStart, None)
        self.assertEqual(result.ticketingEnd, None)
        self.assertEqual(result.totalAmount, None)
        self.assertEqual(result.ticketPayment, None)
        self.assertEqual(result.systemFee, None)
        self.assertEqual(result.ticketingFee, None)
        self.assertEqual(result.ticketCountTotal, None)
        self.assertEqual(result.ticketCount, None)
        self.assertEqual(result.kogyoName, None)
        self.assertEqual(result.koenDate, None)

    def test_ticketing_for_paid_order_earlier(self):
        u"""前払後日の発券、発券開始日時より前"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum

        self.famiport_order_payment.paid_at = datetime(2015, 5, 21, 13, 40, 1)
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521135001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[1].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.TicketingBeforeStartError.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, None)
        self.assertEqual(result.playGuideId, None)
        self.assertEqual(result.playGuideName, None)
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, None)  # reserve number
        self.assertEqual(result.ticketingStart, None)
        self.assertEqual(result.ticketingEnd, None)
        self.assertEqual(result.totalAmount, None)
        self.assertEqual(result.ticketPayment, None)
        self.assertEqual(result.systemFee, None)
        self.assertEqual(result.ticketingFee, None)
        self.assertEqual(result.ticketCountTotal, None)
        self.assertEqual(result.ticketCount, None)
        self.assertEqual(result.kogyoName, None)
        self.assertEqual(result.koenDate, None)

    def test_payment_only(self):
        u"""前払のみ"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340126',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment_only.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)

        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.PrepaymentOnly.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340126')
        self.assertEqual(result.orderId, u'000011112227')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340126')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')
        self.assertEqual(len(result.tickets), 0)

    def test_payment_only_payment_sheet_text(self):
        u"""前払のみで払込票にテキスト"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340126',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment_only.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_payment_only.payment_sheet_text = u'text'

        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.PrepaymentOnly.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340126')
        self.assertEqual(result.orderId, u'000011112227')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340126')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')
        self.assertEqual(len(result.tickets), 1)
        self.assertEqual(result.tickets[0].barCodeNo, None)
        self.assertEqual(result.tickets[0].ticketClass, None)
        self.assertEqual(result.tickets[0].templateCode, None)
        self.assertEqual(result.tickets[0].ticketData, u'text')

    def test_cash_on_delivery_reissuing(self):
        """代引"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100002',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 9, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result1 = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result1.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result1.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result1.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result1.storeCode, u'000009')
        self.assertEqual(result1.sequenceNo, u'15052100002')
        self.assertEqual(result1.barCodeNo, u'01234012340123')
        self.assertEqual(result1.orderId, u'000011112223')
        self.assertEqual(result1.playGuideId, u'012340123401234012340123')
        self.assertEqual(result1.playGuideName, u'チケットスター')
        self.assertEqual(result1.orderTicketNo, u'01234012340123')
        self.assertEqual(result1.exchangeTicketNo, u'')
        self.assertEqual(result1.ticketingStart, u'')
        self.assertEqual(result1.ticketingEnd, u'')
        self.assertEqual(result1.totalAmount, u'00010540')
        self.assertEqual(result1.ticketPayment, u'00010000')
        self.assertEqual(result1.systemFee, u'00000324')
        self.assertEqual(result1.ticketingFee, u'00000216')
        self.assertEqual(result1.ticketCountTotal, u'2')
        self.assertEqual(result1.ticketCount, u'2')
        self.assertEqual(result1.kogyoName, u'7/1公演')
        self.assertEqual(result1.koenDate, u'201507011900')

        self.assertIsNotNone(self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at)

        result2 = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result2.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result2.replyClass, '')
        self.assertEqual(result2.replyCode, ReplyCodeEnum.TicketAlreadyIssuedError.value)

        self.famiport_order_cash_on_delivery.make_reissueable(
            datetime(2015, 5, 21, 0, 10, 0),
            self.request
            )

        result3 = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result3.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result3.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result3.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result3.storeCode, u'000009')
        self.assertEqual(result3.sequenceNo, u'15052100002')
        self.assertEqual(result3.barCodeNo, u'01234012340123')
        self.assertEqual(result3.orderId, u'000011112223')
        self.assertEqual(result3.playGuideId, u'012340123401234012340123')
        self.assertEqual(result3.playGuideName, u'チケットスター')
        self.assertEqual(result3.orderTicketNo, u'01234012340123')
        self.assertEqual(result3.exchangeTicketNo, u'')
        self.assertEqual(result3.ticketingStart, u'')
        self.assertEqual(result3.ticketingEnd, u'')
        self.assertEqual(result3.totalAmount, u'00010540')
        self.assertEqual(result3.ticketPayment, u'00010000')
        self.assertEqual(result3.systemFee, u'00000324')
        self.assertEqual(result3.ticketingFee, u'00000216')
        self.assertEqual(result3.ticketCountTotal, u'2')
        self.assertEqual(result3.ticketCount, u'2')
        self.assertEqual(result3.kogyoName, u'7/1公演')
        self.assertEqual(result3.koenDate, u'201507011900')

    def test_cash_on_delivery_reissuing2(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=self.famiport_order_cash_on_delivery.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)
        barcode_no = result.barCodeNo

        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100002',
            playGuideId=u'012340123401234012340123',
            barCodeNo=barcode_no,
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100002')
        self.assertEqual(result.barCodeNo, barcode_no)
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=barcode_no,
            orderId=u'000011112223',
            totalAmount=u'00010540'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, barcode_no)
        self.assertEqual(result.orderId, u'000011112223')

        self.famiport_order_cash_on_delivery.make_reissueable(self.now, self.request)

        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=self.famiport_order_cash_on_delivery.famiport_receipts[0].reserve_number,
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)
        barcode_no = result.barCodeNo

        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100005',
            playGuideId=u'012340123401234012340123',
            barCodeNo=barcode_no,
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100005')
        self.assertEqual(result.barCodeNo, barcode_no)
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_twice(self):
        """2度目以降の入金発券要求で発券済みエラーを返す"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100002',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100002')
        self.assertEqual(result.barCodeNo, u'01234012340123')
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340123')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.TicketAlreadyIssuedError.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340123')
        self.assertEqual(result.orderId, None)
        self.assertEqual(result.playGuideId, None)
        self.assertEqual(result.playGuideName, None)
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, None)
        self.assertEqual(result.ticketingStart, None)
        self.assertEqual(result.ticketingEnd, None)
        self.assertEqual(result.totalAmount, None)
        self.assertEqual(result.ticketPayment, None)
        self.assertEqual(result.systemFee, None)
        self.assertEqual(result.ticketingFee, None)
        self.assertEqual(result.ticketCountTotal, None)
        self.assertEqual(result.ticketCount, None)
        self.assertEqual(result.kogyoName, None)
        self.assertEqual(result.koenDate, None)

    def test_payment_and_ticketing_and_reissuing(self):
        u"""前払後日の支払と発券を両方"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Prepayment.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112224')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340124')
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            orderId=u'000011112224',
            totalAmount=u'00010540'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112224')

        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522211234',
            sequenceNo=u'15052100005',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[1].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Paid.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100005')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112225')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')  # reserve number
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00000000')
        self.assertEqual(result.ticketPayment, u'00000000')
        self.assertEqual(result.systemFee, u'00000000')
        self.assertEqual(result.ticketingFee, u'00000000')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100006',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            orderId=u'000011112225',
            totalAmount=u'00010540'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100006')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112225')

        # 再発券許可
        self.famiport_order_payment.make_reissueable(self.now, self.request)

        # 支払いはやり直せないことを確認
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100007',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.AlreadyPaidError.value)

        # 発券はやり直せることを確認
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100008',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[1].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Paid.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100008')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112225')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')  # reserve number
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00000000')
        self.assertEqual(result.ticketPayment, u'00000000')
        self.assertEqual(result.systemFee, u'00000000')
        self.assertEqual(result.ticketingFee, u'00000000')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_payment_and_ticketing_and_reissuing2(self):
        u"""前払後日の支払と発券を両方 (再発券時に発券期限切れ)"""
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Prepayment.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112224')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340124')
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            orderId=u'000011112224',
            totalAmount=u'00010540'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112224')

        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522211234',
            sequenceNo=u'15052100005',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[1].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Paid.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100005')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112225')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')  # reserve number
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00000000')
        self.assertEqual(result.ticketPayment, u'00000000')
        self.assertEqual(result.systemFee, u'00000000')
        self.assertEqual(result.ticketingFee, u'00000000')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100006',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            orderId=u'000011112225',
            totalAmount=u'00010540'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100006')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112225')

        # 再発券許可
        self.famiport_order_payment.make_reissueable(self.now, self.request)

        # 発券は発券期限後もやり直せることを確認
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100008',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self.famiport_order_payment.famiport_receipts[1].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_payment.ticketing_end_at = self.famiport_order_payment.ticketing_start_at = datetime(2015, 5, 21, 0, 0, 0)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Paid.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100008')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112225')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, u'4321043210434')  # reserve number
        self.assertEqual(result.ticketingStart, u'20150521000000')
        self.assertEqual(result.ticketingEnd, u'20150521000000')
        self.assertEqual(result.totalAmount, u'00000000')
        self.assertEqual(result.ticketPayment, u'00000000')
        self.assertEqual(result.systemFee, u'00000000')
        self.assertEqual(result.ticketingFee, u'00000000')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')


class FamiPortPaymentTicketingCompletionBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 発券完了
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def test_cash_on_delivery(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        # self.famiport_order_cash_on_delivery
        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            orderId=u'000011112223',
            totalAmount=u'00010540'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340123')
        self.assertEqual(result.orderId, u'000011112223')

    def test_not_payment_request_received(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        # self.famiport_order_cash_on_delivery
        f_request = FamiPortPaymentTicketingCompletionRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            orderId=u'000011112223',
            totalAmount=u'00010540'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = None
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'99')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340123')
        self.assertEqual(result.orderId, u'000011112223')

class FamiPortPaymentTicketingCancelResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # キャンセル (VOID)
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def test_cash_on_delivery(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        # self.famiport_order_cash_on_delivery
        f_request = FamiPortPaymentTicketingCancelRequest(
            storeCode=u'00009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            orderId=u'000011112223',
            cancelCode=u'01'
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now, self.request)
        self.assertEqual(result.resultCode, '00')
        self.assertEqual(result.replyCode, u'00')
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340123')
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(self.famiport_order_cash_on_delivery.famiport_receipts[0].void_at, self.now)
        self.assertEqual(self.famiport_order_cash_on_delivery.famiport_receipts[0].void_reason, 1)



class FamiPortRefundEntryResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 払戻
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def test_it(self):
        from ..models import FamiPortRefund, FamiPortRefundEntry, FamiPortRefundType
        from .models import (
            FamiPortRefundEntryResponseTextTypeEnum,
            FamiPortRefundEntryResponseEntryTypeEnum,
            FamiPortRefundEntryResponseErrorCodeEnum,
            FamiPortRefundEntryRequest,
            FamiPortRefundEntryResponse,
            )
        # self.famiport_order_cash_on_delivery
        f_request = FamiPortRefundEntryRequest(
            businessFlg=u'3',
            textTyp=u'%d' % FamiPortRefundEntryResponseTextTypeEnum.Inquiry.value,
            entryTyp=u'%d' % FamiPortRefundEntryResponseEntryTypeEnum.Register.value,
            shopNo=self.famiport_order_cash_on_delivery.famiport_receipts[0].shop_code,
            registerNo=u'01',
            timeStamp=u'20150601',
            barCode1=self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].completed_at = \
            self.famiport_order_cash_on_delivery.issued_at = \
            self.famiport_order_cash_on_delivery.paid_at = \
                datetime(2015, 5, 21, 13, 50, 0)
        refund = FamiPortRefund(
            type=FamiPortRefundType.Type1.value,
            client_code=self.famiport_order_cash_on_delivery.client_code,
            send_back_due_at=datetime(2015, 8, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 6, 30, 23, 59, 59)
            )
        refund_entry = FamiPortRefundEntry(
            famiport_ticket=self.famiport_order_cash_on_delivery.famiport_tickets[0],
            serial=0,
            shop_code=self.famiport_order_cash_on_delivery.famiport_receipts[0].shop_code,
            ticket_payment=self.famiport_order_cash_on_delivery.famiport_tickets[0].price,
            ticketing_fee=0,
            other_fees=0,
            famiport_refund=refund
            )
        self.session.add(refund_entry)
        self.session.flush()
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, datetime(2015, 6, 1, 0, 0, 0), self.request)
        self.assertEqual(result.businessFlg, u'3')
        self.assertEqual(result.textTyp, u'1')
        self.assertEqual(result.entryTyp, u'1')
        self.assertEqual(result.shopNo, u'0000009')
        self.assertEqual(result.errorCode, u'0')
        self.assertEqual(result.barCode1, self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number)
        self.assertEqual(result.resultCode1, u'0')
        self.assertEqual(result.mainTitle1, u'7/1公演')
        self.assertEqual(result.perfDay1, u'20150701')
        self.assertEqual(result.repayment1, u'5000')
        self.assertEqual(result.refundStart1, u'20150601')
        self.assertEqual(result.refundEnd1, u'20150630')
        self.assertEqual(result.ticketTyp1, u'1')
        self.assertEqual(result.charge1, u'0')
        self.assertEqual(result.barCode2, None)
        self.assertEqual(result.resultCode2, None)
        self.assertEqual(result.mainTitle2, None)
        self.assertEqual(result.perfDay2, None)
        self.assertEqual(result.repayment2, None)
        self.assertEqual(result.refundStart2, None)
        self.assertEqual(result.refundEnd2, None)
        self.assertEqual(result.ticketTyp2, None)
        self.assertEqual(result.charge2, None)
        self.assertEqual(result.barCode3, None)
        self.assertEqual(result.resultCode3, None)
        self.assertEqual(result.mainTitle3, None)
        self.assertEqual(result.perfDay3, None)
        self.assertEqual(result.repayment3, None)
        self.assertEqual(result.refundStart3, None)
        self.assertEqual(result.refundEnd3, None)
        self.assertEqual(result.ticketTyp3, None)
        self.assertEqual(result.charge3, None)
        self.assertEqual(result.barCode4, None)
        self.assertEqual(result.resultCode4, None)
        self.assertEqual(result.mainTitle4, None)
        self.assertEqual(result.perfDay4, None)
        self.assertEqual(result.repayment4, None)
        self.assertEqual(result.refundStart4, None)
        self.assertEqual(result.refundEnd4, None)
        self.assertEqual(result.ticketTyp4, None)
        self.assertEqual(result.charge4, None)

    def test_out_of_term(self):
        from ..models import FamiPortRefund, FamiPortRefundEntry, FamiPortRefundType
        from .models import (
            FamiPortRefundEntryResponseTextTypeEnum,
            FamiPortRefundEntryResponseEntryTypeEnum,
            FamiPortRefundEntryResponseErrorCodeEnum,
            FamiPortRefundEntryRequest,
            FamiPortRefundEntryResponse,
            )
        # self.famiport_order_cash_on_delivery
        f_request = FamiPortRefundEntryRequest(
            businessFlg=u'3',
            textTyp=u'%d' % FamiPortRefundEntryResponseTextTypeEnum.Inquiry.value,
            entryTyp=u'%d' % FamiPortRefundEntryResponseEntryTypeEnum.Register.value,
            shopNo=self.famiport_order_cash_on_delivery.famiport_receipts[0].shop_code,
            registerNo=u'01',
            timeStamp=u'20150601',
            barCode1=self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].completed_at = \
            self.famiport_order_cash_on_delivery.issued_at = \
            self.famiport_order_cash_on_delivery.paid_at = \
                datetime(2015, 5, 21, 13, 50, 0)
        refund = FamiPortRefund(
            type=FamiPortRefundType.Type1.value,
            client_code=self.famiport_order_cash_on_delivery.client_code,
            send_back_due_at=datetime(2015, 8, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 6, 30, 23, 59, 59)
            )
        refund_entry = FamiPortRefundEntry(
            famiport_ticket=self.famiport_order_cash_on_delivery.famiport_tickets[0],
            serial=0,
            shop_code=self.famiport_order_cash_on_delivery.famiport_receipts[0].shop_code,
            ticket_payment=self.famiport_order_cash_on_delivery.famiport_tickets[0].price,
            ticketing_fee=0,
            other_fees=0,
            famiport_refund=refund
            )
        self.session.add(refund_entry)
        self.session.flush()
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, datetime(2015, 7, 1, 0, 0, 0), self.request)
        self.assertEqual(result.businessFlg, u'3')
        self.assertEqual(result.textTyp, u'1')
        self.assertEqual(result.entryTyp, u'1')
        self.assertEqual(result.shopNo, u'0000009')
        self.assertEqual(result.errorCode, u'0')
        self.assertEqual(result.barCode1, self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number)
        self.assertEqual(result.resultCode1, u'3')
        self.assertEqual(result.mainTitle1, u'7/1公演')
        self.assertEqual(result.perfDay1, u'20150701')
        self.assertEqual(result.repayment1, u'5000')
        self.assertEqual(result.refundStart1, u'20150601')
        self.assertEqual(result.refundEnd1, u'20150630')
        self.assertEqual(result.ticketTyp1, u'1')
        self.assertEqual(result.charge1, u'0')
        self.assertEqual(result.barCode2, None)
        self.assertEqual(result.resultCode2, None)
        self.assertEqual(result.mainTitle2, None)
        self.assertEqual(result.perfDay2, None)
        self.assertEqual(result.repayment2, None)
        self.assertEqual(result.refundStart2, None)
        self.assertEqual(result.refundEnd2, None)
        self.assertEqual(result.ticketTyp2, None)
        self.assertEqual(result.charge2, None)
        self.assertEqual(result.barCode3, None)
        self.assertEqual(result.resultCode3, None)
        self.assertEqual(result.mainTitle3, None)
        self.assertEqual(result.perfDay3, None)
        self.assertEqual(result.repayment3, None)
        self.assertEqual(result.refundStart3, None)
        self.assertEqual(result.refundEnd3, None)
        self.assertEqual(result.ticketTyp3, None)
        self.assertEqual(result.charge3, None)
        self.assertEqual(result.barCode4, None)
        self.assertEqual(result.resultCode4, None)
        self.assertEqual(result.mainTitle4, None)
        self.assertEqual(result.perfDay4, None)
        self.assertEqual(result.repayment4, None)
        self.assertEqual(result.refundStart4, None)
        self.assertEqual(result.refundEnd4, None)
        self.assertEqual(result.ticketTyp4, None)
        self.assertEqual(result.charge4, None)

    def test_different_shop_out_of_term(self):
        from ..models import FamiPortRefund, FamiPortRefundEntry, FamiPortRefundType
        from .models import (
            FamiPortRefundEntryResponseTextTypeEnum,
            FamiPortRefundEntryResponseEntryTypeEnum,
            FamiPortRefundEntryResponseErrorCodeEnum,
            FamiPortRefundEntryRequest,
            FamiPortRefundEntryResponse,
            )
        # self.famiport_order_cash_on_delivery
        f_request = FamiPortRefundEntryRequest(
            businessFlg=u'3',
            textTyp=u'%d' % FamiPortRefundEntryResponseTextTypeEnum.Inquiry.value,
            entryTyp=u'%d' % FamiPortRefundEntryResponseEntryTypeEnum.Register.value,
            shopNo=u'0000010',
            registerNo=u'01',
            timeStamp=u'20150601',
            barCode1=self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].completed_at = \
            self.famiport_order_cash_on_delivery.issued_at = \
            self.famiport_order_cash_on_delivery.paid_at = \
                datetime(2015, 5, 21, 13, 50, 0)
        refund = FamiPortRefund(
            type=FamiPortRefundType.Type1.value,
            client_code=self.famiport_order_cash_on_delivery.client_code,
            send_back_due_at=datetime(2015, 8, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 6, 30, 23, 59, 59)
            )
        refund_entry = FamiPortRefundEntry(
            famiport_ticket=self.famiport_order_cash_on_delivery.famiport_tickets[0],
            serial=0,
            shop_code=self.famiport_order_cash_on_delivery.famiport_receipts[0].shop_code,
            ticket_payment=self.famiport_order_cash_on_delivery.famiport_tickets[0].price,
            ticketing_fee=0,
            other_fees=0,
            famiport_refund=refund
            )
        self.session.add(refund_entry)
        self.session.flush()
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, datetime(2015, 7, 1, 0, 0, 0), self.request)
        self.assertEqual(result.businessFlg, u'3')
        self.assertEqual(result.textTyp, u'1')
        self.assertEqual(result.entryTyp, u'1')
        self.assertEqual(result.shopNo, u'0000010')
        self.assertEqual(result.errorCode, u'0')
        self.assertEqual(result.barCode1, self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number)
        self.assertEqual(result.resultCode1, u'3')
        self.assertEqual(result.mainTitle1, u'7/1公演')
        self.assertEqual(result.perfDay1, u'20150701')
        self.assertEqual(result.repayment1, u'5000')
        self.assertEqual(result.refundStart1, u'20150601')
        self.assertEqual(result.refundEnd1, u'20150630')
        self.assertEqual(result.ticketTyp1, u'1')
        self.assertEqual(result.charge1, u'0')
        self.assertEqual(result.barCode2, None)
        self.assertEqual(result.resultCode2, None)
        self.assertEqual(result.mainTitle2, None)
        self.assertEqual(result.perfDay2, None)
        self.assertEqual(result.repayment2, None)
        self.assertEqual(result.refundStart2, None)
        self.assertEqual(result.refundEnd2, None)
        self.assertEqual(result.ticketTyp2, None)
        self.assertEqual(result.charge2, None)
        self.assertEqual(result.barCode3, None)
        self.assertEqual(result.resultCode3, None)
        self.assertEqual(result.mainTitle3, None)
        self.assertEqual(result.perfDay3, None)
        self.assertEqual(result.repayment3, None)
        self.assertEqual(result.refundStart3, None)
        self.assertEqual(result.refundEnd3, None)
        self.assertEqual(result.ticketTyp3, None)
        self.assertEqual(result.charge3, None)
        self.assertEqual(result.barCode4, None)
        self.assertEqual(result.resultCode4, None)
        self.assertEqual(result.mainTitle4, None)
        self.assertEqual(result.perfDay4, None)
        self.assertEqual(result.repayment4, None)
        self.assertEqual(result.refundStart4, None)
        self.assertEqual(result.refundEnd4, None)
        self.assertEqual(result.ticketTyp4, None)
        self.assertEqual(result.charge4, None)

    def test_different_shop(self):
        from ..models import FamiPortRefund, FamiPortRefundEntry, FamiPortRefundType
        from .models import (
            FamiPortRefundEntryResponseTextTypeEnum,
            FamiPortRefundEntryResponseEntryTypeEnum,
            FamiPortRefundEntryResponseErrorCodeEnum,
            FamiPortRefundEntryRequest,
            FamiPortRefundEntryResponse,
            )
        # self.famiport_order_cash_on_delivery
        f_request = FamiPortRefundEntryRequest(
            businessFlg=u'3',
            textTyp=u'%d' % FamiPortRefundEntryResponseTextTypeEnum.Inquiry.value,
            entryTyp=u'%d' % FamiPortRefundEntryResponseEntryTypeEnum.Register.value,
            shopNo=u'0000010',
            registerNo=u'01',
            timeStamp=u'20150601',
            barCode1=self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number
            )
        self.famiport_order_cash_on_delivery.famiport_receipts[0].inquired_at = datetime(2015, 5, 21, 13, 39, 12)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].payment_request_received_at = datetime(2015, 5, 21, 13, 39, 13)
        self.famiport_order_cash_on_delivery.famiport_receipts[0].completed_at = \
            self.famiport_order_cash_on_delivery.issued_at = \
            self.famiport_order_cash_on_delivery.paid_at = \
                datetime(2015, 5, 21, 13, 50, 0)
        refund = FamiPortRefund(
            type=FamiPortRefundType.Type1.value,
            client_code=self.famiport_order_cash_on_delivery.client_code,
            send_back_due_at=datetime(2015, 8, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 6, 30, 23, 59, 59)
            )
        refund_entry = FamiPortRefundEntry(
            famiport_ticket=self.famiport_order_cash_on_delivery.famiport_tickets[0],
            serial=0,
            shop_code=self.famiport_order_cash_on_delivery.famiport_receipts[0].shop_code,
            ticket_payment=self.famiport_order_cash_on_delivery.famiport_tickets[0].price,
            ticketing_fee=0,
            other_fees=0,
            famiport_refund=refund
            )
        self.session.add(refund_entry)
        self.session.flush()
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, datetime(2015, 6, 1, 0, 0, 0), self.request)
        self.assertEqual(result.businessFlg, u'3')
        self.assertEqual(result.textTyp, u'1')
        self.assertEqual(result.entryTyp, u'1')
        self.assertEqual(result.shopNo, u'0000010')
        self.assertEqual(result.errorCode, u'0')
        self.assertEqual(result.barCode1, self.famiport_order_cash_on_delivery.famiport_tickets[0].barcode_number)
        self.assertEqual(result.resultCode1, u'7')
        self.assertEqual(result.mainTitle1, u'7/1公演')
        self.assertEqual(result.perfDay1, u'20150701')
        self.assertEqual(result.repayment1, u'5000')
        self.assertEqual(result.refundStart1, u'20150601')
        self.assertEqual(result.refundEnd1, u'20150630')
        self.assertEqual(result.ticketTyp1, u'1')
        self.assertEqual(result.charge1, u'0')
        self.assertEqual(result.barCode2, None)
        self.assertEqual(result.resultCode2, None)
        self.assertEqual(result.mainTitle2, None)
        self.assertEqual(result.perfDay2, None)
        self.assertEqual(result.repayment2, None)
        self.assertEqual(result.refundStart2, None)
        self.assertEqual(result.refundEnd2, None)
        self.assertEqual(result.ticketTyp2, None)
        self.assertEqual(result.charge2, None)
        self.assertEqual(result.barCode3, None)
        self.assertEqual(result.resultCode3, None)
        self.assertEqual(result.mainTitle3, None)
        self.assertEqual(result.perfDay3, None)
        self.assertEqual(result.repayment3, None)
        self.assertEqual(result.refundStart3, None)
        self.assertEqual(result.refundEnd3, None)
        self.assertEqual(result.ticketTyp3, None)
        self.assertEqual(result.charge3, None)
        self.assertEqual(result.barCode4, None)
        self.assertEqual(result.resultCode4, None)
        self.assertEqual(result.mainTitle4, None)
        self.assertEqual(result.perfDay4, None)
        self.assertEqual(result.repayment4, None)
        self.assertEqual(result.refundStart4, None)
        self.assertEqual(result.refundEnd4, None)
        self.assertEqual(result.ticketTyp4, None)
        self.assertEqual(result.charge4, None)


class TextFamiPortResponseGeneratorTest(unittest.TestCase):
    def test_it(self):
        from .builders import TextFamiPortResponseGenerator
        response = mock.Mock(
            _serialized_attrs=[
                ('a', 'A'),
                'b',
                'c',
                ],
            encrypt_key=None,
            encrypted_fields=[],
            a=u'123',
            b=u'456',
            c=None
            )
        x = TextFamiPortResponseGenerator(response)
        self.assertEqual(x.serialize(response), u'A=123\r\nb=456\r\nc=')


