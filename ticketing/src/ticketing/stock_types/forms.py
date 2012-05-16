# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField
from wtforms.validators import Required, Length

class StockTypeForm(Form):
    name            = TextField(u'名称', validators=[Required()])
    type            = IntegerField(u'')
    fill_color      = TextField(u'色')
    fill_type       = SelectField(u'塗りつぶしパターン')
    fill_image      = TextField(u'塗りつぶしイメージ')
    stroke_color    = SelectField(u'線の色')
    stroke_width    = SelectField(u'線の太さ')
    stroke_patten   = SelectField(u'線の種類')
