from .interfaces import IBoosterSettings
from zope.interface import implementer
from pyramid.path import (
    caller_package,
    DottedNameResolver
    )

@implementer(IBoosterSettings)
class BoosterSettings(object):
    @classmethod
    def from_settings(cls, settings, prefix="booster."):
        ## todo:
        resolver = DottedNameResolver(caller_package())

        event_id = settings[prefix+"event_id"]
        membership_name = settings[prefix+"membership_name"]
        event_id = settings[prefix+"event_id"]
        mail_sender = settings[prefix+"sender"]
        mail_render_names = resolver.maybe_resolve(settings[prefix+"mail_render_names"])
        mail_extra_info_populators = resolver.maybe_resolve(settings[prefix+"mail_extra_info_populators"])
        mail_subject = settings[prefix+"mail_subject"]        
        return cls(event_id, membership_name, mail_sender, mail_subject, mail_render_names, mail_extra_info_populators)

    def __init__(self, event_id,  membership_name, mail_sender, mail_subject, mail_render_names, mail_extra_info_populators):
        self.event_id = event_id
        self.membership_name = membership_name
        self.mail_sender = mail_sender
        self.mail_subject = mail_subject
        self.mail_render_names = mail_render_names
        self.mail_extra_info_populators = mail_extra_info_populators

def add_booster_settings(config, settings, prefix="booster."):
    bsettings = BoosterSettings.from_settings(settings, prefix=prefix)
    config.registry.registerUtility(bsettings, IBoosterSettings)

def includeme(config):
    config.add_directive("add_booster_settings", add_booster_settings)
