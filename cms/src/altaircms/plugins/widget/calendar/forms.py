# -*- coding:utf-8 -*-

from wtforms.form import Form
from wtforms import fields

class CalendarSelectForm(Form):
    CHOICES = [("thismonth", u"今月"),  ("list", u"一覧"), ("term", u"開始日/終了日")]
    calendar_type = fields.SelectField("Calendar type", choices=CHOICES)
    
