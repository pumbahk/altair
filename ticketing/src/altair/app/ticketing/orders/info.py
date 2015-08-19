# encoding: utf-8

import itertools
from zope.interface import implementer, provider, providedBy
from markupsafe import Markup, escape
from altair.viewhelpers.datetime_ import create_date_time_formatter
from pyramid.i18n import get_localizer
from altair.app.ticketing.payments.api import get_payment_plugin, get_delivery_plugin, get_payment_delivery_plugin
from altair.app.ticketing.payments.directives import PAYMENT_CONFIG

from .interfaces import IOrderDescriptorRegistry, IOrderDescriptor, IOrderDescriptorRenderer

@implementer(IOrderDescriptorRegistry)
class OrderDescriptorRegistry(object):
    def __init__(self):
        self.descriptors = {}

    def add_descriptor(self, descriptor):
        descriptors_for_object = self.descriptors.get(descriptor.target)
        if descriptors_for_object is None:
            descriptors_for_object = self.descriptors[descriptor.target] = {}
        descriptors_for_object[descriptor.name] = descriptor

    def get_descriptor(self, obj, name):
        descriptors_for_object = self.descriptors.get(obj)
        if descriptors_for_object is None:
            return None
        descriptor = descriptors_for_object.get(name)
        return descriptor


def get_name_for_target(request, target):
    for iface in providedBy(target):
        for name, obj in request.registry.utilities.lookupAll([], iface):
            if obj is target:
                return name
    return None


@implementer(IOrderDescriptor)
class OrderDescriptor(object):
    def __init__(self, target, name, renderers=None):
        self.target = target
        self.target_name = None
        self.name = name
        if renderers is None:
            renderers = {}
        self.renderers = renderers

    def get_display_name(self, request):
        if self.target_name is None:
            self.target_name = get_name_for_target(request, self.target)
        return get_localizer(request).translate('%s:%s' % (self.target_name, self.name))
        return self.display_names.get(request.localized_name) or self.key[1]

    def set_renderer(self, renderer):
        self.renderers[renderer.flavor] = flavor

    def get_renderer(self, flavor):
        return self.renderers.get(flavor)


@provider(IOrderDescriptorRenderer)
def render_html_text_generic(request, descr_registry, descr, value):
    if value is None:
        return Markup(u'')
    elif isinstance(value, unicode):
        return Markup(escape(value))
    elif isinstance(value, (int, long, Decimal)):
        return Markup(escape(unicode(value)))
    else:
        return Markup(u'unrenderable value <i>%s</i>' % escape(repr(value)))

@provider(IOrderDescriptorRenderer)
def render_html_datetime_generic(request, descr_registry, descr, value):
    fmt = create_date_time_formatter(request)
    return Markup(escape(fmt.format_datetime(value)))

@provider(IOrderDescriptorRenderer)
def render_html_currency_generic(request, descr_registry, descr, value):
    return Markup(escape('¥%d' % value))

@implementer(IOrderDescriptorRenderer)
class GenericBooleanRenderer(object):
    def __init__(self, false_value, true_value):
        self.false_value = false_value
        self.true_value = true_value

    def __call__(self, request, descr_registry, descr, value):
        return get_localizer(request).translate(self.true_value if value else self.false_value)

def render_html_exchange_sheet_form(request, descr_registry, descr, exchange_sheet):
    return Markup(u'''<form action="{exchange_sheet_url}" method="POST">
  <input type="hidden" name="iraihyo_id_00" value="{exchange_sheet_number}">
  <input type="submit" name="submit" value="引換票を表示" class="btn"/>
  </form>'''.format(exchange_sheet_url=escape(exchange_sheet['url']), exchange_sheet_number=escape(exchange_sheet['number'])))

def render_html_sej_branches(request, descr_registry, descr, branches):
    items = []
    for branch in reversed(branches):
        pairs = []    
        for k, v in branch.items():
            _descr = descr_registry.get_descriptor(descr.target, k)
            if _descr is not None:
                renderer = _descr.get_renderer('html')
                display_name = _descr.get_display_name(request)
                display_value = renderer(request, descr_registry, _descr, v)
            else:
                default_renderer = request.registry.queryUtility(IOrderDescriptorRenderer, name='html')
                display_name = k
                display_value = default_renderer(request, descr_registry, _descr, v)
            pairs.append(u'%s: %s' % (display_name, display_value))
        items.append(u', '.join(pairs))
    return u' ← '.join(items)

def register_default_renderers(config):
    def register():
        config.registry.registerUtility(IOrderDescriptorRenderer, render_html_text_generic, name='html')
    config.action(register_default_renderers, register, order=PAYMENT_CONFIG + 1)

