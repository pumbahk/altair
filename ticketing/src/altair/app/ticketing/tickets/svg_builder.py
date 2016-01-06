# -*- coding:utf-8 -*-
from zope.interface import implementer
import logging
logger = logging.getLogger(__name__)

from sqlalchemy.exc import InvalidRequestError
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.core.utils import (
    merge_dict_recursive,
    tree_dict_from_flatten
)
from .interfaces import ISVGBuilder

class SimpleControl(object):
    def get_template(self, template):
        return template
    def get_vals(self, template, vals):
        return vals

class OrderAttributesForOverwriteData(object):
    def sep(self, s):
        return s.split(".")

    def __getitem__(self, order_id):
        order = Order.query.get(order_id)
        if order is None:
            return {}
        try:
            return tree_dict_from_flatten(order.attributes, self.sep)
        except InvalidRequestError as e:
            #stale association proxy, parent object has gone out of scope
            logger.error(repr(e))
            return {}

class TicketModelControl(object):
    def __init__(self):
        self.overwrite_data = OrderAttributesForOverwriteData()

    def get_template(self, ticket):
        return ticket.drawing

    def overwrite_attributes(self, build_vals):
        order_dict = build_vals.get("order")
        if order_dict is None:
            return {}
        order_id = order_dict.get("id", None) #order.idは露出させないほうがよさそうなのでpop => 無理だった
        if order_id is None:
            return {}
        return self.overwrite_data[order_id]

    def get_vals(self, ticket, build_vals):
        # logger.info(build_vals)
        vals = ticket.vars_defaults.copy()
        vals.update(build_vals)
        overwrite_vals = self.overwrite_attributes(build_vals)
        # logger.info(overwrite_vals)
        return merge_dict_recursive(vals, overwrite_vals)

@implementer(ISVGBuilder)
class SVGBuilder(object):
    """rendering svg"""
    def __init__(self, control, renderer):
        self.control = control
        self.renderer = renderer

    def build(self, template_model, vals, transform=None):
        template = self.control.get_template(template_model)
        if transform:
            template = transform(template)
        vals = self.control.get_vals(template_model, vals)
        rendered = self.renderer.render(template, vals)
        return self.renderer.render(rendered, vals)
