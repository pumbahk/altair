# -*- coding:utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, IntegerField, BooleanField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from ticketing.formhelpers import DateTimeField, Translations, Required, NullableTextField
from ticketing.core.models import Product, SalesSegment
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

    description = TextField(
        label=u'詳細',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )

    lotting_announce_datetime = DateTimeField(
        label=u"抽選結果発表予定日",
        validators=[
            Required(),
        ],
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
        sales_segment = SalesSegment(
            sales_segment_group_id=self.data['sales_segment_group_id'],
            start_at=self.data['start_at'],
            end_at=self.data['end_at'],
            upper_limit=self.data['upper_limit'],
            seat_choice=self.data['seat_choice'],
            )
        lot = Lot(
            event=event,
            sales_segment=sales_segment,
            name=self.data['name'],
            limit_wishes=self.data['limit_wishes'],
            entry_limit=self.data['entry_limit'],
            description=self.data['description'],
            lotting_announce_datetime=self.data['lotting_announce_datetime'],
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
            Required(),
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