def register_descriptors(config):
    from altair.app.ticketing.payments.plugins import (
        MULTICHECKOUT_PAYMENT_PLUGIN_ID,
        CHECKOUT_PAYMENT_PLUGIN_ID,
        SEJ_PAYMENT_PLUGIN_ID,
        RESERVE_NUMBER_PAYMENT_PLUGIN_ID,
        FREE_PAYMENT_PLUGIN_ID,
        FAMIPORT_PAYMENT_PLUGIN_ID,
        SHIPPING_DELIVERY_PLUGIN_ID,
        SEJ_DELIVERY_PLUGIN_ID,
        RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
        QR_DELIVERY_PLUGIN_ID,
        ORION_DELIVERY_PLUGIN_ID,
        FAMIPORT_DELIVERY_PLUGIN_ID,
        )
    def register():
        descriptor_registrations = [
            (
                [get_payment_plugin(config.registry, MULTICHECKOUT_PAYMENT_PLUGIN_ID)],
                {
                    u'ahead_com_code': {
                        'html': render_html_text_generic,
                        },
                    u'ahead_com_name': {
                        'html': render_html_text_generic,
                        },
                    u'approval_no': {
                        'html': render_html_text_generic,
                        },
                    u'card_brand': {
                        'html': render_html_text_generic,
                        },
                    }
                ),
            (
                [get_payment_plugin(config.registry, CHECKOUT_PAYMENT_PLUGIN_ID)],
                {
                    u'order_id': {
                        'html': render_html_text_generic,
                        },
                    u'order_control_id': {
                        'html': render_html_text_generic,
                        },
                    u'used_point': {
                        'html': render_html_text_generic,
                        },
                    u'sales_at': {
                        'html': render_html_text_generic,
                        },
                    }
                ),
            (
                [
                    get_payment_plugin(config.registry, RESERVE_NUMBER_PAYMENT_PLUGIN_ID),
                    get_delivery_plugin(config.registry, RESERVE_NUMBER_DELIVERY_PLUGIN_ID)
                    ],
                {
                    u'reserved_number': {
                        'html': render_html_text_generic,
                        },
                    },
                ),
            (
                [
                    get_payment_delivery_plugin(config.registry, SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID),
                    get_payment_plugin(config.registry, SEJ_PAYMENT_PLUGIN_ID),
                    ],
                {
                    u'pay_store_name': {
                        'html': render_html_text_generic,
                        },
                    u'ticketing_store_name': {
                        'html': render_html_text_generic,
                        },
                    u'billing_number': {
                        'html': render_html_text_generic,
                        },
                    u'exchange_number': {
                        'html': render_html_text_generic,
                        },
                    u'exchange_sheet': {
                        'html': render_html_exchange_sheet_form,
                        },
                    u'branches': {
                        'html': render_html_sej_branches,
                        },
                    },
                ),
            (
                [
                    get_delivery_plugin(config.registry, SEJ_DELIVERY_PLUGIN_ID)
                    ],
                {
                    u'ticketing_store_name': {
                        'html': render_html_text_generic,
                        },
                    u'exchange_number': {
                        'html': render_html_text_generic,
                        },
                    u'exchange_sheet': {
                        'html': render_html_exchange_sheet_form,
                        },
                    u'branches': {
                        'html': render_html_sej_branches,
                        },
                    },
                ),
            (
                [
                    get_delivery_plugin(config.registry, SHIPPING_DELIVERY_PLUGIN_ID)
                    ],
                {
                    u'delivered': {
                        'html': GenericBooleanRenderer(
                            u'not delivered yet',
                            u'delivered'
                            ),
                        }
                    }
                ),
            (
                [
                    get_payment_delivery_plugin(config.registry, FAMIPORT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID),
                    get_payment_plugin(config.registry, FAMIPORT_PAYMENT_PLUGIN_ID),
                    ],
                {
                    u'payment_reserve_number': {
                        'html': render_html_text_generic,
                        },
                    u'ticketing_reserve_number': {
                        'html': render_html_text_generic,
                        },
                    u'payment_shop_name': {
                        'html': render_html_text_generic,
                        },
                    u'ticketing_shop_name': {
                        'html': render_html_text_generic,
                        },
                    },
                ),
            (
                [
                    get_delivery_plugin(config.registry, FAMIPORT_DELIVERY_PLUGIN_ID)
                    ],
                {
                    u'ticketing_reserve_number': {
                        'html': render_html_text_generic,
                        },
                    u'ticketing_shop_name': {
                        'html': render_html_text_generic,
                        },
                    },
                ),
            ]
        descr_registry = OrderDescriptorRegistry()
        for plugins, descriptor_infos in descriptor_registrations:
            for plugin in plugins:
                assert plugin is not None
                for descr_name, renderers in descriptor_infos.items():
                    descriptor = OrderDescriptor(plugin, descr_name, renderers)
                    descr_registry.add_descriptor(descriptor)
        config.registry.registerUtility(descr_registry, IOrderDescriptorRegistry)
    config.action(register_descriptors, register, order=PAYMENT_CONFIG + 5)

def includeme(config):
    register_descriptors(config) 
