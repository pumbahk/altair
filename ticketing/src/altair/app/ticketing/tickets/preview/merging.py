# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from .fillvalues import (
    template_fillvalues,
    template_collect_vars,
)

def _remove_empty_values_from_mapping(mapping):
    dels = []
    for k in mapping:
        if not mapping[k]:
            dels.append(k)
    for k in dels:
        del mapping[k]
    return mapping


def emit_to_another_template(template, ticket):
    svg = template.drawing
    fill_mapping = _remove_empty_values_from_mapping(ticket.fill_mapping)
    return template_fillvalues(svg, fill_mapping)


class TicketVarsCollector(object):
    def __init__(self, ticket):
        self.ticket = ticket
        self.base_template = ticket.base_template

    def is_support(self):
        return self.base_template is not None

    @property
    def template(self):
        if self.is_support():
            logger.info("base template found id=%s", self.ticket.id)
            return self.base_template.drawing
        else:
            logger.info("base template not found id=%s", self.ticket.id)
            return self.ticket.drawing

    def collect_from_self(self):
        template = self.ticket.drawing
        vars_values = template_collect_vars(template)
        params ={}
        for k in vars_values:
            params[k] = ""
        return params

    def collect_from_base_template(self):
        template = self.base_template.drawing
        vars_values = template_collect_vars(template)
        fill_mapping = self.ticket.fill_mapping
        params = {}
        for k in vars_values:
            params[k] = fill_mapping.get(k, "")
        return params

    def collect(self):
        if self.is_support():
            return self.collect_from_base_template()
        else:
            return self.collect_from_self()
