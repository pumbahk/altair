import logging
from zope.interface import implementer

from .interfaces import IFanclubOAuth

logger = logging.getLogger(__name__)

@implementer(IFanclubOAuth)
class FanclubOAuth(object):
    def __init__(self, endpoint, consumer_key, secret, timeout=10):
        self.endpoint = endpoint
        self.consumer_key = consumer_key
        self.secret = secret
        self.timeout = int(timeout)

    def get_access_token(self, request, token):
        pass


def get_oauth_consumer_key_from_config(config, prefix):
    settings = config.registry.settings
    consumer_key_builder = settings.get(prefix + 'oauth.consumer_key_builder')
    if consumer_key_builder is not None:
        consumer_key_builder = consumer_key_builder.strip()
    if not consumer_key_builder:
        consumer_key = settings[prefix + 'oauth.consumer_key']
    else:
        consumer_key = config.maybe_dotted(consumer_key_builder)
    return consumer_key

def get_oauth_consumer_secret_from_config(config, prefix):
    settings = config.registry.settings
    consumer_secret_builder = settings.get(prefix + 'oauth.consumer_secret_builder')
    if consumer_secret_builder is not None:
        consumer_secret_builder = consumer_secret_builder.strip()
    if not consumer_secret_builder:
        consumer_secret = settings[prefix + 'oauth.secret']
    else:
        consumer_secret = config.maybe_dotted(consumer_secret_builder)
    return consumer_secret

def fanclub_oauth_from_config(config, prefix):
    settings = config.registry.settings
    consumer_key = get_oauth_consumer_key_from_config(config, prefix)
    consumer_secret = get_oauth_consumer_secret_from_config(config, prefix)
    return FanclubOAuth(
        endpoint=settings[prefix + 'oauth.endpoint.access_token'],
        consumer_key=consumer_key,
        secret=consumer_secret,
        timeout=settings[prefix + 'timeout']
        )

def includeme(config):
    from . import CONFIG_PREFIX
    config.registry.registerUtility(
        fanclub_oauth_from_config(config, CONFIG_PREFIX),
        IFanclubOAuth
        )
