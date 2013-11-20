# -*- coding:utf-8 -*-
import venusian
from pyramid.exceptions import ConfigurationError
from pyramid.renderers import (
    render_to_response,
    RendererHelper
)
from pyramid.interfaces import PHASE2_CONFIG
from zope.interface import Interface

def verify_static_renderer(config, renderer):
    def register():
        try:
            assert RendererHelper(renderer, registry=config.registry).renderer.implementation()
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(repr(e))
    ## renderer factory registration on PHASE1_CONFIG(=-20). so.
    config.action((Interface, renderer), register, order=PHASE2_CONFIG)

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

@static_renderer("altair.app.ticketing:templates/common/simpleform.html")
def formbody_response(request, form, renderer):
    return render_to_response(renderer, {"form": form}, request=request)
