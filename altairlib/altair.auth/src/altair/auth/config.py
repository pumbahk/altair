import os
import logging
from pyramid.path import AssetResolver
from pyramid.interfaces import IRequest
from repoze.who.interfaces import IAPIFactory, IAPI
from .interfaces import IWhoAPIDecider
from .api import get_who_api_factory_registry

logger = logging.getLogger(__name__)

def set_who_api_decider(config, callable):
    callable = config.maybe_dotted(callable)
    reg = config.registry

    def register():
        reg.adapters.register([IRequest], IWhoAPIDecider, "", callable)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='who api decider',
                                 title='altair.auth WHO API Decider',
                                 type_name=str(callable))
    intr['callable'] = callable

    config.action('altair.auth.set_who_api_decider', register,
                  introspectables=(intr,))

    

def add_who_api_factory(config, name, who_api_factory):
    reg = config.registry

    def register():
        _who_api_factory = config.maybe_dotted(who_api_factory)
        get_who_api_factory_registry(reg).register(name, _who_api_factory)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='who api factory',
                                 title='{name} {who_api_factory}'.format(name=name, who_api_factory=who_api_factory), 
                                 type_name=str(IAPIFactory))
    config.action('altair.auth.add_who_api_factory.{0}'.format(name), register,
                  introspectables=(intr,))

def includeme(config):
    config.add_directive('add_who_api_factory', add_who_api_factory)
    config.add_directive('set_who_api_decider', set_who_api_decider)
