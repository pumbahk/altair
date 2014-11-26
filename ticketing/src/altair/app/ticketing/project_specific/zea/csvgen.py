# encoding: utf-8
import csv
from dateutil.parser import parse as parsedate

class Wrapper(object):
    def __init__(self, inner):
        self.__inner = inner
        self.__item_cache = {}
        self.__attr_cache = {}
        self.__as_datetime_cache = None

    def __getitem__(self, k):
        if k in self.__item_cache:
            retval = self.__item_cache[k]
        else:
            try:
                retval = self.__class__(self.__inner[k])
            except:
                retval = self.__class__(None)
            self.__item_cache[k] = retval
        return retval

    def __getattr__(self, k):
        if k in self.__attr_cache:
            retval = self.__attr_cache[k]
        else:
            try:
                retval = self.__class__(getattr(self.__inner, k))
            except:
                retval = self.__class__(None)
            self.__attr_cache[k] = retval
        return retval

    @property
    def _as_datetime(self):
        if self.__as_datetime_cache is None:
            self.__as_datetime_cache = self.__class__(parsedate(self.__inner) if self.__inner is not None else None)
        return self.__as_datetime_cache

    def __format__(self, format_spec):
        return u'-' if self.__inner is None else self.__inner.__format__(format_spec)

    def __unicode__(self):
        return unicode(self.__inner) if self.__inner is not None else u'-'
       
    def __str__(self):
        return self.__unicode__()


class CSVGen(object):
    def __init__(self, columns):
        self.columns = columns

    def header_row(self):
        return [k for k, _ in self.columns]

    def data_row(self, record):
        _record = Wrapper(record)
        return [f.format(_record) for _, f in self.columns]

columns = [
    (u'予約番号', u'{.order_no}'),
    (u'ステータス', u'{.status}'),
    (u'決済ステータス', u'{.payment_status}'),
    (u'予約日時', u'{.created_at:%Y-%m-%d %H:%M:%S}'),
    (u'支払日時', u'{.paid_at:%Y-%m-%d %H:%M:%S}'),
    (u'キャンセル日時', u'{.canceled_at:%Y-%m-%d %H:%M:%S}'),
    (u'決済方法', u'{.payment_delivery_method_pair.payment_method.name}'),
    (u'合計金額', u'{.total_amount}'),
    (u'姓', u'{.shipping_address.last_name}'),
    (u'名', u'{.shipping_address.first_name}'),
    (u'セイ', u'{.shipping_address.last_name_kana}'),
    (u'メイ', u'{.shipping_address.first_name_kana}'),
    (u'性別', u'{.attributes[性別]}'),
    (u'郵便番号', u'{.shipping_address.zip}'),
    (u'国', u'{.shipping_address.country}'),
    (u'都道府県', u'{.shipping_address.prefecture}'),
    (u'市区町村', u'{.shipping_address.city}'),
    (u'町名番地', u'{.shipping_address.address_1}'),
    (u'建物名等', u'{.shipping_address.address_2}'),
    (u'自宅電話番号', u'{.shipping_address.tel_1}'),
    (u'携帯電話番号', u'{.shipping_address.tel_2}'),
    (u'メールアドレス', u'{.shipping_address.email_1}'),
    (u'イベント', u'{.performance.event.title}'),
    (u'公演', u'{.performance.name}'),
    (u'公演コード', u'{.performance.code}'),
    (u'販売区分', u'{.sales_segment.sales_segment_group.name}'),
    (u'誕生日', u'{.attributes[誕生日]._as_datetime:%Y-%m-%d}'),
    (u'ニックネーム', u'{.attributes[ニックネーム]}'),
    (u'メールマガジンの配信', u'{.attributes[メールマガジンの配信]}'),
    (u'好きなメンバー', u'{.attributes[好きなメンバー]}'),
    ]

def make_csv_gen(request):
    return CSVGen(columns)
