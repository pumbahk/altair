from .mu import Mailer
from .interfaces import IMuMailerFactory

from zope.interface import implementer

from s3 import includeme as s3_includeme

@implementer(IMuMailerFactory)
class DefaultMuMailerFactory(object):
    def __init__(self, config):
        self.config = {
            "MailId": config.registry.settings.get('altair.mu.mail_id'),
            "AuthKey": config.registry.settings.get('altair.mu.auth_key')
        }
        self.from_address = config.registry.settings.get('altair.mu.from_address')
        self.from_name = config.registry.settings.get('altair.mu.from_name')

    def __call__(self):
        return Mailer(self.from_address, self.from_name, self.config)


def includeme(config):
    factory = DefaultMuMailerFactory(config)
    if factory is not None:
        config.registry.registerUtility(factory, IMuMailerFactory)

    s3_includeme(config)
