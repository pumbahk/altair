# encoding: utf-8
from .interfaces import ICommunicator
from .eagles_communicator import EaglesCommunicator

def get_proxies(config):
    http_proxy = config.registry.settings.get('altair.discount_code.eagles_communicator.http_proxy', '')
    https_proxy = config.registry.settings.get('altair.discount_code.eagles_communicator.https_proxy', '')

    if not (http_proxy and https_proxy):
        return None
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    return proxies

def includeme(config):


    config.registry.registerUtility(
        EaglesCommunicator(
            endpoint_base=config.registry.settings.get('altair.discount_code.eagles_communicator.endpoint_base'),
            client_name=config.registry.settings.get('altair.discount_code.eagles_communicator.client_name'),
            hash_key=config.registry.settings.get('altair.discount_code.eagles_communicator.hash_key'),
            hash_key_extauth=config.registry.settings.get('altair.eagles_extauth.hash_key'),
            proxies=get_proxies(config),
            timeout=int(config.registry.settings.get('altair.eagles_extauth.timeout', 10))
            ),
        ICommunicator,
        name='disc_code_eagles'
        )