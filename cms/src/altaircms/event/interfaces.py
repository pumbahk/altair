from zope.interface import Interface


class IAPIKeyValidator(Interface):
    def __call__(apikey):
        """ validate api key"""

class IEventRepositiry(Interface):
    def parse_and_save_event(data):
        """ """
