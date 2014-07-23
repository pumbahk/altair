# -*- coding: utf-8 -*-

from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurIntegerField, OurDecimalField, OurSelectField, OurBooleanField
from wtforms import HiddenField
from wtforms.validators import NumberRange, Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput

from altair.formhelpers import DateTimeField, Translations, Required, after1900
from altair.app.ticketing.core.models import SalesSegment, PaymentMethod, DeliveryMethod, PaymentDeliveryMethodPair, FeeTypeEnum
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID
from altair.saannotation import get_annotations_for

class PaymentDeliveryMethodPairForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        self.organization_id = kwargs.pop('organization_id', None)
        super(PaymentDeliveryMethodPairForm, self).__init__(formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[]
        )
    sales_segment_group_id = HiddenField(
        validators=[Optional()]
        )
    system_fee = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.system_fee)['label'],
        places=2,
        default=0,
        validators=[Required()]
        )
    system_fee_type = OurSelectField(
        label=get_annotations_for(PaymentDeliveryMethodPair.system_fee_type)['label'],
        default=FeeTypeEnum.Once.v[0],
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
        )
    special_fee_name = OurTextField(
        label=get_annotations_for(PaymentDeliveryMethodPair.special_fee_name)['label'],
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    special_fee = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.special_fee)['label'],
        places=2,
        default=0,
        validators=[Required()]
        )
    special_fee_type = OurSelectField(
        label=get_annotations_for(PaymentDeliveryMethodPair.special_fee_type)['label'],
        default=FeeTypeEnum.Once.v[0],
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
        )
    transaction_fee = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.transaction_fee)['label'],
        places=2,
        default=0,
        validators=[Required()]
        )
    delivery_fee_per_order = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.delivery_fee_per_order)['label'],
        places=2,
        default=0,
        validators=[Required()]
        )
    delivery_fee_per_principal_ticket = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.delivery_fee_per_principal_ticket)['label'],
        places=2,
        default=0,
        validators=[Required()]
        )
    delivery_fee_per_subticket = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.delivery_fee_per_subticket)['label'],
        places=2,
        default=0,
        validators=[Required()]
        )
    discount = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.discount)['label'],
        places=2,
        default=0,
        validators=[Required()]
        )
    discount_unit = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.discount_unit)['label'],
        validators=[Optional()]
        )

    def _payment_methods(field):
        return [
            (pm.id, pm.name)
            for pm in PaymentMethod.filter_by_organization_id(field.form.organization_id)
            ]
    payment_method_id = OurSelectField(
        label=get_annotations_for(PaymentDeliveryMethodPair.payment_method_id)['label'],
        validators=[Required(u'選択してください')],
        choices=_payment_methods,
        coerce=int
        )

    def _delivery_methods(field):
        return [
            (dm.id, dm.name)
            for dm in DeliveryMethod.filter_by_organization_id(field.form.organization_id)
            ]
    delivery_method_id = OurSelectField(
        label=get_annotations_for(PaymentDeliveryMethodPair.delivery_method_id)['label'],
        validators=[Required(u'選択してください')],
        choices=_delivery_methods,
        coerce=int
        )

    unavailable_period_days = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.unavailable_period_days)['label'],
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ],
        default=0,
    )

    public = OurBooleanField(
        label=get_annotations_for(PaymentDeliveryMethodPair.public)['label'],
        default=False,
        widget=CheckboxInput(),
        )

    payment_period_days = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.payment_period_days)['label'],
        validators=[
            Required(),
            NumberRange(min=1, max=364, message=u'有効な値を入力してください(1〜364)'),
            ],
        default=3
        )

    issuing_interval_days = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_interval_days)['label'],
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
            ],
        default=0
        )

    issuing_start_at = DateTimeField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_start_at)['label'],
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M'
        )

    issuing_end_at = DateTimeField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_end_at)['label'],
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M'
        )

    def validate_payment_method_id(form, field):
        if field.data is None or form.delivery_method_id.data is None:
            return
        kwargs = {
            'sales_segment_group_id':form.sales_segment_group_id.data,
            'payment_method_id':field.data,
            'delivery_method_id':form.delivery_method_id.data,
        }
        pdmp = PaymentDeliveryMethodPair.filter_by(**kwargs).first()
        if pdmp and (form.id.data is None or pdmp.id != form.id.data):
            raise ValidationError(u'既に設定済みの決済・引取方法の組み合せがあります')

    def validate_special_fee_name(form, field):
        if field.data is None:
            return
        elif form.special_fee.data > 0 and form.special_fee_name.data == "":
            raise ValidationError(u'特別手数料金額を設定する場合、特別手数料名も設定してください')

    def validate(form):
        status = super(type(form), form).validate()
        if status:
            # あんしん支払いサービスの場合は、決済手数料と特別手数料は設定不可
            payment_method = PaymentMethod.query.filter_by(id=form.payment_method_id.data).first()
            if payment_method and payment_method.payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID:
                error_message = u'楽天あんしん支払いサービスでは、決済手数料は設定できません'
                if form.transaction_fee.data > 0:
                    form.transaction_fee.errors.append(error_message)
                    status = False

            # コンビニ発券開始日時をチェックする
            if form.id.data:
                from altair.app.ticketing.events.sales_segments.forms import validate_issuing_start_at
                from altair.app.ticketing.events.sales_segments.exceptions import IssuingStartAtOutTermException
                pdmp = PaymentDeliveryMethodPair.query.filter_by(id=form.id.data).one()
                for ss in pdmp.sales_segments:
                    if not ss.performance:
                        continue
                    performance_end_on = ss.performance.end_on or ss.performance.start_on
                    end_at = ss.end_at
                    if ss.use_default_end_at:
                        end_at = ss.sales_segment_group.end_for_performance(ss.performance)
                    try:
                        validate_issuing_start_at(performance_end_on, end_at, pdmp, form.issuing_start_at.data, form.issuing_interval_days.data)
                    except IssuingStartAtOutTermException as e:
                        if form.issuing_start_at.data:
                            form.issuing_start_at.errors.append(e.message)
                        else:
                            form.issuing_interval_days.errors.append(e.message)
                        status = False
                        break
        return status
