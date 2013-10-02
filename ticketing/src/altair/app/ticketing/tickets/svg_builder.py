# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import ISVGBuilder

class SimpleControl(object):
    def get_template(self, template):
        return template
    def get_vals(self, template, vals):
        return vals

class TicketModelControl(object):
    QR_PLACEHOLDER = "IdentifiedQRSource" #todo:rename
    QR_TAG_FORMAT = u'<ts:qrcode content="{}"/>'

    def get_template(self, ticket):
        return ticket.data['drawing']

    def _update_vals_for_unique_qrcode(self, ticket, vals):
        if "qr_tag_format" in ticket.data:
            qr_fmt = ticket.data["qr_tag_format"]
            vals[self.QR_PLACEHOLDER] = qr_fmt.format(vals.get(self.QR_PLACEHOLDER, ""))
        return vals

    def get_vals(self, ticket, vals):
        return self._update_vals_for_unique_qrcode(ticket, vals)

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
