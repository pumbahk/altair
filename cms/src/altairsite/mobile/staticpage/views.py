# -*- coding:utf-8 -*-
import logging 
logger = logging.getLogger(__name__)
import os.path
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from urlparse import urljoin

from altaircms.page.staticupload.api import as_static_page_response
from altairsite.config import usersite_view_config
from altairsite.fetcher import get_current_page_fetcher
from datetime import datetime

def not_static_path(info, request):
    return not request.path.startswith("static")

## deprecated view?
@usersite_view_config(route_name="staticpage", request_type="altair.mobile.interfaces.IMobileRequest", custom_predicates=(not_static_path, ))
def staticpage_view(context, request):
    # logger.debug("req2:"+request.path)
    path = request.matchdict["page_name"]
    if os.path.splitext(path)[1] == "":
        path=os.path.join(path.rstrip("/"), "index.html")
        redirect_url = urljoin(request.current_route_path(page_name=path).replace("%2F", "/"), '?' + request.query_string)
        return HTTPFound(redirect_url)

    prefix = path.split("/", 1)[0]
    if prefix == path:
        prefix = ""
    static_page = get_current_page_fetcher(request).static_page(request, prefix, datetime.now())
    if not static_page:
        raise HTTPNotFound()
    return as_static_page_response(request, static_page, path)

