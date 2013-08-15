# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField, DecimalField
from wtforms.validators import Length, Optional, NumberRange
from wtforms.widgets import TextArea

from altair.formhelpers import Translations, Required
from altair.formhelpers.fields import OurBooleanField, LazySelectField
from altair.app.ticketing.core.models import PaymentMethodPlugin, FeeTypeEnum

class PaymentMethodForm(Form):

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
        label=u'決済方法名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    fee = DecimalField(
        label=u'決済手数料',
        places=0,
        validators=[Required()],
    )
    fee_type = SelectField(
        label=u'手数料計算単位',
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
    )
    payment_plugin_id = LazySelectField(
        label=u'決済方法',
        validators=[Required(u'選択してください')],
        choices=lambda field: [(pmp.id, pmp.name) for pmp in PaymentMethodPlugin.all()],
        coerce=int,
    )
    description = TextField(
        label=u"説明文(HTML)", 
        widget=TextArea()
    )
    hide_voucher = OurBooleanField(
        label=u'払込票を表示しない',
    )

    public = OurBooleanField(
        label=u'公開する',
    )
    
