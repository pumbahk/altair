# -*- coding:utf-8 -*-
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPBadRequest
from datetime import datetime
import sqlalchemy.orm as orm
from altaircms.helpers.viewhelpers import FlashMessage
from pyramid.view import view_config
from pyramid.view import view_defaults
import logging
logger = logging.getLogger(__file__)
from altaircms.models import DBSession
from altaircms.models import Performance

from altaircms.page.models import PageSet
from altaircms.page.models import Page
from altaircms.page.models import PageType
from altaircms.page.models import PageDefaultInfo
from altaircms.page import subscribers as page_subscribers
from altaircms.page.nameresolver import GetPageInfoException
from altaircms.auth.api import require_login
from altaircms.auth.api import get_or_404
from altaircms.event.models import Event
from altaircms.models import Genre
from altaircms.subscribers import notify_model_create

@view_config(permission="performance_update", route_name="plugins_jsapi_getti", renderer="json")
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
    perfs = perfs.options(orm.joinedload(Performance.event))

    for obj in perfs:
        if obj.event.organization_id != request.organization.id:
            continue
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
    pageset = get_or_404(request.allowable(PageSet), PageSet.id==pageset_id)
    
    pageset.take_in_event(None)
    for page in pageset.pages:
        page_subscribers.notify_page_update(request, page)
    DBSession.add(pageset)
    return "OK"

from altaircms.page.views import page_editable_from_pagetype

@view_config(permission="page_create",
             route_name="plugins_jsapi_addpage", renderer="json", request_method="POST", 
             custom_predicates=(require_login,))
def pageset_addpage(context, request):
    pageset_id = request.matchdict["pageset_id"]
    pageset = get_or_404(request.allowable(PageSet), PageSet.id==pageset_id)
    if not page_editable_from_pagetype(context, pageset.pagetype):
        raise HTTPForbidden("not enough permission to edit it")
    try:
        created = pageset.create_page(force=True)

        if created:
            DBSession.add(created)
            DBSession.flush()
            params = {"tags": "", "private_tags": "", "mobile_tags": ""} #xxx:
            page_subscribers.notify_page_create(request, created, params)
            notify_model_create(request, created, params)
            FlashMessage.success(u"新しいページが作成されました.")
            return "OK"
        else:
            logger.warn("base page is not found")
            raise HTTPBadRequest("NG")
    except Exception, e:
        logger.exception(str(e))

@view_defaults(route_name="plugins_jsapi_page_publish_status", renderer="json", request_method="POST", 
               custom_predicates=(require_login,))
class PageUpdatePublishStatus(object):
    def __init__(self, request):
        self.request = request

    @view_config(match_param="status=publish", )
    def page_status_to_publish(self):
        pageid = self.request.matchdict["page_id"]
        page = self.request.allowable(Page).filter_by(id=pageid).first()
        if page is None:
            return False
        else:
            self.request.allowable(Page)\
            .filter(Page.id!=pageid)\
            .filter(Page.pageset_id==page.pageset_id)\
            .filter(Page.publish_begin==page.publish_begin).update({"published": False})
            page.published = True
            DBSession.add(page)
            return True

    @view_config(match_param="status=unpublish")
    def page_status_to_unpublish(self):
        pageid = self.request.matchdict["page_id"]
        page = self.request.allowable(Page).filter_by(id=pageid).first()
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
        pagetype = PageType.query.filter_by(id=params["pagetype"]).one()
        pdi = PageDefaultInfo.query.filter(PageDefaultInfo.pagetype_id==params["pagetype"]).first()
        if pdi is None:
            return {"error": u"ページの初期設定が登録されていません"}
        genre = Genre.query.filter_by(id=params["genre"]).first()
        try:
            if "event" in params:
                event = Event.query.filter_by(id=params["event"]).first()
                info = pdi.get_page_info(pagetype, genre, event)
            else:
                event = None
                info = pdi.get_page_info(pagetype, genre, None)
        except GetPageInfoException, e:
            logger.warn("*api page default info* invalid request: %s" % str(e))
            return {"error": e.jmessage}

        name = params["name"]
        result = {
            "name": name or info.name, 
            "caption": info.caption,
            "title_prefix": info.title_prefix,
            "title": info.title,
            "title_suffix": info.title_suffix,
            "event": event.id if event else None,
            "url": info.url.lstrip("/") if not info.url.startswith(("http://", "https://")) else info.url, 
            "genre": params["genre"], 
            "keywords": info.keywords, 
            "description": info.description, 
            }
        return result
    except Exception, e:
        logger.exception(str(e))
        return {"error": str(e)}

from ...tag.api import put_tags
import json

@view_config(route_name="plugins_jsapi_page_tag_delete", renderer="json", request_method="POST", 
             custom_predicates=(require_login, ))
def delete_page_tags(request):
    """ buggy"""
    page = request.allowable(Page).filter_by(id=request.matchdict["page_id"]).first()
    if page is None:
        return "FAIL"
    try:
        params = json.loads(request.params)
        put_tags(page, "page", params["tags"], params["private_tags"], request)
        return "OK"
    except ValueError:
        return "FAIL"
   
   
        

