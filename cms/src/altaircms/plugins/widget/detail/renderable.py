# -*- coding:utf-8 -*-

from pyramid.renderers import render
import os

here = "altaircms.plugins.widget:detail"

class DescriptionAndImage(object):
    def __init__(self, widget, request):
        self.widget = widget
        self.request = request

    def render(self):
        template_name = os.path.join(here, "description_and_image.mako")
        return render(template_name, 
                      {"widget": self.widget}, 
                      self.request)
        
def description_and_image(widget, request):
    return DescriptionAndImage(widget, request)

def dummy(widget, resuest):
    return "dummy"
