# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, FormField, FieldList
from wtforms.validators import Regexp, Length, Optional, ValidationError

from ticketing.models import record_to_multidict
from ticketing.formhelpers import Translations, Required
from ticketing.products.models import Stock, StockHolder

class StockForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    stock_holder_id = HiddenField(
        validators=[Optional()],
    )
    stock_type_id = HiddenField(
        validators=[Required()],
    )
    stock_type_name = HiddenField(
        validators=[Optional()],
    )
    quantity = TextField(
        label=u'在庫数',
        validators=[Required()],
    )


class StockForms(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(StockForms, self).__init__(formdata, obj, prefix, **kwargs)

        def _append_stock_type(stock_types):
            for stock_type in stock_types:
                self.stock_forms.append_entry({'stock_type_id':stock_type.id, 'stock_type_name':stock_type.name})

        if 'stock_types' in kwargs:
            _append_stock_type(kwargs['stock_types'])
        if 'stock_holder_id' in kwargs:
            stocks = Stock.filter_by(stock_holder_id=kwargs['stock_holder_id']).all()
            if stocks:
                for stock in stocks:
                    entry = self.stock_forms.append_entry(stock)
                    entry.form.stock_type_name.data = stock.stock_type.name
            else:
                stock_holder = StockHolder.get(kwargs['stock_holder_id'])
                _append_stock_type(stock_holder.performance.event.stock_types)

    stock_holder_id = HiddenField(
        validators=[Required()],
    )
    stock_forms = FieldList(FormField(StockForm))
