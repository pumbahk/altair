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
    def __init__(self, form=DeliveryMethodForm):
        self.form = form

    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return self.form(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
