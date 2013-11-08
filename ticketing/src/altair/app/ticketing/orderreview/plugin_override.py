# encoding: utf-8

import logging

logger = logging.getLogger(__name__)

def setup_renderers(config):
    import os
    import functools
    from zope.interface import implementer
    from pyramid.interfaces import IRendererFactory
    from pyramid.renderers import RendererHelper
    from pyramid.path import AssetResolver
    from pyramid_selectable_renderer import SelectableRendererFactory
    from altair.app.ticketing.payments.interfaces import IPaymentViewRendererLookup
    from altair.app.ticketing.cart import selectable_renderer

    @implementer(IPaymentViewRendererLookup)
    class SelectByOrganization(object):
        def __init__(self, selectable_renderer_factory, key_factory):
            self.selectable_renderer_factory = selectable_renderer_factory
            self.key_factory = key_factory

        def __call__(self, path_or_renderer_name, info, for_, plugin_type, plugin_id, **kwargs):
            info_ = RendererHelper(
                name=self.key_factory(path_or_renderer_name),
                package=None,
                registry=info.registry
                )
            return self.selectable_renderer_factory(info_)

    # カートにあるやつと少し中身が違います!!!!
    # コピペ(・A・)ｲｸﾅｲ!!
    @implementer(IPaymentViewRendererLookup)
    class Overridable(object):
        def __init__(self, selectable_renderer_factory, key_factory, resolver):
            self.bad_templates = set()
            self.selectable_renderer_factory = selectable_renderer_factory
            self.key_factory = key_factory
            self.resolver = resolver

        def get_template_paths(self, path):
            return [
                '%%(membership)s/plugins/%s' % path,
                'plugins/%s' % path,
                ]

        def __call__(self, path_or_renderer_name, info, for_, plugin_type, plugin_id, **kwargs):
            paths = self.get_template_paths(path_or_renderer_name)
            for path in paths:
                info_ = RendererHelper(
                    self.key_factory(path),
                    package=None,
                    registry=info.registry
                    )
                renderer = self.selectable_renderer_factory(info_)

                resolved_uri = "templates/%s" % renderer.implementation().uri # XXX hack: this needs to be synchronized with the value in mako.directories
                if resolved_uri in self.bad_templates:
                    continue
                else:
                    asset = self.resolver.resolve(resolved_uri)
                    if not asset.exists():
                        logger.debug('template %s does not exist' % resolved_uri)
                        self.bad_templates.add(resolved_uri)
                        continue
                return renderer
            return None

    config.include(selectable_renderer)

    renderer_factory = functools.partial(
        SelectableRendererFactory,
        selectable_renderer.selectable_renderer.select_fn
        ) # XXX

    config.add_payment_view_renderer_lookup(
        SelectByOrganization(
            renderer_factory,
            selectable_renderer.selectable_renderer
            ),
        'select_by_organization'
        )
    config.add_payment_view_renderer_lookup(
        Overridable(
            renderer_factory,
            selectable_renderer.selectable_renderer,
            AssetResolver(__name__)
            ),
        'overridable'
        )

def includeme(config):
    setup_renderers(config)
