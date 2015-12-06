# encoding: utf-8
import venusian
from pyramid.util import viewdefaults
from .interfaces import ILateBoundRendererHelper

class lbr_view_config(object):
    venusian = venusian # for testing injection
    def __init__(self, **settings):
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings['for_']
        self.__dict__.update(settings)

    def add_view(self, config, *args, **kwargs):
        config.add_lbr_view(*args, **kwargs)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            self.add_view(config, view=ob, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped

class lbr_notfound_view_config(object):
    venusian = venusian # for testing injection
    def __init__(self, **settings):
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings['for_']
        self.__dict__.update(settings)

    def add_notfound_view(self, config, *args, **kwargs):
        config.add_lbr_notfound_view(*args, **kwargs)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            self.add_notfound_view(config, view=ob, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)

        if info.scope == 'class':
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped


class lbr_layout_config(object):
    venusian = venusian # for testing injection
    def __init__(self, name='', context=None, template=None, containment=None, **kwargs):
        self.name = name
        self.context = context
        self.template = template
        self.containment = containment
        self.kwargs = kwargs

    def add_layout(self, config, *args, **kwargs):
        config.add_lbr_layout(*args, **kwargs)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            self.add_layout(config, name, context, template, containment, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid_layout')

        settings['_info'] = info.codeinfo # fbo "action_method"
        return wrapped

@viewdefaults
def add_lbr_view(config, view=None, name="", **kwargs):
    renderer = kwargs.get('renderer')
    if renderer is not None:
        if ILateBoundRendererHelper.providedBy(renderer):
            renderer.bind(config.registry, config.package)
    config.add_view(view, name, **kwargs)

@viewdefaults
def add_lbr_notfound_view(config, view=None, name="", **kwargs):
    renderer = kwargs.get('renderer')
    if renderer is not None:
        if ILateBoundRendererHelper.providedBy(renderer):
            renderer.bind(config.registry, config.package)
    config.add_notfound_view(view, name, **kwargs)

def add_lbr_layout(config, layout=None, template=None, name='', context=None, containment=None, **kwargs):
    if template is not None:
        if ILateBoundRendererHelper.providedBy(template):
            template.bind(config.registry, config.package)
    config.add_layout(layout, template, name, context, containment, **kwargs)

def includeme(config):
    config.add_directive('add_lbr_view', add_lbr_view)
    config.add_directive('add_lbr_notfound_view', add_lbr_notfound_view)
    config.add_directive('add_lbr_layout', add_lbr_layout)
