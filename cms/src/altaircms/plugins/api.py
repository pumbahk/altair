# -*- coding:utf-8 -*-

### widget dispatch api
from ConfigParser import SafeConfigParser
from pyramid.path import AssetResolver

from pyramid.exceptions import ConfigurationError
from . import widget_aggregate as aggregate
from .interfaces import IWidgetAggregateDispatcher
from .helpers import list_from_setting_value ## for convinience

def page_type(request, page):
    if page.event_id is None:
        return "other_page"
    else:
        return "event_page"

def set_widget_aggregator_dispatcher(config, inifiles):
    assetresolver = AssetResolver()
    converted_paths = []

    for ini in inifiles:
        resolved = assetresolver.resolve(ini)
        if not resolved.exists():
            raise ConfigurationError("inifile: %s is not found" % resolved.abspath())
        converted_paths.append(resolved.abspath())
    dispatcher = parse_inifiles(config, converted_paths)
    config.registry.registerUtility(dispatcher, IWidgetAggregateDispatcher)

def get_widget_aggregator_dispatcher(request):
    return request.registry.getUtility(IWidgetAggregateDispatcher)

def get_widget_utility(request, page,_type):
    if not hasattr(request, "_widget_utilities"):
        request._widget_utilities = {}
    utility = request._widget_utilities.get((page.organization_id, type))
    if utility is None:
        dispacher = get_widget_aggregator_dispatcher(request)
        utility = dispacher.dispatch(request, page).utilities[_type]
        request._widget_utilities[(page.organization_id, type)] = utility
    return utility


def parse_inifiles(config, inifiles, validator=aggregate.widget_conflict_validator,_open=open):
    dispatcher = aggregate.WidgetAggregatorDispatcher()

    for inifile in inifiles:
        configparser = SafeConfigParser()
        with _open(inifile) as rf: ## use asset resolver ?
            configparser.readfp(rf)

        waconfig = aggregate.WidgetAggregatorConfig(config, configparser)
        dispatcher.add_dispatch_cont(waconfig.get_keys,
                                     waconfig.dispatch_function, 
                                     waconfig.create_subdispatch_dict(config, validator=validator)
                                     )
    return dispatcher
        
