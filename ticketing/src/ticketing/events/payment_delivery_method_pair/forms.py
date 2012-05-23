# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, DecimalField, IntegerField, SelectMultipleField, HiddenField
from wtforms.validators import Required, NumberRange, Regexp, Length, Optional, ValidationError

from ticketing.utils import Translations
from ticketing.products.models import PaymentMethod, DeliveryMethod
from ticketing.events.models import PaymentDeliveryMethodPair

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

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[]
    )
    sales_segment_id = HiddenField(
        validators=[]
    )
    transaction_fee = DecimalField(
        label=u'決済手数料',
        places=2,
        validators=[
            Required(u'入力してください'),
            NumberRange(min=0.0, max=100.0, message=u'%(min)sから%(max)sの間で設定してください')
        ]
    )
    delivery_fee = DecimalField(
        label=u'配送手数料',
        places=2,
        validators=[
            Required(u'入力してください'),
            NumberRange(min=0.0, max=100.0, message=u'%(min)sから%(max)sの間で設定してください')
        ]
    )
    discount = DecimalField(
        label=u'割引',
        places=2,
        validators=[
            Optional(),
            NumberRange(min=0.0, max=100.0, message=u'%(min)sから%(max)sの間で設定してください')
        ]
    )
    discount_unit = IntegerField(
        label=u'割引数',
        validators=[Optional()]
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

    def validate_payment_method_ids(form, field):
        if field.data is None or form.delivery_method_ids.data is None or form.id is None:
            return
        for payment_method_id in field.data:
            for delivery_method_id in form.delivery_method_ids.data:
                kwargs = {
                    'sales_segment_id':form.sales_segment_id.data,
                    'payment_method_id':payment_method_id,
                    'delivery_method_id':delivery_method_id,
                }
                pdmp = PaymentDeliveryMethodPair.filter_by(**kwargs).first()
                if pdmp and (form.id is None or pdmp.id != form.id.data):
                    raise ValidationError(u'既に設定済みの決済・配送方法の組み合せがあります')
