# encoding: utf-8
from codecs import getencoder
from datetime import date
import decimal
import logging
from enum import Enum
from ..datainterchange.fileio import (
    Column,
    FixedRecordMarshaller,
    ZeroPaddedNumericString,
    Integer,
    ZeroPaddedInteger,
    WideWidthString,
    DateTime,
    Boolean,
    )
from ..models import FamiPortOrderType, FamiPortReceiptType
from collections import OrderedDict

logger = logging.getLogger(__name__)

LOCK_NAME = __name__  # batch用のロック名

class SalesReportEntryType(Enum):
    Payment                   = 1
    Ticketing                 = 2
    CashOnDelivery            = 3
    DirectSalesPayment        = 8
    DirectSalesCashOnDelivery = 9

sales_report_schema = [
    Column('unique_key', ZeroPaddedNumericString(length=10)),     # ユニークキー
    Column('type', Integer(length=1)),                            # 処理区分
    Column('management_number', ZeroPaddedNumericString(length=9)), # 管理番号
    Column('event_code', ZeroPaddedNumericString(length=6)),      # 興行コード
    Column('event_code_sub', ZeroPaddedNumericString(length=4)),  # 興行コード (サブ)
    Column('sales_segment_code', ZeroPaddedNumericString(length=3)),  # 受付情報コード
    Column('performance_code', ZeroPaddedNumericString(length=3)),# 公演コード
    Column('event_name', WideWidthString(length=60, conversion=True)),             # 興行名称
    Column('performance_date', DateTime(length=12, format=u'%Y%m%d%H%M')), # 開演日時
    Column('ticket_payment', ZeroPaddedInteger(length=9, pytype=decimal.Decimal)),        # チケット料金
    Column('ticketing_fee', ZeroPaddedInteger(length=8, pytype=decimal.Decimal)),         # 発券料金
    Column('other_fees', ZeroPaddedInteger(length=8, pytype=decimal.Decimal)),            # その他手数料
    Column('shop', ZeroPaddedNumericString(length=7)),            # 店舗コード
    Column('settlement_date', DateTime(length=8, pytype=date, format=u'%Y%m%d')), # 売上日
    Column('processed_at', DateTime(length=14, format=u'%Y%m%d%H%M%S')), # 処理日時
    Column('valid', Boolean(true_sign=u'+', false_sign=u'-')),    # 赤黒区分 (True=valid)
    Column('ticket_count', ZeroPaddedInteger(length=6)),          # チケット枚数
    Column('subticket_count', ZeroPaddedInteger(length=6)),       # 副券枚数
    ]

def make_marshaller(f, encoding='cp932', eor='\n'):
    encoder = getencoder(encoding)
    marshaller = FixedRecordMarshaller(sales_report_schema)
    def out(rendered):
        f.write(encoder(rendered)[0] + eor)
    def _(row):
        marshaller(row, out)
    return _

