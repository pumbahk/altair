from .interfaces import IBoosterSettings
from zope.interface import implementer

@implementer(IBoosterSettings)
class BoosterSettings(object):
    @classmethod
    def from_settings(cls, settings, prefix="booster."):
        event_id = settings[prefix+"event_id"]
        membership_name = settings[prefix+"membership_name"]
        return cls(event_id, membership_name)

    def __init__(self, event_id,  membership_name):
        self.event_id = event_id
        self.membership_name = membership_name

def add_booster_settings(config, settings, prefix="booster."):
    bsettings = BoosterSettings.from_settings(settings, prefix=prefix)
    config.registry.registerUtility(bsettings, IBoosterSettings)

def includeme(config):
    config.add_directive("add_booster_settings", add_booster_settings)
