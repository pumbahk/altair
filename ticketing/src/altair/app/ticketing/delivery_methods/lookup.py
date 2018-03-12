# encoding: utf-8

from pyramid.interfaces import IRequest
from .interfaces import IDeliveryFormMaker
from .directives import Discriminator

def lookup_delivery_form_maker(request_or_registry, organization_code):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(organization_code + "-delivery-form-maker"))
    delivery_form_maker = registry.utilities.lookup([], IDeliveryFormMaker, name=key)
    if not delivery_form_maker:
        delivery_form_maker = registry.queryUtility(IDeliveryFormMaker, name="general-delivery-form-maker")
    return delivery_form_maker