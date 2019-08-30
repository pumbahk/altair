# encoding: utf-8

from zope.interface import implementer

from ..interfaces import IDeliveryFormMaker
from ..forms import QRAESDeliveryMethodForm, DeliveryMethodForm

@implementer(IDeliveryFormMaker)
class QRAESDeliveryFormMaker(object):

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return QRAESDeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)


@implementer(IDeliveryFormMaker)
class WebCouponDeliveryFormMaker(object):

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return DeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)