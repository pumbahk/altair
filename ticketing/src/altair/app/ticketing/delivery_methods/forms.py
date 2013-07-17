# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField, DecimalField
from wtforms.validators import Length, Optional
from wtforms.widgets import TextArea

from altair.formhelpers import Translations, Required, OurBooleanField
from altair.formhelpers.fields import LazySelectField
from altair.app.ticketing.core.models import DeliveryMethodPlugin, FeeTypeEnum

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
        label=u'引取方法名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    fee = DecimalField(
        label=u'発券/引取手数料',
        places=2,
        validators=[Required()]
    )
    fee_type = SelectField(
        label=u'手数料計算単位',
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
    )
    delivery_plugin_id = LazySelectField(
        label=u'引取方法',
        validators=[Required(u'選択してください')],
        choices=lambda field: [(pmp.id, pmp.name) for pmp in DeliveryMethodPlugin.all()],
        coerce=int
    )
    description = TextField(
        label=u"説明文(HTML)", 
        widget=TextArea()
    )
    hide_voucher = OurBooleanField(
        label=u'払込票を表示しない',
    )
