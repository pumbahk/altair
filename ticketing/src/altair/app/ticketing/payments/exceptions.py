# encoding: utf-8
import sys
import traceback

class PaymentPluginException(Exception):
    def __init__(self, message, order_no, back_url, ignorable=False):
        """
        back_url に値がセットされている => カート救済可能
                             されていない => カート救済不可能
        """
        super(PaymentPluginException, self).__init__(message)
        self.order_no = order_no
        self.back_url = back_url
        nested_exc_info = sys.exc_info()
        if nested_exc_info[0] is None:
            nested_exc_info = None
        self.nested_exc_info = nested_exc_info
        self.ignorable = ignorable

    def __str__(self):
        buf = []
        if self.message is not None:
            buf.append(self.message)
        if self.nested_exc_info:
            buf.append('\n  -- nested exception --\n')
            for line in traceback.format_exception(*self.nested_exc_info):
                for _line in line.rstrip().split('\n'):
                    buf.append('  ')
                    buf.append(_line)
                    buf.append('\n')
        return ''.join(buf)

class PaymentDeliveryMethodPairNotFound(Exception):
    """
    不思議な経路をたどるなどしてPDMPが取得できない.
    """
