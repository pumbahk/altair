# -*- coding:utf-8 -*-
from wtforms.validators import ValidationError
from . import append_errors

def validate_term(data, begin, end, message=u"開始日よりも後に終了日が設定されています"):
    if data.get(end) and data.get(begin):
        if data[begin] > data[end]:
            raise ValidationError(message)

def validate_filetype(data, fieldname, failfn, message=u"不正なファイルです"):
    v = data.get(fieldname)
    if v != u"" and failfn(v):
        raise ValidationError(message)

def with_append_error(data, k, fn, *args, **kwargs):
    try:
        fn(data, *args, **kwargs)
        return True
    except ValidationError as e:
        append_errors(data, k, e.message)
        return False
