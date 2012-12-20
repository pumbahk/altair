from .interfaces import ILayoutCreator
from .creation import LayoutCreator

def get_layout_creator(request):
    return request.registry.getUtility(ILayoutCreator)

def register_layout_creator(config, dir_setting):
    creator = LayoutCreator(dir_setting)
    config.registry.registerUtility(creator, ILayoutCreator)
