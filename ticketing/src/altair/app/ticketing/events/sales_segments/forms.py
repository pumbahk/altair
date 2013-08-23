# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, TextAreaField, SelectField, HiddenField, IntegerField, BooleanField, SelectMultipleField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput
from sqlalchemy.sql import or_, and_, select

from altair.formhelpers import (Translations, Required, RequiredOnUpdate, DateTimeFormat, OurForm, OurDateTimeField,
                                   OurIntegerField, OurBooleanField, OurSelectField, OurDecimalField,
                                   BugFreeSelectField, PHPCompatibleSelectMultipleField, CheckboxMultipleSelect,
                                SwitchOptional,
)
from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment, Account
from altair.app.ticketing.loyalty.models import PointGrantSetting, SalesSegment_PointGrantSetting

propagation_attrs = ('margin_ratio', 'refund_ratio', 'printing_fee', 'registration_fee', 'reporting')

class SalesSegmentForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', context=None, **kwargs):
        super(SalesSegmentForm, self).__init__(formdata, obj, prefix, **kwargs)

        performance_id_choices = [(u'', u'(なし)')]
        sales_segment_group_id_choices = [(u'', u'(なし)')]

        if context is not None:
            performance_id_choices.extend([(unicode(p.id),
              u'%s (%s)' % (p.name, p.start_on.strftime('%Y-%m-%d %H:%M'))) \
             for p in context.event.performances])
            if context.sales_segment_group is not None:
                sales_segment_groups = [context.sales_segment_group]
            else:
                sales_segment_groups = context.event.sales_segment_groups
            sales_segment_group_id_choices.extend([(unicode(s.id), s.name) for s in sales_segment_groups])

            self.account_id.choices = [
                (a.id, a.name) for a in context.user.organization.accounts
            ]

            if context.performance is not None:
                self.performance_id.data = self.performance_id.default = context.performance.id

            if context.sales_segment_group is not None:
                self.payment_delivery_method_pairs.choices = \
                    [(unicode(pdmp.id),
                      u'%s - %s' % (pdmp.payment_method.name, pdmp.delivery_method.name))
                     for pdmp in context.sales_segment_group.payment_delivery_method_pairs
                    ]
                self.account_id.default = context.sales_segment_group.account_id

                self.payment_delivery_method_pairs.default = [int(pdmp.id) for pdmp in context.sales_segment_group.payment_delivery_method_pairs]

                for field_name in propagation_attrs:
                    field = getattr(self, field_name)
                    field.default = getattr(context.sales_segment_group, field_name)

                self.sales_segment_group_id.data = self.sales_segment_group_id.default = context.sales_segment_group.id
            else:
                for field_name in propagation_attrs:
                    field = getattr(self, field_name)
                    field.default = getattr(context.user.organization.setting, field_name, None)
            self.process(formdata, obj, **kwargs)

        if obj and obj.payment_delivery_method_pairs is not None:
            self.payment_delivery_method_pairs.data = [int(pdmp.id) for pdmp in obj.payment_delivery_method_pairs]

        self.performance_id.choices = performance_id_choices
        self.sales_segment_group_id.choices = sales_segment_group_id_choices

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    sales_segment_group_id = BugFreeSelectField(
        label=u'販売区分グループ',
        validators=[Required()],
        choices=[],
        coerce=lambda x: int(x) if x else None
    )
    performance_id = BugFreeSelectField(
        label=u'公演',
        choices=[],
        coerce=lambda x: int(x) if x else None
    )
    seat_choice = OurBooleanField(
        label=u'座席選択可',
        default=True,
        widget=CheckboxInput()
    )
    public = OurBooleanField(
        label=u'一般公開',
        default=True,
        widget=CheckboxInput()
    )
    reporting = OurBooleanField(
        label=u'レポート対象',
        default=True,
        widget=CheckboxInput()
    )
    payment_delivery_method_pairs = PHPCompatibleSelectMultipleField(
        label=u'決済・引取方法',
        validators=[Required()],
        choices=[],
        coerce=lambda x : int(x) if x else u'',
        widget=CheckboxMultipleSelect(multiple=True)
    )
    start_at = OurDateTimeField(
        label=u'販売開始日時',
        validators=[DateTimeFormat()],
        format='%Y-%m-%d %H:%M'
    )
    end_at = OurDateTimeField(
        label=u'販売終了日時',
        validators=[DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(hour=u'23', minute=u'59', second='59')
    )
    upper_limit = OurIntegerField(
        label=u'購入上限枚数',
        default=10,
        validators=[RequiredOnUpdate()]
    )
    order_limit = OurIntegerField(
        label=u'購入回数制限',
        default=0,
        validators=[RequiredOnUpdate()]
    )
    account_id = OurSelectField(
        label=u'配券元',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    margin_ratio = OurDecimalField(
        label=u'販売手数料率(%)',
        places=2,
        default=0,
        validators=[Required()]
    )
    refund_ratio = OurDecimalField(
        label=u'払戻手数料率(%)',
        places=2,
        default=0,
        validators=[Required()]
    )
    printing_fee = OurDecimalField(
        label=u'印刷代金(円/枚)',
        places=2,
        default=0,
        validators=[Required()]
    )
    registration_fee = OurDecimalField(
        label=u'登録手数料(円/公演)',
        places=2,
        default=0,
        validators=[Required()]
    )
    x_auth3d_notice = TextAreaField(
        label=u'クレジットカード 3D認証フォーム 注記事項',
        validators=[Optional()],
    )

    def validate(self):
        if super(SalesSegmentForm, self).validate():
            start_at = self.start_at.data
            end_at = self.end_at.data

            # 販売開始日時と販売終了日時の前後関係をチェックする
            if start_at > end_at:
                self.start_at.errors.append(u'販売開始日時が販売終了日時より後に設定されています')
                self.end_at.errors.append(u'販売終了日時が販売開始日時より前に設定されています')
                return False
            
            
            # 同一公演の期限かぶりをチェックする
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


class EditSalesSegmentForm(OurForm):

    def _get_translations(self):
        return Translations()

    seat_choice = OurBooleanField(
        label=u'座席選択可',
        default=True,
        widget=CheckboxInput()
    )
    use_default_seat_choice = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        default=True,
        widget=CheckboxInput()
    )
    public = OurBooleanField(
        label=u'一般公開',
        default=True,
        widget=CheckboxInput()
    )
    use_default_public = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        default=True,
        widget=CheckboxInput()
    )
    reporting = OurBooleanField(
        label=u'レポート対象',
        default=True,
        widget=CheckboxInput()
    )
    use_default_reporting = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        default=True,
        widget=CheckboxInput()
    )

    payment_delivery_method_pairs = PHPCompatibleSelectMultipleField(
        label=u'決済・引取方法',
        validators=[SwitchOptional('use_default_payment_delivery_method_pairs'),
                    Required()],
        choices=[],
        coerce=lambda x : int(x) if x else u'',
        widget=CheckboxMultipleSelect(multiple=True)
    )
    use_default_payment_delivery_method_pairs = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        default=True,
        widget=CheckboxInput()
    )

    start_at = OurDateTimeField(
        label=u'販売開始日時',
        #validators=[Optional(), DateTimeFormat()],
        validators=[SwitchOptional('use_default_start_at'),
                    Required(),
                    DateTimeFormat()],
        format='%Y-%m-%d %H:%M'
    )
    use_default_start_at = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        widget=CheckboxInput()
    )

    end_at = OurDateTimeField(
        label=u'販売終了日時',
        validators=[Optional(), DateTimeFormat()],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(hour=u'23', minute=u'59', second='59')
    )
    use_default_end_at = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        widget=CheckboxInput()
    )

    upper_limit = OurIntegerField(
        label=u'購入上限枚数',
        default=10,
        validators=[SwitchOptional('use_default_upper_limit'),
                    Required()]
    )
    use_default_upper_limit = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        widget=CheckboxInput()
    )

    order_limit = OurIntegerField(
        label=u'購入回数制限',
        default=0,
        validators=[SwitchOptional('use_default_order_limit'),
                    Required()]
    )
    use_default_order_limit = OurBooleanField(
        label=u'販売区分グループの値を利用する',
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
        label=u'販売区分グループの値を利用する',
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
        label=u'販売区分グループの値を利用する',
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
        label=u'販売区分グループの値を利用する',
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
        label=u'販売区分グループの値を利用する',
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
        label=u'販売区分グループの値を利用する',
        widget=CheckboxInput()
    )

    auth3d_notice = TextAreaField(
        label=u'クレジットカード 3D認証フォーム 注記事項',
        validators=[Optional()],
    )
    use_default_auth3d_notice = OurBooleanField(
        label=u'販売区分グループの値を利用する',
        widget=CheckboxInput()
    )

    def _validate_terms(self):
        start_at = self.start_at.data
        end_at = self.end_at.data

        # 販売開始日時と販売終了日時の前後関係をチェックする
        if start_at > end_at:
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

    def validate(self):
        if super(EditSalesSegmentForm, self).validate():
            if not self._validate_terms():
                return False
            #if not self._validate_performance_terms():
            #    return False

            return True


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


