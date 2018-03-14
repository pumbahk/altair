# encoding: utf-8

from zope.interface import implementer

from ..interfaces import IDeliveryFormMaker

from .base import QRAESDeliveryFormMaker, QRAESDeliveryMethodForm


def includeme(config):
    config.add_delivery_form_maker(BWQRAESDeliveryFormMaker(), u"BW")

@implementer(IDeliveryFormMaker)
class BWQRAESDeliveryFormMaker(QRAESDeliveryFormMaker):
    def __init__(self):
        super(QRAESDeliveryFormMaker, self).__init__()

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return QRAESDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)