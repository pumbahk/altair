# encoding: utf-8
from base64 import b64encode
from ..communication.models import ReplyClassEnum
       
order_type_strings = {
    int(ReplyClassEnum.CashOnDelivery.value): u'代引',
    int(ReplyClassEnum.Prepayment.value): u'前払後日発券の支払',
    int(ReplyClassEnum.Paid.value): u'前払後日発券の発券 or 発券のみ',
    int(ReplyClassEnum.PrepaymentOnly.value): u'前払のみ',
    }


class Helpers(object):
    def __init__(self, request):
        self.request = request

    def order_type_as_string(self, order_type):
        return order_type_strings.get(order_type, u'???')

    def to_data_scheme(self, data):
        return u'data:image/jpeg;base64,' + b64encode(data)
