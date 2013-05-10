def includeme(config):
    from .stockstatus import StockDataAPI
    from altaircms.plugins.interfaces import IExternalAPI
    api_impl = StockDataAPI(config.registry.settings["altaircms.backend.url"],
                            config.registry.settings["altaircms.backend.apikey"])
    config.registry.registerUtility(api_impl, IExternalAPI, api_impl.__class__.__name__)
