import traceback
import sys

__all__ = [
    'UsersiteException',
    ]

class UsersiteException(Exception):
    def __init__(self, msg=None):
        nested_exc_info = sys.exc_info()
        Exception.__init__(self, *[msg, nested_exc_info])

    @property
    def message(self):
        return self.args[0]

    @property
    def nested_exc_info(self):
        return self.args[1]

    @property
    def nested_exc_type(self):
        return self.args[1] and self.args[1][0]

    @property
    def nested_exc_value(self):
        return self.args[1] and self.args[1][1]

    @property
    def nested_exc_traceback(self):
        return self.args[1] and self.args[1][2]

    def __str__(self):
        buf = []
        if self.message is not None:
            buf.append(self.message)
        if self.nested_exc_traceback:
            buf.append('\n  -- nested exception --\n')
            for line in traceback.format_exception(*self.nested_exc_info):
                for _line in line.rstrip().split('\n'):
                    buf.append('  ')
                    buf.append(_line)
                    buf.append('\n')
        return ''.join(buf)

class IgnorableSystemException(UsersiteException):
    pass
