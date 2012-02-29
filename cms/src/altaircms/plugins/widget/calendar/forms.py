# -*- coding:utf-8 -*-

from wtforms.form import Form
from wtforms import fields

class CalendarSelectForm(Form):
    CHOICES = [("this_month", u"今月のカレンダーを表示"),  ("list", u"一覧"), ("term", u"楽天チケット")]
    calendar_type = fields.SelectField("Calendar type", choices=CHOICES, default="this_month")

    
