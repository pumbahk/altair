# encoding: utf-8

from pyramid.threadlocal import get_current_request
from altair.viewhelpers.datetime_ import create_date_time_formatter
from datetime import datetime

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
        'Not a valid datetime value': u'日時の形式を確認してください',
        'Not a valid date value': u'日付の形式を確認してください',
        'Invalid value for %(field)s': u'%(field)sに不正な値が入力されています',
        "Required field `%(field)s' is not supplied": u'「%(field)s」が空欄になっています',
        u'Field must be a date/time after or equal to %(datetime)s': u'%(datetime)s 以降にしてください',
        u'Field must be a date/time before %(datetime)s': u'%(datetime)s より前にしてください',
        'year': u'年',
        'month': u'月',
        'day': u'日',
        'hour': u'時',
        'minute': u'分',
        'second': u'秒',
        }
    def __init__(self, request=None, messages=None):
        if request is None:
            request = get_current_request() 
        if messages:
            self.messages = dict(self.messages, **messages)
        self.formatter = create_date_time_formatter(request)

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

    def format_datetime(self, date):
        if isinstance(date, datetime):
            return self.formatter.format_datetime(date)
        else:
            return self.formatter.format_date(date)

    def format_date(self, date):
        return self.formatter.format_date(date)

