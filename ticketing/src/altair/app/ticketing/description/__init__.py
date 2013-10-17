# -*- coding:utf-8 -*-
from .interfaces import IModelDescription

def setup_model_description(config):
    from altair.app.ticketing.core.models import Organization
    from .impl import organization_description
    from altair.app.ticketing.core.models import Event
    from .impl import event_description
    from altair.app.ticketing.core.models import Performance
    from .impl import performance_description

    config.registry.adapters.register((), IModelDescription, name=Organization.__name__, value=organization_description)
    config.registry.adapters.register((), IModelDescription, name=Event.__name__, value=event_description)
    config.registry.adapters.register((), IModelDescription, name=Performance.__name__, value=performance_description)

    
    
def includeme(config):
    # config.include(".panels")
    config.include(setup_model_description)
