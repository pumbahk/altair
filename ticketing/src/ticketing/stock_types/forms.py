# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, HiddenField, BooleanField
from wtforms.validators import Required, Length, Optional
from ticketing.products.models import StockTypeEnum

class StockTypeForm(Form):

    id = HiddenField(
        label='',
        validators=[Optional()],
    )
    event_id = HiddenField(
        label='',
        validators=[Required(u'入力してください')]
    )
    name = TextField(
        label=u'名称',
        validators=[Required(u'入力してください')]
    )
    type = BooleanField(
        label=u'座席以外を登録する',
        default=StockTypeEnum.Seat.v
    )
    fill_color = TextField(
        label=u'塗りつぶし色',
    )
    fill_type = SelectField(
        label=u'塗りつぶしパターン',
        choices=[
            ('FloodFill', u'べた塗り'),
            ('LinearGradientFill', u'グラデーション（線形）'),
            ('RadialGradientFill', u'グラデーション（放射状）'),
            ('ImageTileFill', u'画像パターン'),
        ],
        coerce=str,
    )
    fill_image = TextField(
        label=u'塗りつぶしイメージ',
    )
    stroke_color = TextField(
        label=u'線の色',
    )
    stroke_width = SelectField(
        label=u'線の太さ',
        choices=[
            (1, '1'),
            (2, '2'),
            (3, '3'),
        ],
        coerce=int,
    )
    stroke_patten = SelectField(
        label=u'線の種類',
        choices=[
            ('solid', u'実線'),
            ('double', u'2重線'),
            ('dashed', u'点線'),
        ],
        coerce=str,
    )


class StockAllocationForm(Form):

    stock_type_id = HiddenField(
        label='',
        validators=[Required()]
    )
    performance_id = HiddenField(
        label='',
        validators=[Required()]
    )
    quantity = TextField(
        label=u'在庫数',
        validators=[Required(u'入力してください')]
    )
