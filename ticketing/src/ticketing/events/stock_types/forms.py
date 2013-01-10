# -*- coding: utf-8 -*-

from wtforms import Form
from ticketing.formhelpers import OurForm, OurTextField, OurSelectField, OurIntegerField, OurBooleanField, NullableTextField
from wtforms import HiddenField, FieldList
from wtforms.validators import Length, Optional
from wtforms.widgets import CheckboxInput, TextArea

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import StockTypeEnum

class StockTypeForm(OurForm):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()],
    )
    name = OurTextField(
        label=u'名称',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    quantity_only = OurIntegerField(
        label=u'数受け(自由席等、座席の割当をせずに在庫数の設定のみで販売するもの)',
        default=0,
        widget=CheckboxInput(),
    )
    type = OurIntegerField(
        label=u'座席以外(駐車場、グッズ等)を登録する',
        default=StockTypeEnum.Seat.v,
        widget=CheckboxInput(),
    )
    display_order = OurTextField(
        label=u'表示順',
        hide_on_new=True,
        default=u'1'
    )
    fill_color = OurTextField(
        label=u'塗りつぶし色',
        hide_on_new=True
    )
    description = NullableTextField(
        widget=TextArea(),
        label=u'説明',
        hide_on_new=True
        )
