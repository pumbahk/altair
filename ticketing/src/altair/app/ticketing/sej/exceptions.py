# -*- coding: utf-8 -*-

from altair.app.ticketing.payments.exceptions import PaymentPluginException

class SejErrorBase(Exception):
    pass

class SejError(SejErrorBase):
    def __init__(self, message, order_no, error_code=None, error_field=None):
        super(SejError, self).__init__(message)
        self.order_no = order_no
        self.error_type = error_code
        self.error_field = error_field
        self.error_msg = message

    def __str__(self):
        return u"X_shop_order_id=%s&Error_Type=%s&Error_Msg=%s&Error_Field=%s" % (
            self.order_no,
            (str(self.error_type) if self.error_type is not None else u''),
            (self.error_msg if self.error_msg is not None else u''),
            (self.error_field if self.error_field is not None else u'')
            )

class SejRequestError(SejErrorBase):
    pass

class SejServerError(SejErrorBase):
    status_code  = 0
    reason      = ''
    body        = ''

    def __init__(self, status_code, reason, body):
        self.status_code = status_code
        self.reason = reason
        self.body = body

    def __str__(self):
        return "status_code=%d&reason=%s: body: %s" % (self.status_code, self.reason, self.body)
