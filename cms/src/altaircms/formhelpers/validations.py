# -*- coding:utf-8 -*-
from wtforms.validators import ValidationError
from . import append_errors
from functools import partial

def validate_term(begin, end, message=u"開始日よりも後に終了日が設定されています", data=None):
    if data.get(end) and data.get(begin):
        if data[begin] > data[end]:
            raise ValidationError(message)

def validate_filetype(fieldname, failfn, message=u"不正なファイルです", data=None):
    v = data.get(fieldname)
    if v != u"" and failfn(v):
        raise ValidationError(message)

class ValidationQueue(object):
    def __init__(self):
        self.queue = []

    def enqueue(self, k, fn, *args, **kwargs):
        self.queue.append((k, partial(fn, *args, **kwargs)))
    
    def __call__(self, data, errors):
        for k, fn in self.queue:
            try:
                fn(data=data)
            except ValidationError as e:
                append_errors(errors, k, e.message)
                return False
        return True
