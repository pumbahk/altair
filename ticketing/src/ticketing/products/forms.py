# -*- coding: utf-8 -*-

from decimal import Decimal

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField
from wtforms.validators import Length, NumberRange, EqualTo, Optional, ValidationError
from sqlalchemy.sql import func

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import SalesSegment, Product, ProductItem, StockHolder, StockType, Stock, Performance

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
            self.seat_stock_type_id.choices = [
                (stock_type.id, stock_type.name) for stock_type in StockType.filter_by(**conditions).all()
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'商品ID',
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
    display_order = IntegerField(
        label=u'表示順',
    )
    seat_stock_type_id = SelectField(
        label=u'席種',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    sales_segment_id = SelectField(
        label=u'販売区分',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )

    def validate_price(form, field):
        if field.data and form.id.data:
            product = Product.get(form.id.data)
            for performance in product.event.performances:
                conditions = {
                    'performance_id':performance.id,
                    'product_id':form.id.data,
                }
                sum_amount = ProductItem.filter_by(**conditions)\
                                        .with_entities(func.sum(ProductItem.price))\
                                        .scalar() or 0
                if Decimal(field.data) < Decimal(sum_amount):
                    raise ValidationError(u'既に登録された商品合計金額以上で入力してください')


class ProductItemForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'performance_id' in kwargs:
            performance = Performance.get(kwargs['performance_id'])
            stock_holders = StockHolder.get_seller(performance.event)
            self.stock_holders.choices = [(sh.id, sh.name) for sh in stock_holders]
        if self.stock_holders.data:
            conditions ={
                'performance_id':self.performance_id.data,
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
    name = TextField(
        label=u'商品明細名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
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

            # 同一Product内に登録できる席種は1つのみ
            stock = Stock.get(field.data)
            if stock.stock_type.is_seat:
                product = Product.get(form.product_id.data)
                for product_item in product.items_by_performance_id(form.performance_id.data):
                    if product_item.stock_type.is_seat:
                        raise ValidationError(u'1つの商品に席種を複数登録することはできません')

    def validate_price(form, field):
        if field.data and form.product_id.data:
            product = Product.get(form.product_id.data)
            conditions = {
                'performance_id':form.performance_id.data,
                'product_id':form.product_id.data,
            }
            sum_amount = ProductItem.filter(ProductItem.id!=form.id.data)\
                                    .filter_by(**conditions)\
                                    .with_entities(func.sum(ProductItem.price))\
                                    .scalar() or 0
            sum_amount = Decimal(field.data) + Decimal(sum_amount)
            if product and product.price < sum_amount:
                raise ValidationError(u'商品合計金額以内で入力してください')
