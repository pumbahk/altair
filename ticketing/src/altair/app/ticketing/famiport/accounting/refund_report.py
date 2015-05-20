# encoding: utf-8
from ..data_interchange.fileio import (
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
from codecs import getencoder
from datetime import date

refund_report_schema = [
    Column('unique_key', ZeroPaddedNumericString(length=17)),     # ユニークキー
    Column('type', Integer(length=1)),                            # 処理区分
    Column('management_number', ZeroPaddedNumericString(length=9)), # 管理番号
    Column('event_code', ZeroPaddedNumericString(length=6)),      # 興行コード
    Column('event_code_sub', ZeroPaddedNumericString(length=4)),  # 興行コード (サブ)
    Column('acceptance_info_code', ZeroPaddedInteger(length=3)),  # 受付情報コード
    Column('performance_code', ZeroPaddedNumericString(length=3)),# 公演コード
    Column('event_name', WideWidthString(length=60)),             # 興行名称
    Column('performance_date', DateTime(length=12, format=u'%Y%m%d%H%M')), # 開演日時
    Column('ticket_price', ZeroPaddedInteger(length=9)),          # チケット料金
    Column('ticketing_fee', ZeroPaddedInteger(length=8)),         # 発券料金
    Column('other_fees', ZeroPaddedInteger(length=8)),            # その他手数料
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
    def _(row):
        f.write(encoder(marshaller(row))[0] + eor)
    return _
