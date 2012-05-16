# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, HiddenField
from wtforms.validators import Required, Length
from ticketing.products.models import StockTypeEnum

class StockTypeForm(Form):
    name            = TextField(u'名称', validators=[Required()])
    type            = IntegerField(u'区分', default=StockTypeEnum.Seat.v)
    fill_color      = TextField(u'色')
    fill_type       = SelectField(u'塗りつぶしパターン')
    fill_image      = TextField(u'塗りつぶしイメージ')
    stroke_color    = SelectField(u'線の色')
    stroke_width    = SelectField(u'線の太さ')
    stroke_patten   = SelectField(u'線の種類')

class StockAllocationForm(Form):
    stock_type_id  = HiddenField('', validators=[Required()])
    performance_id = HiddenField('', validators=[Required()])
    quantity       = TextField(u'在庫数', validators=[Required()])
