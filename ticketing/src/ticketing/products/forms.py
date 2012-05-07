# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, SelectMultipleField, HiddenField
from wtforms.validators import Required, Length, NumberRange, EqualTo, Optional, ValidationError

from ticketing.products.models import PaymentMethod, DeliveryMethod, PaymentDeliveryMethodPair, SalesSegment
from ticketing.utils import DateTimeField

class ProductForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.sales_segment_id.choices = [
                (sales_segment.id, sales_segment.name) for sales_segment in SalesSegment.get_by_organization_id(kwargs['organization_id'])
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

class SalesSegmentForm(Form):

    name = TextField(
        label=u'販売区分名',
        validators=[Required(u'入力してください')]
    )
    start_at = DateTimeField(
        label=u'販売開始日時',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M'
    )
    end_at = DateTimeField(
        label=u'販売終了日時',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M'
    )

class PaymentDeliveryMethodPairForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.payment_method_ids.choices = [
                (pm.id, pm.name) for pm in PaymentMethod.get_by_organization_id(kwargs['organization_id'])
            ]
            self.delivery_method_ids.choices = [
                (dm.id, dm.name) for dm in DeliveryMethod.get_by_organization_id(kwargs['organization_id'])
            ]

    transaction_fee = IntegerField(
        label=u'決済手数料',
        validators=[Required(u'入力してください')]
    )
    delivery_fee = IntegerField(
        label=u'配送手数料',
        validators=[Required(u'入力してください')]
    )
    discount = IntegerField(
        label=u'割引',
        validators=[Required(u'入力してください')]
    )
    discount_unit = IntegerField(
        label=u'割引数',
        validators=[Required(u'入力してください')]
    )
    discount_type = IntegerField(
        label=u'割引区分',
        validators=[Required(u'入力してください')]
    )
    payment_method_ids = SelectMultipleField(
        label=u'決済方法',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    delivery_method_ids = SelectMultipleField(
        label=u'配送方法',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    sales_segment_id = HiddenField(
        validators=[]
    )

    def validate_payment_method_ids(form, field):
        if field.data is None or form.delivery_method_ids.data is None:
            return
        for payment_method_id in field.data:
            for delivery_method_id in form.delivery_method_ids.data:
                if PaymentDeliveryMethodPair.find(form.sales_segment_id.data, payment_method_id, delivery_method_id):
                    raise ValidationError(u'既に設定済みの決済・配送方法の組み合せがあります')
