from altair.pyramid_dynamic_renderer import IDynamicRendererHelperFactory, RendererHelperProxy
from altair.app.ticketing.cart.rendering import OverridableTemplateRendererHelperFactory

def overridable_renderer(name):
    return RendererHelperProxy(
        lambda name, package, registry, **kwargs: \
            registry.queryUtility(
                IDynamicRendererHelperFactory,
                name="fc_auth.overridable"
                )(name, package, registry, **kwargs),
        name
        )

def includeme(config):
    config.registry.registerUtility(
        OverridableTemplateRendererHelperFactory(
            config.registry.__name__,
            lambda name, package, registry, request, **kwargs: request.view_context,
            [
                '%(package)s:templates/%(organization_short_name)s/%(ua_type)s/fc_auth/%(membership)s/%(path)s',
                '%(package)s:templates/%(organization_short_name)s/%(ua_type)s/fc_auth/%(path)s',
                '%(their_package)s:templates/%(organization_short_name)s/%(ua_type)s/%(path)s',
                ]
            ),
        IDynamicRendererHelperFactory,
        name="fc_auth.overridable"
        )
