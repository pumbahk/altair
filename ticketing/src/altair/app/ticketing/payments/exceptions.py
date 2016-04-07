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


class OrderLikeValidationFailure(Exception):
    def __init__(self, message, path):
        super(OrderLikeValidationFailure, self).__init__(message, path)

    @property
    def message(self):
        return self.args[0]

    @property
    def path(self):
        return self.args[1]


class CancellationValidationFailure(Exception):
    """キャンセル出来ない状態にあるときに発生させる例外
    """
    def __init__(self, message):
        super(CancellationValidationFailure, self).__init__(message)

    @property
    def message(self):
        return self.args[0]


class PaymentDeliveryMethodPairNotFound(Exception):
    """
    不思議な経路をたどるなどしてPDMPが取得できない.
    """

class PaymentCartNotAvailable(Exception):
    """
    Cartがexpireしたなどで取得できんかった.
    """
