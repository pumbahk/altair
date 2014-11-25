# encoding: utf-8

import re
import copy
from wtforms import validators
from wtforms.compat import string_types

__all__ = (
    'Email',
    'MultipleEmail',
    'SejCompliantEmail',
    )

class Email(validators.Regexp):
    def __init__(self, message=None):
        super(Email, self).__init__(r'^[a-zA-Z0-9_+\-*/=.]+@[^.][a-zA-Z0-9_\-.]*\.[a-z]{2,10}$', re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'Invalid email address.')

        super(Email, self).__call__(form, field)

class MultipleEmail(Email):
    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'不正な文字が含まれています')

        if field.data:
            if not isinstance(field.data, string_types):
                raise validators.ValidationError(self.message)

            f = copy.copy(field)
            for email in field.data.split(u','):
                email = email.strip()
                match_obj = re.search(r'<(.*)>', email or '', re.IGNORECASE)
                f.data = email if match_obj is None else match_obj.group(1)
                super(MultipleEmail, self).__call__(form, f)

class SejCompliantEmail(validators.Regexp):
    def __init__(self, message=None):
        super(SejCompliantEmail, self).__init__(r'^[0-9A-Za-z_./+?-]+@(?:[0-9A-Za-z_-]+\.)*[0-9A-Za-z_-]+$', 0, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext('Invalid email address.')
        if not field.data:
            return
        super(SejCompliantEmail, self).__call__(form, field)

