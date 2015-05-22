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

sales_report_schema = [
    Column('unique_key', ZeroPaddedNumericString(length=10)),     # ユニークキー
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
