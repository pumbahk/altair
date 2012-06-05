# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Required, Regexp, Length, Optional, ValidationError

class StockForm(Form):

    id = HiddenField(
        label='',
        validators=[Optional()],
    )
    stock_holder_id = HiddenField(
        label='',
        validators=[Required()]
    )
    stock_type_id = HiddenField(
        label='',
        validators=[Required()]
    )
    quantity = TextField(
        label=u'在庫数',
        validators=[Required(u'入力してください')]
    )
