# encoding: utf-8

from zope.interface import implementer

from altair.formhelpers import OurBooleanField
from altair.formhelpers.validators import DynSwitchDisabled, ValidationError

from altair.app.ticketing.payments.plugins import QR_AES_DELIVERY_PLUGIN_ID

from ..interfaces import IDeliveryFormMaker

from .base import QRAESDeliveryFormMaker, QRAESDeliveryMethodForm

def includeme(config):
    config.add_delivery_form_maker(HTQRAESDeliveryFormMaker(), u"HT")

class HTQRAESDeliveryMethodForm(QRAESDeliveryMethodForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(HTQRAESDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

    # フィルド名は必ず'qr_aes_'からの文字列で命名ください。
    qr_aes_allow_sp = OurBooleanField(
        label=u'スマートフォンでの表示',
        validators=[
            DynSwitchDisabled('{delivery_plugin_id} <> "%d"' % QR_AES_DELIVERY_PLUGIN_ID)
        ])

@implementer(IDeliveryFormMaker)
class HTQRAESDeliveryFormMaker(QRAESDeliveryFormMaker):
    def __init__(self):
        super(QRAESDeliveryFormMaker, self).__init__()

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return HTQRAESDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)