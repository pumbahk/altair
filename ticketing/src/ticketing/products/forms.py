# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, DateTimeField, SelectField, IntegerField, SelectMultipleField
from wtforms.validators import Required, Length, NumberRange, EqualTo, Optional

from ticketing.products.models import PaymentMethod, DeliveryMethod

class ProductForm(Form):

    name = TextField(
        label=u'商品名',
        validators=[Required(u'入力してください')]
    )
    price = TextField(
        label=u'価格',
        validators=[Required(u'入力してください')]
    )
    sales_segment_id = TextField(
        validators=[Required()]
    )

class SalesSegmentForm(Form):

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
