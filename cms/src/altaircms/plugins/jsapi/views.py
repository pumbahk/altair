# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.view import view_defaults

from altaircms.models import DBSession
from altaircms.models import Performance

from altaircms.page.models import PageSet
from altaircms.page.models import Page
from altaircms.page.models import PageDefaultInfo
from altaircms.page import subscribers as page_subscribers

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

    for obj in Performance.query.filter(Performance.id.in_(codes.keys())):
        changed.append(obj.id)
        getti_code = codes[obj.id]

        pc = "https://www.e-get.jp/tstar/pt/&s=%s" % getti_code
        mb = "https://www.e-get.jp/tstar/mt/&s=%s" % getti_code
        obj.purchase_link = pc
        obj.mobile_purchase_link = mb
        DBSession.add(obj)

    return {"status": "ok", 
            "changed": changed}

### page
@view_config(permission="page_create",
             route_name="plugins_jsapi_addpage", renderer="json", request_method="POST")
def pageset_addpage(request):
    pageset_id = request.matchdict["pageset_id"]
    pageset = PageSet.query.filter_by(id=pageset_id).first()
    created = pageset.create_page()

    if created:
        DBSession.add(created)
        DBSession.flush()
        page_subscribers.notify_page_create(request, created)
        return "OK"
    else:
        return "FAIL"


@view_defaults(route_name="plugins_jsapi_page_publish_status", renderer="json", request_method="POST")
class PageUpdatePublishStatus(object):
    def __init__(self, request):
        self.request = request

    @view_config(match_param="status=publish")
    def page_status_to_publish(self):
        pageid = self.request.matchdict["page_id"]
        page = Page.query.filter_by(id=pageid).first()
        if page is None:
            return False
        else:
            Page.query.filter(Page.event_id==page.event_id).filter(Page.id!=pageid).filter(Page.publish_begin==page.publish_begin).update({"published": False})
            page.published = True
            DBSession.add(page)
            return True

    @view_config(match_param="status=unpublish")
    def page_status_to_unpublish(self):
        pageid = self.request.matchdict["page_id"]
        page = Page.query.filter_by(id=pageid).first()
        if page is None:
            return False
        else:
            page.published = False
            DBSession.add(page)
            return True


@view_config(route_name="plugins_api_page_info_default", renderer="json")
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
