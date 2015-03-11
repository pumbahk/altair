# -*- coding: utf-8 -*-

import re
import json
import logging
from datetime import timedelta
from collections import namedtuple

from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError, NumberRange
from wtforms.widgets import CheckboxInput, Input, HTMLString
from altair.formhelpers.widgets.context import Rendrant
from altair.app.ticketing.utils import DateTimeRange
from markupsafe import escape
from sqlalchemy.sql import or_, and_, select

from altair.formhelpers import (
    Translations,
    DateTimeFormat,
    OurTextAreaField,
    OurDateTimeField,
    OurIntegerField,
    OurBooleanField,
    OurSelectField,
    OurDecimalField,
    BugFreeSelectField,
    PHPCompatibleSelectMultipleField,
    BugFreeSelectMultipleField,
    JSONField
    )
from altair.formhelpers.widgets import CheckboxMultipleSelect
from altair.formhelpers.form import OurForm
from altair.formhelpers.validators import Required, RequiredOnUpdate, SwitchOptional
from altair.formhelpers.filters import zero_as_none, blank_as_none
from altair.app.ticketing.helpers import label_text_for
from altair.app.ticketing.core.models import (
    SalesSegmentGroup,
    SalesSegment,
    SalesSegmentSetting,
    Account,
    Performance,
    calculate_date_from_order_like,
    CartMixin
    )
from altair.app.ticketing.loyalty.models import PointGrantSetting, SalesSegment_PointGrantSetting
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID

from .resources import ISalesSegmentAdminResource
from .exceptions import IssuingStartAtOutTermException
from zope.interface import providedBy

propagation_attrs = ('margin_ratio', 'refund_ratio', 'printing_fee', 'registration_fee', 'reporting')

logger = logging.getLogger(__name__)

UPPER_LIMIT_OF_MAX_QUANTITY = 99  # 購入数が大きすぎるとcartやlotでプルダウンが表示出来なくなる事があるため上限数を制限する

DummyPerformance = namedtuple('DummyPerformance', ['start_on', 'end_on'])
DummyPDMP = namedtuple('DummyPDMP', [
    'issuing_start_day_calculation_base',
    'issuing_interval_days',
    'issuing_start_at'
    ])
DummySalesSegment = namedtuple('DummySalesSegment', ['start_at', 'end_at', 'performance'])
class DummyCart(CartMixin):
    def __init__(self,
            performance_start_on,
            performance_end_on,
            sales_segment_start_at,
            sales_segment_end_at,
            issuing_start_day_calculation_base,
            issuing_start_at,
            issuing_interval_days,
            created_at):
        performance = None
        if performance_start_on is not None:
            performance = DummyPerformance(
                performance_start_on,
                performance_end_on
                )
        else:
            performance = None
        self.sales_segment = DummySalesSegment(
            sales_segment_start_at,
            sales_segment_end_at,
            performance
            )
        self.payment_delivery_pair = DummyPDMP(
            issuing_start_day_calculation_base,
            issuing_interval_days,
            issuing_start_at
            )
        self.created_at = created_at
        self.performance = performance

