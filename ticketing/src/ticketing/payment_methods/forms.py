# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField, DecimalField
from wtforms.validators import Required, Length, Optional

from ticketing.products.models import PaymentMethodPlugin

class PaymentMethodForm(Form):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    organization_id = HiddenField(
        validators=[Optional()],
    )
    name = TextField(
        label=u'決済方法名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    fee = DecimalField(
        label=u'決済手数料',
        places=2,
        validators=[
            Required(u'入力してください'),
        ]
    )
    payment_plugin_id = SelectField(
        label=u'決済方法',
        validators=[Required(u'選択してください')],
        choices=[(pmp.id, pmp.name) for pmp in PaymentMethodPlugin.all()],
        coerce=int
    )
