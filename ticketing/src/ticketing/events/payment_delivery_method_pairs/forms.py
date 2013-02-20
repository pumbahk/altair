# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, DecimalField, IntegerField, HiddenField
from wtforms.validators import NumberRange, Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import SalesSegment, PaymentMethod, DeliveryMethod, PaymentDeliveryMethodPair

class PaymentDeliveryMethodPairForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.payment_method_id.choices = [
                (pm.id, pm.name) for pm in PaymentMethod.filter_by_organization_id(kwargs['organization_id'])
            ]
            self.delivery_method_id.choices = [
                (dm.id, dm.name) for dm in DeliveryMethod.filter_by_organization_id(kwargs['organization_id'])
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[]
    )
    sales_segment_group_id = HiddenField(
        validators=[Optional()]
    )
    system_fee = DecimalField(
        label=u'システム利用料',
        places=2,
        default=0,
        validators=[Required()],
    )
    transaction_fee = DecimalField(
        label=u'決済手数料',
        places=2,
        default=0,
        validators=[Required()],
    )
    delivery_fee = DecimalField(
        label=u'引取手数料',
        places=2,
        default=0,
        validators=[Required()],
    )
    discount = DecimalField(
        label=u'割引額',
        places=2,
        default=0,
        validators=[Required()],
    )
    discount_unit = IntegerField(
        label=u'割引数',
        validators=[Optional()]
    )
    payment_method_id = SelectField(
        label=u'決済方法',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    delivery_method_id = SelectField(
        label=u'引取方法',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    unavailable_period_days = IntegerField(
        label=u'選択不可期間',
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ],
        default=0,
    )
    public = IntegerField(
        label=u'一般公開',
        default=0,
        widget=CheckboxInput(),
    )

    def validate_payment_method_id(form, field):
        if field.data is None or form.delivery_method_id.data is None or form.id is None:
            return
        kwargs = {
            'sales_segment_group_id':form.sales_segment_group_id.data,
            'payment_method_id':field.data,
            'delivery_method_id':form.delivery_method_id.data,
        }
        pdmp = PaymentDeliveryMethodPair.filter_by(**kwargs).first()
        if pdmp and (form.id is None or pdmp.id != form.id.data):
            raise ValidationError(u'既に設定済みの決済・引取方法の組み合せがあります')
