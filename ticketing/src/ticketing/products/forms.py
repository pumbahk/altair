# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField
from wtforms.validators import Required, Length, NumberRange, EqualTo, Optional, ValidationError

from ticketing.events.models import SalesSegment
from ticketing.products.models import ProductItem, StockHolder, Stock

class ProductForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'event_id' in kwargs:
            conditions ={
                'event_id':kwargs['event_id'],
            }
            self.sales_segment_id.choices = [
                (sales_segment.id, sales_segment.name) for sales_segment in SalesSegment.filter_by(**conditions).all()
            ]

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required(u'入力してください')]
    )
    name = TextField(
        label=u'商品名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    price = IntegerField(
        label=u'価格',
        validators=[Required(u'入力してください')]
    )
    sales_segment_id = SelectField(
        label=u'販売区分',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )


class ProductItemForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'user_id' in kwargs and 'performance_id' in kwargs:
            conditions ={
                'performance_id':kwargs['performance_id']
            }
            stock_holders = StockHolder.filter_by(**conditions).all()
            self.stock_holders.choices = []
            for sh in stock_holders:
                if sh.account.user_id == kwargs['user_id']:
                    self.stock_holders.choices.append((sh.id, sh.name))
        if self.stock_holders.data:
            conditions ={
                'stock_holder_id':self.stock_holders.data
            }
            self.stock_id.choices = [
                (stock.id, stock.id) for stock in Stock.filter_by(**conditions).all()
            ]

    id = HiddenField(
        label='',
        validators=[Optional()]
    )
    performance_id = HiddenField(
        label='',
        validators=[Required()]
    )
    product_id = HiddenField(
        label='',
        validators=[Required()]
    )
    price = TextField(
        label=u'価格',
        validators=[Required(u'入力してください')]
    )
    quantity = IntegerField(
        label=u'個数',
        validators=[Required(u'入力してください')]
    )
    stock_holders = SelectField(
        label=u'商品構成',
        validators=[Required(u'入力してください')],
        choices=[],
        coerce=int
    )
    stock_id = SelectField(
        label=u'在庫数',
        validators=[Required(u'入力してください')],
        choices=[],
        coerce=int
    )

    def validate_stock_id(form, field):
        if field.data and form.product_id.data and not form.id.data:
            conditions = {
                'stock_id':field.data,
                'product_id':form.product_id.data,
            }
            if ProductItem.filter_by(**conditions).first():
                raise ValidationError(u'既に登録済みの在庫です')
