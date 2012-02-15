from altaircms.models import DBSession
from . import renderable

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class UsingLayoutMixin(object):
    def get_layout_image(self, page):
        layout = page.layout
        return renderable.LayoutImage.from_json(layout.blocks)

class SampleCoreResource(UsingLayoutMixin):
    def __init__(self, request):
        self.request = request

    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()

