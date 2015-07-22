# encoding: utf-8

from zope.interface import implements
from .users.models import SexEnum
from .interfaces import ITicketingFormatter

class Japanese_Japan_Formatter(object):
    implements(ITicketingFormatter)

    SEX_TO_STRING_MAP = {
        SexEnum.NoAnswer.v: u'未回答',
        SexEnum.Male.v: u'男性',
        SexEnum.Female.v: u'女性'
        }
    WEEK_NAMES = [u'月', u'火', u'水', u'木', u'金', u'土', u'日']

    def sex_as_string(self, sex):
        return self.SEX_TO_STRING_MAP[sex] 

    def format_date(self, date):
        return unicode(date.strftime('%Y年 %0m月 %0d日'), 'utf-8') + u' (%s)' % self.WEEK_NAMES[date.weekday()]

    def format_weekday(self, weekday):
        return self.WEEK_NAMES[weekday]

    def format_date_compressed(self, date):
        return unicode(date.strftime('%Y年%0m月%0d日'), 'utf-8') + u'(%s)' % self.WEEK_NAMES[date.weekday()]

    def format_date_short(self, date):
        return unicode(date.strftime('%Y/%0m/%0d'), 'utf-8') + u' (%s)' % self.WEEK_NAMES[date.weekday()]

    def format_time(self, time):
        return unicode(time.strftime('%H時 %M分'), 'utf-8')

    def format_time_short(self, time):
        return unicode(time.strftime('%H:%M'), 'utf-8')

    def format_datetime(self, datetime):
        return self.format_date(datetime) + u' ' + self.format_time(datetime)

    def format_datetime_short(self, datetime):
        return self.format_date_short(datetime) + u' ' + self.format_time_short(datetime)

    def format_currency(self, dec):
        return u'{0:0,.0f}円'.format(dec)

def includeme(config):
    config.registry.registerUtility(Japanese_Japan_Formatter(), ITicketingFormatter, 'ja_JP')
