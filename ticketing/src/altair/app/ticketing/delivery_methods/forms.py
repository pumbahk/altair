# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField, DecimalField
from wtforms.validators import Length, Optional
from wtforms.widgets import TextArea

from altair.formhelpers import Translations, Required, OurBooleanField
from altair.formhelpers.fields import LazySelectField
from altair.app.ticketing.core.models import DeliveryMethod, DeliveryMethodPlugin
from altair.saannotation import get_annotations_for

class DeliveryMethodForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=get_annotations_for(DeliveryMethod.id)['label'],
        validators=[Optional()]
        )
    organization_id = HiddenField(
        label=get_annotations_for(DeliveryMethod.organization_id)['label'],
        validators=[Optional()]
        )
    name = TextField(
        label=get_annotations_for(DeliveryMethod.name)['label'],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            ]
        )
    fee_per_order = DecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_order)['label'],
        places=0,
        validators=[Required()]
        )
    fee_per_principal_ticket = DecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_principal_ticket)['label'],
        places=0,
        validators=[Required()]
        )
    fee_per_subticket = DecimalField(
        label=get_annotations_for(DeliveryMethod.fee_per_subticket)['label'],
        places=0,
        validators=[Required()]
        )
    delivery_plugin_id = LazySelectField(
        label=get_annotations_for(DeliveryMethod.delivery_plugin_id)['label'],
        validators=[Required(u'選択してください')],
        choices=lambda field: [(pmp.id, pmp.name) for pmp in DeliveryMethodPlugin.all()],
        coerce=int
        )
    description = TextField(
        label=get_annotations_for(DeliveryMethod.description)['label'],
        widget=TextArea()
        )
    hide_voucher = OurBooleanField(
        label=get_annotations_for(DeliveryMethod.hide_voucher)['label']
        )
    display_order = TextField(
        label=u'表示順',
        default=0,
    )
    selectable = OurBooleanField(
        label=u'使用可否',
        default=True,
    )