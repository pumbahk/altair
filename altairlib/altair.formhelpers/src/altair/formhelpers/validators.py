# encoding: utf-8

import re
from wtforms import validators
from wtforms.compat import string_types
from datetime import date, datetime

__all__ = (
    'Required',
    'RequiredOnUpdate',
    'Phone',
    'DateTimeFormat',
    'DateTimeInRange',
    'Katakana',
    'JISX0208',
    'CP932',
    'SejCompliantEmail',
    'Zenkaku',
    'after1900',
    'SwitchOptional',
    )

def todatetime(d):
    if not isinstance(d, date):
        raise TypeError()
    return datetime.fromordinal(d.toordinal())

class Required(validators.Required):
    def __call__(self, form, field):
        # allow Zero input
        if field.data != 0:
            super(Required, self).__call__(form, field)

class RequiredOnUpdate(validators.Required):
    def __init__(self):
        self.delegated = Required()

    def __call__(self, form, field):
        if not getattr(form, 'new_form', False):
            self.delegated(form, field)

class Phone(validators.Regexp):
    def __init__(self, message=None):
        super(Phone, self).__init__(r'^[0-9¥-]*$', re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'電話番号を確認してください')
        super(Phone, self).__call__(form, field)

class DateTimeFormat(object):
    def __init__(self, message=u''):
        self.message = message

    def __call__(self, form, field):
        try:
            data = todatetime(field.data)
        except:
            if not field.errors and not self.message: # input data is emputy
                message = field.gettext('This field is required.')
            else:
                message = self.message                
            raise validators.ValidationError(message)

class DateTimeInRange(object):
    def __init__(self, from_=None, to=None):
        self.from_ = from_ and todatetime(from_)
        self.to = to and todatetime(to)

    def format_datetime(self, field, date, type_):
        if hasattr(field._translations, 'format_datetime'):
            if type_ == datetime:
                return field._translations.format_datetime(date)
            else:
                return field._translations.format_date(date)
        else:
            if type_ == datetime:
                return date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return date.strftime("%Y-%m-%d")

    def __call__(self, form, field):
        if field.data is None:
            return
        data = todatetime(field.data)
        if self.from_ is not None and self.from_ > data:
            raise ValueError(field.gettext(u'Field must be a date/time after or equal to %(datetime)s') % dict(field=field.label, datetime=self.format_datetime(field, self.from_, field.data.__class__)))
        if self.to is not None and self.to <= data:
            raise ValueError(field.gettext(u'Field must be a date/time before %(datetime)s') % dict(field=field.label, datetime=self.format_datetime(field, self.to, field.data.__class__)))

Katakana = validators.Regexp(ur'^[ァ-ヶ]+$', message=u'カタカナで入力してください')

class Charset(object):
    def __init__(self, encoding, message=None):
        self.encoding = encoding
        self.message = message or u'利用不可能な文字 (%(characters)s) が含まれています'

    def __call__(self, form, field):
        bad_chars = set()
        bad_chars = self.get_error_chars(field.data)
        if bad_chars:
            raise validators.ValidationError(field.gettext(self.message) % dict(characters=u'「' + u'」「'.join(bad_chars) + u'」'))

    def get_error_chars(self, *args, **kwds):
        return [ch for ch in self.generate_error_chars(*args, **kwds)]

    def generate_error_chars(self, data):
        for c in data:
                try:
                    c.encode(self.encoding)
                except UnicodeEncodeError:
                    yield c

JISX0208 = Charset('Shift_JIS')
CP932 = Charset('CP932')

class SejCompliantEmail(validators.Regexp):
    def __init__(self, message=None):
        super(SejCompliantEmail, self).__init__(r'^[0-9A-Za-z_./+?-]+@(?:[0-9A-Za-z_-]+\.)*[0-9A-Za-z_-]+$', 0, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext('Invalid email address.')
        if not field.data:
            return
        super(SejCompliantEmail, self).__call__(form, field)

def Zenkaku(form, field):
    try:
        cp932_value = field.data.encode('Shift_JIS')
        if not re.match(r"^(?:[\x81-\x9f\xe0-\xfe][\x40-\x7e\x80-\xfc])+$", cp932_value):
            raise Exception()
    except:
        raise validators.ValidationError(field.gettext(u'全角で入力してください'))

after1900 = DateTimeInRange(from_=date(1900, 1, 1))


class SwitchOptional(validators.Optional):
    """
    :param switch_field:
        If field named `switch_field` is True, this field marked as optional.
    :param strip_whitespace:
        If True (the default) also stop the validation chain on input which
        consists of only whitespace.
    """
    field_flags = ('optional', )

    def __init__(self, switch_field, strip_whitespace=True):
        super(SwitchOptional, self).__init__(strip_whitespace=strip_whitespace)
        self.switch_field = switch_field

    def __call__(self, form, field):
        if form[self.switch_field].data:
            super(SwitchOptional, self).__call__(form, field)
