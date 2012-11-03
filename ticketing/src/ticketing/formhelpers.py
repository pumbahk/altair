# -*- coding:utf-8 -*-

import re
from datetime import datetime
from exceptions import ValueError
import unicodedata

from wtforms import validators, fields
import logging

logger = logging.getLogger(__name__)

'''
Customized field definition datetime format of "%Y-%m-%d %H:%M"
'''
class DateTimeField(fields.DateTimeField):

    def _value(self):
        if self.raw_data:
            try:
                dt = datetime.strptime(self.raw_data[0], '%Y-%m-%d %H:%M:%S')
                return dt.strftime(self.format)
            except:
                return u' '.join(self.raw_data)
        else:
            return self.data.strftime(self.format) if self.data else u''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = u' '.join(valuelist)
            try:
                self.data = datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise validators.ValidationError(u'日付の形式を確認してください')

class BugFreeSelectField(fields.SelectField):
    def pre_validate(self, form):
        for v, _ in self.choices:
            if self.data == self.coerce(v):
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))

class Translations(object):
    messages={
        'Not a valid choice': u'不正な選択です',
        'Not a valid decimal value': u'数字または小数で入力してください',
        'Not a valid integer value': u'数字で入力してください',
        'Invalid email address.':u'不正なメールアドレスです',
        'This field is required.':u'入力してください',
        'Field must be at least %(min)d characters long.' : u'%(min)d文字以上で入力してください。',
        'Field cannot be longer than %(max)d characters.' : u'%(max)d文字以内で入力してください。',
        'Field must be between %(min)d and %(max)d characters long.' : u'%(min)d文字から%(max)d文字の間で入力してください。',
    }
    def __init__(self, messages = None):
        if messages:
            self.messages = dict(self.messages, **messages)

    def gettext(self, string):
        return self.messages.get(string, string)

    def ngettext(self, singular, plural, n):
        ural = singular if n == 1 else plural
        message  = self.messages.get(ural)
        if message:
            return message
        else:
            logger.warn("localize message not found: '%s'", ural)
            return ural


class Required(validators.Required):

    def __call__(self, form, field):
        # allow Zero input
        if field.data != 0:
            super(Required, self).__call__(form, field)

class Phone(validators.Regexp):
    def __init__(self, message=None):
        super(Phone, self).__init__(r'^[0-9¥-]*$', re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'電話番号を確認してください')
        super(Phone, self).__call__(form, field)

def text_type_but_none_if_not_given(value):
    return unicode(value) if value is not None else None

def Zenkaku(form, field):
    try:
        cp932_value = field.data.encode('Shift_JIS')
        if not re.match(r"^(?:[\x81-\x9f\xe0-\xfe][\x40-\x7e\x80-\xfc])+$", cp932_value):
            raise Exception()
    except:
        raise validators.ValidationError(field.gettext(u'全角で入力してください'))

Katakana = validators.Regexp(ur'^[ァ-ヶ]+$', message=u'カタカナで入力してください')

def NFKC(unistr):
    return unistr and unicodedata.normalize('NFKC', unistr)

def lstrip(chars):
    def stripper(unistr):
        return unistr and unistr.lstrip(chars)
    return stripper

def strip(chars):
    def stripper(unistr):
        return unistr and unistr.strip(chars)
    return stripper

REGEX_HYPHEN = re.compile('\-')
def strip_hyphen():
    def stripper(unistr):
        print unistr
        return unistr and REGEX_HYPHEN.sub('', unistr)
    return stripper

strip_spaces = strip(u' 　')

class SejCompliantEmail(validators.Regexp):
    def __init__(self, message=None):
        super(SejCompliantEmail, self).__init__(r'^[0-9A-Za-z_./+?-]+@(?:[0-9A-Za-z_-]+\.)*[0-9A-Za-z_-]+$', 0, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext('Invalid email address.')

        super(SejCompliantEmail, self).__call__(form, field)

def capitalize(unistr):
    return unistr and unistr.upper()

def ignore_regexp(regexp):
    def replace(target):
        if target is None:
            return None
        return re.sub(regexp, "", target)
    return replace

ignore_space_hyphen = ignore_regexp(re.compile(u"[ \-ー　]"))
