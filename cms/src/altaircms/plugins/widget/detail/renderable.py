# -*- coding:utf-8 -*-

from pyramid.renderers import render
import os

here = "altaircms.plugins.widget:detail"

class Description(object):
    def __init__(self, widget, request, ctx=None):
        self.widget = widget
        self.request = request
        self.ctx = ctx or {}
        self.ctx.update(widget=widget)

    def render(self):
        template_name = os.path.join(here, "description.mako")
        return render(template_name, self.ctx, self.request)

def description(widget, request, ctx=None):
    return Description(widget, request, ctx)

def dummy(widget, resuest):
    return "dummy"
