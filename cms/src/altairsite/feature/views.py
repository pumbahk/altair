# -*- coding:utf-8 -*-
import logging 
logger = logging.getLogger(__name__)
import os.path
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from urlparse import urljoin

from altaircms.page.staticupload.api import as_static_page_response
from altairsite.config import usersite_view_config
from altairsite.front.resources import AccessControlPC
from datetime import datetime
from altaircms.front.helpers import trim_japanese

@usersite_view_config(route_name="features")
def features_view(context, request):
    path = trim_japanese(request.matchdict["page_name"])
    if os.path.splitext(path)[1] == "":
        return HTTPFound(urljoin(request.route_path("features", page_name=os.path.join(path.rstrip("/"), "index.html")).replace("%2F", "/"), '?' + request.query_string))

    control = AccessControlPC(request)
    static_page = control.fetch_static_page_from_params(path, datetime.now())
    if not static_page:
        raise HTTPNotFound()
    return as_static_page_response(request, static_page, path)

