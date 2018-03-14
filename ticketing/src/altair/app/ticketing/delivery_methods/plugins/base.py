# encoding: utf-8

from zope.interface import implementer

from altair.app.ticketing.core.models import DeliveryMethodPlugin

from ..interfaces import IDeliveryFormMaker
from ..forms import DeliveryMethodForm

class QRAESDeliveryMethodForm(DeliveryMethodForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(QRAESDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.delivery_plugin_id.choices = [(dmp.id, dmp.name) for dmp in DeliveryMethodPlugin.all()]

    def get_customized_fields(self):
        names = []
        for attr in dir(self):
            if attr.startswith('qr_aes_'):
                names.append(attr)
        return names

@implementer(IDeliveryFormMaker)
class QRAESDeliveryFormMaker(object):

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return QRAESDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)