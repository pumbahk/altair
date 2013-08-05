# -*- coding: utf-8 -*-

import unicodedata
from wtforms import Form
from wtforms import HiddenField, FieldList
from wtforms.validators import Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput, TextArea

from altair.formhelpers import Translations, Required
from altair.formhelpers import OurForm, OurTextField, OurSelectField, OurIntegerField, OurBooleanField, NullableTextField
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

    def validate_name(form, field):
        stock_type = StockType.query.filter(
            StockType.name==field.data,
            StockType.event_id==form.event_id.data,
            StockType.quantity_only==form.quantity_only.data,
            StockType.id!=form.id.data
        ).count()
        if stock_type > 0:
            raise ValidationError(u'既に登録済みの席種名です')

    def validate_quantity_only(form, field):
        if form.id.data:
            stock_type = StockType.query.filter_by(id=form.id.data).first()
            if stock_type.quantity_only != bool(field.data):
                for stock in stock_type.stocks:
                    if stock.quantity > 0:
                        p = stock.performance
                        raise ValidationError(u'既に配席されている為、変更できません (%s席 @ %s %s)' % (stock.quantity, p.name, p.start_on.strftime("%m/%d")))

    def validate_display_order(form, field):
        if not field.data:
            return

        display_order_uc = unicodedata.normalize('NFKC',field.data)
        if display_order_uc.isdigit():
            return

        raise ValueError(u"数字を入力して下さい")
