# -*- coding:utf-8 -*-

from wtforms.form import Form
from wtforms import fields

class CalendarSelectForm(Form):
    CHOICES = [("this_month", u"今月のカレンダー"), ("term", u"開始日終了日指定"), ("list", u"一覧"),]
    calendar_type = fields.SelectField("Calendar type", choices=CHOICES, default="this_month")

class SelectTermForm(Form):
    from_date = fields.DateField(u"開始")
    to_date = fields.DateField(u"終了")


    