def gen_records_from_order_model(famiport_order, start_date, end_date):
    famiport_sales_segment = famiport_order.famiport_sales_segment
    famiport_performance = famiport_sales_segment.famiport_performance
    famiport_event = famiport_performance.famiport_event
    famiport_client = famiport_event.client
    playguide = famiport_client.playguide

    subticket_count = sum(1 if famiport_ticket.is_subticket else 0 for famiport_ticket in famiport_order.famiport_tickets)
    ticket_count = len(famiport_order.famiport_tickets) - subticket_count
    basic_dict = dict(
        event_code=famiport_event.code_1,
        event_code_sub=famiport_event.code_2,
        sales_segment_code=famiport_sales_segment.code,
        performance_code=famiport_performance.code,
        event_name=famiport_event.name_1,
        performance_date=famiport_performance.start_at,
        ticket_count=ticket_count,
        subticket_count=subticket_count
        )

    completed_or_canceled_famiport_receipts_during_the_period = []
    payment_famiport_receipt = None
    ticketing_famiport_receipt = None
    for famiport_receipt in famiport_order.famiport_receipts:
        if famiport_receipt.created_at >= end_date:
            continue
        if famiport_receipt.completed_at is None or \
           famiport_receipt.completed_at >= end_date:
            continue
        applicable_for_valid_entry = \
            famiport_receipt.completed_at >= start_date
        applicable_for_invalidated_entry = False
        if famiport_receipt.canceled_at is not None:
            applicable_for_invalidated_entry = (
                famiport_receipt.canceled_at >= start_date and \
                famiport_receipt.canceled_at < end_date
                )
        if famiport_receipt.canceled_at is None or \
           famiport_receipt.canceled_at >= end_date:
            if famiport_receipt.is_payment_receipt:
                payment_famiport_receipt = famiport_receipt
            if famiport_receipt.is_ticketing_receipt:
                ticketing_famiport_receipt = famiport_receipt
        # 同日の発券・払込とキャンセルは打消し合うので除外する
        if applicable_for_valid_entry ^ applicable_for_invalidated_entry:
            # 除外の対象でなければ以下
            if famiport_receipt.canceled_at is not None and \
               famiport_receipt.canceled_at >= start_date and \
               famiport_receipt.canceled_at < end_date:
                processed_at = famiport_receipt.canceled_at
            else:
                processed_at = famiport_receipt.completed_at
            completed_or_canceled_famiport_receipts_during_the_period.append((processed_at, famiport_receipt))

    completed_or_canceled_famiport_receipts_during_the_period = sorted(
        completed_or_canceled_famiport_receipts_during_the_period,
        key=lambda processed_at_and_famiport_receipt: processed_at_and_famiport_receipt[0]
        )

    dicts = []
    reported_famiport_receipts = []
    for processed_at, famiport_receipt in completed_or_canceled_famiport_receipts_during_the_period:
        logger.info('processing FamiPortReceipt(id=%d, reserve_number=%s)' % (famiport_receipt.id, famiport_receipt.reserve_number))
        valid = famiport_receipt.canceled_at is None or (famiport_receipt.canceled_at >= end_date)
        management_number = famiport_order.famiport_order_identifier[3:12]
        unique_key = '%d%s' % (
            playguide.discrimination_code,
            management_number,
            )
        if famiport_receipt.type == FamiPortReceiptType.Payment.value:
            assert famiport_order.type in (FamiPortOrderType.Payment.value, FamiPortOrderType.PaymentOnly.value)
            if famiport_order.paid_at is None:
                logger.warning('FamiPortOrder(id=%d) paid_at=None while FamiPortReceipt.type=Payment' % (famiport_order.id, ))
            dict_ = dict(
                type=SalesReportEntryType.Payment.value,
                unique_key=unique_key,
                management_number=management_number,
                processed_at=processed_at,
                settlement_date=processed_at.date(),
                ticket_payment=famiport_order.ticket_payment,
                ticketing_fee=decimal.Decimal(0),
                other_fees=famiport_order.system_fee,
                shop=famiport_receipt.shop_code,
                valid=valid,
                **basic_dict
                )
            dicts.append(dict_)
            reported_famiport_receipts.append(famiport_receipt)
        elif famiport_receipt.type == FamiPortReceiptType.Ticketing.value:
            assert famiport_order.type in (FamiPortOrderType.Payment.value, FamiPortOrderType.Ticketing.value)
            if famiport_order.issued_at is None:
                logger.warning('FamiPortOrder(id=%d) issued_at=None while FamiPortReceipt.type=Ticketing' % (famiport_order.id, ))
            if not valid or (ticketing_famiport_receipt is famiport_receipt):
                dict_ = dict(
                    type=SalesReportEntryType.Ticketing.value,
                    unique_key=unique_key,
                    management_number=management_number,
                    processed_at=processed_at,
                    settlement_date=processed_at.date(),
                    ticket_payment=decimal.Decimal(0),
                    ticketing_fee=famiport_order.ticketing_fee,
                    other_fees=decimal.Decimal(0),
                    shop=famiport_receipt.shop_code,
                    valid=valid,
                    **basic_dict
                    )
                dicts.append(dict_)
                reported_famiport_receipts.append(famiport_receipt)
        elif famiport_receipt.type == FamiPortReceiptType.CashOnDelivery.value:
            assert famiport_order.type == FamiPortOrderType.CashOnDelivery.value
            if famiport_order.paid_at is None:
                logger.warning('FamiPortOrder(id=%d) paid_at=None while FamiPortReceipt.type=CashOnDelivery' % (famiport_order.id, ))
            if famiport_order.issued_at is None:
                logger.warning('FamiPortOrder(id=%d) issued_at=None while FamiPortReceipt.type=CashOnDelivery' % (famiport_order.id, ))
            logger.debug('valid=%s, payment_famiport_receipt=FamiPortReceipt(id=%s, reserve_number=%s), famiport_receipt=FamiPortReceipt(id=%s, reserve_number=%s)' % (valid, payment_famiport_receipt and payment_famiport_receipt.id, payment_famiport_receipt and payment_famiport_receipt.reserve_number, famiport_receipt.id, famiport_receipt.reserve_number))
            if not valid or (payment_famiport_receipt is famiport_receipt):
                dict_ = dict(
                    type=SalesReportEntryType.CashOnDelivery.value,
                    unique_key=unique_key,
                    management_number=management_number,
                    processed_at=processed_at,
                    settlement_date=processed_at.date(),
                    ticket_payment=famiport_order.ticket_payment,
                    ticketing_fee=famiport_order.ticketing_fee,
                    other_fees=famiport_order.system_fee,
                    shop=famiport_receipt.shop_code,
                    valid=valid,
                    **basic_dict
                    )
                dicts.append(dict_)
                reported_famiport_receipts.append(famiport_receipt)
        else:
            raise AssertionError('invalid value for FamiPortReceipt.type: %d' % famiport_receipt.type)
    return dicts, reported_famiport_receipts

def build_sales_record(f, famiport_orders, start_date, end_date, **kwargs):
    marshaller = make_marshaller(f, **kwargs)
    reported_famiport_receipts = []
    for order in famiport_orders:
        logger.info('processing FamiPortOrder(id=%d)' % order.id)
        records, reported_famiport_receipts_for_order = gen_records_from_order_model(order, start_date, end_date)
        logger.info('%d records generated for %d receipts' % (len(records), len(reported_famiport_receipts_for_order)))
        for record in records:
            marshaller(record)
        reported_famiport_receipts.extend(reported_famiport_receipts_for_order)
    return reported_famiport_receipts
