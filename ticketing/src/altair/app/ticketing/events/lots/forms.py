# -*- coding:utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.validators import Optional, AnyOf, Length, Email, Regexp

from altair.formhelpers import (
    DateTimeField, Translations, Required, DateField, Max, OurDateWidget,
    after1900, CheckboxMultipleSelect, BugFreeSelectMultipleField,
    NFKC, Zenkaku, Katakana, strip_spaces, ignore_space_hyphen,
)
from altair.app.ticketing.core.models import ReportFrequencyEnum, ReportPeriodEnum
from altair.app.ticketing.core.models import Product, SalesSegment, SalesSegmentGroup, Operator
from altair.app.ticketing.events.sales_segments.resources import SalesSegmentGroupCreate
from altair.app.ticketing.lots.models import Lot

from .models import LotEntryReportSetting

class LotForm(Form):
    name = TextField(
        label=u'抽選名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    limit_wishes = IntegerField(
        label=u'希望上限',
        validators=[
            Required(),
        ],
    )

    entry_limit = IntegerField(
        label=u'申し込み上限',
        validators=[
            Required(),
        ],
    )

    description = TextAreaField(
        label=u'詳細',
        validators=[
            Required(),
        ],
    )

    lotting_announce_datetime = DateTimeField(
        label=u"抽選結果発表予定日",
        validators=[
            Required(),
        ],
    )

    auth_type = SelectField(
        label=u"認証方法",
        validators=[
            ## 認証方法一覧にあるかって確認はchocesでやってくれるのだろうか
        ],
        choices=[('', ''), ('rakuten', 'rakuten'), ('fc_auth', 'fc_auth')],
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
        label=u"販売開始",
        validators=[
            Required(),
        ],
    )

    end_at = DateTimeField(
        label=u"販売終了",
        validators=[
            Required(),
        ],
    )

    upper_limit = IntegerField(
        label=u'購入上限',
        validators=[
            Required(),
        ],
    )
    seat_choice = BooleanField(
        label=u"席選択可能",
        validators=[
            Required(),
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
            auth_type=self.data['auth_type'],
            )
        creator = SalesSegmentGroupCreate(sales_segment_group)
        sales_segment = creator.create_sales_lot_segment(lot)
        sales_segment.sales_segment_group_id=self.data['sales_segment_group_id']
        sales_segment.start_at=self.data['start_at']
        sales_segment.end_at=self.data['end_at']
        sales_segment.upper_limit=self.data['upper_limit']
        sales_segment.seat_choice=self.data['seat_choice']
        sales_segment.account_id=sales_segment_group.account_id
        sales_segment.auth3d_notice=self.data['auth3d_notice']

        return lot
    

    def update_lot(self, lot):
        sales_segment = lot.sales_segment
        sales_segment.sales_segment_group_id=self.data['sales_segment_group_id']
        sales_segment.start_at=self.data['start_at']
        sales_segment.end_at=self.data['end_at']
        sales_segment.upper_limit=self.data['upper_limit']
        sales_segment.seat_choice=self.data['seat_choice']
        sales_segment.auth3d_notice = self.data['auth3d_notice']

        lot.name=self.data['name']
        lot.limit_wishes=self.data['limit_wishes']
        lot.entry_limit=self.data['entry_limit']
        lot.description=self.data['description']
        lot.lotting_announce_datetime=self.data['lotting_announce_datetime']
        lot.auth_type = self.data['auth_type']

        return lot

class ProductForm(Form):
    name = TextField(
        label=u'商品名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    price = TextField(
        label=u'金額',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
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

    performance_id = SelectField(
        label=u'公演',
        validators=[
            Required(),
        ],
        choices=[],
        coerce=int,
    )


    def create_product(self, lot):
        product = Product(
            name=self.data["name"],
            price=self.data["price"],
            display_order=self.data["display_order"],
            description=self.data["description"],
            seat_stock_type_id=self.data["seat_stock_type_id"],
            performance_id=self.data["performance_id"],
            sales_segment=lot.sales_segment)
        return product

    def apply_product(self, product):
        product.name = self.data["name"]
        product.price = self.data["price"]
        product.display_order = self.data["display_order"]
        product.description = self.data["description"]
        product.seat_stock_type_id = self.data["seat_stock_type_id"]
        product.performance_id = self.data["performance_id"]

        return product


class SearchEntryForm(Form):
    """
    販売区分
    決済方法
    引き取り方法
    ステータス
    """
    entry_no = TextField(
        label=u'予約番号',
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

    include_canceled = BooleanField(
        label=u"キャンセルした申込を含める",
        validators=[
            Required(),
        ],
    )

    electing = BooleanField(
        label=u"当選予定",
        validators=[
            Required(),
        ],
    )

    elected = BooleanField(
        label=u"当選",
        validators=[
            Required(),
        ],
    )

    rejecting = BooleanField(
        label=u"落選予定",
        validators=[
            Required(),
        ],
    )

    rejected = BooleanField(
        label=u"落選",
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




class LotEntryReportMailForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        if 'organization_id' in kwargs:
            operators = Operator.query.filter_by(organization_id=kwargs['organization_id']).all()
            self.operator_id.choices = [('', '')] + [(o.id, o.name) for o in operators]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Optional()],
    )
    lot_id = HiddenField(
        validators=[Optional()],
    )
    operator_id = SelectField(
        label=u'オペレータ',
        validators=[Optional()],
        choices=[],
        coerce=lambda v: None if not v else int(v)
    )
    name = TextField(
        label=u'名前',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    email = TextField(
        label=u'メールアドレス',
        validators=[
            Optional(),
            Email()
        ]
    )
    frequency = SelectField(
        label=u'送信頻度',
        validators=[Required()],
        choices=[(kind.v[0], kind.v[1]) for kind in ReportFrequencyEnum],
        coerce=int
    )
    day_of_week = SelectField(
        label=u'送信曜日',
        validators=[Optional()],
        choices=[
            ('', ''),
            (1, u'月'),
            (2, u'火'),
            (3, u'水'),
            (4, u'木'),
            (5, u'金'),
            (6, u'土'),
            (7, u'日'),
        ],
        coerce=lambda v: None if not v else int(v)
    )
    time = SelectField(
        label=u'送信時間',
        validators=[Required()],
        choices=[(h, u'%d時' % h) for h in range(0, 24)],
        coerce=lambda v: None if not v else int(v)
    )
    start_on = DateTimeField(
        label=u'開始日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_on = DateTimeField(
        label=u'終了日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    period = SelectField(
        label=u'レポート対象期間',
        validators=[Required()],
        choices=sorted([(kind.v[0], kind.v[1]) for kind in ReportPeriodEnum]),
        coerce=int
    )

    def validate_operator_id(form, field):
        if field.data:
            q = LotEntryReportSetting.query_reporting_about(
                event_id=form.event_id.data,
                lot_id=form.lot_id.data,
                time=form.time.data,
                frequency=form.frequency.data,
                day_of_week=form.day_of_week.data,
            ).filter(LotEntryReportSetting.operator_id==form.operator_id.data)


            if q.count() > 0:
                raise ValidationError(u'既に登録済みのオペレーターです')

    def validate_email(form, field):
        if field.data:
            q = LotEntryReportSetting.query_reporting_about(
                event_id=form.event_id.data,
                lot_id=form.lot_id.data,
                time=form.time.data,
                frequency=form.frequency.data,
                day_of_week=form.day_of_week.data,
            ).filter(LotEntryReportSetting.email==form.email.data)

            if q.count() > 0:
                raise ValidationError(u'既に登録済みのメールアドレスです')

    def validate_frequency(form, field):
        if field.data:
            if field.data == ReportFrequencyEnum.Weekly.v[0] and not form.day_of_week.data:
                raise ValidationError(u'週次の場合は曜日を必ず選択してください')

    def process(self, formdata=None, obj=None, **kwargs):
        super(type(self), self).process(formdata, obj, **kwargs)
        if not self.event_id.data:
            self.event_id.data = None
        if not self.lot_id.data:
            self.lot_id.data = None

    def validate(self):
        status = super(type(self), self).validate()
        if status:
            # event_id or lot_id のどちらか必須
            if (self.event_id.data and self.lot_id.data) or (not self.event_id.data and not self.lot_id.data):
                self.event_id.errors.append(u'エラーが発生しました')
                status = False
            # operator_id or email のどちらか必須
            email_length = len(self.email.data) if self.email.data else 0
            if not self.operator_id.data and email_length == 0:
                self.operator_id.errors.append(u'オペレーター、またはメールアドレスのいずれかを入力してください')
                status = False
            if self.operator_id.data and email_length > 0:
                self.operator_id.errors.append(u'オペレーター、メールアドレスの両方を入力することはできません')
                status = False
        return status

    def sync(self, obj):
        obj.lot_id = self.lot_id.data or None
        obj.event_id = self.event_id.data or None
        obj.operator_id = self.operator_id.data
        obj.name = self.name.data
        obj.email = self.email.data
        obj.frequency = self.frequency.data
        obj.day_of_week = self.day_of_week.data
        obj.time = self.time.data
        obj.start_on = self.start_on.data
        obj.end_on = self.end_on.data
        obj.period = self.period.data

