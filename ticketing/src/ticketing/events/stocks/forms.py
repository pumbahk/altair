# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, IntegerField, ValidationError
from wtforms.validators import Length, NumberRange, Optional

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import Seat, Stock

class AllocateSeatForm(Form):

    def _get_translations(self):
        return Translations()

    id = TextField(
        validators=[Required()],
    )
    stock_id = IntegerField(
        validators=[Required()],
    )

class AllocateStockForm(Form):

    def _get_translations(self):
        return Translations()

    id = IntegerField(
        validators=[Required()],
    )
    quantity = IntegerField(
        validators=[
            Required(),
            NumberRange(min=0, message=u'在庫数に有効な値を入力してください'),
        ],
    )

    def validate_quantity(form, field):
        # Seatの割当数と一致すること
        stock = Stock.get(form.id.data)
        if stock and stock.stock_type and stock.stock_type.is_seat:
            allocated_seats = Seat.filter_by(stock_id=form.id.data).count()
            if allocated_seats != int(form.quantity.data):
                raise ValidationError(u'席種に割り当てられている在庫数合計が一致しません')

class AllocateStockTypeForm(Form):

    def _get_translations(self):
        return Translations()

    id = IntegerField(
        validators=[Required()],
    )
    name = TextField(
        validators=[
            Required(),
            Length(max=255, message=u'席種名は255文字以内で入力してください'),
        ]
    )
    style = TextField(
        validators=[Required()]
    )
