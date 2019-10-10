# -*- coding: utf-8 -*-

import re
import json
from collections import OrderedDict

from altair.formhelpers.form import OurForm
from altair.formhelpers.validators import SwitchOptionalBase
from altair.formhelpers.fields import OurTextField, OurIntegerField, OurDecimalField, OurSelectField, OurBooleanField, \
    OurField, TimeField
from altair.formhelpers.widgets.datetime import OurTimeWidget
from wtforms import HiddenField
from wtforms.validators import NumberRange, Regexp, Length, Optional, ValidationError, InputRequired
from wtforms.widgets import Input, CheckboxInput, RadioInput
from wtforms.widgets.core import HTMLString, html_params
from wtforms.fields.core import _unset_value
from cgi import escape
from .pdmp_validation import validate_checkout_payment_and_fees, validate_payment_delivery_combination, \
    validate_issuing_start_time

from altair.formhelpers import DateTimeField, Translations, Required, after1900
from altair.app.ticketing.core.models import (
    PaymentMethod,
    DeliveryMethod,
    PaymentDeliveryMethodPair,
    FeeTypeEnum,
    DateCalculationBase,
)

from altair.saannotation import get_annotations_for

from altair.app.ticketing.payments.api import get_payment_delivery_methods
from altair.app.ticketing.payments.plugins import (
    CHECKOUT_PAYMENT_PLUGIN_ID,
    MULTICHECKOUT_PAYMENT_PLUGIN_ID,
    SHIPPING_DELIVERY_PLUGIN_ID
)

from markupsafe import Markup


def _get_msg(target):
    msg = u'手数料は「予約ごと」または「{}」どちらか一方を入力してください。<br/>'
    msg += u'取得しない手数料は「0」を入力してください。'
    msg = Markup(msg.format(target))
    return msg


def required_when_absolute(field_name):  # Optional validation works when date is on relative basis
    return [SwitchOptionalBase(lambda form, _: form[field_name].data != DateCalculationBase.Absolute.v), Required()]


def required_when_relative_time(field_name):  # Optional validation works when date is on absolute basis
    return [
        SwitchOptionalBase(lambda form, _: form[field_name].data == DateCalculationBase.Absolute.v),
        InputRequired(u'正しく入力してください')
    ]


