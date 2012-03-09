# -*- coding:utf-8 -*-

from wtforms.form import Form
from wtforms import fields

class DetailSelectForm(Form):
    CHOICES = [("description", u"楽天チケット")]
    kind  = fields.SelectField("Detail type", choices=CHOICES, default="rakuten")
