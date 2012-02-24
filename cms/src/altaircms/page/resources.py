# coding: utf-8
from altaircms.models import DBSession
from altaircms.layout.models import Layout
from . import renderable

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class UsingRenderMixin(object):
    def get_layout_render(self, page):
        # @FIXME: 以下が表示される
        # DetachedInstanceError: Parent instance <Page at 0x10d7c78d0> is not 
        # bound to a Session; lazy load operation of attribute 'layout' cannot proceed
        # layout = page.layout
        layout = DBSession.query(Layout).filter_by(id=page.layout_id).one()
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

