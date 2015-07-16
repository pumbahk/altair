# coding: utf-8
import logging
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
from pyramid.decorator import reify
from .models import PageType
from altaircms.auth.models import RolePermission
logger = logging.getLogger()

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
    @reify
    def pagetype(self):
        if "pagetype" in self.request.params:
            return self.request.allowable(PageType).filter(PageType.name==self.request.params["pagetype"]).first()
        elif "pagetype" in self.request.matchdict:
            return self.request.allowable(PageType).filter(PageType.name==self.request.matchdict["pagetype"]).first()

    def get_access_status_from_pagetype(self, pagetype, important_name, name):
        if pagetype is None:
            logger.info("pagetype is not found")
            return False
        if self.request.user is None:
            logger.info("not login user")
            return False
        try:
            if pagetype.is_important:
                status = self.request.user.has_permission_by_name(important_name)
            else:
                status = self.request.user.has_permission_by_name(name)
            if not status:
                logger.info("permission is not found. url={0}, pagetype={1}, user={2}".format(self.request.url, self.request.user.id, pagetype.id))
            return status
        except Exception as e:
            logger.exception(str(e))
            return False
        
    def get_access_status(self, important_name, name):
        return self.get_access_status_from_pagetype(self.pagetype, important_name, name)

    ## todo. obsolute all
    Page = models.Page
    add = add_data
    delete = delete_data
       
    def get_layout_render(self, page):
        ## pageはallowableなもののみ
        assert page.organization_id == self.request.organization.id

        layout = page.layout
        return renderable.LayoutRender(layout)

    def create_page(self, form):
        page = models.Page.from_dict(form.data)
        pageset = models.PageSet.get_or_create(page)

        page.title = form.data['title_prefix'] + form.data['title'] + form.data['title_suffix']
        if form.data["parent"]:
            pageset.parent = form.data["parent"]
        if form.data["genre"]:
            pageset.genre = form.data["genre"]
        if form.data["url"] is None or form.data["url"] == u'':
            pageset.url = u''
        self.add(page, flush=True)
        subscribers.notify_page_create(self.request, page, form.data)

        if page.layout.disposition_id:
            page.layout.default_disposition.bind_page(page, DBSession)

        notify_model_create(self.request, page, form.data)
        notify_model_create(self.request, pageset, form.data)
        return page

    def update_page(self, page, form):
        params = form.data
        for k, v in params.iteritems():
            setattr(page, k, v)
        self.add(page, flush=True)
        subscribers.notify_page_update(self.request, page, params)
        return page

    def delete_page(self, page):
        subscribers.notify_page_delete(self.request, page)
        self.delete(page)

    def delete_pageset(self, pageset):
        for page in pageset.pages:
            subscribers.notify_page_delete(self.request, page)
        pageset.delete()
        self.delete(pageset)

    def clone_page(self, page):
        cloned = page.clone(DBSession, request=self.request)
        subscribers.notify_page_create(self.request, cloned, {"tags": divide_tag(page.pageset.tags, True), "private_tags": divide_tag(page.pageset.private_tags, False), "mobile_tags": divide_tag(page.pageset.mobile_tags, True)}) #xxx:
        return cloned

def divide_tag(tags, publicp):
    labels = []
    for tag in tags:
        if tag.publicp == publicp and tag.organization_id:
            labels.append(tag.label)
    return ",".join(labels)