# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, FormField, IntegerField, FieldList
from wtforms.validators import Regexp, Length, NumberRange, Optional, ValidationError
from sqlalchemy.sql import func

from ticketing.core.models import record_to_multidict, DBSession
from ticketing.formhelpers import Translations, Required
from ticketing.core.models import Stock, StockHolder, StockAllocation

class StockForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    performance_id = HiddenField(
        validators=[Required()],
    )
    stock_holder_id = HiddenField(
        validators=[Required()],
    )
    stock_type_id = HiddenField(
        validators=[Required()],
    )
    stock_type_name = HiddenField(
        validators=[Optional()],
    )
    quantity = IntegerField(
        label=u'在庫数',
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ],
    )

    def validate_quantity(form, field):
        # 同一Performanceの同一StockTypeにおける合計がStockAllocation.quantityを超えないこと
        conditions = {
            'stock_type_id':form.stock_type_id.data,
            'performance_id':form.performance_id.data,
        }
        allocated_quantity = StockAllocation.filter_by(**conditions).with_entities(StockAllocation.quantity).scalar() or 0
        sum_quantity = Stock.filter(Stock.id!=form.id.data)\
                            .filter_by(**conditions)\
                            .with_entities(func.sum(Stock.quantity))\
                            .scalar() or 0
        if allocated_quantity < (sum_quantity + int(form.quantity.data)):
            raise ValidationError(u'割り当てられている在庫数以上は入力できません')


class StockForms(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(StockForms, self).__init__(formdata, obj, prefix, **kwargs)

        def _append_stock_type(stock_types):
            for stock_type in stock_types:
                self.stock_forms.append_entry({'stock_type_id':stock_type.id, 'stock_type_name':stock_type.name})

        if 'stock_types' in kwargs:
            _append_stock_type(kwargs['stock_types'])
        if 'stock_holder_id' in kwargs:
            stock_holder = StockHolder.get(kwargs['stock_holder_id'])
            stocks = stock_holder.stocks_by_performance(kwargs['performance_id'])
            if stocks:
                for stock in stocks:
                    entry = self.stock_forms.append_entry(stock)
                    entry.form.stock_type_name.data = stock.stock_type.name
            else:
                _append_stock_type(stock_holder.event.stock_types)

    performance_id = HiddenField(
        validators=[Required()],
    )
    stock_holder_id = HiddenField(
        validators=[Required()],
    )
    stock_forms = FieldList(FormField(StockForm))
