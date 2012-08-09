from zope.interface import Interface
from zope.interface import Attribute

class IConflictValidateFunction(Interface):
    def __call__(config, target):
        """ validate target element is ok or not. one of target candidates is widget name"""

class IWidgetAggregateDispatcher(Interface):
    def dispatch(request, something):
        pass

class IWidgetUtility(Interface):
    """ has convinience functions. this is adhoc"""

    settings = Attribute("settings")

    def parse_settings(config, configparser):
        """parse settings. default flow is below.
        settings = dict(configparser.items("your-widget-name"))
        self.settings = self.bulid_settings(settings)
        """

class IExternalAPI(Interface):
    external_url = Attribute("external url")

from pyramid.interfaces import IDict
class IExtraResource(IDict):
    """ settings object for each organization
    """
    
