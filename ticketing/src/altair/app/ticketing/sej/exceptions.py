# -*- coding: utf-8 -*-

from altair.app.ticketing.payments.exceptions import PaymentPluginException

class SejErrorBase(Exception):
    pass

class SejError(SejErrorBase):
    error_type  = 0
    error_msg   = ''
    error_field = ''

    def __init__(self, message, order_no, error_code=None, error_field=None):
        super(SejError, self).__init__(message, order_no, back_url)
        self.error_type = error_code
        self.error_field = error_field
        self.error_msg = message

    def __str__(self):
        return u"Error_Type=%d&Error_Msg=%s&Error_Field=%s" % (self.error_type, self.error_msg, self.error_field)

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

class SejResponseError(SejErrorBase):
    code = 0
    reason = ''
    params = dict()

    def __init__(self, code, reason, params):
        self.code = code
        self.reason = reason
        self.params = params

    def response(self):
        from .helpers import make_sej_response
        return make_sej_response(self.params)
