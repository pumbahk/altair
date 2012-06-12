# -*- coding: utf-8 -*-

from decimal import Decimal

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField
from wtforms.validators import Length, NumberRange, EqualTo, Optional, ValidationError

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import SalesSegment, Product, ProductItem, StockHolder, Stock

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

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()]
    )
    name = TextField(
        label=u'商品名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    price = DecimalField(
        label=u'価格',
        places=2,
        validators=[Required()]
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
        if 'user_id' in kwargs and 'event_id' in kwargs:
            conditions ={
                'event_id':kwargs['event_id']
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

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()]
    )
    performance_id = HiddenField(
        validators=[Required()]
    )
    product_id = HiddenField(
        validators=[Required()]
    )
    price = TextField(
        label=u'単価',
        validators=[Required()]
    )
    quantity = IntegerField(
        label=u'販売単位 (席数・個数)',
        validators=[Required()]
    )
    stock_holders = SelectField(
        label=u'配券先',
        validators=[Required()],
        choices=[],
        coerce=int
    )
    stock_id = SelectField(
        label=u'席種・その他',
        validators=[Required()],
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

    def validate_price(form, field):
        if field.data and form.product_id.data:
            product = Product.get(form.product_id.data)
            if product and product.price < Decimal(field.data):
                raise ValidationError(u'商品合計金額以内で入力してください')
