from pyramid_layout.layout import layout_config
from . import selectable_renderer

@layout_config(template=selectable_renderer('base.html'))
class BaseLayout(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

