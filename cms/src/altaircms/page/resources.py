# coding: utf-8
from altaircms.models import DBSession
from altaircms.layout.models import Layout
import altaircms.security as security
from . import renderable
from . import models

def set_with_dict(obj, D):
    for k, v in D.items():
        setattr(obj, k, v)
    return obj

class UsingRenderMixin(object):
    def get_layout_render(self, page):
        layout = DBSession.query(Layout).filter_by(id=page.layout_id).one()
        return renderable.LayoutRender(layout)

    def get_page_render(self, page):
        return renderable.PageRender(page)

    def get_page(self, page_id):
        return models.Page.query.filter(models.Page.id==page_id).one()

    def page_clone(self, page):
        return page.clone(DBSession)

class PageResource(UsingRenderMixin, 
                   security.RootFactory):

    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()

