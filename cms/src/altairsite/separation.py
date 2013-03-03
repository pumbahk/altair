# -*- coding:utf-8 -*-
from pyramid.httpexceptions import HTTPNotFound
from altaircms.auth.models import Organization
from altaircms.auth.interfaces import IAllowableQuery
from altaircms.auth.models import Host
from sqlalchemy.orm.exc import NoResultFound
import logging
logger = logging.getLogger(__name__)

def get_organization_from_request(request, override_host=None):
    host_name = override_host or request.host
    try:
        return Organization.query.filter(Organization.id==Host.organization_id,  Host.host_name==host_name).first()
    except NoResultFound:
        raise Exception("Host that named %s is not Found" % host_name)

class AllowableQueryFilterByOrganization(object):
    ExceptionClass = HTTPNotFound
    def __init__(self, request):
        if hasattr(request,  "organization"):
            self.call = self.allowable_query
        else:
            self.call = self.allowable_query_with_fetch
        self.request = request

    def __call__(self,  model,  qs=None):
        return self.call(model, qs=qs)

    def allowable_query(self, model, qs=None):
        query = qs or model.query
        organization = self.request.organization
        if organization is None:
            logger.warn("*separation host=%s organization is not found",  self.request.host)
            raise self.ExceptionClass("organization is not found")
        return query.with_transformation(organization.inthere("organization_id"))

    def allowable_query_with_fetch(self, model, qs=None):
        query = qs or model.query
        organization = get_organization_from_request(self.request)
        if organization is None:
            logger.warn("*separation host=%s organization is not found",  self.request.host)
            raise self.ExceptionClass("organization is not found")
        return query.with_transformation(organization.inthere("organization_id"))

## selectable renderer
from pyramid_selectable_renderer import SelectableRendererSetup 
from pyramid_selectable_renderer.custom import RecieveTemplatePathFormat, RecieveTemplatePathCandidatesDict
from pyramid_selectable_renderer.custom import SelectByRequestGen

@SelectByRequestGen.generate
def get_template_path_args(request):
    try:
        return dict(prefix=request.organization.short_name)
    except:
        return dict(prefix="__default__")

## use this. view_config(...,  renderer=selectable_renderer="%(prefix)/errors.html")
selectable_renderer = SelectableRendererSetup(
    RecieveTemplatePathFormat,
    get_template_path_args, 
    renderer_name = "selectable_renderer")

tstar_mobile_or_not_renderer = SelectableRendererSetup(
    RecieveTemplatePathCandidatesDict, 
    SelectByRequestGen.generate(lambda r : r.organization.short_name), 
    renderer_name = "tstar_mobile_or_not_renderer"
)

def includeme(config):
    """
    """
    config.registry.registerUtility(AllowableQueryFilterByOrganization, IAllowableQuery)
    config.set_request_property(get_organization_from_request, "organization", reify=True)
    config.set_request_property(AllowableQueryFilterByOrganization, "allowable", reify=True)
    
    selectable_renderer.register_to(config)
    tstar_mobile_or_not_renderer.register_to(config)
