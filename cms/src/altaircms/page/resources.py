# coding: utf-8
import logging
from datetime import datetime
from altaircms.models import DBSession
from altaircms.layout.models import Layout
import altaircms.widget.forms as wf
import altaircms.security as security
from altaircms.layout import renderable
from altaircms.subscribers import notify_model_create
from altaircms.widget.models import WidgetDisposition
from altaircms.tag.api import put_tags
from . import helpers as h
from . import models
from . import subscribers
# from .api import get_static_page_utility
# from altaircms.auth.api import get_or_404

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
        ## pageはallowableなもののみ
        assert page.organization_id == self.request.organization.id

        wd = WidgetDisposition.from_page(page, DBSession, data["save_type"]) # page`type is shallow or deep
        if data:
            for k, v in data.iteritems():
                setattr(wd, k, v)
        return wd

    def bind_disposition(self, page, wdisposition):
        return wdisposition.bind_page(page, DBSession)

    def delete_disposition(self, wdisposition):
        wdisposition.delete_widgets()
        self.delete(wdisposition)



class PageResource(security.RootFactory):
    Page = models.Page
    add = add_data
    delete = delete_data
       
    def get_layout_render(self, page):
        ## pageはallowableなもののみ
        assert page.organization_id == self.request.organization.id

        layout = page.layout
        return renderable.LayoutRender(layout)

    def create_page(self, form):
        tags, private_tags, params =  h.divide_data(form.data)
        page = models.Page.from_dict(params)
        put_tags(page, "page", tags, private_tags, self.request)
        pageset = models.PageSet.get_or_create(page)

        if form.data["parent"]:
            pageset.parent = form.data["parent"]

        self.add(page, flush=True)
        subscribers.notify_page_create(self.request, page, params)
        notify_model_create(self.request, page, form.data)
        notify_model_create(self.request, pageset, form.data)
        return page

    def update_page(self, page, form):
        tags, private_tags, params =  h.divide_data(form.data)
        for k, v in params.iteritems():
            setattr(page, k, v)
        page.pageset.event = params["event"]
        page.pageset.url = params["url"]
        put_tags(page, "page", tags, private_tags, self.request)

        if form.data["parent"]:
            page.pageset.parent = form.data["parent"]

        self.add(page, flush=True)
        subscribers.notify_page_update(self.request, page, params)
        return page

    def delete_page(self, page):
        subscribers.notify_page_delete(self.request, page)
        self.delete(page)

    def delete_pageset(self, pageset):
        for page in pageset.pages:
            subscribers.notify_page_delete(self.request, page)
        self.delete(pageset)

    def clone_page(self, page):
        cloned = page.clone(DBSession, request=self.request)
        subscribers.notify_page_create(self.request, cloned)
        return cloned

class StaticPageResource(security.RootFactory):
    def create_static_page(self, data):
        static_page = models.StaticPage(name=data["name"])
        DBSession.add(static_page)
        notify_model_create(self.request, static_page, data)
        DBSession.flush()
        return static_page

    def touch_static_page(self, static_page, _now=datetime.now):
        static_page.updated_at = _now()
        DBSession.add(static_page)
        return static_page

    def delete_static_page(self, static_page):
        DBSession.delete(static_page)
