# -*- coding: utf-8 -*-

import logging
from wtforms import HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError, NumberRange
from wtforms.widgets import CheckboxInput, TableWidget
from datetime import datetime, timedelta
from altair.app.ticketing.security import get_plugin_names
from altair.formhelpers import (
    OurTextField,
    OurTextAreaField,
    OurDateTimeField,
    Translations,
    Required,
    RequiredOnUpdate,
    OurForm,
    OurIntegerField,
    OurBooleanField,
    OurDecimalField,
    OurSelectField,
    OurSelectMultipleField,
    OurTimeField,
    JSONField,
    zero_as_none,
    blank_as_none
    )
from altair.formhelpers.fields.datetime import Min, Max
from altair.formhelpers.widgets.datetime import OurTimeWidget
from altair.app.ticketing.helpers import label_text_for
from altair.app.ticketing.core.models import SalesSegmentKindEnum, Event, StockHolder, Account, SalesSegmentGroup, SalesSegmentGroupSetting
from altair.app.ticketing.skidata.models import SkidataProperty
from ..sales_segments.forms import ExtraFormEditorWidget
from ..sales_segments.forms import UPPER_LIMIT_OF_MAX_QUANTITY

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
        fix_boolean(formdata, 'display_seat_no')
        fix_boolean(formdata, 'public')
        fix_boolean(formdata, 'reporting')
        fix_boolean(formdata, 'sales_counter_selectable')
        fix_boolean(formdata, 'enable_point_allocation')
        fix_boolean(formdata, 'enable_resale')
        context = kwargs.pop('context', None)
        super(SalesSegmentGroupForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.context = context
        if context.event:
            self.copy_to_stock_holder.choices = [('', u'変更しない')] + [
                (str(sh.id), sh.name) for sh in StockHolder.get_own_stock_holders(context.event)
            ]
            self.account_id.choices = [
                (a.id, a.name) for a in Account.query.filter_by(organization_id=context.event.organization_id)
            ]
            self.account_id.default = context.event.account_id
            for field_name in ('margin_ratio', 'refund_ratio', 'printing_fee', 'registration_fee'):
                field = getattr(self, field_name)
                field.default = getattr(context.event.organization.setting, field_name)
            self.event_id.data = self.event_id.default = context.event.id
            self.process(formdata, obj, **kwargs)
            if context.event.is_skidata_enable():
                props = SkidataProperty.find_sales_segment_group_props(context.organization.id)
                self.skidata_property.choices = [(p.id, p.name) for p in props]
        if 'new_form' in kwargs:
            self.reporting.data = True
            self.enable_point_allocation.data = True if context.organization.setting.enable_point_allocation else False
        if obj is not None and hasattr(obj, u'skidata_property'):
            skidata_property = obj.skidata_property
            self.skidata_property.data = skidata_property.id if skidata_property else None

        stock_holders = StockHolder.get_own_stock_holders(event=context.event)
        self.stock_holder_id.choices = [(sh.id, sh.name) for sh in stock_holders]

        self.public_kind = [
            SalesSegmentKindEnum.normal.k,
            SalesSegmentKindEnum.early_firstcome.k,
            SalesSegmentKindEnum.added_sales.k,
            SalesSegmentKindEnum.early_lottery.k,
            SalesSegmentKindEnum.added_lottery.k,
            SalesSegmentKindEnum.first_lottery.k,
            SalesSegmentKindEnum.sales_counter.k
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()]
    )
    kind = OurSelectField(
        label=u'種別',
        validators=[Required()],
        choices=[(k, getattr(SalesSegmentKindEnum, k).v) for k in SalesSegmentKindEnum.order.v],
        coerce=str,
        help=u'''
          この販売区分の用途を指定します。<br />
          ・販売用途<br />
          　一般発売, 先行先着, 追加発売, 窓口販売<br />
          ・抽選用途<br />
          　先行抽選, 追加抽選, 最速抽選<br />
          ・インナー等一般公開しないもの<br />
          　当日券, 関係者, その他
        '''
    )
    name = OurTextField(
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
        hide_on_new=False,
        widget=OurTimeWidget(omit_second=True),
        missing_value_defaults=dict(hour=Min, minute=Min, second=Min)
    )
    end_day_prior_to_performance = OurIntegerField(
        label=u'販売終了日時(公演開始までの日数)',
        validators=[Optional()],
        hide_on_new=False
    )
    end_time = OurTimeField(
        label=u'販売終了日時(時刻)',
        validators=[],
        hide_on_new=False,
        widget=OurTimeWidget(omit_second=True),
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max)
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
        hide_on_new=False
    )
    display_seat_no = OurBooleanField(
        label=label_text_for(SalesSegmentGroupSetting.display_seat_no),
        widget=CheckboxInput(),
        hide_on_new=True
    )
    max_quantity = OurIntegerField(
        label=label_text_for(SalesSegmentGroup.max_quantity),
        default=10,
        validators=[RequiredOnUpdate(),
                    NumberRange(min=0, max=UPPER_LIMIT_OF_MAX_QUANTITY, message=u'範囲外です'),
                    ],
        hide_on_new=True
    )
    max_quantity_per_user = OurIntegerField(
        label=label_text_for(SalesSegmentGroupSetting.max_quantity_per_user),
        default=0,
        filters=[zero_as_none],
        validators=[Optional()],
        hide_on_new=True
    )
    max_product_quatity = OurIntegerField(
        label=u'商品購入上限数',
        default=None,
        filters=[zero_as_none],
        validators=[Optional()],
        hide_on_new=True
    )
    order_limit = OurIntegerField(
        label=u'購入回数制限',
        default=0,
        validators=[Optional()],
        hide_on_new=True
    )
    public = OurBooleanField(
        label=u'一般公開',
        hide_on_new=False
    )
    disp_orderreview = OurBooleanField(
        label=u'マイページへの購入履歴表示/非表示',
        hide_on_new=True
    )
    disp_agreement = OurBooleanField(
        label=u'規約の表示/非表示',
        hide_on_new=True
    )
    agreement_body = OurTextAreaField(
        label=u'規約内容',
        validators=[Optional()],
        hide_on_new=True
    )
    reporting = OurBooleanField(
        label=u'レポート対象',
        hide_on_new=True
    )
    sales_counter_selectable = OurBooleanField(
        label=label_text_for(SalesSegmentGroupSetting.sales_counter_selectable),
        hide_on_new=True,
        help=u'''
          窓口業務でこの販売区分を選択可能にします。<br />
          例外として「公演管理編集」権限があるオペレーターは常に選択可能です。
        '''
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
    copy = OurIntegerField(
        label='',
        default=0,
        widget=CheckboxInput(),
    )
    copy_payment_delivery_method_pairs = OurIntegerField(
        label=u'決済・引取方法をコピーする',
        default=1,
        widget=CheckboxInput(),
    )
    copy_products = OurIntegerField(
        label=u'商品をコピーする',
        default=1,
        widget=CheckboxInput(),
    )
    copy_to_stock_holder = OurSelectField(
        label=u'商品在庫の配券先を一括設定する',
        validators=[Optional()],
        choices=[],
        hide_on_new=True,
        coerce=str,
    )
    auth3d_notice = OurTextAreaField(
        label=u'クレジットカード 3D認証フォーム 注記事項',
        validators=[Optional()],
        hide_on_new=True
    )
    extra_form_fields = JSONField(
        label=u'追加フィールド',
        filters=[blank_as_none],
        validators=[Optional()],
        widget=ExtraFormEditorWidget()
        )
    stock_holder_id = OurSelectField(
        label=u'配券先(予約がある商品明細以外は、すべて変更されます)',
        validators=[Optional()],
        choices=[],
        coerce=int
        )
    display_order = OurIntegerField(
        label=u'表示順',
        default=1,
        validators=[Required()],
        hide_on_new=False
    )
    enable_point_allocation = OurBooleanField(
        label=label_text_for(SalesSegmentGroupSetting.enable_point_allocation),
        default=False,
        validators=[Optional()],
        hide_on_new=True
    )
    skidata_property = OurSelectField(
        label=u'SKIDATAチケット種別',
        validators=[Optional()],
        coerce=int
    )
    enable_resale = OurBooleanField(
        label=u'リセール出品可否',
        hide_on_new=True
    )

    def _validate_skidata_property(self, *args, **kwargs):
        if not self.skidata_property.data:
            return True
        from sqlalchemy.orm.exc import NoResultFound
        try:
            SkidataProperty.find_by_id(self.skidata_property.data)
        except NoResultFound:
            append_error(self.skidata_property, ValidationError(u'対象のデータが存在しません'))
            return False
        return True

    def _validate_start(self, *args, **kwargs):
        msg1 = u"{0},{1}どちらかを指定してください".format(
            label_text_for(self.start_at),
            label_text_for(self.start_day_prior_to_performance)
        )
        msg2 = u"{0},{1}は両方指定してください".format(
            label_text_for(self.start_day_prior_to_performance),
            label_text_for(self.start_time)
        )

        if self.start_at.data is not None:
            if self.start_day_prior_to_performance.data is not None or self.start_time.data is not None:
                append_error(self.start_at, ValidationError(msg1))
                return False
        else:
            if bool(int(self.start_day_prior_to_performance.data is not None) ^ int(self.start_time.data is not None)):
                append_error(self.start_day_prior_to_performance, ValidationError(msg2))
                return False
            else:
                if self.start_day_prior_to_performance.data is None:
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

        if self.end_at.data is not None:
            if self.end_day_prior_to_performance.data is not None or self.end_time.data is not None:
                append_error(self.end_at, ValidationError(msg1))
                return False
        else:
            if bool(int(self.end_day_prior_to_performance.data is not None) ^ int(self.end_time.data is not None)):
                append_error(self.end_day_prior_to_performance, ValidationError(msg2))
                return False
            else:
                if self.end_day_prior_to_performance.data is None:
                    append_error(self.end_at, ValidationError(msg1))
                    return False
        return True

    def _start_for_performance(self, performance):
        """ 公演開始日に対応した販売開始日時を算出
        start_atによる直接指定の場合は、start_atを利用する
        """

        if self.start_at.data:
            return self.start_at.data

        if self.start_time.data is None or self.start_day_prior_to_performance.data is None:
            return None
        s = performance.start_on
        d = datetime(s.year, s.month, s.day,
                     self.start_time.data.hour, self.start_time.data.minute)
        d -= timedelta(days=self.start_day_prior_to_performance.data)
        return d


    def _end_for_performance(self, performance):
        """ 公演開始日に対応した販売終了日時を算出
        end_atによる直接指定の場合は、end_atを利用する
        """
        if self.end_at.data:
            return self.end_at.data

        if self.end_time.data is None or self.end_day_prior_to_performance.data is None:
            return None

        s = performance.start_on
        d = datetime(s.year, s.month, s.day,
                     self.end_time.data.hour, self.end_time.data.minute)
        d -= timedelta(days=self.end_day_prior_to_performance.data)
        return d

    def _validate_display_seat_no(self, *args, **kwargs):
        if self.id.data:
            if self.seat_choice.data and not self.display_seat_no.data:
                append_error(self.display_seat_no, ValidationError(u'座席選択可の場合は座席番号は非表示にできません'))
                return False
        return True

    def _validate_term(self, *args, **kwargs):
        if self.end_at.data is not None and self.start_at.data is not None and self.end_at.data < self.start_at.data:
            append_error(self.end_at, ValidationError(u'開演日時より過去の日時は入力できません'))
            return False

        # コンビニ発券開始日時をチェックする
        if self.id.data:
            from altair.app.ticketing.events.sales_segments.forms import validate_issuing_start_at
            from altair.app.ticketing.events.sales_segments.exceptions import IssuingStartAtOutTermException
            ssg = SalesSegmentGroup.query.filter_by(id=self.id.data).one()
            for ss in ssg.sales_segments:
                if not ss.performance or not ss.use_default_end_at:
                    continue
                performance_start_on = ss.performance.start_on
                performance_end_on = ss.performance.end_on or ss.performance.start_on
                ss_start_at = self._start_for_performance(ss.performance)
                ss_end_at = self._end_for_performance(ss.performance)
                if ss_start_at is None:
                    continue
                for pdmp in ss.payment_delivery_method_pairs:
                    try:
                        validate_issuing_start_at(
                            performance_start_on=performance_start_on,
                            performance_end_on=performance_end_on,
                            sales_segment_start_at=ss_start_at,
                            sales_segment_end_at=ss_end_at,
                            pdmp=pdmp)
                    except IssuingStartAtOutTermException as e:
                        append_error(self.end_at, ValidationError(e.message))
                        return False

        return True

    def _validate_public(self, *args, **kwargs):
        if self.public.data and self.kind.data not in self.public_kind:
            append_error(self.kind, ValidationError(u'この種別は一般公開できません'))
            return False
        return True

    def validate(self, *args, **kwargs):
        return all([fn(*args, **kwargs) for fn in [
            super(type(self), self).validate,
            self._validate_start,
            self._validate_end,
            self._validate_term,
            self._validate_display_seat_no,
            self._validate_public
            ]])


class SalesSegmentGroupAndLotForm(SalesSegmentGroupForm):
    lot_form_flag = HiddenField(default=False)
    original_kind = HiddenField(default=False)
    lot_name = OurTextField(
        label=u'抽選名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    limit_wishes = OurIntegerField(
        label=u'希望取得上限',
        validators=[
            Required(),
            NumberRange(min=1, message=u'1以上で入力してしてください')
        ],
    )

    entry_limit = OurIntegerField(
        label=u'申込上限回数',
        validators=[
            Required(),
        ],
    )

    description = OurTextAreaField(
        label=u'注意文言',
        default=u'',
    )

    lotting_announce_datetime = OurDateTimeField(
        label=u"抽選結果発表予定日",
        format='%Y-%m-%d %H:%M',
        validators=[
            Required(),
        ],
    )

    lotting_announce_timezone = OurSelectField(
        label=u"抽選予定時間帯",
        validators=[
            Optional(),
        ],
        choices=[
              ('', u'時間まで表示')
            , ('morning', u'午前(6:00 - 12:00)')
            , ('day', u'昼以降(12:00 - 16:00)')
            , ('evening', u'夕方以降(16:00 - 19:00)')
            , ('night', u'夜(19:00 - 2:00)')
            , ('next_morning', u'明朝(翌2:00 - 翌6:00)')
        ],
    )

    custom_timezone_label = OurTextField(
        label=u'抽選時間帯カスタムラベル（抽選予定時間帯より優先）',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    lot_entry_user_withdraw = OurBooleanField(
        label=u'抽選申込ユーザ取消',
        default=True,
        widget=CheckboxInput()
    )

    def _auth_types(field):
        retval = [('', u'なし')]
        if hasattr(field._form, 'context'):
            retval.extend(get_plugin_names(field._form.context.request))
        return retval

    auth_type = OurSelectField(
        label=u"認証方法",
        choices=_auth_types
    )

    def validate_kind(self, sales_segment_group):
        # 抽選に申込があった場合は、抽選の種別から一般の種別に変更できない
        if self.original_kind.data.count("lottery") and not self.kind.data.count("lottery"):
            for lot in sales_segment_group.get_lots():
                if lot.entries:
                    append_error(self.kind, ValidationError(u"抽選に申込があるため、種別の変更はできません。"))
                    return False
        return True

    def validate(self, *args, **kwargs):
        if not all([fn(*args, **kwargs) for fn in [
            self._validate_start,
            self._validate_end,
            self._validate_term,
            self._validate_display_seat_no,
            self._validate_public,
            self._validate_skidata_property
                ]]):
            return False

        """
        以下の場合抽選のバリデーションを実施しない
        ・一般の種別のもの
        ・抽選から抽選に更新した場合
        """
        if not self.kind.data.count("lottery"):
            return True

        if self.original_kind.data:
            if self.original_kind.data.count("lottery") and self.kind.data.count("lottery"):
                return True

        # 抽選のバリデーション
        return all([fn((), {}) for fn in [
            self.lot_name.validate,
            self.limit_wishes.validate,
            self.entry_limit.validate,
            self.description.validate,
            self.lotting_announce_datetime.validate,
            self.lotting_announce_timezone.validate,
            self.custom_timezone_label.validate,
        ]])


class CheckedOurSelectMultipleField(OurSelectMultipleField):
    def iter_choices(self):
        current_value = self.data if self.data is not None else self.coerce(self.default)
        for value, label in self.choices:
            yield (value, label, self.coerce(value) == current_value)


class CopyLotForm(SalesSegmentGroupAndLotForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(SalesSegmentGroupAndLotForm, self).__init__(formdata, obj, prefix, **kwargs)
        perfs = self.context.lot.sales_segment.event.performances
        self.performances.choices = [(p.id, p.name) for p in perfs]

    sales_segment_group = HiddenField()
    lot = HiddenField()
    performances = OurSelectMultipleField(
        label=u'コピーするパフォーマンス',
        validators=[Optional()],
        choices=[],
        widget=TableWidget(),
        option_widget=CheckboxInput(),
        coerce=int,
    )

    def set_hidden_data(self, lot):
        self.lot.data = lot
        self.sales_segment_group.data = lot.sales_segment.sales_segment_group

    def create_by_lot(self, lot):
        self.set_hidden_data(lot)
        self.lot_name.data = lot.name
        self.limit_wishes.data = lot.limit_wishes
        self.entry_limit.data = lot.entry_limit
        self.description.data = lot.description
        self.lotting_announce_datetime.data = lot.lotting_announce_datetime
        self.lotting_announce_timezone.data = lot.lotting_announce_timezone
        self.custom_timezone_label.data = lot.custom_timezone_label
        self.auth_type.data = lot.auth_type
        self.lot_entry_user_withdraw.data = lot.lot_entry_user_withdraw
        self.performances.data = [s.id for s in lot.performances]

    def create_exclude_performance(self):
        exclude_performances = []
        for sales_segment in self.sales_segment_group.data.sales_segments:
            if not sales_segment.performance:
                continue
            if sales_segment.performance.id not in self.performances.data:
                exclude_performances.append(sales_segment.performance.id)
        return exclude_performances

    def validate(self, *args, **kwargs):
        # 抽選が選択されている場合の追加のバリデーション
        return all([fn((), {}) for fn in [
            self.lot_name.validate,
            self.limit_wishes.validate,
            self.entry_limit.validate,
            self.description.validate,
            self.lotting_announce_datetime.validate,
            self.lotting_announce_timezone.validate,
            self.custom_timezone_label.validate,
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

    membergroups = OurSelectMultipleField(
        label=u"membergroups",
        choices=[],
        widget=TableWidget(),
        option_widget=CheckboxInput(),
        coerce=unicode,
    )
