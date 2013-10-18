# -*- coding:utf-8 -*-
import logging
from .fanstatic_resources import bj89ers, nh, nh_dev
from altair.mobile.interfaces import IMobileRequest
from pyramid.config import ConfigurationError
from .interfaces import (
    ITrackingCodeInjector,
    ITrackingCodeInjectorFactory,
    ITrackingInterceptor,
    ITrackingInterceptorFactory,
    ITrackingInterceptorPredicateFactory,
    ITrackingInjectorPredicateFactory,
    )

CONFIG_PREFIX = __name__
DEFAULT_TRACKER_TYPE = 'google_analytics'
CONTENT_TYPES = ['text/html', 'text/xml', 'application/xhtml+xml']

logger = logging.getLogger(__name__)

class TrackerConfiguration(object):
    def __init__(self, name, domain, injector, handler, interceptor_predicate, injector_predicate):
        self.name = name
        self.domain = domain
        self.injector = injector
        self.handler = handler
        self.interceptor_predicate = interceptor_predicate
        self.injector_predicate = injector_predicate

def retrieve_settings(registry):
    settings_dict = {}
    _prefix = CONFIG_PREFIX + '.'
    for k, v in registry.settings.items():
        if k.startswith(_prefix):
            setting_name, _, dotted_key = k[len(_prefix):].partition('.')
            key_comps = dotted_key.split('.')
            ns = settings_dict.setdefault(setting_name, {})
            for key_comp in key_comps[:-1]:
                ns = ns.setdefault(key_comp, {})
            ns[key_comps[-1]] = v
    return settings_dict

def create_injector(registry, type_, **kwargs):
    factory = registry.queryUtility(ITrackingCodeInjectorFactory, type_)
    return factory and factory(type_, **kwargs)

def create_interceptor(registry, handler, type_, **kwargs):
    factory = registry.queryUtility(ITrackingInterceptorFactory, type_)
    return factory and factory(handler, type_, **kwargs)

def get_interceptor_predicate_factory(registry, predicate_name):
    return registry.queryUtility(ITrackingInterceptorPredicateFactory, predicate_name)

def get_injector_predicate_factory(registry, predicate_name):
    return registry.queryUtility(ITrackingInjectorPredicateFactory, predicate_name)

def call_factory(registry, factory, args):
    if isinstance(args, dict):
        return factory(registry, **args)
    else:
        return factory(registry, args)

def resolve_predicates(registry, predicates_config):
    interceptor_predicates = []
    injector_predicates = []

    if predicates_config:
        for predicate_name, args in predicates_config.items():
            factory = get_interceptor_predicate_factory(registry, predicate_name)
            if factory:
                interceptor_predicate = call_factory(registry, factory, args)
                interceptor_predicates.append(interceptor_predicate)
            factory = get_injector_predicate_factory(registry, predicate_name)
            if factory:
                injector_predicate = call_factory(registry, factory, args)
                injector_predicates.append(injector_predicate)

    if interceptor_predicates:
        def interceptor_predicate(request):
            return all(
                interceptor_predicate.should_intercept(request)
                for interceptor_predicate in interceptor_predicates
                )
    else:
        def interceptor_predicate(request):
            return True

    if injector_predicates:
        def injector_predicate(request, response):
            return all(
                injector_predicate.should_inject(request, response)
                for injector_predicate in injector_predicates
                )
    else:
        def injector_predicate(request, response):
            return True

    return interceptor_predicate, injector_predicate

def gaq_tween_factory(handler, registry):
    import re
    setting_names = re.split(r'\s+', registry.settings.get(CONFIG_PREFIX, ''))
    settings_dict = retrieve_settings(registry)

    tracker_configs = {}

    for setting_name in setting_names:
        settings_for_name = settings_dict[setting_name]
        type_ = settings_for_name.pop('type', DEFAULT_TRACKER_TYPE)
        predicates_config = settings_for_name.pop('predicates', None)
        domain = settings_for_name['domain']
        injector = create_injector(registry, type_, **settings_for_name)
        if injector is None:
            raise ConfigurationError('could not find a suitable injector for type %s' % type_)

        _handler = create_interceptor(registry, handler, type_, **settings_for_name)
        interceptor_predicate_fn, injector_predicate_fn = resolve_predicates(registry, predicates_config)
        tracker_configs[domain] = \
            TrackerConfiguration(
                name=setting_name,
                domain=domain,
                injector=injector,
                handler=_handler,
                interceptor_predicate=interceptor_predicate_fn,
                injector_predicate=injector_predicate_fn
                )
        logger.info('creating tracker configuration [%s] type=%s, injector=%r, handler=%r, %r' % (setting_name, type_, injector, _handler, settings_for_name))

    def should_apply_injector(request, response):
        return response.content_type in CONTENT_TYPES

    def tween(request):
        if not IMobileRequest.providedBy(request) or request.mobile_ua.carrier.is_nonmobile:
            tracker_config = tracker_configs.get(request.host)
            logger.debug('looking up tracker configuration for host %s' % request.host)
            if tracker_config is not None:
                logger.debug('applying tracking configuration %s for %s' % (tracker_config.name, tracker_config.domain))
                if tracker_config.interceptor_predicate(request) and tracker_config.handler:
                    logger.debug('intercepting the request for tracking')
                    response = tracker_config.handler(request)
                else:
                    logger.debug('not intercepting the request because of predicate mismatch')
                    response = handler(request)

                if tracker_config.injector is not None and \
                   should_apply_injector(request, response) and \
                   tracker_config.injector_predicate(request, response):
                    logger.debug('injecting the tracking code into response')
                    response = tracker_config.injector(request, response)
                else:
                    logger.debug('not injecting the tracking code into response')
                return response
        return handler(request)
    return tween

def includeme(config):
    import pyramid
    config.include('.predicates')
    config.include('.ga')
    # fanstaticよりも先
    config.add_tween(".gaq_tween_factory", over='pyramid_fanstatic.tween_factory')    
