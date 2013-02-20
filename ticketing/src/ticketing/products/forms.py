# -*- coding: utf-8 -*-

from decimal import Decimal

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField
from wtforms.validators import Length, NumberRange, EqualTo, Optional, ValidationError
from wtforms.widgets import CheckboxInput, TextArea
from sqlalchemy.sql import func

from ticketing.formhelpers import Translations, Required, BugFreeSelectField, OurTextField, OurSelectField, OurIntegerField, OurDecimalField, OurForm, NullableTextField
from ticketing.core.models import SalesSegment, SalesSegmentGroup, Product, ProductItem, StockHolder, StockType, Stock, Performance, TicketBundle

class ProductForm(OurForm):
    @classmethod
    def from_model(cls, product):
        form = cls(
            id = product.id, 
            event_id = product.event_id, 
            name = product.name, 
            price = product.price, 
            display_order = product.display_order, 
            seat_stock_type_id = product.seat_stock_type_id, 
            sales_segment_group_id = product.sales_segment_id, 
            public = 1 if product.public else 0, # why integer?
            description = product.description
            )
        return form


    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(ProductForm, self).__init__(formdata, obj, prefix, **kwargs)
        if 'event_id' in kwargs:
            conditions ={
                'event_id':kwargs['event_id'],
            }
            self.sales_segment_group_id.choices = [
                (sales_segment.id, sales_segment.name) for sales_segment in SalesSegmentGroup.filter_by(**conditions).all()
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
    name = OurTextField(
        label=u'商品名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    price = OurDecimalField(
        label=u'価格',
        places=2,
        validators=[Required()]
    )
    display_order = OurIntegerField(
        label=u'表示順',
        default=1,
        hide_on_new=True,
    )
    seat_stock_type_id = OurSelectField(
        label=u'席種',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    sales_segment_group_id = OurSelectField(
        label=u'販売区分グループ',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    public = OurIntegerField(
        label=u'一般公開',
        default=0,
        hide_on_new=True,
        widget=CheckboxInput(),
    )
    description = NullableTextField(
        label=u'説明',
        hide_on_new=True,
        widget=TextArea()
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
        performance_id = kwargs.get('performance_id')
        event_id = kwargs.get('event_id')
        if performance_id is not None:
            performance = Performance.get(performance_id)
            event_id = performance.event_id
            stock_holders = StockHolder.get_own_stock_holders(event=performance.event)
            self.stock_holders.choices = [(sh.id, sh.name) for sh in stock_holders]

        if event_id is not None:
            ticket_bundles = TicketBundle.filter_by(event_id=event_id)
            self.ticket_bundle_id.choices = [(u'', u'(なし)')] + [(tb.id, tb.name) for tb in ticket_bundles]

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
    ticket_bundle_id = BugFreeSelectField(
        label=u'券面構成',
        validators=[],
        coerce=lambda v: None if not v else int(v)
    )

    def validate_stock_id(form, field):
        if field.data and form.product_id.data and not form.id.data:
            conditions = {
                'stock_id':field.data,
                'product_id':form.product_id.data,
            }
            if ProductItem.filter_by(**conditions).first():
                raise ValidationError(u'既に登録済みの在庫です')

            stock = Stock.get(field.data)
            if stock.stock_type.is_seat:
                # 同一Product内に登録できる席種は1つのみ
                product = Product.get(form.product_id.data)
                for product_item in product.items_by_performance_id(form.performance_id.data):
                    if product_item.stock_type.is_seat:
                        raise ValidationError(u'1つの商品に席種を複数登録することはできません')

                # 商品の席種と在庫の席種は同一であること
                if stock.stock_type.id != product.seat_stock_type_id:
                    raise ValidationError(u'商品の席種と異なる在庫を登録することはできません')

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


class ProductItemGridForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        performance_id = kwargs.get('performance_id')
        event_id = kwargs.get('event_id')

        if performance_id is not None:
            self.performance_id.data = performance_id
            performance = Performance.get(performance_id)
            event_id = performance.event_id
            stock_holders = StockHolder.get_own_stock_holders(event=performance.event)
            self.stock_holder_id.choices = [(sh.id, sh.name) for sh in stock_holders]
        if event_id is not None:
            stock_types = StockType.query.filter_by(event_id=event_id).all()
            self.stock_type_id.choices = [(st.id, st.name) for st in stock_types]
            ticket_bundles = TicketBundle.filter_by(event_id=event_id)
            self.ticket_bundle_id.choices = [(u'', u'(なし)')] + [(tb.id, tb.name) for tb in ticket_bundles]
        if self.stock_holder_id.data:
            conditions ={
                'performance_id':self.performance_id.data,
                'stock_holder_id':self.stock_holder_id.data
            }
            self.stock_id.choices = [
                (stock.id, stock.id) for stock in Stock.filter_by(**conditions).all()
            ]

    def _get_translations(self):
        return Translations()

    product_item_id = HiddenField(
        validators=[Optional()]
    )
    performance_id = HiddenField(
        validators=[Required()]
    )
    product_id = HiddenField(
        validators=[Required()]
    )
    product_item_name = TextField(
        label=u'商品明細名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
    )
    product_item_price = TextField(
        label=u'単価',
        validators=[Required()]
    )
    product_item_quantity = IntegerField(
        label=u'販売単位 (席数・個数)',
        validators=[Required()]
    )
    stock_type_id = SelectField(
        label=u'席種',
        validators=[],
        choices=[],
        coerce=int
    )
    stock_holder_id = SelectField(
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
    ticket_bundle_id = BugFreeSelectField(
        label=u'券面構成',
        validators=[],
        coerce=lambda v: None if not v else int(v)
    )

    def validate_stock_id(form, field):
        if field.data and form.product_id.data and not form.product_item_id.data:
            conditions = {
                'stock_id':field.data,
                'product_id':form.product_id.data,
                }
            if ProductItem.filter_by(**conditions).first():
                raise ValidationError(u'既に登録済みの在庫です')

            stock = Stock.get(field.data)
            if stock.stock_type.is_seat:
                # 同一Product内に登録できる席種は1つのみ
                product = Product.get(form.product_id.data)
                for product_item in product.items_by_performance_id(form.performance_id.data):
                    if product_item.stock_type.is_seat:
                        raise ValidationError(u'1つの商品に席種を複数登録することはできません')

                # 商品の席種と在庫の席種は同一であること
                if stock.stock_type.id != product.seat_stock_type_id:
                    raise ValidationError(u'商品の席種と異なる在庫を登録することはできません')

    def validate_product_item_price(form, field):
        if field.data and form.product_id.data:
            product = Product.get(form.product_id.data)
            conditions = {
                'performance_id':form.performance_id.data,
                'product_id':form.product_id.data,
                }
            sum_amount = ProductItem.filter(ProductItem.id!=form.product_item_id.data)\
                         .filter_by(**conditions)\
                         .with_entities(func.sum(ProductItem.price))\
                         .scalar() or 0
            sum_amount = Decimal(field.data) + Decimal(sum_amount)
            if product and product.price < sum_amount:
                raise ValidationError(u'商品合計金額以内で入力してください')
