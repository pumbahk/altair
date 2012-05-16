# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField
from wtforms.validators import Required, Length

class StockTypeForm(Form):
    name            = TextField(u'名称', validators=[Required()])
    fill_color      = TextField(u'色', validators=[Required()])
    fill_type       = SelectField(u'塗りつぶしパターン')
    fill_image      = TextField(u'塗りつぶしイメージ', validators=[Required()])
    stroke_color    = SelectField(u'線の色')
    stroke_width    = SelectField(u'線の太さ')
    stroke_patten   = SelectField(u'線の種類')
