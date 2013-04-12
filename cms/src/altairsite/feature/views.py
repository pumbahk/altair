# -*- coding:utf-8 -*-
import logging 
logger = logging.getLogger(__name__)
import os.path
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from urlparse import urljoin

from altaircms.page.models import StaticPage
from altaircms.page.api import as_static_page_response, StaticPageNotFound
from altairsite.config import usersite_view_config

@usersite_view_config(route_name="features")
def features_view(context, request):
    path = request.matchdict["path"]
    prefix = path.split("/", 1)[0]
    logger.debug("prefix: %s" % prefix)

    if os.path.splitext(path)[1] == "":
        return HTTPFound(urljoin(request.route_path("features", path=os.path.join(path.rstrip("/"), "index.html")).replace("%2F", "/"), '?' + request.query_string))
    if prefix:
        static_page = request.allowable(StaticPage).filter(StaticPage.name==prefix, StaticPage.published==True, StaticPage.interceptive==False).first()
        if static_page:
            return as_static_page_response(request, static_page, path)
    raise HTTPNotFound()
