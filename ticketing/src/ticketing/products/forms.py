# -*- coding: utf-8 -*-

from decimal import Decimal

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField, BooleanField
from wtforms.validators import Length, NumberRange, EqualTo, Optional, ValidationError
from wtforms.widgets import CheckboxInput, TextArea
from sqlalchemy.sql import func

from ticketing.formhelpers import Translations, Required, BugFreeSelectField, OurTextField, OurSelectField, OurIntegerField, OurBooleanField, OurDecimalField, OurForm, NullableTextField
from ticketing.core.models import SalesSegment, SalesSegmentGroup, Product, ProductItem, StockHolder, StockType, Stock, Performance, TicketBundle
from ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID

class ProductForm(OurForm):
    @classmethod
    def from_model(cls, product):
        form = cls(
            id=product.id, 
            performance_id=product.performance_id, 
            name=product.name, 
            price=product.price, 
            display_order=product.display_order, 
            seat_stock_type_id=product.seat_stock_type_id, 
            sales_segment_id=product.sales_segment_id, 
            public=1 if product.public else 0, # why integer?
            description=product.description
            )
        return form

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(ProductForm, self).__init__(formdata, obj, prefix, **kwargs)
        if 'performance_id' in kwargs:
            performance = Performance.query.filter_by(id=kwargs['performance_id']).one()
            self.sales_segment_id.choices = [
                (sales_segment.id, sales_segment.name) \
                for sales_segment in SalesSegment.filter(SalesSegment.performance_id == performance.id).all()
                ]
            self.seat_stock_type_id.choices = [
                (stock_type.id, stock_type.name) \
                for stock_type in StockType.filter(StockType.event_id == performance.event_id).all()
                ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'商品ID',
        validators=[Optional()],
        )
    performance_id = HiddenField(
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
    sales_segment_id = OurSelectField(
        label=u'販売区分',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
        )
    public = OurBooleanField(
        label=u'一般公開',
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
            sum_amount = ProductItem.query \
                .filter(
                    (ProductItem.performance_id == form.performance_id.data) & \
                    (ProductItem.product_id == form.id.data)
                    ) \
                .with_entities(func.sum(ProductItem.price)) \
                .scalar() or 0
            if Decimal(field.data) < Decimal(sum_amount):
                raise ValidationError(u'既に登録された商品合計金額以上で入力してください')

    def validate_seat_stock_type_id(form, field):
        if form.id.data:
            product = Product.get(form.id.data)
            if product.items and field.data != product.seat_stock_type_id:
                raise ValidationError(u'既に在庫が割り当てられているため、席種は変更できません')


class ProductItemForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(ProductItemForm, self).__init__(formdata, obj, prefix, **kwargs)
        product_id = kwargs.get('product_id')
        performance_id = kwargs.get('performance_id')

        if product_id is not None:
            self.product_id.data = product_id
            product = Product.get(product_id)
            performance_id = product.performance_id
        if performance_id is not None:
            self.performance_id.data = performance_id
            performance = Performance.get(performance_id)
            event_id = performance.event_id
            stock_holders = StockHolder.get_own_stock_holders(event=performance.event)
            self.stock_holder_id.choices = [(sh.id, sh.name) for sh in stock_holders]
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
        if formdata is not None:
            conditions ={
                'performance_id':self.performance_id.data,
                'stock_holder_id':self.stock_holder_id.data,
                'stock_type_id':self.stock_type_id.data
            }
            stock = Stock.query.filter_by(**conditions).first()
            if stock:
                self.stock_id.data = stock.id

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
    product_item_name = OurTextField(
        label=u'商品明細名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
    )
    product_item_price = OurDecimalField(
        label=u'単価',
        validators=[Required()]
    )
    product_item_quantity = OurIntegerField(
        label=u'販売単位 (席数・個数)',
        validators=[Required()]
    )
    stock_type_id = OurSelectField(
        label=u'席種',
        validators=[Required()],
        choices=[],
        coerce=int
    )
    stock_holder_id = OurSelectField(
        label=u'配券先',
        validators=[Required()],
        choices=[],
        coerce=int
    )
    stock_id = HiddenField(
        label=u'席種・その他',
        validators=[Required()],
    )
    ticket_bundle_id = OurSelectField(
        label=u'券面構成',
        validators=[],
        coerce=lambda v: None if not v else int(v)
    )

    def validate_stock_id(form, field):
        if not field.data:
            raise ValidationError(u'席種および配券先を選択してください')
        elif form.product_id.data:
            conditions = {
                'stock_id':field.data,
                'product_id':form.product_id.data,
                }
            product_item = ProductItem.filter_by(**conditions).first()
            if product_item:
                if not form.product_item_id.data or product_item.id != int(form.product_item_id.data):
                    raise ValidationError(u'既に登録済みの在庫です')

            stock = Stock.get(field.data)
            if stock.stock_type.is_seat:
                # 商品の席種と在庫の席種は同一であること
                product = Product.get(form.product_id.data)
                if stock.stock_type.id != product.seat_stock_type_id:
                    raise ValidationError(u'商品の席種と異なる在庫を登録することはできません')
                # 同一Product内に登録できる席種は1つのみ
                #for product_item in product.items_by_performance_id(form.performance_id.data):
                for product_item in product.items:
                    if product_item.id != int(form.product_item_id.data) and product_item.stock_type.is_seat:
                        raise ValidationError(u'1つの商品に席種を複数登録することはできません')

    def validate_product_item_price(form, field):
        if field.data and form.product_id.data and form.product_item_id.data:
            product = Product.get(form.product_id.data)
            sum_amount = int(field.data) * int(form.product_item_quantity.data)
            for item in product.items:
                if item.id != int(form.product_item_id.data):
                    sum_amount += item.quantity * item.price
            if product.price < sum_amount:
                raise ValidationError(u'単価×販売単位が商品合計金額以内になるように入力してください')

    def validate_ticket_bundle_id(form, field):
        # 引取方法にコンビニ発券が含まれていたら必須
        if not field.data and form.product_id.data:
            product = Product.get(form.product_id.data)
            if product:
                for pdmp in product.sales_segment.payment_delivery_method_pairs:
                    if pdmp.delivery_method.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
                        raise ValidationError(u'券面構成を選択してください')
