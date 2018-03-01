# encoding: utf-8

from pyramid.interfaces import IRequest

from .interfaces import IQRAESPlugin, IQRAESDeliveryFormMaker
from .directives import Discriminator

def lookup_qr_aes_plugin(request_or_registry, organization_code):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(organization_code + "-plugin"))
    return registry.utilities.lookup([], IQRAESPlugin, name=key)

def lookup_qr_aes_delivery_form_maker(request_or_registry, organization_code):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(organization_code + "-form-helper"))
    return registry.utilities.lookup([], IQRAESDeliveryFormMaker, name=key)