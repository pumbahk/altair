# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, TextAreaField, SelectField, HiddenField, IntegerField, BooleanField, SelectMultipleField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput
from sqlalchemy.sql import or_, and_, select

from altair.formhelpers import (
    Translations,
    DateTimeFormat,
    OurDateTimeField,
    OurIntegerField,
    OurBooleanField,
    OurSelectField,
    OurDecimalField,
    BugFreeSelectField,
    PHPCompatibleSelectMultipleField,
    BugFreeSelectMultipleField,
    )
from altair.formhelpers.widgets import CheckboxMultipleSelect
from altair.formhelpers.form import OurForm
from altair.formhelpers.validators import Required, RequiredOnUpdate, SwitchOptional
from altair.formhelpers.filters import zero_as_none
from altair.app.ticketing.helpers import label_text_for
from altair.app.ticketing.core.models import (
    SalesSegmentGroup,
    SalesSegment,
    SalesSegmentSetting,
    Account,
    )
from altair.app.ticketing.loyalty.models import PointGrantSetting, SalesSegment_PointGrantSetting

from .resources import ISalesSegmentAdminResource
from zope.interface import providedBy

propagation_attrs = ('margin_ratio', 'refund_ratio', 'printing_fee', 'registration_fee', 'reporting')

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
        default=True,
        widget=CheckboxInput()
    )
    use_default_display_seat_no = OurBooleanField(
        label=u'グループの値を利用',
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
        label=u'一般チケットの購入履歴表示/非表示',
        default=True,
        widget=CheckboxInput()
    )
    disp_agreement = OurBooleanField(
        label=u'規約の表示/非表示',
        hide_on_new=True
    )
    agreement_body = TextAreaField(
        label=u'規約内容',
        validators=[Optional()],
    )
    use_default_disp_orderreview = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )
    use_default_disp_agreement = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )
    use_default_agreement_body = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )
    reporting = OurBooleanField(
        label=u'レポート対象',
        default=True,
        widget=CheckboxInput()
    )
    use_default_reporting = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )
    sales_counter_selectable = OurBooleanField(
        label=label_text_for(SalesSegmentSetting.sales_counter_selectable),
        default=True,
        widget=CheckboxInput(),
        help=u'''
          窓口業務でこの販売区分を選択可能にします。<br />
          例外として「公演管理編集」権限があるオペレーターは常に選択可能です。
        '''
    )
    use_default_sales_counter_selectable = OurBooleanField(
        label=u'グループの値を利用',
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
                for pdmp in field.form.context.sales_segment_group.payment_delivery_method_pairs
                ] if field.form.context.sales_segment_group else [],
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
        default=10,
        validators=[SwitchOptional('use_default_max_quantity'),
                    Required()],
        hide_on_new=True
    )
    use_default_max_quantity = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )
    max_quantity_per_user = OurIntegerField(
        label=label_text_for(SalesSegmentSetting.max_quantity_per_user),
        default=0,
        filters=[zero_as_none],
        validators=[Optional()],
        hide_on_new=True
    )
    use_default_max_quantity_per_user = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )
    max_product_quatity = OurIntegerField(
        label=u'商品購入上限数',
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    use_default_max_product_quatity = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )
    order_limit = OurIntegerField(
        label=u'購入回数制限',
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    use_default_order_limit = OurBooleanField(
        label=u'グループの値を利用',
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
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_margin_ratio'),
                    Required()]
    )
    use_default_margin_ratio = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )

    refund_ratio = OurDecimalField(
        label=u'払戻手数料率(%)',
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_refund_ratio'),
                    Required()]
    )
    use_default_refund_ratio = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )

    printing_fee = OurDecimalField(
        label=u'印刷代金(円/枚)',
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_printing_fee'),
                    Required()]
    )
    use_default_printing_fee = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )

    registration_fee = OurDecimalField(
        label=u'登録手数料(円/公演)',
        places=2,
        default=0,
        validators=[SwitchOptional('use_default_registration_fee'),
                    Required()]
    )
    use_default_registration_fee = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )

    auth3d_notice = TextAreaField(
        label=u'クレジットカード 3D認証フォーム 注記事項',
        validators=[Optional()],
    )
    use_default_auth3d_notice = OurBooleanField(
        label=u'グループの値を利用',
        widget=CheckboxInput()
    )

    copy_performances = PHPCompatibleSelectMultipleField(
        label=u'コピー先の公演(複数選択可)',
        validators=[Optional()],
        choices=lambda field: [
            (p.id, u'%s' % p.name) for p in field.form.context.event.performances
        ] if field.form.context.event else [],
        coerce=lambda x : int(x) if x else u''
    )
    copy_products = OurBooleanField(
        label=u'商品をコピーする',
        default=True,
        widget=CheckboxInput()
    )

    def _validate_terms(self):
        start_at = self.start_at.data
        end_at = self.end_at.data

        # 販売開始日時と販売終了日時の前後関係をチェックする
        if start_at is not None and end_at is not None and start_at > end_at:
            self.start_at.errors.append(u'販売開始日時が販売終了日時より後に設定されています')
            self.end_at.errors.append(u'販売終了日時が販売開始日時より前に設定されています')
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
            ],
        coerce=lambda x: long(x) if x else None
        )

    def __init__(self, formdata=None, obj=None, prefix='', context=None, **kwargs):
        super(PointGrantSettingAssociationForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.context = context


