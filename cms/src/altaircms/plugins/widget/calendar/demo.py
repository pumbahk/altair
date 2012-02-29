from zope.interface import implements
from altaircms.interfaces import IRenderable

class RenderableAdaptor(object):
    implements(IRenderable)
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def render(self):
        return self.fn(*self.args, **self.kwargs)
        
class ThisMonthDemo(object):
    implements(IRenderable)

    def render(self):
        return "ho"

class ListDemo(object):
    implements(IRenderable)

    def render(self):
        return "hu"

class TermDemo(object):
    implements(IRenderable)

    def render(self):
        return "he"

def thismonth():
    return ThisMonthDemo()

def list():
    return ListDemo()

def term():
    import os
    from mako.templates import Template
    here = os.path.abspath(os.path.dirname(__file__))
    Template(filename=os.path.join(here, "rakuten.calendar.mako"))
    return TermDemo()
