import logging

logger = logging.getLogger(__name__)

def includeme(config):
    from .stockstatus import StockDataAPI
    from altaircms.plugins.interfaces import IExternalAPI
    backend_url = config.registry.settings.get("altaircms.backend.inner.url")
    if backend_url is None:
        logger.warning('altaircms.backend.inner.url is not given. Using deprecated altaircms.backend.url instead')
        backend_url = config.registry.setting.get('altaircms.backend.url')
    api_impl = StockDataAPI(backend_url,
                            config.registry.settings["altaircms.backend.apikey"])
    config.registry.registerUtility(api_impl, IExternalAPI, api_impl.__class__.__name__)
