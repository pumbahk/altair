# -*- coding:utf-8 -*-
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from altaircms.auth.models import Organization
from altaircms.auth.interfaces import IAllowableQuery
from altaircms.auth.models import Host

import logging
logger = logging.getLogger(__name__)

def get_organization_from_request(request, override_host=None):
    if hasattr(request, "_organization"):
        return request._organization
    host_name = override_host or request.host
    organization = Organization.query.filter(Organization.id==Host.organization_id,  Host.host_name==host_name).first()
    if organization is None:
        logger.error("Host that named %s is not Found" % host_name)
        #raise Exception("Host that named %s is not Found" % host_name)
        raise HTTPBadRequest
    request._organization = organization
    return organization

class AllowableQueryFilterByOrganization(object):
    ExceptionClass = HTTPNotFound
    def __init__(self, request):
        self.request = request

    def __call__(self, model, qs=None):
        query = qs or model.query
        organization = get_organization_from_request(self.request)
        if organization is None:
            logger.warn("*separation host=%s organization is not found",  self.request.host)
            raise self.ExceptionClass("organization is not found")
        if not hasattr(model, "organization_id"):
            return query
        return query.with_transformation(organization.inthere("organization_id"))

## selectable renderer
from pyramid_selectable_renderer import SelectableRendererSetup 
from pyramid_selectable_renderer.custom import ReceiveTemplatePathFormat, ReceiveTemplatePathCandidatesDict
from pyramid_selectable_renderer.custom import SelectByRequestGen

@SelectByRequestGen.generate
def get_template_path_args(request):
    try:
        return dict(prefix=request.organization.short_name)
    except:
        return dict(prefix="__default__")

## use this. view_config(...,  renderer=selectable_renderer="%(prefix)/errors.html")
selectable_renderer = SelectableRendererSetup(
    ReceiveTemplatePathFormat,
    get_template_path_args, 
    renderer_name = "selectable_renderer")

tstar_mobile_or_not_renderer = SelectableRendererSetup(
    ReceiveTemplatePathCandidatesDict,
    SelectByRequestGen.generate(lambda r : r.organization.short_name), 
    renderer_name = "tstar_mobile_or_not_renderer"
)

def enable_search_function(info, request):
    use_full_usersite = request.organization.use_full_usersite if request.organization else False

    enable_orgs = 'RT', 'RL', 'KT'
    if use_full_usersite:
        for enable_org in enable_orgs:
            if enable_org == request.organization.short_name:
                return True

## todo: もっと細かく用途制限
def enable_full_usersite_function(info, request):
    return request.organization.use_full_usersite if request.organization else False
enable_smartphone = enable_full_usersite_function
enable_mobile = enable_full_usersite_function


def includeme(config):
    """
    """
    config.registry.registerUtility(AllowableQueryFilterByOrganization, IAllowableQuery)
    config.set_request_property(get_organization_from_request, "organization", reify=True)
    config.set_request_property(AllowableQueryFilterByOrganization, "allowable", reify=True)
    
    selectable_renderer.register_to(config)
    tstar_mobile_or_not_renderer.register_to(config)
