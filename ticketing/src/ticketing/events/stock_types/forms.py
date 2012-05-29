# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, HiddenField, BooleanField
from wtforms.validators import Required, Length, Optional
from wtforms.widgets import CheckboxInput

from ticketing.utils import Translations
from ticketing.products.models import StockTypeEnum

class StockTypeForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required(u'入力してください')],
    )
    name = TextField(
        label=u'名称',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    type = IntegerField(
        label=u'座席以外を登録する',
        default=StockTypeEnum.Seat.v,
        widget=CheckboxInput(),
    )
    fill_color = TextField(
        label=u'塗りつぶし色',
    )
    stroke_color = TextField(
        label=u'線の色',
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
