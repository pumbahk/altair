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

class TicketModelControl(object):
    def get_template(self, ticket):
        return ticket.drawing

    def get_vals(self, ticket, build_vals):
        # logger.info(build_vals)
        vals = ticket.vars_defaults
        vals.update(build_vals)
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
