# -*- coding: utf-8 -*-

import logging
from decimal import Decimal
from datetime import datetime
import distutils.util

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField, BooleanField
from wtforms.validators import Length, NumberRange, EqualTo, Optional, ValidationError
from wtforms.widgets import CheckboxInput, TextArea
from sqlalchemy.sql import func
from sqlalchemy.orm import object_session

from altair.formhelpers import (
    Translations,
    Required,
    OurForm,
    )
from altair.formhelpers.fields import (
    BugFreeSelectField,
    OurTextField,
    OurSelectField,
    OurIntegerField,
    OurBooleanField,
    OurDecimalField,
    NullableTextField,
    OurPHPCompatibleSelectMultipleField,
    )
from altair.formhelpers.widgets import (
    CheckboxMultipleSelect,
    )
from altair.formhelpers.validators import JISX0208
from altair.app.ticketing.core.models import (
    SalesSegment, Product, ProductItem, StockHolder, StockType, TicketBundle,
    SalesSegmentGroup, Event, Ticket, TicketFormat, DeliveryMethod,
    )
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
from altair.app.ticketing.helpers import label_text_for
from .formhelpers import validate_ticket_bundle_and_sales_segment_set

logger = logging.getLogger(__name__)


class ProductFormMixin(object):

    id = HiddenField(
        label=label_text_for(Product.id),
        validators=[Optional()],
        )
    name = OurTextField(
        label=label_text_for(Product.name),
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            JISX0208,
            ]
        )
    price = OurDecimalField(
        label=label_text_for(Product.price),
        places=0,
        validators=[Required()]
        )
    seat_stock_type_id = OurSelectField(
        label=label_text_for(Product.seat_stock_type),
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
        )
    display_order = OurIntegerField(
        label=label_text_for(Product.display_order),
        default=1,
        hide_on_new=True,
        )
    public = OurBooleanField(
        label=u'一般公開',
        widget=CheckboxInput(),
        default=True
        )
    must_be_chosen = OurBooleanField(
        label=u'必須',
        widget=CheckboxInput(),
        default=False
        )
    description = NullableTextField(
        label=u'説明',
        hide_on_new=True,
        widget=TextArea()
        )
    sales_segment_id = OurSelectField(
        label=label_text_for(Product.sales_segment_id),
        choices=[],
        coerce=int
        )
    performance_id = HiddenField(
        validators=[Optional()]
        )
    min_product_quantity = OurIntegerField(
        label=u'商品購入下限数',
        hide_on_new=True,
        default=None,
        validators=[Optional()],
        )
    max_product_quantity = OurIntegerField(
        label=u'商品購入上限数',
        hide_on_new=True,
        default=None,
        validators=[Optional()],
        )

    applied_point_grant_settings = OurPHPCompatibleSelectMultipleField(
        label=u'適用されるポイント付与設定',
        choices=lambda field: [(pgs.id, pgs.name) for pgs in field._form.sales_segment.point_grant_settings] if field._form.sales_segment else [],
        hide_on_new=True,
        coerce=long,
        widget=CheckboxMultipleSelect(multiple=True)
        )
    all_sales_segment = OurBooleanField(
        label=u'同じ公演の全ての販売区分に追加',
        widget=CheckboxInput(),
        )

    def validate_min_product_quantity(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError(u'0以上の数値を入力してください')

    def validate_max_product_quantity(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError(u'0以上の数値を入力してください')

    def validate_product(self, *args, **kwargs):
        validity = True
        if self.id.data:
            # 販売期間内で公開済みの場合、またはこの商品が予約/抽選申込されている場合は
            # 価格、席種の変更は不可
            product = Product.query.filter_by(id=self.id.data).one()
            now = datetime.now()
            if (product.public and product.sales_segment.public and product.sales_segment.in_term(now) and product.performance.public)\
               or product.has_order() or product.has_lot_entry_products():
                error_message = u'既に販売中か予約および抽選申込がある為、変更できません'
                if self.price.data != product.price:
                    self.price.errors.append(error_message)
                    validity = False
                if long(self.seat_stock_type_id.data or 0) != product.seat_stock_type_id:
                    self.seat_stock_type_id.errors.append(error_message)
                    validity = False
        if self.min_product_quantity.data is not None and \
           self.max_product_quantity.data is not None and \
           self.min_product_quantity.data > self.max_product_quantity.data:
            errors = self.max_product_quantity.errors
            if errors is None:
                errors = []
            else:
                errors = list(errors)
            errors.append(u'最大商品購入数には最小商品購入数以上の値を指定してください')
            self.max_product_quantity.errors = errors
            validity = False
        return validity


class ProductItemFormMixin(object):

    product_id = HiddenField(
        validators=[Optional()]
        )
    product_item_id = HiddenField(
        validators=[Optional()]
        )
    product_item_quantity = OurIntegerField(
        label=u'販売単位 (席数・個数)',
        default='1',
        validators=[Optional()]
        )
    product_item_price = OurDecimalField(
        label=u'単価',
        places=0,
        hide_on_new=True,
        validators=[Optional()]
        )
    product_item_name = OurTextField(
        label=u'商品明細名',
        hide_on_new=True,
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'), 
            JISX0208,  
            ]
        )
    ticket_bundle_id = OurSelectField(
        label=u'券面構成',
        validators=[Required()],
        coerce=lambda v: None if not v else int(v)
        )

    stock_holder_id = OurSelectField(
        label=u'配券先',
        validators=[Optional()],
        choices=[],
        coerce=int
        )
    stock_type_id = OurSelectField(
        label=u'席種',
        validators=[Optional()],
        choices=[],
        coerce=int
        )

    def validate_stock_holder_id(form, field):
        # 既に予約があるならStockHolderの変更は不可
        if form.product_item_id.data:
            pi = ProductItem.query.filter_by(id=form.product_item_id.data).one()
            stock = pi.stock
            if stock.stock_holder_id != field.data:
                count = Order.query.join(OrderedProduct, OrderedProductItem, ProductItem).filter(ProductItem.id==pi.id).count()
                if count > 0:
                    raise ValidationError(u'既にこの商品明細への予約がある為、変更できません')

    def validate_product_item(self):
        status = True
        if self.product_item_id.data:
            # 販売期間内で公開済みの場合、またはこの商品が予約/抽選申込されている場合は
            # 価格(単価)、販売単位の変更は不可。商品価格、席種も不可であるが商品明細編集では項目なし。
            pi = ProductItem.query.filter_by(id=self.product_item_id.data).one()
            product = pi.product
            now = datetime.now()
            if (product.public and product.sales_segment.public and product.sales_segment.in_term(now) and product.performance.public)\
               or product.has_order() or product.has_lot_entry_products():
                error_message = u'既に販売中か予約および抽選申込がある為、変更できません'
                if self.product_item_price.data != pi.price:
                    self.product_item_price.errors.append(error_message)
                    status = False
                if self.product_item_quantity.data != pi.quantity:
                    self.product_item_quantity.errors.append(error_message)
                    status = False
        return status


class ProductAndProductItemForm(OurForm, ProductFormMixin, ProductItemFormMixin):

    def __init__(self, formdata=None, obj=None, prefix='', sales_segment=None, **kwargs):
        super(ProductAndProductItemForm, self).__init__(formdata, obj, prefix, **kwargs)
        if sales_segment is None:
            raise Exception('sales_segment must be non-None value')

        event = sales_segment.sales_segment_group.event
        self.sales_segment = sales_segment
        self.sales_segment_id.choices = [(sales_segment.id, sales_segment.name)]
        self.sales_segment_id.data = sales_segment.id
        self.seat_stock_type_id.choices = [
            (stock_type.id, stock_type.name) \
            for stock_type in StockType.filter(StockType.event_id == event.id).all()
            ]
        self.performance_id.data = sales_segment.performance.id

        stock_holders = StockHolder.get_own_stock_holders(event=event)
        self.stock_holder_id.choices = [(sh.id, sh.name) for sh in stock_holders]

        ticket_bundles = TicketBundle.query.filter_by(event_id=event.id).all()
        self.ticket_bundle_id.choices = [(u'', u'(なし)')] + [(tb.id, tb.name) for tb in ticket_bundles]
        if self.name.data and not self.product_item_name.data:
            self.product_item_name.data = self.name.data
        if self.price.data and not self.product_item_price.data:
            self.product_item_price.data = self.price.data / Decimal(self.product_item_quantity.data)
        if not self.product_item_price.data:
            # 0円商品
            self.product_item_price.data = 0

    def _get_translations(self):
        return Translations()

    ticket_bundle_id = OurSelectField(
        label=u'券面構成',
        validators=[Optional()],
        coerce=lambda v: None if not v else int(v)
        )

    @classmethod
    def from_model(cls, product, product_item=None):
        product_item_params = dict()
        if product_item:
            product_item_params = dict(
                product_item_id=product_item.id,
                product_item_quantity=product_item.quantity,
                product_item_price=product_item.price,
                product_item_name=product_item.name,
                ticket_bundle_id=product_item.ticket_bundle_id,
                stock_holder_id=product_item.stock.stock_holder_id,
                stock_type_id=product_item.stock.stock_type_id,
                )
        form = cls(
            id=product.id,
            name=product.name,
            price=product.price,
            seat_stock_type_id=product.seat_stock_type_id,
            display_order=product.display_order,
            public=product.public,
            must_be_chosen=product.must_be_chosen,
            description=product.description,
            sales_segment_id=product.sales_segment_id,
            performance_id=product.performance_id,
            min_product_quantity=product.min_product_quantity,
            max_product_quantity=product.max_product_quantity,
            sales_segment=product.sales_segment,
            applied_point_grant_settings=[pgs.id for pgs in product.point_grant_settings],
            all_sales_sagment=0,
            **product_item_params
            )
        return form

    def validate_seat_stock_type_id(form, field):
        if field.data and form.id.data and not form.product_item_id.data:
            stock_type = StockType.get(field.data)
            if stock_type.is_seat:
                # 商品の席種と在庫の席種は同一であること
                product = Product.get(form.id.data)
                for product_item in product.items:
                    st = product_item.stock.stock_type
                    if st.is_seat and st.id != field.data:
                        raise ValidationError(u'商品の席種と異なる在庫を登録することはできません')

    def validate(self, *args, **kwargs):
        status = super(ProductAndProductItemForm, self).validate(*args, **kwargs)
        if status:
            status = self.validate_product(*args, **kwargs)
        if status:
            status = self.validate_product_item(*args, **kwargs)
            self.price.errors += self.product_item_price.errors
        if not self.id.data or self.product_item_id.data:
            error_message = u'入力してください'
            required_fields = [
                self.stock_holder_id,
                self.product_item_quantity,
                self.ticket_bundle_id
                ]
            for field in required_fields:
                if not field.data:
                    field.errors.append(error_message)
                    status = False
        return status


class ProductItemForm(OurForm, ProductItemFormMixin):

    def __init__(self, formdata=None, obj=None, prefix='', product=None, **kwargs):
        super(ProductItemForm, self).__init__(formdata, obj, prefix, **kwargs)
        if product is None:
            raise Exception('product must be non-None value')

        event = product.sales_segment.sales_segment_group.event
        self.sales_segment = product.sales_segment
        self.product = product
        self.product_id.data = product.id

        stock_holders = StockHolder.get_own_stock_holders(event=event)
        self.stock_holder_id.choices = [(sh.id, sh.name) for sh in stock_holders]

        stock_types = StockType.query.filter_by(event_id=event.id).all()
        self.stock_type_id.choices = [(st.id, st.name) for st in stock_types]

        ticket_bundles = TicketBundle.filter_by(event_id=event.id)
        self.ticket_bundle_id.choices = [(u'', u'(なし)')] + [(tb.id, tb.name) for tb in ticket_bundles]

    def _get_translations(self):
        return Translations()

    def validate_ticket_bundle_id(self, field):
        ticket_bundle = TicketBundle.filter_by(id=field.data).one()
        validate_ticket_bundle_and_sales_segment_set(ticket_bundle=ticket_bundle, sales_segment=self.sales_segment)

    def validate_stock_type_id(form, field):
        if not field.data:
            raise ValidationError(u'席種を選択してください')
        elif form.product_id.data:
            stock_type = StockType.get(field.data)
            if stock_type.is_seat:
                # 商品の席種と在庫の席種は同一であること
                product = Product.get(form.product_id.data)
                if stock_type.id != product.seat_stock_type_id:
                    raise ValidationError(u'商品の席種と異なる在庫を登録することはできません')

    def validate(self, *args, **kwargs):
        status = super(ProductItemForm, self).validate(*args, **kwargs)
        if status:
            status = self.validate_product_item(*args, **kwargs)

        error_message = u'入力してください'
        required_fields = [
            self.product_id,
            self.product_item_quantity,
            self.product_item_name,
            self.ticket_bundle_id,
            self.stock_holder_id,
            self.stock_type_id
            ]
        for field in required_fields:
            if not field.data:
                field.errors.append(error_message)
                status = False
        return status

class ProductCopyForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', copy_sales_segments=None, **kwargs):
        super(ProductCopyForm, self).__init__(formdata, obj, prefix, **kwargs)
        if copy_sales_segments:
            self.copy_sales_segments.choices = [
                (sales_segment.id, sales_segment.sales_segment_group.name)
                for sales_segment in copy_sales_segments
                ]

    copy_sales_segments = OurPHPCompatibleSelectMultipleField(
        label=u'コピー先を選択してください',
        validators=[Required()],
        choices=[],
    )

class ProductAndProductItemAPIForm(OurForm, ProductFormMixin, ProductItemFormMixin):

    def __init__(self, formdata=None, obj=None, prefix='', sales_segment=None, **kwargs):
        super(ProductAndProductItemAPIForm, self).__init__(formdata, obj, prefix, **kwargs)
        if sales_segment is None:
            raise Exception('sales_segment must be non-None value')

        self.sales_segment = sales_segment
        event = sales_segment.sales_segment_group.event
        stock_holders = StockHolder.get_own_stock_holders(event=event)
        self.stock_holder_id.choices = [(sh.id, sh.name) for sh in stock_holders]

        stock_types = StockType.query.filter_by(event_id=event.id).all()
        self.stock_type_id.choices = [(st.id, st.name) for st in stock_types]

        ticket_bundles = TicketBundle.filter_by(event_id=event.id)
        self.ticket_bundle_id.choices = [(u'', u'(なし)')] + [(tb.id, tb.name) for tb in ticket_bundles]

        if formdata:
            self.id.data = formdata['product_id']
            self.seat_stock_type_id.data = formdata['stock_type_id']
            try:
                self.public.data = bool(distutils.util.strtobool(formdata['public']))
            except Exception as e:
                self.public.data = True
            try:
                self.must_be_chosen.data = bool(distutils.util.strtobool(formdata['must_be_chosen']))
            except Exception as e:
                self.must_be_chosen.data = False
            try:
                self.is_leaf.data = bool(distutils.util.strtobool(formdata['is_leaf']))
            except Exception as e:
                self.is_leaf.data = False

    def _get_translations(self):
        return Translations()

    public = OurBooleanField(
        default=True
        )
    must_be_chosen = OurBooleanField(
        default=False
    )
    name = OurTextField(
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
            JISX0208,
            ]
        )
    price = OurDecimalField(
        places=0,
        validators=[Optional()]
        )
    display_order = OurIntegerField(
        default=1,
        hide_on_new=True,
        validators=[Optional()]
        )
    performance_id = HiddenField(
        validators=[Optional()]
        )
    is_leaf = OurBooleanField(
        default=False
        )

    id = HiddenField(
        validators=[Optional()],
        )
    seat_stock_type_id = HiddenField(
        validators=[Optional()],
        )
    description = HiddenField(
        validators=[Optional()],
        )
    sales_segment_id = HiddenField(
        validators=[Optional()],
        )
    min_product_quantity = HiddenField(
        validators=[Optional()],
        )
    max_product_quantity = HiddenField(
        validators=[Optional()],
        )
    applied_point_grant_settings = HiddenField(
        validators=[Optional()],
        )
    all_sales_segment = HiddenField(
        validators=[Optional()],
        )

    def validate_stock_type_id(form, field):
        if not field.data:
            raise ValidationError(u'席種を選択してください')
        elif form.is_leaf.data and form.product_id.data:
            stock_type = StockType.get(field.data)
            if stock_type.is_seat:
                # 商品の席種と在庫の席種は同一であること
                product = Product.get(form.product_id.data)
                if stock_type.id != product.seat_stock_type_id:
                    raise ValidationError(u'商品の席種と異なる在庫を登録することはできません')

    def validate_ticket_bundle_id(self, field):
        ticket_bundle = TicketBundle.filter_by(id=field.data).one()
        validate_ticket_bundle_and_sales_segment_set(ticket_bundle=ticket_bundle, sales_segment=self.sales_segment)

    def validate(self, *args, **kwargs):
        status = super(ProductAndProductItemAPIForm, self).validate(*args, **kwargs)
        if status:
            status = self.validate_product(*args, **kwargs)
        if status:
            status = self.validate_product_item(*args, **kwargs)

        error_message = u'入力してください'
        required_fields = [
            self.product_item_quantity,
            self.product_item_name,
            self.ticket_bundle_id,
            self.stock_holder_id,
            ]
        if not self.is_leaf.data:
            required_fields += [
                self.name,
                self.display_order,
                ]
        for field in required_fields:
            if not field.data:
                field.errors.append(error_message)
                status = False
        return status


class PreviewImageDownloadForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        self.sales_segment = kwargs.pop('sales_segment')
        super(PreviewImageDownloadForm, self).__init__(formdata, obj, prefix, **kwargs)

    def delivery_methods(field):
        return set(
            (pdmp.delivery_method_id, pdmp.delivery_method.name)
            for pdmp in field._form.sales_segment.payment_delivery_method_pairs)

    def ticket_formats(field):
        tickets = object_session(field._form.sales_segment) \
            .query(TicketFormat.id, TicketFormat.name) \
            .join(Ticket.ticket_format) \
            .join(TicketFormat.delivery_methods) \
            .join(Ticket.event) \
            .join(Event.sales_segment_groups) \
            .join(SalesSegmentGroup.sales_segments) \
            .filter(SalesSegment.id == field._form.sales_segment.id) \
            .group_by(TicketFormat.id)
        return tickets
 
    delivery_method_id = OurSelectField(
        label=u'配送方法',
        validators=[Required(u'選択してください')],
        choices=delivery_methods,
        coerce=int,
    )

    ticket_format_id = OurSelectField(
        label=u'チケット様式',
        validators=[Required(u'選択してください')],
        choices=ticket_formats,
        coerce=int,
    )

