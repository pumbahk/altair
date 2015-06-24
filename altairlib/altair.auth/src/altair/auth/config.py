from __future__ import absolute_import

import os
import logging
from pyramid.path import AssetResolver
from pyramid.interfaces import IRequest
from .interfaces import IWhoAPIDecider, IRequestClassifier, IPlugin, IForbiddenHandler
from .api import get_plugin_registry

logger = logging.getLogger(__name__)

def set_who_api_decider(config, callable, classification=None):
    callable = config.maybe_dotted(callable)
    reg = config.registry
    def register():
        logger.info("who_api_decider %s [%s] registered" % (callable, classification))
        if classification is None:
            reg.registerUtility(callable, IWhoAPIDecider)
        else:
            reg.registerUtility(callable, IWhoAPIDecider, name=classification)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='who api decider',
                                 title='altair.auth WHO API Decider',
                                 type_name=str(callable))
    intr['callable'] = callable

    config.action('altair.auth.set_who_api_decider', register,
                  introspectables=(intr,))

def set_request_classifier(config, callable):
    callable = config.maybe_dotted(callable)
    reg = config.registry

    def register():
        reg.registerUtility(callable, IRequestClassifier)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='request classifier',
                                 title='altair.auth Request Classifier',
                                 type_name=str(callable))
    intr['callable'] = callable

    config.action('altair.auth.set_request_classifier', register,
                  introspectables=(intr,))
    
    
def add_auth_plugin(config, auth_plugin):
    reg = config.registry

    def register():
        _auth_plugin = config.maybe_dotted(auth_plugin)
        get_plugin_registry(reg).register(_auth_plugin)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='auth plugin',
                                 title='{name} {auth_plugin}'.format(name=auth_plugin.name, auth_plugin=auth_plugin), 
                                 type_name=str(IPlugin))
    config.action('altair.auth.add_auth_plugin.{0}'.format(auth_plugin.name), register,
                  introspectables=(intr,))
    
    
def set_forbidden_handler(config, forbidden_handler):
    reg = config.registry

    def register():
        _forbiden_handler = config.maybe_dotted(forbidden_handler)
        reg.registerUtility(forbidden_handler, IForbiddenHandler)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='forbidden handler',
                                 title='%r' % forbidden_handler,
                                 type_name=str(IForbiddenHandler))
    config.action('altair.auth.set_forbidden_handler.{0}'.format(repr(forbidden_handler)), register,
                  introspectables=(intr,))

def includeme(config):
    config.add_directive('add_auth_plugin', add_auth_plugin)
    config.add_directive('set_who_api_decider', set_who_api_decider)
    config.add_directive('set_request_classifier', set_request_classifier)
    config.add_directive('set_forbidden_handler', set_forbidden_handler)
