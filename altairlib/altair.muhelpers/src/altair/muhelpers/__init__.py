from .mu import Mailer
from .interfaces import IMuMailerFactory

from zope.interface import implementer


@implementer(IMuMailerFactory)
class DefaultMuMailerFactory(object):
    def __init__(self, config):
        self.config = {
            "MailId": config.registry.settings.get('altair.mu.mail_id'),
            "AuthKey": config.registry.settings.get('altair.mu.auth_key')
        }

    def __call__(self):
        return Mailer(self.config)


def includeme(config):
    factory = DefaultMuMailerFactory(config)
    if factory is not None:
        config.registry.registerUtility(factory, IMuMailerFactory)
