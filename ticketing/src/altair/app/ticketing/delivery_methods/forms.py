# -*- coding: utf-8 -*-

from wtforms.validators import Length, Optional

from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurSelectField, OurDecimalField, OurHiddenField
from altair.formhelpers.widgets import OurTextArea
from altair.formhelpers import Translations, Required, OurBooleanField
from altair.formhelpers.validators import DynSwitchDisabled, ValidationError
from altair.app.ticketing.core.models import DeliveryMethod, DeliveryMethodPlugin
from altair.saannotation import get_annotations_for
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, QR_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID

class DeliveryMethodForm(OurForm):

    def _get_translations(self):
        return Translations()

    id = OurHiddenField(
        label=get_annotations_for(DeliveryMethod.id)['label'],
        validators=[Optional()]
        )
    organization_id = OurHiddenField(
        label=get_annotations_for(DeliveryMethod.organization_id)['label'],
        validators=[Optional()]
        )
    name = OurTextField(
        label=get_annotations_for(DeliveryMethod.name)['label'],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    fee_per_order = OurDecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_order)['label'],
        places=0,
        validators=[Required()]
        )
    fee_per_principal_ticket = OurDecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_principal_ticket)['label'],
        places=0,
        validators=[Required()]
        )
    fee_per_subticket = OurDecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_subticket)['label'],
        places=0,
        validators=[Required()]
        )
    delivery_plugin_id = OurSelectField(
        label=get_annotations_for(DeliveryMethod.delivery_plugin_id)['label'],
        validators=[Required(u'選択してください')],
        choices=lambda field: [(pmp.id, pmp.name) for pmp in DeliveryMethodPlugin.all()],
        coerce=int
        )
    description = OurTextField(
        label=get_annotations_for(DeliveryMethod.description)['label'],
        widget=OurTextArea()
        )
    hide_voucher = OurBooleanField(
        label=u'引換票を表示しない',
        validators=[
            DynSwitchDisabled('AND({delivery_plugin_id} <> "%d", {delivery_plugin_id} <> "%d")' % (SEJ_DELIVERY_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID))
            ]
        )
    single_qr_mode = OurBooleanField(
        label=u'単一QRモード (一括発券)',
        validators=[
            DynSwitchDisabled('{delivery_plugin_id} <> "%d"' % QR_DELIVERY_PLUGIN_ID)
            ]
        )
    expiration_date = OurTextField(
        label=u'チケット有効期限 (相対)',
        validators=[
            DynSwitchDisabled('{delivery_plugin_id} <> "%d"' % RESERVE_NUMBER_DELIVERY_PLUGIN_ID)
            ]
        )
    display_order = OurTextField(
        label=u'表示順',
        default=0,
    )
    selectable = OurBooleanField(
        label=u'使用可否',
        default=True,
    )

    def validate_expiration_date(form, field):
        if field.data:
            if str(field.data).isdigit() == False:
                raise ValidationError(u'数字（正数）のみ、入力できます。')
