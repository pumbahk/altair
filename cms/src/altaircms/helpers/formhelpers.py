# -*- coding:utf-8 -*-
from wtforms import validators

def required_field(message=None):
    if message is None:
        message = u"このフィールドは必須です。"
    return Required(message=message)

def append_errors(errors, key, v):
    if key not in errors:
        errors[key] = []
    errors[key].append(v)
    return errors

class Required(object):
    field_flags = ('required', )

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            if self.message is None:
                self.message = field.gettext(u'This field is required.')
            raise validators.StopValidation(self.message)
