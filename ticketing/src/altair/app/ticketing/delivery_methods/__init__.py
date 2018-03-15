# -*- coding: utf-8 -*-
from zope.interface import implementer
from .interfaces import IDeliveryFormMaker
from .forms import DeliveryMethodForm

@implementer(IDeliveryFormMaker)
class DeliverFormMaker(object):
    def make_form(self, formdata=None, obj=None, prefix='', **kwargs):
        return DeliveryMethodForm(formdata=formdata, obj=obj, prefix=prefix, **kwargs)


def includeme(config):
    # DeliveryFormMakerを登録するメソッドをconfigに追加
    config.add_directive("add_delivery_form_maker", ".directives.add_delivery_form_maker")
    # 共通のDeliveryFormMakerを登録する
    config.registry.registerUtility(DeliverFormMaker(),IDeliveryFormMaker,name='general-delivery-form-maker')

    config.include('.plugins')

    config.add_route('delivery_methods.index', '/', factory='.resources.DeliveryMethodResource')
    config.add_route('delivery_methods.new', '/new', factory='.resources.DeliveryMethodResource')
    config.add_route('delivery_methods.edit', '/edit/{delivery_method_id}', factory='.resources.DeliveryMethodResource')
    config.add_route('delivery_methods.delete', '/delete/{delivery_method_id}')
    config.scan(".")
