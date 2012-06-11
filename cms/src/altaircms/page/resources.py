# coding: utf-8
import logging
from altaircms.models import DBSession
from altaircms.layout.models import Layout
import altaircms.widget.forms as wf
import altaircms.security as security
from altaircms.layout import renderable

from altaircms.widget.models import WidgetDisposition
from altaircms.tag.api import put_tags
from . import helpers as h
from . import models
from . import subscribers


def add_data(self, data, flush=False):
    DBSession.add(data)
    if flush:
        DBSession.flush()

def delete_data(self, obj, flush=False):
    DBSession.delete(obj)
    if flush:
        DBSession.flush()

class WDispositionResource(security.RootFactory):
    Page = models.Page
    Form = wf.WidgetDispositionSaveForm
    add = add_data
    delete = delete_data

    def get_disposition_from_page(self, page, data=None):
        wd = WidgetDisposition.from_page(page, DBSession)
        if data:
            for k, v in data.iteritems():
                setattr(wd, k, v)
        return wd

    def get_disposition(self, id_):
        return WidgetDisposition.query.filter(WidgetDisposition.id==id_).one()

    def get_disposition_list(self):
        return WidgetDisposition.enable_only_query(self.request.user)

    def bind_disposition(self, page, wdisposition):
        WidgetDisposition.snapshot(page, self.request.user, DBSession) ##
        page = wdisposition.bind_page(page, DBSession)
        return page

    def delete_disposition(self, wdisposition):
        wdisposition.delete_widgets()
        self.delete(wdisposition)



class PageResource(security.RootFactory):
    Page = models.Page
    add = add_data
    delete = delete_data

    def get_disposition_forms(self, page):
        user = self.request.user
        return {"disposition_select": wf.WidgetDispositionSelectForm(), 
                "disposition_save": wf.WidgetDispositionSaveForm(page=page.id, owner_id=user.id)
                }
       
    def get_layout_render(self, page):
        layout = DBSession.query(Layout).filter_by(id=page.layout_id).one()
        return renderable.LayoutRender(layout)

    def get_page(self, page_id):
        return models.Page.query.filter(models.Page.id==page_id).first()

    def create_page(self, form):
        tags, private_tags, params =  h.divide_data(form.data)
        page = models.Page.from_dict(params)
        put_tags(page, "page", tags, private_tags, self.request)
        pageset = models.PageSet.get_or_create(page)

        if form.data["parent"]:
            pageset.parent = form.data["parent"]

        self.add(page, flush=True)
        subscribers.notify_page_create(self.request, page, params)
        return page

    def update_page(self, page, form):
        tags, private_tags, params =  h.divide_data(form.data)
        for k, v in params.iteritems():
            setattr(page, k, v)
        page.pageset.event = params["event"]
        put_tags(page, "page", tags, private_tags, self.request)

        if form.data["parent"]:
            page.pageset.parent = form.data["parent"]

        self.add(page, flush=True)
        subscribers.notify_page_update(self.request, page, params)
        return page

    def delete_page(self, page):
        subscribers.notify_page_delete(self.request, page)
        self.delete(page)

    def clone_page(self, page):
        cloned = page.clone(DBSession, request=self.request)
        subscribers.notify_page_create(self.request, cloned)
        return cloned

