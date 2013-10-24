# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import ISVGBuilder

class SimpleControl(object):
    def get_template(self, template):
        return template
    def get_vals(self, template, vals):
        return vals

import logging
logger = logging.getLogger(__name__)
from altair.app.ticketing.core.models import Order

class OrderAttributesForOverwriteData(object):
    def __init__(self):
        self.attributes_cache = {}

    def __getitem__(self, order_id):
        if order_id in self.attributes_cache:
            return self.attributes_cache[order_id]
        v = self.attributes_cache[order_id] = self._get_order_attributes_for_overwrite(order_id)
        return v

    def _get_order_attributes_for_overwrite(self, order_id):
        order = Order.query.get(order_id)
        if order is None:
            return {}
        return {attr.name:attr.value for attr in order._attributes}

class TicketModelControl(object):
    def __init__(self):
        self.overwrite_data = OrderAttributesForOverwriteData()

    def get_template(self, ticket):
        return ticket.drawing

    def overwrite_attributes(self, build_vals):
        order_dict = build_vals.get("order")
        if order_dict is None:
            return {}
        order_id = order_dict.pop("id", None) #order.idは露出させないほうがよさそうなのでpop
        if order_id is None:
            return {}
        return self.overwrite_data[order_id]

    def get_vals(self, ticket, build_vals):
        # logger.info(build_vals)
        vals = ticket.vars_defaults
        vals.update(build_vals)
        vals.update(self.overwrite_attributes(build_vals))
        return vals

@implementer(ISVGBuilder)
class SVGBuilder(object):
    """rendering svg"""
    def __init__(self, control, renderer):
        self.control = control
        self.renderer = renderer

    def build(self, template_model, vals):
        template = self.control.get_template(template_model)
        vals = self.control.get_vals(template_model, vals)
        return self.renderer.render(template, vals)