def validate_issuing_start_at(
    performance_start_on,
    performance_end_on,
    sales_segment_start_at,
    sales_segment_end_at,
    pdmp,
    issuing_start_day_calculation_base=None,
    issuing_start_at=None,
    issuing_interval_days=None
    ):
    if issuing_start_day_calculation_base is None:
        issuing_start_day_calculation_base = pdmp.issuing_start_day_calculation_base
        issuing_start_at = pdmp.issuing_start_at
        issuing_interval_days = pdmp.issuing_interval_days

    # 公演終了日 < コンビニ発券開始日時 とならないこと
    issuing_start_at = DummyCart(
        performance_start_on=performance_start_on,
        performance_end_on=performance_end_on,
        sales_segment_start_at=sales_segment_start_at,
        sales_segment_end_at=sales_segment_end_at,
        issuing_start_day_calculation_base=issuing_start_day_calculation_base,
        issuing_start_at=issuing_start_at,
        issuing_interval_days=issuing_interval_days,
        created_at=sales_segment_end_at or performance_end_on or performance_start_on
        ).issuing_start_at
    # 複数日にまたがる公演のケースがあるので公演終了日で算出
    logger.debug('performance_end_on={}, issuing_start_at={}'.format(performance_end_on, issuing_start_at))
    delivery_plugin_id = pdmp.delivery_method.delivery_plugin_id
    if delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID and performance_end_on < issuing_start_at:
        pdmp_name = u'{0} - {1}'.format(pdmp.payment_method.name, pdmp.delivery_method.name)
        message = u'決済引取方法「{}」のコンビニ発券開始日時が公演終了日時より後になる可能性があります'.format(pdmp_name)
        raise IssuingStartAtOutTermException(message)

class ExtraFormEditorWidget(Input):
    input_type = 'hidden'

    def __call__(self, field, **kwargs):
        class_ = kwargs.pop('class_', None)
        id_ = kwargs.pop('id', None) or field.id
        classes = ['action-open_extra_form_editor']
        if class_ is not None:
            classes.extend(re.split(ur'\s+', class_))
        button_id = u'%s-btn' % id_
        html = [super(ExtraFormEditorWidget, self).__call__(field, id=id_, **kwargs)]
        html.append('<ul data-for="{name}">'.format(name=escape(field.name)))
        if field.data is not None:
            for f in field.data:
                html.append(u'<li>{display_name} ({name})</li>'.format(display_name=escape(f['display_name']), name=escape(f['name'])))
        html.append('</ul>')
        html.append(u'<button id="{id}" class="{classes}" data-for="{name}">編集</button>'.format(id=escape(button_id), classes=u' '.join(escape(class_) for class_ in classes), name=escape(field.name)))
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is not None:
            js_coercer = js_coercer()
        else:
            js_coercer = u'function (v) { return v; }'
        return ExtraFormEditorWidgetRendrant(
            field,
            HTMLString(u''.join(html)),
            id_,
            button_id,
            js_coercer
            )

class ExtraFormEditorWidgetRendrant(Rendrant):
    def __init__(self, field, html, id_, button_id, coercer):
        super(ExtraFormEditorWidgetRendrant, self).__init__(field, html)
        self.id = id_
        self.button_id = button_id
        self.coercer = coercer

    def render_js_data_provider(self, registry_var_name):
        return u'''<script type="text/javascript">
(function(name, id, buttonId, coercer) {
  var n = document.getElementById(id);
  var bn = document.getElementById(buttonId);
  window[%(registry_var_name)s].registerProvider(name, {
    getValue: function () {
      return coercer(n.value);
    },
    getUIElements: function() {
      return [n, bn];
    }
  });
})(%(name)s, %(id)s, %(button_id)s, %(coercer)s);
</script>''' % dict(name=json.dumps(self.field.short_name), id=json.dumps(self.id), button_id=json.dumps(self.button_id), coercer=self.coercer, registry_var_name=json.dumps(registry_var_name))


