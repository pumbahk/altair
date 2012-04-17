# coding: utf-8
from altaircms.models import DBSession
from altaircms.layout.models import Layout
import altaircms.widget.forms as wf
import altaircms.security as security
from altaircms.layout import renderable

from altaircms.widget.models import WidgetDisposition
from altaircms.tag.api import put_tags

from . import helpers as h
from . import models

class PageResource(security.RootFactory):
    def get_confirmed_form(self, postdata):
        form = wf.WidgetDispositionSaveForm(postdata)
        return form

    def get_forms(self, page):
        return {"disposition_select": self._wdp_select_form(page), 
                "disposition_save": self._wdp_save_form(page)}

    def _wdp_select_form(self, page):
        return wf.WidgetDispositionSelectForm()

    def _wdp_save_form(self, page):
        user = self.request.user
        return wf.WidgetDispositionSaveForm(page=page.id, owner_id=user.id)

    def get_disposition_from_page(self, page, data=None):
        wd = WidgetDisposition.from_page(page, DBSession)
        if data:
            for k, v in data.iteritems():
                setattr(wd, k, v)
        return wd

    def get_disposition(self, id_):
        return WidgetDisposition.query.filter(WidgetDisposition.id==id_).one()

    def get_disposition_list(self, user):
        return WidgetDisposition.enable_only_query(user)

    def bind_disposition(self, page, wdisposition):
        WidgetDisposition.snapshot(page, self.request.user, DBSession)
        page = wdisposition.bind_page(page, DBSession)
        return page

    def delete_disposition(self, wdisposition):
        ## need self.delete()
        wdisposition.delete_widgets()
        self.delete(wdisposition)
        
    def get_layout_render(self, page):
        layout = DBSession.query(Layout).filter_by(id=page.layout_id).one()
        return renderable.LayoutRender(layout)

    def get_page(self, page_id):
        return models.Page.query.filter(models.Page.id==page_id).one()

    def crate_page(self, form):
        tags, private_tags, params =  h.divide_data(form.data)
        page = models.Page.from_dict(params)
        put_tags(page, "page", tags, private_tags, self.request)
        return page

    def update_page(self, page, form):
        tags, private_tags, params =  h.divide_data(form.data)
        for k, v in params.iteritems():
            setattr(page, k, v)
        put_tags(page, "page", tags, private_tags, self.request)
        return page

    def page_clone(self, page):
        return page.clone(DBSession)

    def add(self, data, flush=False):
        DBSession.add(data)
        if flush:
            DBSession.flush()

    def delete(self, obj, flush=False):
        DBSession.delete(obj)
        if flush:
            DBSession.flush()

