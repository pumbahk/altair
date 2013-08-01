from zope.interface import Interface
from altaircms.auth.interfaces import IAPIKeyValidator

class IEventRepository(Interface):
    def parse_and_save_event(request, data):
        """ """
