# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField
from wtforms.validators import Required, Length, NumberRange, EqualTo, Optional, ValidationError

from ticketing.events.models import SalesSegment
from ticketing.products.models import ProductItem

class ProductForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'event_id' in kwargs:
            conditions ={
                'event_id':kwargs['event_id'],
            }
            self.sales_segment_id.choices = [
                (sales_segment.id, sales_segment.name) for sales_segment in SalesSegment.find_by(**conditions)
            ]

    name = TextField(
        label=u'商品名',
        validators=[Required(u'入力してください')]
    )
    price = TextField(
        label=u'価格',
        validators=[Required(u'入力してください')]
    )
    sales_segment_id = SelectField(
        label=u'販売区分',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    event_id = HiddenField("", validators=[Required()])


class ProductItemForm(Form):

    price = TextField(
        label=u'価格',
        validators=[Required(u'入力してください')]
    )
    stock_id = IntegerField("", validators=[Required()])
    product_id = HiddenField("", validators=[Required()])
    performance_id = HiddenField("", validators=[Required()])
    id = HiddenField("", validators=[Optional()])

    def validate_stock_id(form, field):
        if field.data and form.product_id.data and not form.id.data:
            conditions = {
                'stock_id':field.data,
                'product_id':form.product_id.data,
            }
            if ProductItem.find_by(**conditions):
                raise ValidationError(u'既に登録済みの在庫です')
