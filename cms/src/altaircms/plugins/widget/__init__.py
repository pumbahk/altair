from .installer import WidgetPluginInstaller

def widget_plugin_install(config, settings):
    pyramid_settings = config.registry.settings
    WidgetPluginInstaller(pyramid_settings).install(settings)

def includeme(config):
    api_impl = (config.maybe_dotted(".api.StockDataAPI")
                (config.registry.settings["altaircms.backend.url"],
                 config.registry.settings["altaircms.backend.apikey"]))
    config.registry.registerUtility(api_impl,
                                    config.maybe_dotted("altaircms.plugins.interfaces.IExternalAPI"),
                                    api_impl.__class__.__name__)
