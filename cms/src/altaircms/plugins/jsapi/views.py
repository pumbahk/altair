# -*- coding:utf-8 -*-
from datetime import datetime

from pyramid.view import view_config
from pyramid.view import view_defaults

from altaircms.models import DBSession
from altaircms.models import Performance

from altaircms.page.models import PageSet
from altaircms.page.models import Page
from altaircms.page.models import PageDefaultInfo
from altaircms.page.models import PageAccesskey
from altaircms.page import subscribers as page_subscribers
from altaircms.auth.api import require_login
from altaircms.auth.api import get_or_404
from altaircms.event.models import Event

from altaircms.subscribers import notify_model_create

@view_config(permission="performance_update", route_name="plugins_jsapi_getti", renderer="json", 
             custom_predicates=(require_login, ))
def performance_add_getti_code(request):
    """ gettiのコードつける
    """
    ## todo: refactoring
    params = request.params
    codes = {}
    changed = []
    for k, getti_code in params.items():
        _, i = k.split(":", 1)
        codes[int(i)] = getti_code

    perfs = Performance.query.filter(Performance.id.in_(codes.keys()))
    perfs = request.allowable("Event", qs=perfs.filter(Performance.event_id==Event.id))
    for obj in perfs:
        changed.append(obj.id)
        getti_code = codes[obj.id]

        pc = "https://www.e-get.jp/tstar/pt/&s=%s" % getti_code
        mb = "https://www.e-get.jp/tstar/mt/&s=%s" % getti_code
        obj.purchase_link = pc
        obj.mobile_purchase_link = mb
        DBSession.add(obj)

    return {"status": "ok", 
            "changed": changed}


### pageset
@view_config(permission="page_create", 
             route_name="plugins_jsapi_pageset_reset_event", renderer="json", request_method="POST", 
             custom_predicates=(require_login, ))
def pageset_reset_event(request):
    pageset_id = request.matchdict["pageset_id"]
    pageset = get_or_404(request.allowable("PageSet"), PageSet.id==pageset_id)
    
    pageset.take_in_event(None)
    for page in pageset.pages:
        page_subscribers.notify_page_update(request, page)
    DBSession.add(pageset)
    return "OK"


@view_config(permission="page_create",
             route_name="plugins_jsapi_addpage", renderer="json", request_method="POST", 
             custom_predicates=(require_login,))
def pageset_addpage(request):
    pageset_id = request.matchdict["pageset_id"]
    pageset = get_or_404(request.allowable("PageSet"), PageSet.id==pageset_id)
    created = pageset.create_page()

    if created:
        DBSession.add(created)
        DBSession.flush()
        page_subscribers.notify_page_create(request, created)
        notify_model_create(request, created, {})
        return "OK"
    else:
        return "FAIL"


@view_defaults(route_name="plugins_jsapi_page_publish_status", renderer="json", request_method="POST", 
               custom_predicates=(require_login,))
class PageUpdatePublishStatus(object):
    def __init__(self, request):
        self.request = request

    @view_config(match_param="status=publish", )
    def page_status_to_publish(self):
        pageid = self.request.matchdict["page_id"]
        page = self.request.allowable("Page").filter_by(id=pageid).first()
        if page is None:
            return False
        else:
            self.request.allowable("Page").filter(Page.event_id==page.event_id).filter(Page.id!=pageid).filter(Page.publish_begin==page.publish_begin).update({"published": False})
            page.published = True
            DBSession.add(page)
            return True

    @view_config(match_param="status=unpublish")
    def page_status_to_unpublish(self):
        pageid = self.request.matchdict["page_id"]
        page = self.request.allowable("Page").filter_by(id=pageid).first()
        if page is None:
            return False
        else:
            page.published = False
            DBSession.add(page)
            return True


@view_config(route_name="plugins_api_page_info_default", renderer="json", 
             custom_predicates=(require_login, ))
def page_setup_info(request):
    try:
        params = request.params
        pdi = PageDefaultInfo.query.filter(PageDefaultInfo.pageset_id==params["parent"]).one()
        name = params["name"]
        title = pdi.title(name)
        jurl = pdi._url(name)
        url = pdi.url(name)
        parent = params["parent"]
        result = {
            "name": name, 
            "title": title, 
            "jurl": jurl, 
            "url": url, 
            "keywords": pdi.keywords, 
            "description": pdi.description, 
            "parent": parent
            }
        return result
    except Exception, e:
        return {"error": str(e)}

from ...tag.api import put_tags
import json

@view_config(route_name="plugins_jsapi_page_tag_delete", renderer="json", request_method="POST", 
             custom_predicates=(require_login, ))
def delete_page_tags(request):
    """ buggy"""
    page = request.allowable("Page").filter_by(id=request.matchdict["page_id"]).first()
    if page is None:
        return "FAIL"
    try:
        params = json.loads(request.params)
        put_tags(page, "page", params["tags"], params["private_tags"], request)
        return "OK"
    except ValueError:
        return "FAIL"
    
    
@view_defaults(route_name="plugins_jsapi_accesskey", permission="page_update", 
               custom_predicates=(require_login, )) ##?
class PageAccessKeyView(object):
    def __init__(self, request):
        self.request = request

    @view_config(renderer="json", request_method="POST", match_param="action=delete")
    def delete_accesskey(self):
        page_id = self.request.matchdict["page_id"]
        targets = self.request.params.getall("targets[]")
        targets = PageAccesskey.query.filter(PageAccesskey.id.in_(targets)).filter_by(page_id=page_id)
        for t in targets:
            DBSession.delete(t)
        return "OK"

    @view_config(renderer="json", request_method="POST", match_param="action=create")
    def create_accesskey(self):
        page_id = self.request.matchdict["page_id"]
        expire = self.request.params.get("expire", None)
        if expire:
            try:
                expire = datetime.strptime("%Y-%m-%d %H:%M:%S", expire)
            except ValueError:
                expire = None
                
        page = self.request.allowable("Page").filter_by(id=page_id).first()
        if page is None:
            return "FAIL"
        key = page.create_access_key(expire=expire)
        DBSession.add(key)
        return "OK"
        

