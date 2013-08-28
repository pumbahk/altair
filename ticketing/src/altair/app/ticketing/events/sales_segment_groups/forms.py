# -*- coding: utf-8 -*-

import logging
from wtforms import Form
from wtforms import TextField, TextAreaField, SelectField, HiddenField, IntegerField, BooleanField, SelectMultipleField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput

from altair.formhelpers import (
    OurDateTimeField, Translations, Required, RequiredOnUpdate,
    OurForm, OurIntegerField, OurBooleanField, OurDecimalField, OurSelectField,
    OurTimeField, )
from altair.app.ticketing.helpers import label_text_for
from altair.app.ticketing.core.models import SalesSegmentKindEnum, Event, StockHolder, Account

logger = logging.getLogger(__name__)

def fix_boolean(formdata, name):
    if formdata:
        if name in formdata:
            if not formdata[name]:
                del formdata[name]

def append_error(field, error):
    if not hasattr(field.errors, 'append'):
        field.errors = list(field.errors)
    field.errors.append(error)

class SalesSegmentGroupForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        fix_boolean(formdata, 'seat_choice')
        fix_boolean(formdata, 'public')
        fix_boolean(formdata, 'reporting')
        super(SalesSegmentGroupForm, self).__init__(formdata, obj, prefix, **kwargs)
        if 'event_id' in kwargs:
            event = Event.get(kwargs['event_id'])
            self.copy_to_stock_holder.choices = [('', u'変更しない')] + [
                (str(sh.id), sh.name) for sh in StockHolder.get_own_stock_holders(event)
            ]
            self.account_id.choices = [
                (a.id, a.name) for a in Account.query.filter_by(organization_id=event.organization_id)
            ]
            self.account_id.default = event.account_id
            for field_name in ('margin_ratio', 'refund_ratio', 'printing_fee', 'registration_fee'):
                field = getattr(self, field_name)
                field.default = getattr(event.organization.setting, field_name)
            self.process(formdata, obj, **kwargs)
        if 'new_form' in kwargs:
            self.reporting.data = True

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()]
    )
    kind = SelectField(
        label=u'種別',
        validators=[Required()],
        choices=[(k, getattr(SalesSegmentKindEnum, k).v) for k in SalesSegmentKindEnum.order.v],
        coerce=str,
    )
    name = TextField(
        label=u'表示名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    start_at = OurDateTimeField(
        label=u'販売開始日時',
        validators=[],
        format='%Y-%m-%d %H:%M',
        hide_on_new=False
    )
    start_day_prior_to_performance = OurIntegerField(
        label=u'販売開始日時(公演開始までの日数)',
        validators=[Optional()],
        hide_on_new=False
    )
    start_time = OurTimeField(
        label=u'販売開始日時(時刻)',
        validators=[],
        hide_on_new=False
    )
    end_day_prior_to_performance = OurIntegerField(
        label=u'販売終了日時(公演開始までの日数)',
        validators=[Optional()],
        hide_on_new=False
    )
    end_time = OurTimeField(
        label=u'販売終了日時(時刻)',
        validators=[],
        hide_on_new=False
    )
    end_at = OurDateTimeField(
        label=u'販売終了日時',
        validators=[],
        format='%Y-%m-%d %H:%M',
        hide_on_new=False
    )

    seat_choice = OurBooleanField(
        label=u'座席選択可',
        widget=CheckboxInput(),
    )
    upper_limit = OurIntegerField(
        label=u'購入上限枚数',
        default=10,
        validators=[RequiredOnUpdate()],
        hide_on_new=True
    )
    order_limit = OurIntegerField(
        label=u'購入回数制限',
        default=0,
        validators=[RequiredOnUpdate()],
        hide_on_new=True
    )
    public = OurBooleanField(
        label=u'一般公開',
        hide_on_new=True
    )
    reporting = OurBooleanField(
        label=u'レポート対象',
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
    copy = IntegerField(
        label='',
        default=0,
        widget=CheckboxInput(),
    )
    copy_payment_delivery_method_pairs = IntegerField(
        label=u'決済・引取方法をコピーする',
        default=0,
        widget=CheckboxInput(),
    )
    copy_products = IntegerField(
        label=u'商品をコピーする',
        default=0,
        widget=CheckboxInput(),
    )
    copy_to_stock_holder = SelectField(
        label=u'商品在庫の配券先を一括設定する',
        validators=[Optional()],
        choices=[],
        coerce=str,
    )
    auth3d_notice = TextAreaField(
        label=u'クレジットカード 3D認証フォーム 注記事項',
        validators=[Optional()],
    )

    def _validate_start(self, *args, **kwargs):
        msg1 = u"{0},{1}どちらかを指定してください".format(
            label_text_for(self.start_at),
            label_text_for(self.start_day_prior_to_performance)
        )
        msg2 = u"{0},{1}は両方指定してください".format(
            label_text_for(self.start_day_prior_to_performance),
            label_text_for(self.start_time)
        )

        if self.start_at.data:
            if self.start_day_prior_to_performance.data or self.start_time.data:
                append_error(self.start_at, ValidationError(msg1))
                return False
        else:
            if bool(int(bool(self.start_day_prior_to_performance.data)) ^ int(bool(self.start_time.data))):
                append_error(self.start_day_prior_to_performance, ValidationError(msg2))
                return False
            else:
                if not self.start_day_prior_to_performance.data:
                    append_error(self.start_at, ValidationError(msg1))
                    return False
        return True

    def _validate_end(self, *args, **kwargs):
        msg1 = u"{0},{1}どちらかを指定してください".format(
            label_text_for(self.end_at),
            label_text_for(self.end_day_prior_to_performance)
        )
        msg2 = u"{0},{1}は両方指定してください".format(
            label_text_for(self.end_day_prior_to_performance),
            label_text_for(self.end_time)
        )

        if self.end_at.data:
            if self.end_day_prior_to_performance.data or self.end_time.data:
                append_error(self.end_at, ValidationError(msg1))
                return False
        else:
            if bool(int(bool(self.end_day_prior_to_performance.data)) ^ int(bool(self.end_time.data))):
                append_error(self.end_day_prior_to_performance, ValidationError(msg2))
                return False
            else:
                if not self.end_day_prior_to_performance.data:
                    append_error(self.end_at, ValidationError(msg1))
                    return False
        return True

    def _validate_term(self, *args, **kwargs):
        if self.end_at.data is not None and self.start_at.data is not None and self.end_at.data < self.start_at.data:
            append_error(self.end_at, ValidationError(u'開演日時より過去の日時は入力できません'))
            return False
        return True

    def validate(self, *args, **kwargs):
        return all([fn(*args, **kwargs) for fn in [
            super(type(self), self).validate,
            self._validate_start,
            self._validate_end,
            self._validate_term
            ]])


class MemberGroupToSalesSegmentForm(OurForm):
    def _get_translations(self):
        return Translations()

    def __init__(self, formdata=None, obj=None, prefix='', membergroups=None, **kwargs):
        super(MemberGroupToSalesSegmentForm, self).__init__(formdata, obj, prefix, **kwargs)
        membergroups = list(membergroups)
        self.membergroups.choices = [(unicode(s.id), s.name) for s in membergroups or []]
        self.membergroups_height = "%spx" % (len(membergroups)*20)
        if obj:
            self.membergroups.data = [unicode(s.id) for s in obj.membergroups]

    membergroups = SelectMultipleField(
        label=u"membergroups",
        choices=[],
        coerce=unicode,
    )