class SalesSegmentForm(OurForm):
    def _get_translations(self):
        return Translations()

    sales_segment_group_id = BugFreeSelectField(
        label=u'販売区分グループ',
        validators=[Required()],
        choices=[],
        coerce=lambda x: long(x) if x else None
    )
    performance_id = BugFreeSelectField(
        label=u'公演',
        choices=[],
        coerce=lambda x: long(x) if x else None
    )
    lot_id = OurIntegerField(
        label=u'抽選',
    )
    seat_choice = OurBooleanField(
        label=u'座席選択可',
        default=True,
        widget=CheckboxInput()
    )
    use_default_seat_choice = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )
    display_seat_no = OurBooleanField(
        label=label_text_for(SalesSegmentSetting.display_seat_no),
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    use_default_display_seat_no = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    public = OurBooleanField(
        label=u'一般公開',
        default=True,
        widget=CheckboxInput()
    )
    use_default_public = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )
    disp_orderreview = OurBooleanField(
        label=u'マイページへの購入履歴表示/非表示',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    use_default_disp_orderreview = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    disp_agreement = OurBooleanField(
        label=u'規約の表示/非表示',
        hide_on_new=True
    )
    use_default_disp_agreement = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    agreement_body = OurTextAreaField(
        label=u'規約内容',
        hide_on_new=True,
        validators=[Optional()],
    )
    use_default_agreement_body = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    reporting = OurBooleanField(
        label=u'レポート対象',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    use_default_reporting = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )
    sales_counter_selectable = OurBooleanField(
        label=label_text_for(SalesSegmentSetting.sales_counter_selectable),
        hide_on_new=True,
        default=True,
        widget=CheckboxInput(),
        help=u'''
          窓口業務でこの販売区分を選択可能にします。<br />
          例外として「公演管理編集」権限があるオペレーターは常に選択可能です。
        '''
    )
    use_default_sales_counter_selectable = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        default=True,
        widget=CheckboxInput()
    )

    payment_delivery_method_pairs = PHPCompatibleSelectMultipleField(
        label=u'決済・引取方法',
        validators=[SwitchOptional('use_default_payment_delivery_method_pairs'),
                    Required()],
        choices=lambda field: [
                (
                    pdmp.id,
                    u'%s - %s' % (pdmp.payment_method.name, pdmp.delivery_method.name)
                    )
                for pdmp in field._form.context.sales_segment_group.payment_delivery_method_pairs
                ] if field._form.context.sales_segment_group else [],
        coerce=lambda x : int(x) if x else u'',
        widget=CheckboxMultipleSelect(multiple=True)
    )
    use_default_payment_delivery_method_pairs = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )

    start_at = OurDateTimeField(
        label=u'販売開始',
        validators=[SwitchOptional('use_default_start_at'),
                    Required(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M'
    )
    use_default_start_at = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )

    end_at = OurDateTimeField(
        label=u'販売終了',
        validators=[Optional(), DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(hour=u'23', minute=u'59', second='59')
    )
    use_default_end_at = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )
    max_quantity = OurIntegerField(
        label=label_text_for(SalesSegment.max_quantity),
        hide_on_new=True,
        default=10,
        validators=[SwitchOptional('use_default_max_quantity'),
                    Required(),
                    NumberRange(min=0, max=UPPER_LIMIT_OF_MAX_QUANTITY, message=u'範囲外です'),
                    ]
    )
    use_default_max_quantity = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )
    max_quantity_per_user = OurIntegerField(
        label=label_text_for(SalesSegmentSetting.max_quantity_per_user),
        hide_on_new=True,
        default=0,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    use_default_max_quantity_per_user = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )
    max_product_quatity = OurIntegerField(
        label=u'商品購入上限数',
        hide_on_new=True,
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    use_default_max_product_quatity = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )
    order_limit = OurIntegerField(
        label=u'購入回数制限',
        hide_on_new=True,
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    use_default_order_limit = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )

    account_id = OurSelectField(
        label=u'配券元',
        validators=[SwitchOptional('use_default_account_id'),
                    Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    use_default_account_id = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )

    margin_ratio = OurDecimalField(
        label=u'販売手数料率(%)',
        hide_on_new=True,
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_margin_ratio'),
                    Required()]
    )
    use_default_margin_ratio = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )

    refund_ratio = OurDecimalField(
        label=u'払戻手数料率(%)',
        hide_on_new=True,
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_refund_ratio'),
                    Required()]
    )
    use_default_refund_ratio = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )

    printing_fee = OurDecimalField(
        label=u'印刷代金(円/枚)',
        hide_on_new=True,
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_printing_fee'),
                    Required()]
    )
    use_default_printing_fee = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )

    registration_fee = OurDecimalField(
        label=u'登録手数料(円/公演)',
        hide_on_new=True,
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_registration_fee'),
                    Required()]
    )
    use_default_registration_fee = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )

    auth3d_notice = OurTextAreaField(
        label=u'クレジットカード 3D認証フォーム 注記事項',
        hide_on_new=True,
        validators=[Optional()],
    )
    use_default_auth3d_notice = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
    )

    copy_performances = PHPCompatibleSelectMultipleField(
        label=u'コピー先の公演(複数選択可)',
        validators=[Optional()],
        choices=lambda field: [
            (p.id, u'%s' % p.name) for p in field._form.context.event.performances
        ] if field._form.context.event else [],
        coerce=lambda x : int(x) if x else u''
    )
    copy_products = OurBooleanField(
        label=u'商品をコピーする',
        default=True,
        widget=CheckboxInput()
    )

    extra_form_fields = JSONField(
        label=u'追加フィールド',
        filters=[blank_as_none],
        validators=[Optional()],
        widget=ExtraFormEditorWidget()
        )
    use_default_extra_form_fields = OurBooleanField(
        label=u'グループの値を利用',
        hide_on_new=True,
        widget=CheckboxInput()
        )

    def _validate_terms(self):
        ssg = SalesSegmentGroup.query.filter_by(id=self.sales_segment_group_id.data).one()
        ss_start_at = self.start_at.data
        ss_end_at = self.end_at.data
        if self.performance_id.data:
            performance = Performance.get(self.performance_id.data, self.context.organization.id)
            if self.use_default_start_at.data:
                ss_start_at = ssg.start_for_performance(performance)
            if self.use_default_end_at.data:
                ss_end_at = ssg.end_for_performance(performance)

        # 販売開始日時と販売終了日時の前後関係をチェックする
        if ss_start_at is not None and ss_end_at is not None and ss_start_at > ss_end_at:
            self.start_at.errors.append(u'販売開始日時が販売終了日時より後に設定されています')
            self.end_at.errors.append(u'販売終了日時が販売開始日時より前に設定されています')
            return False

        # コンビニ発券開始日時をチェックする
        if self.performance_id.data and ss_end_at is not None:
            performance_start_on = performance.start_on
            performance_end_on = performance.end_on or performance.start_on
            pdmps = self.context.sales_segment_group.payment_delivery_method_pairs
            if not self.use_default_payment_delivery_method_pairs.data:
                pdmps = [x for x in pdmps if x.id in self.payment_delivery_method_pairs.data]
            for pdmp in pdmps:
                try:
                    validate_issuing_start_at(
                        performance_start_on=performance_start_on,
                        performance_end_on=performance_end_on,
                        sales_segment_start_at=ss_start_at,
                        sales_segment_end_at=ss_end_at,
                        pdmp=pdmp)
                except IssuingStartAtOutTermException as e:
                    self.end_at.errors.append(e.message)
                    return False

        return True

    def _validate_performance_terms(self):
        # 同一公演の期限かぶりをチェックする
        start_at = self.start_at.data
        end_at = self.end_at.data
        if start_at is not None and end_at is not None:
            q = SalesSegment.query.filter(
                SalesSegment.performance_id==self.performance_id.data
            ).filter(
                or_(and_(start_at<=SalesSegment.start_at,
                         SalesSegment.start_at<=end_at),
                    and_(start_at<=SalesSegment.end_at,
                         SalesSegment.end_at<=end_at),
                    and_(SalesSegment.start_at<=start_at,
                         end_at<=SalesSegment.end_at),
                    )
            ).filter(
                SalesSegment.sales_segment_group_id==self.sales_segment_group_id.data
            )

            if self.id.data is not None:
                q = q.filter(SalesSegment.id != self.id.data)

            dup = q.first()
            if dup:
                self.start_at.errors.append(u'同一公演について期間がかぶっています。{0}～{1}'.format(
                        dup.start_at, dup.end_at))
                return False
        return True

    def _validate_display_seat_no(self, *args, **kwargs):
        ssg = SalesSegmentGroup.query.filter_by(id=self.sales_segment_group_id.data).one()
        seat_choice = ssg.seat_choice if self.use_default_seat_choice.data else self.seat_choice.data
        display_seat_no = ssg.setting.display_seat_no if self.use_default_display_seat_no.data else self.display_seat_no.data
        if seat_choice and not display_seat_no:
            self.display_seat_no.errors.append(u'座席選択可の場合は座席番号は非表示にできません')
            return False
        return True

    def validate(self):
        if super(SalesSegmentForm, self).validate():
            if not self._validate_terms():
                return False
            #if not self._validate_performance_terms():
            #    return False
            if not self._validate_display_seat_no():
                return False

            return True

    def __init__(self, formdata=None, obj=None, *args, **kwargs):
        context = kwargs.pop('context', None)
        super(SalesSegmentForm, self).__init__(formdata, obj, *args, **kwargs)
        self.context = context

        self.account_id.choices = [
            (a.id, a.name)
            for a in context.organization.accounts
            ]

        if ISalesSegmentAdminResource.providedBy(context):
            performance_id_choices = []
            if context.performance is not None:
                self.performance_id.data = self.performance_id.default = context.performance.id
                performances = [context.performance]
            else:
                performance_id_choices.append((u'', u'(なし)'))
                performances = self.context.event.performances
            performance_id_choices.extend([
                (p.id,
                u'%s (%s)' % (p.name, p.start_on.strftime('%Y-%m-%d %H:%M'))) \
                 for p in performances
                 ])

            self.performance_id.choices = performance_id_choices

        sales_segment_group_id_choices = []

        if context.sales_segment_group is not None:
            sales_segment_groups = [context.sales_segment_group]
            self.account_id.default = context.sales_segment_group.account_id

            self.payment_delivery_method_pairs.default = [long(pdmp.id) for pdmp in context.sales_segment_group.payment_delivery_method_pairs]

            for field_name in propagation_attrs:
                field = getattr(self, field_name)
                field.default = getattr(context.sales_segment_group, field_name)

            self.sales_segment_group_id.data = self.sales_segment_group_id.default = context.sales_segment_group.id
        else:
            sales_segment_group_id_choices.append((u'', u'(なし)'))
            sales_segment_groups = context.event.sales_segment_groups
            for field_name in propagation_attrs:
                field = getattr(self, field_name)
                field.default = getattr(context.organization.setting, field_name, None)
        sales_segment_group_id_choices.extend([(s.id, s.name) for s in sales_segment_groups])
        self.sales_segment_group_id.choices = sales_segment_group_id_choices

        self.process(formdata, obj, **kwargs)

class PointGrantSettingAssociationForm(OurForm):
    point_grant_setting_id = OurSelectField(
        label=u'ポイント付与設定',
        validators=[Required()],
        choices=lambda self: [
            (point_grant_setting.id, point_grant_setting.name)
            for point_grant_setting \
            in PointGrantSetting.filter_by(organization_id=self.form.context.organization.id).filter(~PointGrantSetting.id.in_(select([SalesSegment_PointGrantSetting.c.point_grant_setting_id]).where(SalesSegment_PointGrantSetting.c.sales_segment_id == self.form.context.sales_segment.id)))
            if self.form.context.sales_segment_range.overlap(DateTimeRange(point_grant_setting.start_at, point_grant_setting.end_at))
            ],
        coerce=lambda x: long(x) if x else None
        )

    def __init__(self, formdata=None, obj=None, prefix='', context=None, **kwargs):
        super(PointGrantSettingAssociationForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.context = context
