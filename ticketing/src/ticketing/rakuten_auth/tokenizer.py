import hmac
from zope.interface import implementer
from .interfaces import ITokenizer

def includeme(config):
    settings = config.settings
    secret = settings['altair.rakuten_auth.token_secret']
    tokenizer = Tokenizer(secret)
    config.registry.registerUtility(tokenizer)

@implementer(ITokenizer)
class Tokenizer(object):
    def __init__(self, secret):
        self.secret = secret

    def tokenize(self, nonce, short_clamed_id):
        return hmac.new(key=self.secret, msg=short_clamed_id + nonce).hexdigext()
