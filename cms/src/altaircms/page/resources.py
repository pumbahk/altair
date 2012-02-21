from altaircms.models import DBSession
from . import renderable

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class UsingRenderMixin(object):
    def get_layout_render(self, page):
        layout = page.layout
        return renderable.LayoutRender(layout)
    def get_page_render(self, page):
        return renderable.PageRender(page)

class SampleCoreResource(UsingRenderMixin):
    def __init__(self, request):
        self.request = request

    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()

