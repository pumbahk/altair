# -*- coding:utf-8 -*-

from unittest import TestCase
from pyramid.testing import DummyRequest, setUp, tearDown
from altair.app.ticketing.famiport.testing import _setup_db, _teardown_db
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.famiport.models import (
    FamiPortReceipt,
    FamiPortReceiptType,
    FamiPortOrder,
    FamiPortOrderType
)
from ..utils import ValidateUtils
from datetime import datetime, timedelta

class RebookTest(TestCase):
    # def setUp(self):
    #     self.request = DummyRequest()
    #     self.config = setUp(request=self.request)
    #     self.engine = _setup_db(
    #         self.config.registry,
    #         [
    #             'altair.app.ticketing.famiport.models',
    #             'altair.app.ticketing.famiport.optool.models',
    #             ]
    #         )
    #     self.session = get_global_db_session(self.config.registry, 'famiport')
    #
    # def tearDown(self):
    #     _teardown_db(self.config.registry)
    #     tearDown()

    def test_canceled_receipt(self):
        """キャンセル済みのFamiPortReceiptはvalidationに引っかかることを確認"""
        canceled_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.PaymentOnly.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        canceled_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.Ticketing.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        canceled_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.CashOnDelivery.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        canceled_payment_receipt_errors = ValidateUtils.validate_rebook_cond(canceled_payment_receipt, datetime.now())
        canceled_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(canceled_ticketing_receipt, datetime.now())
        canceled_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(canceled_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(canceled_payment_receipt_errors, msg='Canceled payment receipt should not be rebookable.')
        self.assertTrue(canceled_ticketing_receipt_errors, msg='Canceled ticketing receipt should not be rebookable.')
        self.assertTrue(canceled_cash_on_delivery_receipt_errors, msg='Canceled cache on delivery receipt should not be rebookable.')

    def test_payment_due_passed_receipt(self):
        """支払期限が過ぎている予約のFamiPortReceiptはvalidationに引っかかることを確認"""
        due_passed_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.PaymentOnly.value,
                        payment_due_at=datetime.now() - timedelta(minutes=10)
                    )
                )

        due_passed_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.Ticketing.value,
                        payment_due_at=datetime.now() - timedelta(minutes=10)
                    )
                )

        due_passed_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.CashOnDelivery.value,
                        payment_due_at=datetime.now() - timedelta(minutes=10)
                    )
                )

        due_passed_payment_receipt_errors = ValidateUtils.validate_rebook_cond(due_passed_payment_receipt, datetime.now())
        due_passed_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(due_passed_ticketing_receipt, datetime.now())
        due_passed_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(due_passed_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(due_passed_payment_receipt_errors, msg='Payment due passed payment_receipt should not be rebookable.')
        self.assertTrue(due_passed_cash_on_delivery_receipt_errors, msg='Payment due passed cache on delivery receipt should not be rebookable.')

        # 発券レシートは支払期限関係ないのでエラー出ない
        self.assertFalse(due_passed_ticketing_receipt_errors, msg='Payment due passed ticketing receipt should not be rebookable.')

    def test_unpaid_receipt(self):
        """入金発券要求していないFamiPortReceiptはvalidationに引っかかることを確認"""
        unpaid_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.PaymentOnly.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        unissued_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.Ticketing.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        unpaid_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.CashOnDelivery.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        unpaid_payment_receipt_errors = ValidateUtils.validate_rebook_cond(unpaid_payment_receipt, datetime.now())
        unissued_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(unissued_ticketing_receipt, datetime.now())
        unpaid_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(unpaid_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(unpaid_payment_receipt_errors, msg='Unpaid payment receipt should not be rebookable.')
        self.assertTrue(unissued_ticketing_receipt_errors, msg='Unissued ticketing receipt should not be rebookable.')
        self.assertTrue(unpaid_cash_on_delivery_receipt_errors, msg='Unpaid cache on delivery receipt should not be rebookable.')

    def test_incomplete_receipt(self):
        """入金発券確定待ちのFamiPortReceiptはvalidationに引っかからないことを確認"""
        incomplete_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.PaymentOnly.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        incomplete_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.Ticketing.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        incomplete_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.CashOnDelivery.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        incomplete_payment_receipt_errors = ValidateUtils.validate_rebook_cond(incomplete_payment_receipt, datetime.now())
        incomplete_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(incomplete_ticketing_receipt, datetime.now())
        incomplete_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(incomplete_cash_on_delivery_receipt, datetime.now())

        self.assertFalse(incomplete_payment_receipt_errors, msg='Incomplete payment receipt should be rebookable.')
        self.assertFalse(incomplete_ticketing_receipt_errors, msg='Incomplete ticketing receipt should be rebookable.')
        self.assertFalse(incomplete_cash_on_delivery_receipt_errors, msg='Incomplete cash on delivery receipt should be rebookable.')

    def test_complete_receipt(self):
        """入金発券完了済みのFamiPortReceiptはvalidationに引っかかることを確認"""
        complete_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=2),
                    completed_at=datetime.now() - timedelta(minutes=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.PaymentOnly.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        complete_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=2),
                    completed_at=datetime.now() - timedelta(minutes=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.Ticketing.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        complete_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=2),
                    completed_at=datetime.now() -  timedelta(minutes=1),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.CashOnDelivery.value,
                        payment_due_at=datetime.now() + timedelta(minutes=10)
                    )
                )

        complete_payment_receipt_errors = ValidateUtils.validate_rebook_cond(complete_payment_receipt, datetime.now())
        complete_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(complete_ticketing_receipt, datetime.now())
        complete_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(complete_cash_on_delivery_receipt, datetime.now())
        self.assertTrue(complete_payment_receipt_errors, msg='Complete payment receipt should not be rebookable.')
        self.assertTrue(complete_ticketing_receipt_errors, msg='Complete ticketing receipt should not be rebookable.')
        self.assertTrue(complete_cash_on_delivery_receipt_errors, msg='Complete cash on delivery receipt should not be rebookable.')
