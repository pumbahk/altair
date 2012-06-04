# -*- coding:utf-8 -*-
import logging
from functools import wraps
class not_support_if_keyerror(object):
    """ keyerrorが出たとき、エラーメッセージに差し替えるデコレータ
    """
    def __init__(self, fmt):
        self.fmt = fmt

    def __call__(self, fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except KeyError as e:
                logging.warn(e)
                return self._not_support_message(e)
        return decorated

    def _not_support_message(self, err):
        return self.fmt % {"err": err}
