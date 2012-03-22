# coding: utf-8
from altaircms.models import DBSession
from altaircms.layout.models import Layout
import altaircms.widget.forms as wf
import altaircms.security as security
from . import renderable
from . import models
from altaircms.widget.models import WidgetDisposition

class ForDispositionMixin(object):
    def get_forms(self, page):
        return {"disposition_select": self._wdp_select_form(page), 
                "disposition_save": self._wdp_save_form(page)}
    def _wdp_select_form(self, page):
        return wf.WidgetDispositionSelectForm() ## dynamic に絞り込みたい

    def _wdp_save_form(self, page):
        return wf.WidgetDispositionSaveForm(page=page.id)

    def get_disposition(self, page):
        return WidgetDisposition.from_page(page, DBSession)

class ForPageMixin(object):
    def get_layout_render(self, page):
        layout = DBSession.query(Layout).filter_by(id=page.layout_id).one()
        return renderable.LayoutRender(layout)

    def get_page_render(self, page):
        return renderable.PageRender(page)

    def get_page(self, page_id):
        return models.Page.query.filter(models.Page.id==page_id).one()

    def page_clone(self, page):
        return page.clone(DBSession)

class PageResource(ForPageMixin, 
                   ForDispositionMixin, 
                   security.RootFactory):

    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()

