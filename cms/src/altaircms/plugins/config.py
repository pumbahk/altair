# -*- coding:utf-8 -*-
import json
from zope.interface import implementer
from pyramid.exceptions import ConfigurationError
from ConfigParser import SafeConfigParser
from pyramid.path import AssetResolver

from . import widget_aggregate as aggregate
from .interfaces import IWidgetAggregateDispatcher, IWidgetUtilitiesDefault
from .interfaces import IExtraResource, IExtraResourceDefault
from .helpers import list_from_setting_value ## for convinience. dont remove-it
from altaircms.auth.api import get_organization_mapping
from altaircms.linklib import Stage

import logging
logger = logging.getLogger(__file__)

class ConfigParserBuilder(object):
    def __init__(self, config, _open=open):
        self.config = config
        self._open = _open

    def list_from_inifile_list(self, inifiles):
        assetresolver = AssetResolver()
        configparsers = []

        for ini in inifiles:
            resolved = assetresolver.resolve(ini)
            if not resolved.exists():
                raise ConfigurationError("inifile: %s is not found" % resolved.abspath())

            configparser = self._configparser_from_inifile(resolved.abspath())
            configparsers.append(configparser)
        return configparsers

    def from_inifile(self, inifile):
        assetresolver = AssetResolver()
        resolved = assetresolver.resolve(inifile)
        if not resolved.exists():
            raise ConfigurationError("inifile: %s is not found" % resolved.abspath())
        return self._configparser_from_inifile(resolved.abspath())

    
    def _configparser_from_inifile(self, path):
        configparser = SafeConfigParser()
        configparser._filename = path
        with self._open(path) as rf:
            configparser.readfp(rf)    
        return configparser

@implementer(IExtraResource)
class ExtraResource(dict):
    def __init__(self, items, stage):
        self.items = items
        self.stage = stage
        self.configure(items)

    def configure(self, items):
        for k, v in items:
            if hasattr(self, k):
                self[k] = getattr(self, k)(v)
            else:
                self[k] = self.parse(v)

    def cart_domain(self, v):
        candidates = json.loads(v)
        return candidates[self.stage].rstrip("/")

    def parse(self, v):
        return [x.decode("utf-8") for x in list_from_setting_value(v)] ## ok?

class WidgetSettingsSetup(object):
    def __init__(self, config, stage):
        self.config = config
        if not Stage.contains(stage):
            raise ConfigurationError("{k} is not found in {candidates}".format(k=stage, candidates=Stage._candidates))
        self.stage = stage

    def each_settings(self, configparsers, validator=aggregate.widget_conflict_validator):
        set_widget_aggregator_dispatcher(self.config, configparsers, validator=validator)
        for configparser in configparsers:
            set_extra_resource(self.config, configparser, self.stage)

    def default_setting(self, configparser, validator=aggregate.widget_conflict_validator):
        set_widget_aggregator_default(self.config, configparser, validator=validator)        
        set_extra_resource_default(self.config,  configparser, self.stage)

def set_extra_resource(config, configparser, stage):
    if not configparser.has_section("extra_resource"):
        raise ConfigurationError("extra_resource section is not found. %s" % configparser._filename)

    mapping = get_organization_mapping(config)
    keys = mapping.get_keypair(configparser.get("base", "organization.name"))
    params = ExtraResource(configparser.items("extra_resource"), stage) #xxx:

    logger.info("add -- extra resource %s" % str(keys))
    config.registry.registerUtility(params, IExtraResource, name=str(keys))

def set_extra_resource_default(config,  configparser, stage):
    if not configparser.has_section("extra_resource"):
        raise ConfigurationError("extra_resource section is not found. %s" % configparser._filename)
    params = ExtraResource(configparser.items("extra_resource"), stage)
    logger.info("add -- extra resource default")
    config.registry.registerUtility(params, IExtraResourceDefault)

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
