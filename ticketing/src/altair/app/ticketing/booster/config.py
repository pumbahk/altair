from .interfaces import IBoosterSettings
from .interfaces import IPertistentProfileFactory
from pyramid.interfaces import IRequest
from zope.interface import implementer

@implementer(IBoosterSettings)
class BoosterSettings(object):
    @classmethod
    def from_settings(cls, settings, prefix="booster."):
        event_id = settings[prefix+"event_id"]
        membership_name = settings[prefix+"membership_name"]
        event_id = settings[prefix+"event_id"]
        return cls(event_id, membership_name)

    def __init__(self, event_id,  membership_name):
        self.event_id = event_id
        self.membership_name = membership_name

def add_booster_settings(config, settings, prefix="booster."):
    bsettings = BoosterSettings.from_settings(settings, prefix=prefix)
    config.registry.registerUtility(bsettings, IBoosterSettings)

def add_persistent_profile_factory(config, factory, name=""):
    config.registry.adapters.register([IRequest], IPertistentProfileFactory, name, factory)

def includeme(config):
    config.add_directive("add_booster_settings", add_booster_settings)
    config.add_directive("add_persistent_profile_factory", add_persistent_profile_factory)
