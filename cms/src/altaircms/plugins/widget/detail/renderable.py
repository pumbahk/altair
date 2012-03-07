# -*- coding:utf-8 -*-

from pyramid.renderers import render
import os

here = "altaircms.plugins.widget:detail"

def description_and_image(widget, request):
    template_name = os.path.join(here, "description_and_image.mako")
    return render(template_name, 
                  {}, 
                  request)

def dummy(widget, resuest):
    return "dummy"
