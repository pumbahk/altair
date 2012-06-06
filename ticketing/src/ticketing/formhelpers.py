# -*- coding:utf-8 -*-

from datetime import datetime
from exceptions import ValueError

from wtforms import validators, fields


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


class Translations(object):

    def gettext(self, string):
        if string == 'Not a valid choice':
            return u'不正な選択です'
        if string == 'Not a valid decimal value':
            return u'数字または小数で入力してください'
        if string == 'Not a valid integer value':
            return u'数字で入力してください'
        if string == 'Invalid email address.':
            return u'不正なメールアドレスです'
        if string == 'This field is required.':
            return u'入力してください'
        return string

    def ngettext(self, singular, plural, n):
        if n == 1:
            return singular
        return plural


class Required(validators.Required):

    def __call__(self, form, field):
        # allow Zero input
        if field.data != 0:
            super(Required, self).__call__(form, field)
