def includeme(config):
    from altair.preview.interfaces import IPreviewPermission
    from .checking import PreviewPermission
    config.include("altair.preview")
    config.registry.registerUtility(PreviewPermission(), IPreviewPermission)

    config.add_tween('altair.preview.tweens.preview_tween', under=".tweens.mobile_encoding_convert_factory")

