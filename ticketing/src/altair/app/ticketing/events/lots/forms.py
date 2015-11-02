# -*- coding:utf-8 -*-

import logging
from datetime import datetime

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, IntegerField, BooleanField, TextAreaField
from wtforms.widgets import CheckboxInput
from wtforms.validators import Length, Optional, ValidationError, NumberRange

from altair.app.ticketing.security import get_plugin_names
from altair.formhelpers import (
    DateTimeField, Translations, Required, Max, OurDateWidget, Email,
    after1900, LazySelectMultipleField, OurBooleanField, OurDecimalField,
    OurSelectField, SwitchOptional,
    )
from altair.app.ticketing.core.models import ReportFrequencyEnum, ReportPeriodEnum
from altair.app.ticketing.core.models import Product, SalesSegment, SalesSegmentGroup, Operator, ReportRecipient
from altair.app.ticketing.events.sales_segments.resources import SalesSegmentAccessor
from altair.app.ticketing.lots.models import Lot
from altair.app.ticketing.events.sales_reports.forms import ReportSettingForm

from .models import LotEntryReportSetting

logger = logging.getLogger(__name__)

UPPER_LIMIT_OF_MAX_QUANTITY_LOTS = 20  # SEJの場合21個以上だとエラーになってしまうので20で縛る


class LotForm(Form):
    name = TextField(
        label=u'抽選名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    limit_wishes = IntegerField(
        label=u'希望取得上限',
        validators=[
            Required(),
        ],
    )

    entry_limit = IntegerField(
        label=u'申込上限回数',
        validators=[
            Required(),
        ],
    )

    description = TextAreaField(
        label=u'注意文言',
        default=u'',
    )

    lotting_announce_datetime = DateTimeField(
        label=u"抽選結果発表予定日",
        format='%Y-%m-%d %H:%M',
        validators=[
            Required(),
        ],
    )

    lotting_announce_timezone = SelectField(
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

    custom_timezone_label = TextField(
        label=u'抽選時間帯カスタムラベル（抽選予定時間帯より優先）',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    def _auth_types(field):
        retval = [('', u'なし')]
        retval.extend(get_plugin_names(field._form.context.request))
        return retval

    auth_type = OurSelectField(
        label=u"認証方法",
        choices=_auth_types
    )

    mail_send_now = OurBooleanField(
        label=u'当選／落選登録時に送信',
        default=False,
        widget=CheckboxInput()
    )

    ### 販売区分

    sales_segment_group_id = SelectField(
        label=u"販売区分グループ",
        validators=[
            Required(),
        ],
        choices=[],
    )

    start_at = DateTimeField(
        label=u"販売開始日時",
        format='%Y-%m-%d %H:%M',
        validators=[
            SwitchOptional('use_default_start_at'),
            Required(),
        ],
    )

    use_default_start_at = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput()
    )

    end_at = DateTimeField(
        label=u"販売終了日時",
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
            hour=Max,
            minute=Max,
            second=Max,
        ),
        validators=[
            SwitchOptional('use_default_end_at'),
            Required(),
        ],
    )

    use_default_end_at = OurBooleanField(
        label=u'グループの値を利用',
        default=True,
        widget=CheckboxInput(),
    )

    max_quantity = IntegerField(
        label=u'購入上限枚数',
        validators=[
            Required(),
            NumberRange(min=0, max=UPPER_LIMIT_OF_MAX_QUANTITY_LOTS, message=u'範囲外です'),
        ],
    )
    auth3d_notice = TextAreaField(
        label=u'クレジットカード 3D認証フォーム 注記事項',
        validators=[Optional()],
    )



    def create_lot(self, event):
        sales_segment_group = SalesSegmentGroup.query.filter(SalesSegmentGroup.id==self.data['sales_segment_group_id']).one()

        lot = Lot(
            event=event,
            organization_id=event.organization_id,
            name=self.data['name'],
            limit_wishes=self.data['limit_wishes'],
            entry_limit=self.data['entry_limit'],
            description=self.data['description'],
            lotting_announce_datetime=self.data['lotting_announce_datetime'],
            lotting_announce_timezone=self.data['lotting_announce_timezone'],
            custom_timezone_label=self.data['custom_timezone_label'],
            auth_type=self.data['auth_type'],
            )
        accessor = SalesSegmentAccessor()
        sales_segment = accessor.create_sales_segment_for_lot(sales_segment_group, lot)
        sales_segment.sales_segment_group_id=self.data['sales_segment_group_id']

        sales_segment.use_default_start_at=self.data['use_default_start_at']
        if sales_segment.use_default_start_at:
            sales_segment.start_at=sales_segment_group.start_at
        else:
            sales_segment.start_at=self.data['start_at']

        sales_segment.use_default_end_at=self.data['use_default_end_at']
        if sales_segment.use_default_end_at:
            sales_segment.end_at=sales_segment_group.end_at
        else:
            sales_segment.end_at=self.data['end_at']

        sales_segment.max_quantity=self.data['max_quantity']
        sales_segment.seat_choice=False
        sales_segment.account_id=sales_segment_group.account_id
        sales_segment.auth3d_notice=self.data['auth3d_notice']

        return lot


    def update_lot(self, lot):
        sales_segment = lot.sales_segment
        sales_segment.sales_segment_group_id=self.data['sales_segment_group_id']
        sales_segment.max_quantity=self.data['max_quantity']
        sales_segment.seat_choice=False
        sales_segment.auth3d_notice = self.data['auth3d_notice']

        sales_segment_group = sales_segment.sales_segment_group
        sales_segment.use_default_start_at=self.data['use_default_start_at']
        if sales_segment.use_default_start_at:
            sales_segment.start_at=sales_segment_group.start_at
        else:
            sales_segment.start_at=self.data['start_at']

        sales_segment.use_default_end_at=self.data['use_default_end_at']
        if sales_segment.use_default_end_at:
            sales_segment.end_at=sales_segment_group.end_at
        else:
            sales_segment.end_at=self.data['end_at']

        lot.name=self.data['name']
        lot.limit_wishes=self.data['limit_wishes']
        lot.entry_limit=self.data['entry_limit']
        lot.description=self.data['description']
        lot.lotting_announce_datetime=self.data['lotting_announce_datetime']
        lot.lotting_announce_timezone=self.data['lotting_announce_timezone']
        lot.custom_timezone_label=self.data['custom_timezone_label']
        lot.auth_type = self.data['auth_type']
        lot.mail_send_now = self.data['mail_send_now']

        return lot

    def _validate_terms(self):
        ssg = SalesSegmentGroup.query.filter_by(id=self.sales_segment_group_id.data).one()
        ss_start_at = self.start_at.data
        ss_end_at = self.end_at.data
        if self.use_default_start_at.data:
            ss_start_at = ssg.start_at
        if self.use_default_end_at.data:
            ss_end_at = ssg.end_at

        # 販売開始日時と販売終了日時の前後関係をチェックする
        if ss_start_at is not None and ss_end_at is not None and ss_start_at > ss_end_at:
            self.start_at.errors.append(u'販売開始日時が販売終了日時より後に設定されています')
            self.end_at.errors.append(u'販売終了日時が販売開始日時より前に設定されています')
            return False

        return True

    def validate(self):
        if super(LotForm, self).validate():
            if not self._validate_terms():
                return False

            return True

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context')
        super(LotForm, self).__init__(*args, **kwargs)

