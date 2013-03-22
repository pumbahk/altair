# -*- coding:utf-8 -*-
import logging 
logger = logging.getLogger(__name__)

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

from altaircms.page.models import StaticPage
from altaircms.page.api import as_static_page_response, StaticPageNotFound

@view_config(route_name="features")
def features_view(context, request):
    path = request.matchdict["path"]
    prefix = path.split("/", 1)[0]
    logger.debug("prefix: %s" % prefix)
    try:
        if prefix:
            static_page = request.allowable(StaticPage).filter(StaticPage.name==prefix, StaticPage.published==True, StaticPage.interceptive==False).first()
            if static_page:
                return as_static_page_response(request, static_page, path)
    except StaticPageNotFound as e:
        logger.info(str(e))
    except Exception, e:
        logger.exception(str(e))
    raise HTTPNotFound()        
