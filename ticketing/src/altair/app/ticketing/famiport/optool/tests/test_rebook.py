# -*- coding:utf-8 -*-

from unittest import TestCase
from pyramid.testing import DummyRequest, setUp, tearDown
from altair.app.ticketing.famiport.testing import _setup_db, _teardown_db
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.famiport.models import FamiPortReceipt, FamiPortReceiptType
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
        canceled_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10)
                )

        canceled_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10)
                )

        canceled_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10)
                )

        canceled_payment_receipt_errors = ValidateUtils.validate_rebook_cond(canceled_payment_receipt, datetime.now())
        canceled_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(canceled_ticketing_receipt, datetime.now())
        canceled_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(canceled_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(canceled_payment_receipt_errors, msg='Canceled payment receipt should not be rebookable.')
        self.assertTrue(canceled_ticketing_receipt_errors, msg='Canceled ticketing receipt should not be rebookable.')
        self.assertTrue(canceled_cash_on_delivery_receipt_errors, msg='Canceled cache on delivery receipt should not be rebookable.')

    def test_voided_receipt(self):
        voided_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    void_at=datetime.now() - timedelta(minutes=10)
                )

        voided_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    void_at=datetime.now() - timedelta(minutes=10)
                )

        voided_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    void_at=datetime.now() - timedelta(minutes=10)
                )

        voided_payment_receipt_errors = ValidateUtils.validate_rebook_cond(voided_payment_receipt, datetime.now())
        voided_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(voided_ticketing_receipt, datetime.now())
        voided_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(voided_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(voided_payment_receipt_errors, msg='Canceled payment receipt should not be rebookable.')
        self.assertTrue(voided_ticketing_receipt_errors, msg='Canceled ticketing receipt should not be rebookable.')
        self.assertTrue(voided_cash_on_delivery_receipt_errors, msg='Canceled cache on delivery receipt should not be rebookable.')

    def test_unpaid_receipt(self):
        unpaid_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430'
                )

        unissued_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                )

        unpaid_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                )

        unpaid_payment_receipt_errors = ValidateUtils.validate_rebook_cond(unpaid_payment_receipt, datetime.now())
        unissued_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(unissued_ticketing_receipt, datetime.now())
        unpaid_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(unpaid_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(unpaid_payment_receipt_errors, msg='Unpaid payment receipt should not be rebookable.')
        self.assertTrue(unissued_ticketing_receipt_errors, msg='Unissued ticketing receipt should not be rebookable.')
        self.assertTrue(unpaid_cash_on_delivery_receipt_errors, msg='Unpaid cache on delivery receipt should not be rebookable.')

    def test_incomplete_receipt(self):
        incomplete_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        incomplete_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        incomplete_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        incomplete_payment_receipt_errors = ValidateUtils.validate_rebook_cond(incomplete_payment_receipt, datetime.now())
        incomplete_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(incomplete_ticketing_receipt, datetime.now())
        incomplete_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(incomplete_cash_on_delivery_receipt, datetime.now())
        # TODO Check if incomplete receipts should be rebookable. If so, make these assertFalse.
        # self.assertTrue(incomplete_payment_receipt_errors, msg='Incomplete payment receipt should not be rebookable.')
        # self.assertTrue(incomplete_ticketing_receipt_errors, msg='Incomplete ticketing receipt should not be rebookable.')
        # self.assertTrue(incomplete_cash_on_delivery_receipt_errors, msg='Incomplete cash on delivery receipt should not be rebookable.')

    def test_complete_receipt(self):
        complete_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=2),
                    completed_at=datetime.now() - timedelta(minutes=1)
                )

        complete_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=2),
                    completed_at=datetime.now() - timedelta(minutes=1)
                )

        complete_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=2),
                    completed_at=datetime.now() -  timedelta(minutes=1)
                )

        complete_payment_receipt_errors = ValidateUtils.validate_rebook_cond(complete_payment_receipt, datetime.now())
        complete_ticketing_receipt_errors = ValidateUtils.validate_rebook_cond(complete_ticketing_receipt, datetime.now())
        complete_cash_on_delivery_receipt_errors = ValidateUtils.validate_rebook_cond(complete_cash_on_delivery_receipt, datetime.now())

        self.assertFalse(complete_payment_receipt_errors, msg='Complete payment receipt should be rebookable.')
        self.assertFalse(complete_ticketing_receipt_errors, msg='Complete ticketing receipt should be rebookable.')
        self.assertFalse(complete_cash_on_delivery_receipt_errors, msg='Complete cash on delivery receipt should be rebookable.')