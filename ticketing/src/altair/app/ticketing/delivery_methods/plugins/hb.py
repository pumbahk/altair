# encoding: utf-8

from zope.interface import implementer

from ..interfaces import IDeliveryFormMaker

from .base import QRAESDeliveryFormMaker, QRAESDeliveryMethodForm

def includeme(config):
    config.add_delivery_form_maker(HBQRAESDeliveryFormMaker(), u"HB")

class HBQRAESDeliveryMethodForm(QRAESDeliveryMethodForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(HBQRAESDeliveryMethodForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

@implementer(IDeliveryFormMaker)
class HBQRAESDeliveryFormMaker(QRAESDeliveryFormMaker):
    def __init__(self):
        super(QRAESDeliveryFormMaker, self).__init__()

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return HBQRAESDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)