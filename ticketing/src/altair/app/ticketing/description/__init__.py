# -*- coding:utf-8 -*-
from .interfaces import IModelDescription

def includeme(config):
    from altair.app.ticketing.core.models import Event
    from .api import event_description
    from altair.app.ticketing.core.models import Performance
    from .api import performance_description
    # config.include(".panels")
    config.registry.adapters.register((), IModelDescription, name=Event.__name__, value=event_description)
    config.registry.adapters.register((), IModelDescription, name=Performance.__name__, value=performance_description)

    
