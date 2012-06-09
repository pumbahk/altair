# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, HiddenField, BooleanField, FieldList
from wtforms.validators import Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput
from sqlalchemy.sql import func

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import Stock

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

    def validate_quantity(form, field):
        # 同一Performanceの同一StockTypeにおけるStock.quantityの合計を超えないこと
        conditions = {
            'stock_type_id':form.stock_type_id.data,
            'performance_id':form.performance_id.data,
        }
        sum_quantity = Stock.filter_by(**conditions).with_entities(func.sum(Stock.quantity)).scalar()
        if sum_quantity > int(field.data):
            raise ValidationError(u'既に割り当てている在庫数の合計以下にはできません')
