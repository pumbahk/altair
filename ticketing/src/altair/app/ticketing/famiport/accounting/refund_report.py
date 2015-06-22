# encoding: utf-8
import decimal
from codecs import getencoder
from datetime import date
from ..datainterchange.fileio import (
    Column,
    FixedRecordMarshaller,
    ZeroPaddedNumericString,
    NumericString,
    Integer,
    ZeroPaddedInteger,
    WideWidthString,
    DateTime,
    Boolean,
    )

refund_report_schema = [
    Column('unique_key', ZeroPaddedNumericString(length=17)),     # ユニークキー
    Column('type', Integer(length=1)),                            # 処理区分
    Column('management_number', ZeroPaddedNumericString(length=9)), # 管理番号
    Column('event_code', ZeroPaddedNumericString(length=6)),      # 興行コード
    Column('event_code_sub', ZeroPaddedNumericString(length=4)),  # 興行コード (サブ)
    Column('sales_segment_code', ZeroPaddedNumericString(length=3)),  # 受付情報コード
    Column('performance_code', ZeroPaddedNumericString(length=3)),# 公演コード
    Column('event_name', WideWidthString(length=60)),             # 興行名称
    Column('performance_date', DateTime(length=12, format=u'%Y%m%d%H%M')), # 開演日時
    Column('ticket_payment', ZeroPaddedInteger(length=9, pytype=decimal.Decimal)),          # チケット料金
    Column('ticketing_fee', ZeroPaddedInteger(length=8, pytype=decimal.Decimal)),         # 発券料金
    Column('other_fees', ZeroPaddedInteger(length=8, pytype=decimal.Decimal)),            # その他手数料
    Column('start_at', DateTime(length=12, format=u'%Y%m%d%H%M')), # 払戻開始日時
    Column('end_at', DateTime(length=12, format=u'%Y%m%d%H%M')),  # 払戻終了日時
    Column('processed_at', DateTime(length=12, format=u'%Y%m%d%H%M')), # 払戻処理日時
    Column('shop', ZeroPaddedNumericString(length=7)),            # 払戻店舗コード
    Column('shop_of_issue', ZeroPaddedNumericString(length=7)),   # 発券店舗コード
    Column('issued_at', DateTime(length=14, format=u'%Y%m%d%H%M%S')), # 発券処理日時
    Column('valid', Boolean(true_sign=u'+', false_sign=u'-')),    # 赤黒区分 (True=valid)
    Column('barcode_number', NumericString(length=13)),           # チケットバーコード番号
    Column('send_back_due_at', DateTime(length=8, pytype=date, format=u'%Y%m%d')) # 原券必着日
    ]

def make_marshaller(f, encoding='cp932', eor='\n'):
    encoder = getencoder(encoding)
    marshaller = FixedRecordMarshaller(refund_report_schema)
    def out(rendered):
        f.write(encoder(rendered)[0] + eor)
    def _(row):
        marshaller(row, out)
    return _

def gen_record_from_refund_model(refund_entry):
    famiport_refund = refund_entry.famiport_refund
    famiport_ticket = refund_entry.famiport_ticket
    famiport_order = famiport_ticket.famiport_order
    famiport_sales_segment = famiport_order.famiport_sales_segment
    famiport_performance = famiport_sales_segment.famiport_performance
    famiport_event = famiport_performance.famiport_event
    famiport_client = famiport_event.client
    playguide = famiport_client.playguide
    
    management_number = famiport_order.famiport_order_identifier[3:12]
    unique_key = '%d%s%02d%05d' % (
        playguide.discrimination_code,
        management_number,
        0,
        refund_entry.serial,
        )

    return dict(
        unique_key=unique_key,
        type=int(famiport_refund.type),
        management_number=management_number,
        event_code=famiport_event.code_1,
        event_code_sub=famiport_event.code_2,
        sales_segment_code=famiport_sales_segment.code,
        performance_code=famiport_performance.code,
        event_name=famiport_event.name_1,
        performance_date=famiport_performance.start_at,
        ticket_payment=refund_entry.ticket_payment,
        ticketing_fee=refund_entry.ticketing_fee,
        other_fees=refund_entry.other_fees,
        start_at=famiport_refund.start_at,
        end_at=famiport_refund.end_at,
        processed_at=famiport_order.created_at,
        shop=refund_entry.shop_code,
        shop_of_issue=famiport_order.ticketing_famiport_receipt.shop_code,
        issued_at=famiport_ticket.issued_at,
        valid=True,
        barcode_number=famiport_ticket.barcode_number,
        send_back_due_at=famiport_refund.send_back_due_at,
        )

def build_refund_file(f, refund_entries, **kwargs):
    marshaller = make_marshaller(f, **kwargs)
    for refund_entry in refund_entries:
        marshaller(gen_record_from_refund_model(refund_entry))

