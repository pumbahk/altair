# -*- coding:utf-8 -*-

from wtforms.form import Form
from wtforms import fields

class CalendarSelectForm(Form):
    CHOICES = [("obi", u"帯（縦長)"), ("term", u"開始日終了日指定"),]
    calendar_type = fields.SelectField("Calendar type", choices=CHOICES, default="this_month")

class SelectTermForm(Form):
    from_date = fields.DateField(u"開始")
    to_date = fields.DateField(u"終了")


    
