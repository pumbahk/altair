# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, DecimalField, IntegerField, HiddenField
from wtforms.validators import NumberRange, Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput

from altair.formhelpers import DateTimeField, Translations, Required, after1900
from altair.app.ticketing.core.models import SalesSegment, PaymentMethod, DeliveryMethod, PaymentDeliveryMethodPair, FeeTypeEnum
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID


class PaymentDeliveryMethodPairForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(PaymentDeliveryMethodPairForm, self).__init__(formdata, obj, prefix, **kwargs)
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
    system_fee_type = SelectField(
        label=u'システム利用料計算単位',
        default=FeeTypeEnum.Once.v[0],
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
    )
    special_fee_name = TextField(
        label=u'特別手数料名',
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    special_fee = DecimalField(
        label=u'特別手数料',
        places=2,
        default=0,
        validators=[Required()],
    )
    special_fee_type = SelectField(
        label=u'特別手数料計算単位',
        default=FeeTypeEnum.Once.v[0],
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
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
    payment_period_days = IntegerField(
        label=u'コンビニ窓口での支払期限日数',
        validators=[
            Required(),
            NumberRange(min=1, max=364, message=u'有効な値を入力してください(1〜364)'),
        ],
        default=3,
    )
    issuing_interval_days = IntegerField(
        label=u'コンビニ窓口での発券が可能となるまでの日数',
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ],
        default=0,
    )
    issuing_start_at = DateTimeField(
        label=u'コンビニ発券開始日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    issuing_end_at = DateTimeField(
        label=u'コンビニ発券期限日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
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
                error_message = u'楽天あんしん支払いサービスでは、決済手数料および特別手数料は設定できません'
                if form.transaction_fee.data > 0:
                    form.transaction_fee.errors.append(error_message)
                    status = False
                # Todo: 特別手数料は設定可能にする
                if form.special_fee.data > 0:
                    form.special_fee.errors.append(error_message)
                    status = False

            # コンビニ発券開始日時をチェックする
            if form.id.data:
                from altair.app.ticketing.events.sales_segments.forms import validate_issuing_start_at
                from altair.app.ticketing.events.sales_segments.exceptions import IssuingStartAtOutTermException
                pdmp = PaymentDeliveryMethodPair.query.filter_by(id=form.id.data).one()
                for ss in pdmp.sales_segments:
                    performance_end_on = ss.performance.end_on or ss.performance.start_on
                    end_at = ss.sales_segment_group.end_at if ss.use_default_end_at else ss.end_at
                    try:
                        validate_issuing_start_at(performance_end_on, end_at, pdmp, form.issuing_start_at.data, form.issuing_interval_days.data)
                    except IssuingStartAtOutTermException as e:
                        if form.issuing_start_at.data:
                            form.issuing_start_at.errors.append(e.message)
                        else:
                            form.issuing_interval_days.errors.append(e.message)
                        status = False
        return status
