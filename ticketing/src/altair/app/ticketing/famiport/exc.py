# -*- coding: utf-8 -*-
import sys
import traceback

class FamiPortError(Exception):
    pass


class FamiPortNumberingError(FamiPortError):
    pass


class FamiPortAPIError(Exception):
    def __init__(self, message, client_code=None):
        super(FamiPortAPIError, self).__init__(message)
        self.client_code = client_code
        nested_exc_info = sys.exc_info()
        if nested_exc_info[0] is None:
            nested_exc_info = None
        self.nested_exc_info = nested_exc_info

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

    def __repr__(self):
        return 'FamiPortAPIError(%r, %r)' % (self.message, self.client_code)

class FamiPortAPINotFoundError(FamiPortAPIError):
    pass
