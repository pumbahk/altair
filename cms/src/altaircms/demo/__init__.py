import os
here = os.path.abspath(os.path.dirname(__file__))

def includeme(config):
    config.add_route("demo1", "/demo/demo1")
    config.scan("altaircms.demo")

    assetpath = os.path.join(here, "asset")
    if not os.path.exists(assetpath):
        os.makedirs(assetpath)
    config.registry.settings["asset.storepath"] = assetpath
    from pyramid.threadlocal import get_current_registry
    gregistry = get_current_registry()
    gregistry.settings = config.registry.settings
    from . import initialize
    print "---------------------------------"
    initialize.init()
    print "---------------------------------"
