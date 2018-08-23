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
                u'{package}:templates/{login_body}/{ua_type}/{path}',
                u'{package}:templates/{organization_short_name}/fc_auth/{ua_type}/{path}',
                u'{package}:templates/{organization_short_name}/{ua_type}/fc_auth/{membership}/{path}',
                u'{package}:templates/{organization_short_name}/{ua_type}/fc_auth/{path}',
                u'{their_package}:templates/{organization_short_name}/{ua_type}/{path}',
            ]
        ),
        IDynamicRendererHelperFactory,
        name="fc_auth.overridable"
    )
