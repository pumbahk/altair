
AFTER_REDIRECT_URL = "preview_after_invalidate_url"

def includeme(config):
    from .redirect import PreviewRedirectDefault
    from .interfaces import IPreviewRedirect
    config.registry.registerUtility(PreviewRedirectDefault(), IPreviewRedirect)

    from .interfaces import IPreviewSecret
    from .secret import PreviewSecret
    preview_secret = PreviewSecret.from_settings(config.registry.settings)
    config.registry.registerUtility(preview_secret, IPreviewSecret)

    config.include(setup_view)

def setup_view(config):
    config.add_route("__altair.preview.invalidate", "__preview/_invalidate")
    config.scan(".views")

    
