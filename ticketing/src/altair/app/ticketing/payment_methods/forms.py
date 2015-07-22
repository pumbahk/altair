# -*- coding: utf-8 -*-

import pystache
from wtforms.validators import Length, Optional, NumberRange, ValidationError

from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurSelectField, OurDecimalField, OurHiddenField
from altair.formhelpers.widgets import OurTextArea
from altair.formhelpers import Translations, Required
from altair.formhelpers.fields import OurBooleanField, LazySelectField
from altair.formhelpers.validators import DynSwitchDisabled, LengthInSJIS
from altair.app.ticketing.core.models import PaymentMethodPlugin, FeeTypeEnum
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID, SEJ_PAYMENT_PLUGIN_ID, FAMIPORT_PAYMENT_PLUGIN_ID


class PaymentMethodForm(OurForm):

    def _get_translations(self):
        return Translations()

    id = OurHiddenField(
        label=u'ID',
        validators=[Optional()]
        )
    organization_id = OurHiddenField(
        validators=[Optional()]
        )
    name = OurTextField(
        label=u'決済方法名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    fee = OurDecimalField(
        label=u'決済手数料',
        places=0,
        validators=[Required()]
        )
    fee_type = OurSelectField(
        label=u'手数料計算単位',
        validators=[Required(u'選択してください')],
        choices=[fee_type.v for fee_type in FeeTypeEnum],
        coerce=int
        )
    payment_plugin_id = LazySelectField(
        label=u'決済方法',
        validators=[Required(u'選択してください')],
        choices=lambda field: [(pmp.id, pmp.name) for pmp in PaymentMethodPlugin.all()],
        coerce=int
        )
    description = OurTextField(
        label=u"説明文(HTML)", 
        widget=OurTextArea()
        )
    hide_voucher = OurBooleanField(
        label=u'払込票を表示しない',
        validators=[
            DynSwitchDisabled('AND({payment_plugin_id} <> "%d", {payment_plugin_id} <> "%d")' % (SEJ_PAYMENT_PLUGIN_ID, FAMIPORT_PAYMENT_PLUGIN_ID))
            ]
        )
    payment_sheet_text = OurTextField(
        label=u'ファミポート払込票に印刷する文言',
        validators=[
            LengthInSJIS(max=490),
            DynSwitchDisabled('{payment_plugin_id} <> "%d"' % FAMIPORT_PAYMENT_PLUGIN_ID)
            ],
        widget=OurTextArea()
        )
    public = OurBooleanField(
        label=u'公開する'
        )
    display_order = OurTextField(
        label=u'表示順',
        default=0
        )
    selectable = OurBooleanField(
        label=u'使用可否',
        default=True
        )

    def validate_payment_sheet_text(form, field):
        try:
            pystache.render(field.data, {})
        except:
            raise ValidationError(u'書式が誤っています')

    def validate_payment_plugin_id(form, field):
        if field.data == CHECKOUT_PAYMENT_PLUGIN_ID and form.fee.data > 0:
            raise ValidationError(u'楽天ID決済では、決済手数料は設定できません')
