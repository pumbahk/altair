# This package may contain traces of nuts
import os
from pyramid.path import AssetResolver
from repoze.who.interfaces import IAPIFactory, IAPI
from repoze.who.config import make_api_factory_with_config

def add_who_api_factory(config, name, ini_file):
    assets = AssetResolver(config.package)
    reg = config.registry
    resolver = assets.resolve(ini_file)
    ini_file = resolver.abspath()

    def register():
        global_conf = {'here': os.path.dirname(ini_file)}
        who_api_factory = make_api_factory_with_config(global_conf,
                                                       ini_file)
        reg.registerUtility(who_api_factory, name=name)

    config.action('altair.auth', register)


def who_api_factory(request, name):
    reg = request.registry
    return reg.getUtility(IAPIFactory, name=name)

def who_api(request, name=""):
    factory = who_api_factory(request, name=name)
    api = factory(request.environ)
    return api

def includeme(config):
    """
    """
    config.add_directive('add_who_api_factory',
                         add_who_api_factory)
    ini_specs = config.registry.settings.get('altair.auth.specs', "")

    if isinstance(ini_specs, basestring):
        ini_specs = [i.strip() for i in ini_specs.strip().split("\n")
                     if i.strip()]

    for ini_spec in ini_specs:
        if isinstance(ini_spec, basestring):
            if "=" in ini_spec:
                name, ini_file = ini_spec.split("=", 1)
            else:
                name = os.path.splitext(os.path.basename(ini_spec))[0]
                ini_file = ini_spec
        else:
            name, ini_file = ini_spec
        config.add_who_api_factory(name, ini_file)
    
    