class PDMPPeriodField(OurField):
    def __init__(self, *args, **kwargs):
        inner_field = kwargs.pop('inner_field')
        calculation_base = kwargs.pop('calculation_base')
        base_types = kwargs.pop('base_types')
        _choices = kwargs.pop('choices')
        name_builder = kwargs.pop('name_builder', None)
        prefix = kwargs.pop('prefix', None)
        super(PDMPPeriodField, self).__init__(*args, **kwargs)
        kwargs = {}
        if prefix is not None:
            kwargs['prefix'] = prefix
        self.inner_field = inner_field.bind(self.form, self.name, name_builder=name_builder, **kwargs)
        self.calculation_base = self.form[calculation_base]
        self.base_types = base_types
        choices = []
        lhs_is_select_field = None
        for k, entry in _choices:
            lhs, rhs = [x.strip() for x in entry['template'].split(u'{widget}', 2)]
            option_text = None
            g = re.match(ur'<([^>]*)>', lhs)
            if g is not None:
                if lhs_is_select_field is None:
                    lhs_is_select_field = True
                else:
                    if not lhs_is_select_field:
                        raise ValueError('cannot mix left-hand-side and right-hand-side select fields')
                lhs = None
                option_text = g.group(1)

            g = re.match(ur'<([^>]*)>', rhs)
            if g is not None:
                if lhs_is_select_field is None:
                    lhs_is_select_field = False
                else:
                    if lhs_is_select_field:
                        raise ValueError('cannot mix left-hand-side and right-hand-side select fields')
                rhs = None
                option_text = g.group(1)
            if option_text is None:
                raise ValueError('no option text could be retrieved')
            choices.append((k, dict(lhs=lhs, rhs=rhs, option_text=option_text)))
        self.choices = choices
        self.lhs_is_select_field = lhs_is_select_field
        self.base_type_key = '%s-1' % self.name
        self.subcategory_key = '%s-2' % self.name
        self.base_type_data = None
        self.subcategory_data = None

    def validate(self, form, extra_validators=()):
        if self.base_type_data == 'relative':
            retval = self.inner_field.validate(form, extra_validators)
            self.errors = self.inner_field.errors
            return retval
        else:
            return True

    def process(self, formdata, data=_unset_value):
        self.process_errors = []
        if data is _unset_value:
            try:
                data = self.inner_field.default()
            except TypeError:
                data = self.inner_field.default

        self.object_data = data
        self.inner_field.object_data = data

        try:
            self.inner_field.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if self.calculation_base.data is not None:
            calculation_base_value = self.calculation_base.data
            if calculation_base_value == DateCalculationBase.Absolute.v:
                base_type_data = 'absolute'
                subcategory_data = None
            else:
                base_type_data = 'relative'
                subcategory_data = calculation_base_value

        if formdata is not None:
            if self.base_type_key in formdata:
                base_type_raw_data = formdata.getlist(self.base_type_key)
            else:
                base_type_raw_data = []

            if self.subcategory_key in formdata:
                subcategory_raw_data = formdata.getlist(self.subcategory_key)
            else:
                subcategory_raw_data = []

            base_type_data = None
            try:
                if len(base_type_raw_data) >= 1:
                    base_type_data = base_type_raw_data[0]
            except ValueError as e:
                self.process_errors.append(e.args[0])

            subcategory_data = None
            try:
                if len(subcategory_raw_data) >= 1:
                    subcategory_data = int(subcategory_raw_data[0])
            except ValueError as e:
                self.process_errors.append(e.args[0])

            if base_type_data == 'absolute':
                calculation_base_value = DateCalculationBase.Absolute.v
                self.inner_field.data = None
            elif base_type_data == 'relative':
                if not any(subcategory_data == k for k, _ in self.choices):
                    self.calculation_base.process_errors.append(self.gettext('Not a valid choice'))
                calculation_base_value = subcategory_data
                try:
                    if self.name in formdata:
                        raw_data = formdata.getlist(self.name)
                    else:
                        raw_data = []
                    self.inner_field.process_formdata(raw_data)
                except ValueError as e:
                    self.process_errors.append(e.args[0])
            else:
                self.calculation_base.process_errors.append(self.gettext('Not a valid choice'))

        if base_type_data == 'relative':
            for filter in self.inner_field.filters:
                try:
                    self.inner_field.data = filter(self.inner_field.data)
                except ValueError as e:
                    self.process_errors.append(e.args[0])

        self.data = self.inner_field.data

        self.base_type_data = base_type_data
        self.subcategory_data = subcategory_data
        self.calculation_base.data = calculation_base_value

    def widget(self, _, **kwargs):
        html = []
        subcategory_class = kwargs.pop('subcategory_class', u'')
        if not self.lhs_is_select_field:
            html.append(u'<span class="lhs-content">%s</span>' % escape(self.choices[0][1]['lhs']))
            html.append(self.inner_field())
        html.append(u'<select %s>' % html_params(
            id=self.subcategory_key,
            name=self.subcategory_key,
            class_=subcategory_class
        ))
        for k, choice in self.choices:
            html.append(u'<option value="%s"%s>%s</option>' % (
                escape(unicode(k)),
                u' selected="selected"' if self.subcategory_data == k else u'',
                escape(choice['option_text']),
            ))
        html.append(u'</select>')
        if self.lhs_is_select_field:
            html.append(self.inner_field(**kwargs))
            html.append(u'<span class="rhs-content">%s</span>' % escape(self.choices[0][1]['rhs']))
        return HTMLString(u''.join(html))

    def base_type_radio(self, type):
        option_text = self.base_types[type]
        html = [
            u'<input type="radio" id="%s" name="%s" value="%s" %s/>' % (
                escape('%s-%s' % (self.base_type_key, type)),
                escape(self.base_type_key),
                escape(type),
                u'checked="checked" ' if self.base_type_data == type else u'',
            ),
            escape(option_text),
        ]
        return HTMLString(u''.join(html))


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
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )
    system_fee_type = OurSelectField(
        label=get_annotations_for(PaymentDeliveryMethodPair.system_fee_type)['label'],
        default=FeeTypeEnum.PerUnit.v[1],
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
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )
    special_fee_type = OurSelectField(
        label=get_annotations_for(PaymentDeliveryMethodPair.special_fee_type)['label'],
        default=FeeTypeEnum.PerUnit.v[1],
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
    )
    transaction_fee = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.transaction_fee)['label'],
        places=2,
        default=0,
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )
    delivery_fee_per_order = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.delivery_fee_per_order)['label'],
        places=2,
        default=0,
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )
    delivery_fee_per_principal_ticket = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.delivery_fee_per_principal_ticket)['label'],
        places=2,
        default=0,
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )
    delivery_fee_per_subticket = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.delivery_fee_per_subticket)['label'],
        places=2,
        default=0,
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )
    discount = OurDecimalField(
        label=get_annotations_for(PaymentDeliveryMethodPair.discount)['label'],
        places=2,
        default=0,
        validators=[
            Required(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )
    discount_unit = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.discount_unit)['label'],
        validators=[
            Optional(),
            NumberRange(min=0, message=u'有効な値を入力してください'),
        ]
    )

    def _payment_methods(field):
        return [
            (pm.id, pm.name)
            for pm in PaymentMethod.filter_by_organization_id(field._form.organization_id)
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
            for dm in DeliveryMethod.filter_by_organization_id(field._form.organization_id)
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
        default=True,
        widget=CheckboxInput(),
    )

    _date_calculation_base_types = {
        'absolute': u'日時指定',
        'relative': u'相対指定',
    }

    _date_calculation_bases = [
        (
            DateCalculationBase.OrderDate.v,
            dict(
                template=u'<予約日から> {widget} 日後'
            )
        ),
        (
            DateCalculationBase.OrderDateTime.v,
            dict(
                template=u'<予約日時から> {widget} 日後'
            )
        ),
        (
            DateCalculationBase.PerformanceStartDate.v,
            dict(
                template=u'<公演開始から> {widget} 日後'
            )
        ),
        (
            DateCalculationBase.PerformanceEndDate.v,
            dict(
                template=u'<公演終了から> {widget} 日後'
            )
        ),
        (
            DateCalculationBase.SalesStartDate.v,
            dict(
                template=u'<販売開始から> {widget} 日後'
            )
        ),
        (
            DateCalculationBase.SalesEndDate.v,
            dict(
                template=u'<販売終了から> {widget} 日後'
            )
        ),
    ]

    payment_due_day_calculation_base = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.payment_due_day_calculation_base)['label'],
        default=DateCalculationBase.OrderDate.v,
        widget=Input(input_type='hidden'),
    )

    payment_period_days = PDMPPeriodField(
        label=get_annotations_for(PaymentDeliveryMethodPair.payment_period_days)['label'],
        calculation_base='payment_due_day_calculation_base',
        base_types=_date_calculation_base_types,
        choices=_date_calculation_bases,
        inner_field=OurIntegerField(
            validators=[
                Required(),
                NumberRange(max=364, message=u'有効な値を入力してください(〜364)'),
            ],
            default=3
        )
    )

    payment_period_time = TimeField(
        validators=required_when_relative_time('payment_due_day_calculation_base'),
        widget=OurTimeWidget(omit_second=True),
    )

    payment_due_at = DateTimeField(
        label=get_annotations_for(PaymentDeliveryMethodPair.payment_due_at)['label'],
        validators=required_when_absolute('payment_due_day_calculation_base') + [after1900],
        format='%Y-%m-%d %H:%M'
    )

    issuing_start_day_calculation_base = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_start_day_calculation_base)['label'],
        default=DateCalculationBase.OrderDate.v,
        widget=Input(input_type='hidden'),
    )

    issuing_interval_days = PDMPPeriodField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_interval_days)['label'],
        calculation_base='issuing_start_day_calculation_base',
        base_types=_date_calculation_base_types,
        choices=_date_calculation_bases,
        inner_field=OurIntegerField(
            validators=[
                Required(),
            ],
            default=0
        )
    )

    issuing_interval_time = TimeField(
        validators=required_when_relative_time('issuing_start_day_calculation_base'),
        widget=OurTimeWidget(omit_second=True),
    )

    issuing_start_at = DateTimeField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_start_at)['label'],
        validators=required_when_absolute('issuing_start_day_calculation_base') + [after1900],
        format='%Y-%m-%d %H:%M'
    )

    issuing_end_day_calculation_base = OurIntegerField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_end_day_calculation_base)['label'],
        default=DateCalculationBase.OrderDate.v,
        widget=Input(input_type='hidden'),
    )

    issuing_end_in_days = PDMPPeriodField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_end_in_days)['label'],
        calculation_base='issuing_end_day_calculation_base',
        base_types=_date_calculation_base_types,
        choices=_date_calculation_bases,
        inner_field=OurIntegerField(
            validators=[
                Required(),
                NumberRange(max=364, message=u'有効な値を入力してください'),
            ],
            default=364
        )
    )

    issuing_end_in_time = TimeField(
        validators=required_when_relative_time('issuing_end_day_calculation_base'),
        widget=OurTimeWidget(omit_second=True),
    )

    issuing_end_at = DateTimeField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_end_at)['label'],
        validators=required_when_absolute('issuing_end_day_calculation_base') + [after1900],
        format='%Y-%m-%d %H:%M'
    )

    def validate_payment_due_at(form,field):
        if field.data > form.issuing_end_at.data:
            raise ValidationError(u'支払期限日時を発券期限日時以前に設定してください。');

    def validate_payment_method_id(form, field):
        if field.data is None or form.delivery_method_id.data is None:
            return
        kwargs = {
            'sales_segment_group_id': form.sales_segment_group_id.data,
            'payment_method_id': field.data,
            'delivery_method_id': form.delivery_method_id.data,
        }
        pdmp = PaymentDeliveryMethodPair.filter_by(**kwargs).first()
        if pdmp and (form.id.data is None or pdmp.id != form.id.data):
            raise ValidationError(u'既に設定済みの決済・引取方法の組み合せがあります')

    def validate_special_fee_name(form, field):
        if field.data is None:
            return
        elif form.special_fee.data > 0 and form.special_fee_name.data == "":
            raise ValidationError(u'特別手数料金額を設定する場合、特別手数料名も設定してください')

    def validate_delivery_fee_per_order(form, field):
        if form.data['delivery_fee_per_principal_ticket'] or form.data['delivery_fee_per_subticket']:
            if form.data[field.name]:
                if form.data['delivery_fee_per_principal_ticket'] and form.data['delivery_fee_per_subticket']:
                    raise ValidationError(_get_msg(u'主券・副券'))
                elif form.data['delivery_fee_per_principal_ticket']:
                    raise ValidationError(_get_msg(u'主券'))
                elif form.data['delivery_fee_per_subticket']:
                    raise ValidationError(_get_msg(u'副券'))

    def validate_delivery_fee_per_principal_ticket(form, field):
        if form.data['delivery_fee_per_order'] and form.data[field.name]:
            raise ValidationError(_get_msg(u'主券'))

    def validate_delivery_fee_per_subticket(form, field):
        if form.data['delivery_fee_per_order'] and form.data[field.name]:
            raise ValidationError(_get_msg(u'副券'))

    @property
    def relative_date_fields(self):
        return OrderedDict([
            (self.payment_period_days, self.payment_period_time),
            (self.issuing_interval_days, self.issuing_interval_time),
            (self.issuing_end_in_days, self.issuing_end_in_time)
        ])

    def _process_relative_date(self, formdata):
        def _set_time(prefix, hour, minute):
            formdata[prefix + 'hour'] = str(hour)
            formdata[prefix + 'minute'] = str(minute)

        payment_method, delivery_method = \
            get_payment_delivery_methods(formdata.get(self.payment_method_id.name),
                                         formdata.get(self.delivery_method_id.name))

        for pdmp_field, time_field in self.relative_date_fields.iteritems():
            # 相対日のフィールドは PDMPPeriodField オブジェクトです。
            # base_type_key は相対 (relative) か絶対 (absolute) かの値がセットされるキー名
            # subcategory_key は入力された日数の値がセットされるキー名
            is_relative = formdata.get(pdmp_field.base_type_key) == 'relative'
            try:
                date_calc_base = int(formdata.get(pdmp_field.subcategory_key))
            except (TypeError, ValueError):
                continue
            if is_relative and date_calc_base == DateCalculationBase.OrderDateTime.v:
                # 相対指定の「予約日時から」は時間指定できないので、00:00 にセットする
                _set_time(time_field.name_prefix, 0, 0)
            elif time_field.name == self.payment_period_time.name and not payment_method.pay_at_store():
                # 支払期日はコンビニ支払以外では不要なので相対指定時刻は 23:59 にセットする
                _set_time(self.payment_period_time.name_prefix, 23, 59)
            elif time_field.name == self.issuing_interval_time.name and not delivery_method.regard_issuing_date:
                # コンビニ発券開始日時はコンビニ・QR・イベントゲート引取以外では不要なので相対指定時刻は 00:00 にセットする
                _set_time(self.issuing_interval_time.name_prefix, 0, 0)
            elif time_field.name == self.issuing_end_in_time.name and not delivery_method.regard_issuing_date:
                # コンビニ発券期限日時はコンビニ・QR・イベントゲート引取以外では不要なので相対指定時刻は 23:59 にセットする
                _set_time(self.issuing_end_in_time.name_prefix, 23, 59)

    def process(self, formdata=None, obj=None, _data=None, **kwargs):
        if formdata:
            self._process_relative_date(formdata)
        super(PaymentDeliveryMethodPairForm, self).process(formdata, obj, _data, **kwargs)

    def validate(form, pdmp = None, sales_segments = None):
        status = super(type(form), form).validate()
        status = validate_payment_delivery_combination(status, form) and \
                 validate_checkout_payment_and_fees(status, form) and \
                 validate_issuing_start_time(status=status,
                                             form=form,
                                             pdmp=pdmp,
                                             sales_segments=sales_segments)
        return status

    def basic_default_values(self, payment_method, delivery_method):
        """相対指定のベースとなるデフォルト値を返却します"""
        # コンビニ支払以外は相対指定は不要
        payment_method_read_only = not payment_method.pay_at_store()
        # コンビニ・QR・イベントゲート引取以外は相対指定は不要
        delivery_method_read_only = not delivery_method.regard_issuing_date
        return dict(
            # 選択不可期間
            unavailable_period_days=0,
            # 支払期日
            payment_period_days_two_readonly=payment_method_read_only,            # 相対指定の計算基準タイプ選択不可
            payment_period_days_selected_choice=DateCalculationBase.OrderDate.v,  # 相対指定の計算基準タイプのデフォルト値
            payment_period_days_readonly=payment_method_read_only,                # 相対指定の日数入力不可
            payment_period_time_readonly=payment_method_read_only,                # 相対指定の時刻入力不可
            payment_period_days=3,                                                # 日数のデフォルト値
            payment_period_time_hour=23,                                          # 時のデフォルト値
            payment_period_time_minute=59,                                        # 分のデフォルト値
            # コンビニ発券開始日時
            issuing_interval_days_two_readonly=delivery_method_read_only,           # 相対指定の計算基準タイプ選択不可
            issuing_interval_days_selected_choice=DateCalculationBase.OrderDate.v,  # 相対指定の計算基準タイプのデフォルト値
            issuing_interval_days_readonly=delivery_method_read_only,               # 相対指定の日数入力不可
            issuing_interval_time_readonly=delivery_method_read_only,               # 相対指定の時刻入力不可
            issuing_interval_days=0,                                                # 日数のデフォルト値
            issuing_interval_time_hour=0,                                           # 時のデフォルト値
            issuing_interval_time_minute=0,                                         # 分のデフォルト値
            # コンビニ発券期限日時
            issuing_end_in_days_two_readonly=delivery_method_read_only,           # 相対指定の計算基準タイプ選択不可
            issuing_end_in_days_selected_choice=DateCalculationBase.OrderDate.v,  # 相対指定の計算基準タイプのデフォルト値
            issuing_end_in_days_readonly=delivery_method_read_only,               # 相対指定の日数入力不可
            issuing_end_in_time_readonly=delivery_method_read_only,               # 相対指定の時刻入力不可
            issuing_end_in_days=364,                                              # 日数のデフォルト値
            issuing_end_in_time_hour=23,                                          # 時のデフォルト値
            issuing_end_in_time_minute=59,                                        # 分のデフォルト値
        )

    def default_values_for_pdmp(self, payment_method_id, delivery_method_id):
        """
        相対指定のデフォルト値を返却します。
        See https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId=771004059
        """
        # 選択された決済方法と引取方法を取得
        payment_method, delivery_method = get_payment_delivery_methods(payment_method_id, delivery_method_id)
        # 画面上表示の共通デフォルト値を設定
        default_form_state = self.basic_default_values(payment_method, delivery_method)
        """
        Formのデフォルト値から変更する値のみを以下で更新する
        """
        # 決済方法：コンビニ
        if payment_method.pay_at_store():
            # 引取方法：コンビニ or QRコード・イベントゲート
            if delivery_method.regard_issuing_date:
                # 選択不可期間
                default_form_state['unavailable_period_days'] = 4
                # コンビニ発券期限日時
                default_form_state['issuing_end_in_days_selected_choice'] = DateCalculationBase.PerformanceEndDate.v
                default_form_state['issuing_end_in_days'] = 30
            # 引取方法：窓口受取・WEbクーポン
            if delivery_method.has_reserve_number:
                # 選択不可期間
                default_form_state['unavailable_period_days'] = 4
            # 引取方法：配送
            if delivery_method.delivery_plugin_id == SHIPPING_DELIVERY_PLUGIN_ID:
                # 選択不可期間
                default_form_state['unavailable_period_days'] = 17

        # 決済方法：楽天ペイ・クレジットカード
        if payment_method.payment_plugin_id in (CHECKOUT_PAYMENT_PLUGIN_ID, MULTICHECKOUT_PAYMENT_PLUGIN_ID):
            # 引取方法：配送
            if delivery_method.delivery_plugin_id == SHIPPING_DELIVERY_PLUGIN_ID:
                # 選択不可期間
                default_form_state['unavailable_period_days'] = 14
            # 引取方法：コンビニ・QRコード・イベントゲート
            if delivery_method.regard_issuing_date:
                # コンビニ発券開始日時
                default_form_state['issuing_interval_days_selected_choice'] = DateCalculationBase.OrderDateTime.v
                default_form_state['issuing_interval_days'] = 1
                # コンビニ発券期限日時
                default_form_state['issuing_end_in_days_selected_choice'] = DateCalculationBase.PerformanceEndDate.v
                default_form_state['issuing_end_in_days'] = 30

        # 決済方法：窓口支払・無料
        if payment_method.cash_on_reservation():
            # 引取方法：コンビニ
            if delivery_method.deliver_at_store():
                # 選択不可期間
                default_form_state['unavailable_period_days'] = 4
            # 引取方法：コンビニ・QRコード・イベントゲート
            if delivery_method.regard_issuing_date:
                # コンビニ発券期限日時
                default_form_state['issuing_end_in_days_selected_choice'] = DateCalculationBase.PerformanceEndDate.v
                default_form_state['issuing_end_in_days'] = 30
            # 引取方法：配送
            if delivery_method.delivery_plugin_id == SHIPPING_DELIVERY_PLUGIN_ID:
                # 選択不可期間
                default_form_state['unavailable_period_days'] = 14

        # 支払期日の時刻
        if default_form_state['payment_period_days_selected_choice'] == DateCalculationBase.OrderDateTime.v:
            # 相対指定の計算基準タイプが「予約日時から」のときは入力不可
            default_form_state['payment_period_time_readonly'] = True

        # コンビニ発券開始日の時刻
        if default_form_state['issuing_interval_days_selected_choice'] == DateCalculationBase.OrderDateTime.v:
            # 相対指定の計算基準タイプが「予約日時から」のときは入力不可
            default_form_state['issuing_interval_time_readonly'] = True
        elif default_form_state['issuing_interval_days_selected_choice'] in \
                (DateCalculationBase.PerformanceStartDate.v, DateCalculationBase.PerformanceEndDate.v):
            # 相対指定の計算基準タイプが「公演開始から」「公演終了から」のとき、デフォルト値は 12:00
            default_form_state['issuing_interval_time_hour'] = 12
            default_form_state['issuing_interval_time_minute'] = 0

        # コンビニ発券期限の時刻
        if default_form_state['issuing_end_in_days_selected_choice'] == DateCalculationBase.OrderDateTime.v:
            # 相対指定の計算基準タイプが「予約日時から」のときは入力不可
            default_form_state['issuing_end_in_time_readonly'] = True

        return default_form_state
