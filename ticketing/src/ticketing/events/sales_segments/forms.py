# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, IntegerField, BooleanField, SelectMultipleField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput
from sqlalchemy.sql import or_, and_

from ticketing.formhelpers import (Translations, Required, RequiredOnUpdate, OurForm, OurDateTimeField,
                                   OurIntegerField, OurBooleanField, OurSelectField, OurDecimalField,
                                   BugFreeSelectField, PHPCompatibleSelectMultipleField, CheckboxMultipleSelect)
from ticketing.core.models import SalesSegmentGroup, SalesSegment, Account

class SalesSegmentForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(SalesSegmentForm, self).__init__(formdata, obj, prefix, **kwargs)

        performances = kwargs.get("performances", [])
        self.performance_id.choices = \
            [(u'', u'(なし)')] + \
            [(unicode(p.id),
              u'%s (%s)' % (p.name, p.start_on.strftime('%Y-%m-%d %H:%M'))) \
             for p in performances]
        sales_segment_groups = kwargs.get('sales_segment_groups')

        sales_segment_group = None
        if self.sales_segment_group_id.data:
            sales_segment_group = SalesSegmentGroup.query.filter_by(id=self.sales_segment_group_id.data).first()
        elif obj is not None:
            sales_segment_group = obj.sales_segment_group

        if sales_segment_groups is None:
            if sales_segment_group is not None:
                sales_segment_groups = [sales_segment_group]
            else:
                sales_segment_groups = []

        self.sales_segment_group_id.choices = \
            [(u'', u'(なし)')] + \
            [(unicode(s.id), s.name) \
             for s in sales_segment_groups]

        if sales_segment_group is not None:
            self.payment_delivery_method_pairs.choices = \
                [(unicode(pdmp.id),
                  u'%s - %s' % (pdmp.payment_method.name, pdmp.delivery_method.name))
                 for pdmp in sales_segment_group.payment_delivery_method_pairs
                ]
            self.account_id.choices = [
                (a.id, a.name) for a in Account.query.filter_by(organization_id=sales_segment_group.event.organization_id)
            ]
            self.account_id.default = sales_segment_group.account_id
            for field_name in ('margin_ratio', 'refund_ratio', 'printing_fee', 'registration_fee'):
                field = getattr(self, field_name)
                field.default = getattr(sales_segment_group, field_name)
            self.process(formdata, obj, **kwargs)
        elif performances:
            self.account_id.choices = [
                (a.id, a.name) for a in Account.query.filter_by(organization_id=performances[0].event.organization_id)
            ]
        if obj and obj.payment_delivery_method_pairs is not None:
            self.payment_delivery_method_pairs.data = [int(pdmp.id) for pdmp in obj.payment_delivery_method_pairs]
        elif sales_segment_group is not None and formdata is None:
            self.payment_delivery_method_pairs.data = [int(pdmp.id) for pdmp in sales_segment_group.payment_delivery_method_pairs]

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
    payment_delivery_method_pairs = PHPCompatibleSelectMultipleField(
        label=u'決済・引取方法',
        validators=[Required()],
        choices=[],
        coerce=lambda x : int(x) if x else u'',
        widget=CheckboxMultipleSelect(multiple=True)
    )
    start_at = OurDateTimeField(
        label=u'販売開始日時',
        validators=[RequiredOnUpdate()],
        format='%Y-%m-%d %H:%M',
        hide_on_new=True
    )
    end_at = OurDateTimeField(
        label=u'販売終了日時',
        validators=[RequiredOnUpdate()],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(hour=u'23', minute=u'59', second='59'),
        hide_on_new=True
    )
    upper_limit = OurIntegerField(
        label=u'購入上限枚数',
        default=10,
        validators=[RequiredOnUpdate()],
        hide_on_new=True
    )
    account_id = OurSelectField(
        label=u'配券元',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int,
        hide_on_new=True
    )
    margin_ratio = OurDecimalField(
        label=u'販売手数料率(%)',
        places=2,
        default=0,
        validators=[Required()],
        hide_on_new=True
    )
    refund_ratio = OurDecimalField(
        label=u'払戻手数料率(%)',
        places=2,
        default=0,
        validators=[Required()],
        hide_on_new=True
    )
    printing_fee = OurDecimalField(
        label=u'印刷代金(円/枚)',
        places=2,
        default=0,
        validators=[Required()],
        hide_on_new=True
    )
    registration_fee = OurDecimalField(
        label=u'登録手数料(円/公演)',
        places=2,
        default=0,
        validators=[Required()],
        hide_on_new=True
    )

    def validate_end_at(form, field):
        if field.data is not None and field.data < form.start_at.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')

    def validate(self):
        if super(SalesSegmentForm, self).validate():

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
