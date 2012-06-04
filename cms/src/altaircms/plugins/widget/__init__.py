from .installer import WidgetPluginInstaller

def widget_plugin_install(config, settings):
    pyramid_settings = config.registry.settings
    WidgetPluginInstaller(pyramid_settings).install(settings)

