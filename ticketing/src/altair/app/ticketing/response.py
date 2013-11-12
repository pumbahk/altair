# -*- coding:utf-8 -*-
import venusian
from pyramid.exceptions import ConfigurationError
from pyramid.renderers import (
    render_to_response,
    get_renderer
)
from zope.interface import Interface

def verify_static_renderer(config, renderer):
    def register():
        try:
            get_renderer(renderer).implementation() #xxx.
        except Exception as e:
            raise ConfigurationError(repr(e))
    ## renderer factory registration on PHASE1_CONFIG(=-20). so.
    config.action((Interface, renderer), register)

def static_renderer(renderer, venusian_=venusian):
    """decoratorで渡したtemplateが存在することをconfiguration timeに確認する"""
    def _static_renderer(fn):
        def wrapped(request, kwargs):
            return fn(request, kwargs, renderer)
        def callback(context, name, ob):
            config = context.config
            verify_static_renderer(config, renderer)
        venusian_.attach(wrapped, callback)
        return wrapped
    return _static_renderer

@static_renderer('altair.app.ticketing:templates/refresh.html')
def refresh_response(request, kwargs, renderer):
    return render_to_response(renderer, kwargs, request=request)

