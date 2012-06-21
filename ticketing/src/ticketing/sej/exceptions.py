# -*- coding: utf-8 -*-


class SejRequestError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class SejError(Exception):

    error_type  = 0
    error_msg   = ''
    error_field = ''

    def __init__(self, error_type, error_msg, error_field, error_body):

        self.error_type = error_type
        self.error_field = error_field
        self.error_msg = error_msg

    def __str__(self):
        return u"Error_Type=%d&Error_Msg=%s&Error_Field=%s" % (self.error_type, self.error_type, self.error_field)

class SejServerError(Exception):

    status_code  = 0
    reason      = ''
    body        = ''

    def __init__(self, status_code, reason, body):

        self.status_code = status_code
        self.reason = reason
        self.body = body

    def __str__(self):
        return "status_code=%d&reason=%s: body: %s" % (self.status_code, self.reason, self.body)

class SejResponseError(Exception):

    code = 0
    reason = ''
    params = dict()

    def __init__(self, code, reason, params):
        self.code = code
        self.reason = reason
        self.params = params

    def response(self):
        return make_sej_response(self.params)
