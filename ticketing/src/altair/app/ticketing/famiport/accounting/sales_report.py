# encoding: utf-8
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
from codecs import getencoder
from datetime import date
from enum import Enum
from ..models import FamiPortOrderType

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
    Column('event_name', WideWidthString(length=60)),             # 興行名称
    Column('performance_date', DateTime(length=12, format=u'%Y%m%d%H%M')), # 開演日時
    Column('ticket_payment', ZeroPaddedInteger(length=9)),        # チケット料金
    Column('ticketing_fee', ZeroPaddedInteger(length=8)),         # 発券料金
    Column('other_fees', ZeroPaddedInteger(length=8)),            # その他手数料
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
    def _(row):
        f.write(encoder(marshaller(row))[0] + eor)
    return _

def gen_records_from_order_model(famiport_order, settlement_date):
    famiport_sales_segment = famiport_order.famiport_sales_segment
    famiport_performance = famiport_sales_segment.famiport_performance
    famiport_event = famiport_performance.famiport_event
    famiport_client = famiport_event.client
    playguide = famiport_client.playguide

    management_number = famiport_order.famiport_order_identifier[3:12]
    unique_key = '%d%s' % (
        playguide.discrimination_code,
        management_number,
        )

    subticket_count = sum(1 if famiport_ticket.is_subticket else 0 for famiport_ticket in famiport_order.famiport_tickets)
    ticket_count = len(famiport_order.famiport_tickets) - subticket_count
    basic_dict = dict(
        unique_key=unique_key,
        management_number=management_number,
        event_code=famiport_event.code_1,
        event_code_sub=famiport_event.code_2,
        sales_segment_code=famiport_sales_segment.code,
        performance_code=famiport_performance.code,
        event_name=famiport_event.name_1,
        performance_date=famiport_performance.start_at,
        ticket_payment=famiport_order.ticket_payment,
        ticketing_fee=famiport_order.ticketing_fee,
        other_fees=famiport_order.system_fee,
        shop=famiport_order.shop_code,
        settlement_date=settlement_date,
        valid=True,
        ticket_count=ticket_count,
        subticket_count=subticket_count
        )

    dicts = []
    if famiport_order.type == FamiPortOrderType.CashOnDelivery.value:
        if famiport_order.paid_at is not None and famiport_order.issued_at is not None:
            dicts.append(dict(type=SalesReportEntryType.CashOnDelivery.value, processed_at=famiport_order.paid_at, **basic_dict))
    if famiport_order.type in (FamiPortOrderType.Payment.value, FamiPortOrderType.PaymentOnly.value):
        if famiport_order.paid_at is not None:
            dicts.append(dict(type=SalesReportEntryType.Payment.value, processed_at=famiport_order.paid_at, **basic_dict))
    if famiport_order.type in (FamiPortOrderType.Payment.value, FamiPortOrderType.Ticketing.value):
        if famiport_order.issued_at is not None:
            dicts.append(dict(type=SalesReportEntryType.Ticketing.value, processed_at=famiport_order.issued_at, **basic_dict))
    return dicts

def build_sales_record(f, famiport_orders, **kwargs):
    marshaller = make_marshaller(f, **kwargs)
    for order in famiport_orders:
        records = gen_records_from_order_model(order)
        for record in records:
            marshaller(record)

