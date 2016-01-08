# -*- coding: utf-8 -*-

import re
import json
from collections import OrderedDict
from altair.formhelpers.form import OurForm
from altair.formhelpers.validators import SwitchOptionalBase
from altair.formhelpers.fields import OurTextField, OurIntegerField, OurDecimalField, OurSelectField, OurBooleanField, OurField
from wtforms import HiddenField
from wtforms.validators import NumberRange, Regexp, Length, Optional, ValidationError
from wtforms.widgets import Input, CheckboxInput, RadioInput
from wtforms.widgets.core import HTMLString, html_params
from wtforms.fields.core import _unset_value
from cgi import escape

from altair.formhelpers import DateTimeField, Translations, Required, after1900
from altair.app.ticketing.core.models import (
    SalesSegment,
    PaymentMethod,
    DeliveryMethod,
    PaymentDeliveryMethodPair,
    FeeTypeEnum,
    DateCalculationBase,
    )
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID
from altair.saannotation import get_annotations_for

def required_when_absolute(field_name):
    return [
        SwitchOptionalBase(
            lambda form, _: form[field_name].data != DateCalculationBase.Absolute.v
            ),
        Required(),
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
        html.append('''<script type="text/javascript">
(function(an, rn, n) {
function enableFields(n, v) {
    function _(sn, v) {
        for (; sn != null; sn = sn.nextSibling) {
            if (sn.nodeType == document.ELEMENT_NODE) {
                if (sn != n && sn.nodeName.toUpperCase() != 'LABEL') {
                    if (v)
                        sn.removeAttribute('disabled');
                    else
                        sn.setAttribute('disabled', 'disabled');
                    _(sn.firstChild, v);
                }
            }
        }
    }
    _(n.parentNode.parentNode.firstChild, v);
}

var choices = %(choices)s;
var textNodes = { lhs: null, rhs: null };
var inputNode = null;
for (var sn = n.parentNode.firstChild; sn != null; sn = sn.nextSibling) {
    if (sn.nodeType == document.ELEMENT_NODE) {
        var g = /(lhs|rhs)-content/.exec(sn.getAttribute('class'));
        if (g) {
            textNodes[g[1]] = sn;
        } else {
            if (sn.nodeName.toLowerCase() == 'input')
                inputNode = sn;
        }
    }
}
function refreshState() {
    if (an.checked) {
        enableFields(an, true);
        enableFields(rn, false);
    } else if (rn.checked) {
        enableFields(an, false);
        enableFields(rn, true);
    }
}
an.onchange = rn.onchange = refreshState;
n.onchange = function (e) {
    for (var k in textNodes) {
        if (textNodes[k] != null) {
            textNodes[k].firstChild.nodeValue = choices[n.value][k];
        }
    }
};
refreshState();
})(
    document.getElementById(%(base_type_absolute_key)s),
    document.getElementById(%(base_type_relative_key)s),
    document.getElementById(%(subcategory_key)s)
);
</script>''' % dict(
                choices=json.dumps(
                    dict(
                        (k, dict(lhs=v['lhs'], rhs=v['rhs']))
                        for k, v in self.choices
                        )
                    ),
                base_type_absolute_key=json.dumps(u'%s-absolute' % self.base_type_key),
                base_type_relative_key=json.dumps(u'%s-relative' % self.base_type_key),
                subcategory_key=json.dumps(self.subcategory_key),
                )
            )
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
            Required(),
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
        default=False,
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

    issuing_end_at = DateTimeField(
        label=get_annotations_for(PaymentDeliveryMethodPair.issuing_end_at)['label'],
        validators=required_when_absolute('issuing_end_day_calculation_base') + [after1900],
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
            # 有効な決済方法と引取方法の組み合わせかをチェックする
            if not PaymentDeliveryMethodPair.is_valid_pair(int(form.payment_method_id.data), int(form.delivery_method_id.data)):
                error_message = u'有効な決済方法と引取方法の組み合わせではありません'
                form.payment_method_id.errors.append(error_message)
                form.delivery_method_id.errors.append(error_message)
                status = False

            # 楽天ID決済の場合は、決済手数料と特別手数料は設定不可
            payment_method = PaymentMethod.query.filter_by(id=form.payment_method_id.data).first()
            if payment_method and payment_method.payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID:
                error_message = u'楽天ID決済では、決済手数料は設定できません'
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
                    performance_start_on = ss.performance.start_on
                    performance_end_on = ss.performance.end_on or ss.performance.start_on
                    ss_start_at = ss.start_at
                    ss_end_at = ss.end_at
                    if ss.use_default_end_at:
                        ss_end_at = ss.sales_segment_group.end_for_performance(ss.performance)
                    try:
                        validate_issuing_start_at(
                            performance_start_on=performance_start_on,
                            performance_end_on=performance_end_on,
                            sales_segment_start_at=ss_start_at,
                            sales_segment_end_at=ss_end_at,
                            pdmp=pdmp,
                            issuing_start_day_calculation_base=form.issuing_start_day_calculation_base.data,
                            issuing_start_at=form.issuing_start_at.data,
                            issuing_interval_days=form.issuing_interval_days.data
                            )
                    except IssuingStartAtOutTermException as e:
                        if form.issuing_start_at.data:
                            form.issuing_start_at.errors.append(e.message)
                        else:
                            form.issuing_interval_days.errors.append(e.message)
                        status = False
                        break
        return status
