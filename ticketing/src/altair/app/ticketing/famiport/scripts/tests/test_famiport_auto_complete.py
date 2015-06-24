# -*- coding: utf-8 -*-
import six
from unittest import (
    skip,
    TestCase,
    )
from datetime import (
    datetime,
    timedelta,
    )


if six.PY3:
    from unittest import mock
else:
    import mock  # noqa


class GetNowTest(TestCase):
    def test_it(self):
        from ..famiport_auto_complete import _get_now as target
        _now = target()
        self.assertTrue(isinstance(_now, datetime))


class FamiPortOrderAutoCompleteNotificationContextTest(TestCase):
    def _get_klass(self):
        from ..famiport_auto_complete import FamiPortOrderAutoCompleteNotificationContext as klass
        return klass

    def _create(self, *args, **kwds):
        klass = self._get_klass()
        return klass(*args, **kwds)

    def setUp(self):
        from ...models import (
            FamiPortOrder,
            FamiPortEvent,
            FamiPortClient,
            FamiPortReceipt,
            FamiPortPlayguide,
            FamiPortPerformance,
            FamiPortSalesSegment,
            )
        self.famiport_playguide = mock.Mock(
            discrimination_code='DISCRIMINATION_CODE',
            spec=FamiPortPlayguide,
            )
        self.famiport_client = mock.Mock(
            playguide=self.famiport_playguide,
            spec=FamiPortClient,
            )
        self.famiport_event = mock.Mock(
            code_1='CODE_1',
            code_2='CODE_2',
            name_1='NAME_1',
            name_2='NAME_2',
            client=self.famiport_client,
            spec=FamiPortEvent,
            )
        self.famiport_performance = mock.Mock(
            name='FAMIPORT_PERORMANCE_NAME',
            code='FAMIPORT_PERORMANCE_CODE',
            famiport_event=self.famiport_event,
            spec=FamiPortPerformance,
            )
        self.famiport_sales_segment = mock.Mock(
            famiport_performance=self.famiport_performance,
            spec=FamiPortSalesSegment,
            )
        self.famiport_order = mock.Mock(
            total_amount=100,
            famiport_client=self.famiport_client,
            famiport_sales_segment=self.famiport_sales_segment,
            spec=FamiPortOrder,
            )
        self.receipt = mock.Mock(
            barcode_no='BARCODE_NO',
            reserve_number='RESERVE_NUMBER',
            famiport_order_identifier='FAMIPORT_ORDER_IDENTIFIER',
            shop_code='SHOP_CODE',
            famiport_order=self.famiport_order,
            spec=FamiPortReceipt,
            )
        self.now_ = datetime.now()

        args = []
        kwds = {
            'request': mock.Mock(),
            'session': mock.Mock(),
            'receipt': self.receipt,
            'time_point': self.now_,
            }
        self.obj = self._create(*args, **kwds)

    def test_time_point(self):
        self.assertEqual(self.obj.time_point, self.now_.strftime('%Y/%m/%d %H:%M:%S'))

    def test_reserve_number(self):
        self.assertEqual(self.obj.reserve_number, self.receipt.reserve_number)

    def test_barcode_no(self):
        self.assertEqual(self.obj.barcode_no, self.receipt.barcode_no)

    def test_order_identifier(self):
        self.assertEqual(self.obj.order_identifier, self.receipt.famiport_order_identifier)

    def test_total_amount(self):
        self.assertEqual(self.obj.total_amount, self.receipt.famiport_order.total_amount)

    def test_shop_code(self):
        self.assertEqual(self.obj.shop_code, self.receipt.shop_code)

    def test_event_code_1(self):
        self.assertEqual(self.obj.event_code_1, self.famiport_event.code_1)

    def test_event_code_2(self):
        self.assertEqual(self.obj.event_code_2, self.famiport_event.code_2)

    def test_event_name_1(self):
        self.assertEqual(self.obj.event_name_1, self.famiport_event.name_1)

    def test_event_name_2(self):
        self.assertEqual(self.obj.event_name_2, self.famiport_event.name_2)

    def test_performance_name(self):
        self.assertEqual(self.obj.performance_name, self.famiport_performance.name)

    def test_performance_code(self):
        self.assertEqual(self.obj.performance_code, self.famiport_performance.code)

    def test_playguide_code(self):
        self.assertEqual(self.obj.playguide_code, self.famiport_playguide.discrimination_code)


class FamiPortOrderAutoCompleteNotificationContext_classifier_Test(TestCase):
    def _get_target_class(self):
        from ..famiport_auto_complete import FamiPortOrderAutoCompleteNotificationContext as klass
        return klass

    def _get_type(self):
        from ...models import FamiPortReceiptType as klass
        return klass

    def _create(self, type_):
        from ...models import FamiPortReceipt
        receipt = mock.Mock(
            type=type_,
            spec=FamiPortReceipt,
            )
        args = []
        kwds = {
            'request': mock.Mock(),
            'session': mock.Mock(),
            'receipt': receipt,
            'time_point': mock.Mock(),
        }
        klass = self._get_target_class()
        return klass(*args, **kwds)

    def test_payment(self):
        type_class = self._get_type()
        obj = self._create(type_class.Payment.value)
        self.assertEqual(obj.classifier, u'前払')

    def test_ticketing(self):
        type_class = self._get_type()
        obj = self._create(type_class.Ticketing.value)
        self.assertEqual(obj.classifier, u'代済発券または前払い後日発券')

    def test_cache_on_delivery(self):
        type_class = self._get_type()
        obj = self._create(type_class.CashOnDelivery.value)
        self.assertEqual(obj.classifier, u'代引')


class FamiPortOrderAutoCopleterTest(TestCase):
    def _get_target_class(self):
        from ..famiport_auto_complete import FamiPortOrderAutoCompleter as klass
        return klass

    def _get_target(self, *args, **kwds):
        klass = self._get_target_class()
        return klass(*args, **kwds)

    @skip('')
    @mock.patch('altair.app.ticketing.famiport.scripts.famiport_auto_complete._get_now')
    def test_timepoint(self, _get_now):
        now = datetime.now()
        nine_minutes_ago = now - timedelta(minutes=90)
        _get_now.return_value = now
        session = mock.Mock()
        target = self._get_target(session)
        self.assertEqual(target.time_point, nine_minutes_ago)

    @skip('')
    @mock.patch('altair.app.ticketing.famiport.scripts.famiport_auto_complete.FamiPortOrderAutoCompleter._fetch_target_famiport_receipts')
    @mock.patch('altair.app.ticketing.famiport.scripts.famiport_auto_complete.FamiPortOrderAutoCompleter._do_complete')
    def test_complete(self, _do_complete, _fetch_target_famiport_receipts):
        from ..famiport_auto_complete import AutoCompleterStatus
        session = mock.Mock()
        famiport_receipts = [mock.Mock() for ii in range(10)]
        _fetch_target_famiport_receipts.return_value = famiport_receipts
        target = self._get_target(session)
        res = target.complete()
        self.assertEqual(res, AutoCompleterStatus.success.value)

        do_complete_call_args_list = [call_args[0][0] for call_args in _do_complete.call_args_list]
        session_call_args_list = [call_args[0][0] for call_args in session.add.call_args_list]
        self.assertEqual(do_complete_call_args_list, famiport_receipts)
        self.assertEqual(session_call_args_list, famiport_receipts)

    @skip('not yet implemented')
    def test_do_complete(self):
        pass

    @skip('not yet implemented')
    def test_fetch_target_famiport_orders(self):
        pass
