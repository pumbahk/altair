import hmac
from zope.interface import implementer
from .interfaces import ITokenizer

def includeme(config):
    settings = config.registry.settings
    secret = settings['altair.rakuten_auth.token_secret']
    tokenizer = Tokenizer(secret)
    config.registry.registerUtility(tokenizer)

@implementer(ITokenizer)
class Tokenizer(object):
    def __init__(self, secret):
        self.secret = secret

    def tokenize(self, nonce, short_claimed_id):
        return hmac.new(key=self.secret, msg=short_claimed_id + nonce).hexdigest()
