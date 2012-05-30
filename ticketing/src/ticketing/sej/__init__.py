# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('sej.callback'                 , '/callback')
    config.scan()


class SejError(Exception):

    error_type  = 0
    error_msg   = ''
    error_field = ''

    def __init__(self, error_type, error_msg, error_field):

        self.error_type = error_type
        self.error_field = error_field
        self.error_msg = error_msg

    def __str__(self):
        return "Error_Type=%d&Error_Msg=%s&Error_Field=%s" % (self.error_type, self.error_type, self.error_field)

class SejServerError(Exception):

    status_code  = 0
    reason      = ''

    def __init__(self, status_code, reason):

        self.status_code = status_code
        self.reason = reason

    def __str__(self):
        return "status_code=%d&reason=%s" % (self.status_code, self.reason)

class SejResponseError(Exception):

    code = 0
    reason = ''

    def __init__(self, code, reason, body):
        self.code = code
        self.reason = reason