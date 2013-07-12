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
from ticketing.core.models import Product, SalesSegment, SalesSegmentGroup
from ticketing.lots.models import Lot

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


    def create_lot(self, event):
        sales_segment_group = SalesSegmentGroup.query.filter(SalesSegmentGroup.id==self.data['sales_segment_group_id']).one()
        sales_segment = SalesSegment(
            sales_segment_group_id=self.data['sales_segment_group_id'],
            start_at=self.data['start_at'],
            end_at=self.data['end_at'],
            upper_limit=self.data['upper_limit'],
            seat_choice=self.data['seat_choice'],
            account_id=sales_segment_group.account_id,
            )
        lot = Lot(
            event=event,
            organization_id=event.organization_id,
            sales_segment=sales_segment,
            name=self.data['name'],
            limit_wishes=self.data['limit_wishes'],
            entry_limit=self.data['entry_limit'],
            description=self.data['description'],
            lotting_announce_datetime=self.data['lotting_announce_datetime'],
            auth_type=self.data['auth_type'],
            )
        return lot
    

    def update_lot(self, lot):
        sales_segment = lot.sales_segment
        sales_segment.sales_segment_group_id=self.data['sales_segment_group_id']
        sales_segment.start_at=self.data['start_at']
        sales_segment.end_at=self.data['end_at']
        sales_segment.upper_limit=self.data['upper_limit']
        sales_segment.seat_choice=self.data['seat_choice']

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
