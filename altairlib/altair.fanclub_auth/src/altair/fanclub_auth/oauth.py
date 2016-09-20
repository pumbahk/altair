from zope.interface import implementer

from .interfaces import IFanclubOAuth

logger = logging.getLogger(__name__)

@implementer(IRakutenOAuth)
class FanclubOAuth(object):
    pass

def includeme(config):
    from . import CONFIG_PREFIX
    config.registry.registerUtility(
        rakuten_oauth_from_config(config, CONFIG_PREFIX),
        IRakutenOAuth
        )