class ProductForm(Form):
    name = TextField(
        label=u'商品名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    price = OurDecimalField(
        label=u'金額',
        places=0,
        validators=[
            Required(),
        ],
    )

    display_order = IntegerField(
        label=u'表示順',
        validators=[
            Required(),
        ],
    )

    description = TextField(
        label=u'詳細',
        validators=[
            #Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    seat_stock_type_id = SelectField(
        label=u'席種',
        validators=[
            Required(),
        ],
        choices=[],
        coerce=int,
    )

    performance_id = LazySelectMultipleField(
        label=u'公演',
        validators=[
            Required(),
        ],
        choices=[],
        coerce=int,
    )

    def __init__(self, formdata=None, obj=None, **kwargs):
        super(type(self), self).__init__(formdata, obj, **kwargs)
        self.obj = obj
        if self.obj and not self.performance_id.data:
            self.performance_id.data = [self.obj.performance_id]

    def create_products(self, lot):
        performance_ids = self.data["performance_id"]
        if not isinstance(performance_ids, list):
            performance_ids = [performance_ids]

        return [Product(name=self.data["name"],
                        price=self.data["price"],
                        display_order=self.data["display_order"],
                        description=self.data["description"],
                        seat_stock_type_id=self.data["seat_stock_type_id"],
                        performance_id=performance_id,
                        sales_segment=lot.sales_segment)
                for performance_id in performance_ids]

    def apply_product(self, product):
        product.name = self.data["name"]
        product.price = self.data["price"]
        product.display_order = self.data["display_order"]
        product.description = self.data["description"]
        product.seat_stock_type_id = self.data["seat_stock_type_id"]

        return product

    def validate(self):
        status = super(type(self), self).validate()
        if status:
            if self.obj is not None:
                # 販売期間内で公開済みの場合、またはこの商品が抽選申込されている場合は
                # 価格、席種の変更は不可
                product = self.obj
                now = datetime.now()
                if (product.public and product.sales_segment.public and product.sales_segment.in_term(now))\
                   or product.has_lot_entry_products():
                    error_message = u'既に販売中か抽選申込がある為、変更できません'
                    if self.price.data != str(product.price):
                        self.price.errors.append(error_message)
                        status = False
                    if self.seat_stock_type_id.data != product.seat_stock_type_id:
                        self.seat_stock_type_id.errors.append(error_message)
                        status = False
        return status

class SearchEntryForm(Form):
    """
    販売区分
    決済方法
    引き取り方法
    ステータス
    """
    entry_no = TextField(
        label=u'申込番号',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    tel = TextField(
        label=u'電話番号',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    name = TextField(
        label=u'氏名',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    email = TextField(
        label=u'メールアドレス',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    entried_from = DateTimeField(
        label=u'申込日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateWidget()
    )

    entried_to = DateTimeField(
        label=u'申込日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
            hour=Max,
            minute=Max,
            second=Max
            ),
        widget=OurDateWidget()
    )

    canceled = BooleanField(
        label=u"キャンセル",
        default=False,
        validators=[
            Required(),
        ],
    )

    withdrawed = BooleanField(
        label=u"ユーザ取消",
        default=False,
        validators=[
            Required(),
        ],
    )

    entried = BooleanField(
        label=u"申込",
        default=True,
        validators=[
            Required(),
        ],
    )

    electing = BooleanField(
        label=u"当選予定",
        default=True,
        validators=[
            Required(),
        ],
    )

    elected = BooleanField(
        label=u"当選",
        default=True,
        validators=[
            Required(),
        ],
    )

    rejecting = BooleanField(
        label=u"落選予定",
        default=True,
        validators=[
            Required(),
        ],
    )

    rejected = BooleanField(
        label=u"落選",
        default=True,
        validators=[
            Required(),
        ],
    )

    wish_order = SelectField(
        label=u'希望順位',
        validators=[],
        choices=[],
    )

class SendingMailForm(Form):

    def _get_translations(self):
        return Translations()

    recipient = TextField(
        label=u"送り先メールアドレス",
        validators=[
            Required(),
            Email(),
        ]
    )
    bcc = TextField(
        label=u"bcc",
        validators=[
            Email(),
            Optional()
        ]
    )

class LotEntryReportSettingForm(ReportSettingForm):

    lot_id = HiddenField(
        validators=[Optional()],
    )
    report_type = HiddenField(
        validators=[Optional()],
    )

    def validate_recipients(form, field):
        if field.data:
            q = LotEntryReportSetting.query_reporting_about(
                id=form.id.data,
                event_id=form.event_id.data,
                lot_id=form.lot_id.data,
                time=form.format_report_time(),
                frequency=form.frequency.data,
                day_of_week=form.day_of_week.data,
            ).join(
                LotEntryReportSetting.recipients
            ).filter(
                ReportRecipient.id.in_(field.data)
            )
            if q.count() > 0:
                raise ValidationError(u'既にレポート送信設定済みの送信先です')

    def validate_email(form, field):
        if field.data:
            q = LotEntryReportSetting.query_reporting_about(
                id=form.id.data,
                event_id=form.event_id.data,
                lot_id=form.lot_id.data,
                time=form.format_report_time(),
                frequency=form.frequency.data,
                day_of_week=form.day_of_week.data,
            ).join(
                LotEntryReportSetting.recipients
            ).filter(
                ReportRecipient.email==field.data
            )
            if q.count() > 0:
                raise ValidationError(u'既にレポート送信設定済みの送信先です')

    def validate_event_id(form, field):
        pass

    def process(self, formdata=None, obj=None, **kwargs):
        super(LotEntryReportSettingForm, self).process(formdata, obj, **kwargs)
        if not self.event_id.data:
            self.event_id.data = None
        if not self.lot_id.data:
            self.lot_id.data = None
