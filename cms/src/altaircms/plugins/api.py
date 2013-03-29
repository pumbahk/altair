# -*- coding:utf-8 -*-
import logging 
logger = logging.getLogger(__name__)
### widget dispatch api
from ConfigParser import SafeConfigParser
from pyramid.path import AssetResolver
from pyramid.exceptions import ConfigurationError
from . import widget_aggregate as aggregate
from .interfaces import IWidgetAggregateDispatcher, IWidgetUtilitiesDefault
from .interfaces import IExtraResource, IExtraResourceDefault
from .helpers import list_from_setting_value ## for convinience. dont remove-it
from zope.interface import implementer
from altaircms.auth.api import fetch_correct_organization
from altaircms.auth.api import get_organization_mapping

import logging
logger = logging.getLogger(__file__)


def get_configparsers_from_inifiles(config, inifiles, _open=open):
    assetresolver = AssetResolver()
    configparsers = []

    for ini in inifiles:
        resolved = assetresolver.resolve(ini)
        if not resolved.exists():
            raise ConfigurationError("inifile: %s is not found" % resolved.abspath())
        
        configparser = _configparser_from_inifile(resolved.abspath(), _open=_open)
        configparsers.append(configparser)
    return configparsers

def get_configparser_from_inifile(config, inifile, _open=open):
    assetresolver = AssetResolver()
    resolved = assetresolver.resolve(inifile)
    if not resolved.exists():
        raise ConfigurationError("inifile: %s is not found" % resolved.abspath())
    return _configparser_from_inifile(resolved.abspath(), _open=_open)

    
def _configparser_from_inifile(path, _open=open):
    configparser = SafeConfigParser()
    configparser._filename = path
    with _open(path) as rf:
        configparser.readfp(rf)    
    return configparser

### extra resource

@implementer(IExtraResource)
class ExtraResource(dict):
    def __init__(self, items):
        self.items = items
        for k, v in items:
            self[k] = self.parse(v)

    def parse(self, v):
        return [x.decode("utf-8") for x in list_from_setting_value(v)] ## ok?

def set_extra_resource(config, configparser):
    if not configparser.has_section("extra_resource"):
        raise ConfigurationError("extra_resource section is not found. %s" % configparser._filename)

    mapping = get_organization_mapping(config)
    keys = mapping.get_keypair(configparser.get("base", "organization.name"))
    params = ExtraResource(configparser.items("extra_resource"))

    logger.info("add -- extra resource %s" % str(keys))
    config.registry.registerUtility(params, IExtraResource, name=str(keys))

def set_extra_resource_default(config,  configparser):
    if not configparser.has_section("extra_resource"):
        raise ConfigurationError("extra_resource section is not found. %s" % configparser._filename)
    params = ExtraResource(configparser.items("extra_resource"))
    logger.info("add -- extra resource default")
    config.registry.registerUtility(params, IExtraResourceDefault)
    

def get_extra_resource(request):
    organization = fetch_correct_organization(request)
    mapping = get_organization_mapping(request)
    keys = mapping.get_keypair_from_organization(organization)
    extra = request.registry.queryUtility(IExtraResource, name=str(keys))
    if extra:
        return extra
    return request.registry.getUtility(IExtraResourceDefault)

def get_cart_domain(request):
    extra_resource = get_extra_resource(request)
    if "cart_domain" in extra_resource:
        domain = extra_resource["cart_domain"]
        if isinstance(domain, (list, tuple)):
            domain = domain[0]
        request._cart_domain = domain.rstrip("/")
    else:
        request._cart_domain = ""
    return request._cart_domain


## widget aggregator

def page_type(request, page):
    if page.event_id is None:
        return "other_page"
    else:
        return "event_page"

def set_widget_aggregator_dispatcher(config, configparsers, validator=aggregate.widget_conflict_validator):
    dispatcher = aggregate.WidgetAggregatorDispatcher()
    for configparser in configparsers:
        waconfig = aggregate.WidgetAggregatorConfig(config, configparser)
        logger.info("loading...%s" % configparser._filename)
        dispatcher.add_dispatch_cont(waconfig.get_keys, 
                                     waconfig.dispatch_function,
                                     waconfig.create_subdispatch_dict(config, validator=validator)
                                     )
    config.registry.registerUtility(dispatcher, IWidgetAggregateDispatcher)
    return dispatcher

def set_widget_aggregator_default(config,  configparser,  validator=aggregate.widget_conflict_validator):
    waconfig = aggregate.WidgetAggregatorConfig(config, configparser)
    widget_utilities = waconfig.create_subdispatch_dict(config, validator=validator)
    def get_default_utility(request, page):
        _type = waconfig.dispatch_function(request, page)
        logger.info("matched widget utility is not found. get default widget utility page=%s, type=%s" % (page.id,  _type))
        return widget_utilities[_type]
    config.registry.registerUtility(get_default_utility, IWidgetUtilitiesDefault)

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
