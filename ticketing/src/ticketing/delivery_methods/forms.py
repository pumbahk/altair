# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField, DecimalField
from wtforms.validators import Length, Optional
from wtforms.widgets import TextArea

from ticketing.formhelpers import Translations, Required
from ticketing.core.models import DeliveryMethodPlugin, FeeTypeEnum

class DeliveryMethodForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    organization_id = HiddenField(
        validators=[Optional()],
    )
    name = TextField(
        label=u'配送方法名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    fee = DecimalField(
        label=u'配送手数料',
        places=2,
        validators=[Required()]
    )
    fee_type = SelectField(
        label=u'手数料計算単位',
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
    )
    delivery_plugin_id = SelectField(
        label=u'配送方法',
        validators=[Required(u'選択してください')],
        choices=[(pmp.id, pmp.name) for pmp in DeliveryMethodPlugin.all()],
        coerce=int
    )
    description = TextField(
        validators=[Required()],
        widget=TextArea()
    )
