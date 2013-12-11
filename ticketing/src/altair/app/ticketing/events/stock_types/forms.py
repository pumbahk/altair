# -*- coding: utf-8 -*-

import unicodedata
from wtforms import Form
from wtforms import HiddenField, FieldList
from wtforms.validators import Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput, TextArea

from altair.formhelpers import Translations, Required
from altair.formhelpers import OurForm, OurTextField, OurSelectField, OurIntegerField, OurBooleanField, NullableTextField, NullableIntegerField
from altair.formhelpers.filters import NFKC
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
    min_quantity = NullableIntegerField(
        label=u'席種毎の最小購入数',
        default=None,
        hide_on_new=True
    )
    max_quantity = NullableIntegerField(
        label=u'席種毎の最大購入数',
        default=None,
        hide_on_new=True
    )
    min_product_quantity = NullableIntegerField(
        label=u'席種毎の最小商品購入数',
        default=None,
        hide_on_new=True
    )
    max_product_quantity = NullableIntegerField(
        label=u'席種毎の最大商品購入数',
        default=None,
        hide_on_new=True
    )
    type = OurIntegerField(
        label=u'座席以外(駐車場、グッズ等)を登録する',
        default=StockTypeEnum.Seat.v,
        widget=CheckboxInput(),
    )
    display = OurBooleanField(
        label=u'表示(カートに表示して選択可とする)',
        default=True,
        hide_on_new=True
    )
    display_order = NullableIntegerField(
        label=u'表示順',
        hide_on_new=True,
        default=u'1',
        raw_input_filters=[NFKC],
        validators=[Optional()]
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

    def validate(self, *args, **kwargs):
        if not super(StockTypeForm, self).validate(*args, **kwargs):
            return False
        validity = True
        if self.min_quantity.data is not None and \
           self.max_quantity.data is not None and \
           self.min_quantity.data > self.max_quantity.data:
            errors = self.max_quantity.errors
            if errors is None:
                errors = []
            else:
                errors = list(errors)
            errors.append(u'最大購入数には最小購入数以上の値を指定してください')
            self.max_quantity.errors = errors
            validity = False
        if self.min_product_quantity.data is not None and \
           self.max_product_quantity.data is not None and \
           self.min_product_quantity.data > self.max_product_quantity.data:
            errors = self.max_product_quantity.errors
            if errors is None:
                errors = []
            else:
                errors = list(errors)
            errors.append(u'最大商品購入数には最小商品購入数以上の値を指定してください')
            self.max_product_quantity.errors = errors
            validity = False
        if self.min_quantity.data is not None and \
           self.min_product_quantity.data is not None and \
           self.min_quantity.data < self.min_product_quantity.data:
            errors = self.min_quantity.errors
            if errors is None:
                errors = []
            else:
                errors = list(errors)
            errors.append(u'最小購入数には最小商品購入数以上の値を指定してください')
            self.min_quantity.errors = errors
            validity = False
        if self.max_quantity.data is not None and \
           self.max_product_quantity.data is not None and \
           self.max_quantity.data < self.max_product_quantity.data:
            errors = self.max_quantity.errors
            if errors is None:
                errors = []
            else:
                errors = list(errors)
            errors.append(u'最大購入数には最大商品購入数以上の値を指定してください')
            self.max_quantity.errors = errors
            validity = False
        return validity
           
