# -*- coding: utf-8 -*-

from wtforms import Form
from altair.formhelpers import OurForm, OurTextField, OurSelectField, OurIntegerField, OurBooleanField, NullableTextField
from wtforms import HiddenField, FieldList
from wtforms.validators import Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput, TextArea

from altair.formhelpers import Translations, Required
from altair.app.ticketing.core.models import StockTypeEnum, StockType

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

    def validate_quantity_only(form, field):
        if form.id.data:
            stock_type = StockType.query.filter_by(id=form.id.data).first()
            if stock_type.quantity_only != bool(field.data):
                for stock in stock_type.stocks:
                    if stock.quantity > 0:
                        p = stock.performance
                        raise ValidationError(u'既に配席されている為、変更できません (%s席 @ %s %s)' % (stock.quantity, p.name, p.start_on.strftime("%m/%d")))
