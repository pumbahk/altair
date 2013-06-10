from zope.interface import Interface
from zope.interface import Attribute

class IBoosterSettings(Interface):
    event_id  = Attribute("target event id")
    membership_name = Attribute("target membership name")
