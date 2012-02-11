from altaircms.models import DBSession
from deform.form import Form
from . import forms
from . import renderable

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class UsingFormMixin(object):
    def get_page_form(self, appstruct=None, mapper=None):
        form = Form(forms.UnregisteredPageSchema(), buttons=("submit", ))
        return forms._FormWrapper(form, appstruct=appstruct, mapper=mapper)

class UsingPageMixin(object):
    import altaircms.page.models as m
    def create_page(self, params):
        page = self.m.Page()
        page = set_with_dict(page, params)
        return page

    def get_page(self, page_id):
        return self.m.Page.query.filter(self.m.Page.id==page_id).one()


class UsingLayoutMixin(object):
    def get_layout_image(self, page):
        layout = page.layout
        return renderable.LayoutImage.from_json(layout.blocks)

class SampleCoreResource(UsingPageMixin, UsingFormMixin, UsingLayoutMixin):
    def __init__(self, request):
        self.request = request

    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()

