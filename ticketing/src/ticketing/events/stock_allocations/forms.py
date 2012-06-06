# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, HiddenField, BooleanField, FieldList
from wtforms.validators import Length, Optional
from wtforms.widgets import CheckboxInput

from ticketing.formhelpers import Translations, Required
from ticketing.products.models import StockTypeEnum

class StockAllocationForm(Form):
    stock_type_id = HiddenField(
        label='',
        validators=[Required()]
    )
    venue_id = HiddenField(
        label='',
        validators=[]
    )
    performance_id = HiddenField(
        label='',
        validators=[]
    )
    quantity = TextField(
        label=u'在庫数',
        validators=[Required()]
    )
    seat_l0_id = FieldList(HiddenField(label=u'シートID'))
