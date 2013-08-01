# -*- coding:utf-8 -*-
### widget dispatch api
from .interfaces import IExtraResource, IExtraResourceDefault
from .interfaces import IWidgetAggregateDispatcher
from altaircms.auth.api import fetch_correct_organization
from altaircms.auth.api import get_organization_mapping
from .helpers import list_from_setting_value ## for convinience. dont remove-it

import logging
logger = logging.getLogger(__file__)

### extra resource
def get_extra_resource(request):
    organization = fetch_correct_organization(request)
    mapping = get_organization_mapping(request)
    keys = mapping.get_keypair_from_organization(organization)
    extra = request.registry.queryUtility(IExtraResource, name=str(keys))
    if extra:
        return extra
    return request.registry.getUtility(IExtraResourceDefault)

def _get_scheme_from_request(request):
    return "https" if request.url.startswith("https") else "http"

def get_cart_domain(request):
    extra_resource = get_extra_resource(request)
    if "cart_domain" in extra_resource:
        netloc = extra_resource["cart_domain"]
        scheme = _get_scheme_from_request(request)
        request._cart_domain = "{scheme}://{netloc}".format(scheme=scheme, netloc=netloc)
    else:
        request._cart_domain = ""
    return request._cart_domain


## widget aggregator

def page_type(request, page):
    if page.event_id is None:
        return "other_page"
    else:
        return "event_page"

def get_widget_aggregator_dispatcher(request):
    return request.registry.getUtility(IWidgetAggregateDispatcher)

def get_widget_utility(request, page,_type):
    logger.debug("*get widget utility* %s" % _type)
    if not hasattr(request, "_widget_utilities"):
        request._widget_utilities = {} #weak dict?
    utility = request._widget_utilities.get((page.organization_id, _type))
    if utility:
        return utility
    try:
        dispacher = get_widget_aggregator_dispatcher(request)
        utility = dispacher.dispatch(request, page).utilities[_type]
        request._widget_utilities[(page.organization_id, _type)] = utility
        return utility
    except KeyError:
        logger.warn("widget utility is not found page=%s, type=%s" % (page.id,  _type))
        raise Exception("widget utility is not found page=%s, type=%s" % (page.id,  _type))
