# encoding: utf-8
from altair.app.ticketing.famiport.datainterchange.fileio import (
    Column,
    ZeroPaddedNumericString,
    Integer,
    DateTime,
    Boolean
)


shop_code_change_schema = [
    Column('management_number', ZeroPaddedNumericString(length=9)),       # 管理番号
    Column('type', Integer(length=1)),                                    # 処理区分
    Column('processed_at', DateTime(length=14, format=u'%Y%m%d%H%M%S')),  # 処理日時
    Column('valid', Boolean(true_sign=u'+', false_sign=u'-')),            # 赤黒区分 (True=valid)
    Column('shop_code', ZeroPaddedNumericString(length=7)),               # 実店番
]

shop_code_change_translation = {
    'management_number': u'管理番号',
    'type': u'処理区分',
    'processed_at': u'処理日時',
    'valid': u'赤黒区分 (True=黒, False=赤)',
    'shop_code': u'実店番',
}
