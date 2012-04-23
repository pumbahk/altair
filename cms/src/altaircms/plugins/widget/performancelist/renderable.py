# -*- coding:utf-8 -*-

from pyramid.renderers import render

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
class PfListRenderable(object):
    def __init__(self, widget, event, performanceses, request):
        self.widget = widget
        self.event = event
        self.performanceses = performanceses
        self.request = request

    def render(self):
        return render(self.widget.template_name, 
               {"performances": self.performanceses, "event": self.event, "WEEK": WEEK}, 
               self.request)
