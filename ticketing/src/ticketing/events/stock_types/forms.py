# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, IntegerField, HiddenField, BooleanField, FieldList
from wtforms.validators import Length, Optional
from wtforms.widgets import CheckboxInput

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import StockTypeEnum

class StockTypeForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()],
    )
    name = TextField(
        label=u'名称',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    quantity_only = IntegerField(
        label=u'数受け(自由席等、座席の割当をせずに在庫数の設定のみで販売するもの)',
        default=0,
        widget=CheckboxInput(),
    )
    type = IntegerField(
        label=u'座席以外(駐車場、グッズ等)を登録する',
        default=StockTypeEnum.Seat.v,
        widget=CheckboxInput(),
    )
    display_order = IntegerField(
        label=u'表示順',
    )
    fill_color = TextField(
        label=u'塗りつぶし色',
    )
    stroke_color = TextField(
        label=u'線の色',
    )
