# encoding: utf-8

class PaymentPluginException(Exception):
    def __init__(self, message, order_no, back_url):
        """
        back_url に値がセットされている => カート救済可能
                             されていない => カート救済不可能
        """
        self.message = message
        self.order_no = order_no
        self.back_url = back_url

class PaymentDeliveryMethodPairNotFound(Exception):
    """
    不思議な経路をたどるなどしてPDMPが取得できない.
    """
