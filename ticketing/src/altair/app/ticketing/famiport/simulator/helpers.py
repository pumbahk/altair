# encoding: utf-8
from base64 import b64encode
from ..communication.models import ReplyClassEnum
       
order_type_strings = {
    int(ReplyClassEnum.CashOnDelivery.value): u'代引',
    int(ReplyClassEnum.Prepayment.value): u'前払後日発券の支払',
    int(ReplyClassEnum.Paid.value): u'前払後日発券の発券 or 発券のみ',
    int(ReplyClassEnum.PrepaymentOnly.value): u'前払のみ',
    }

result_code_strings = {
    u'00': u'払戻許可',
    u'01': u'該当データなし',
    u'02': u'払戻済',
    u'03': u'払戻対象期間外',
    u'07': u'当店販売以外',
    }

class Helpers(object):
    def __init__(self, request):
        self.request = request

    def order_type_as_string(self, order_type):
        return order_type_strings.get(order_type, u'???')

    def to_data_scheme(self, data):
        return u'data:image/jpeg;base64,' + b64encode(data)

    def refund_result_code_as_string(self, result_code):
        return result_code_strings[result_code]
