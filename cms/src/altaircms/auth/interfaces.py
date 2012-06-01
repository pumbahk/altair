from zope.interface import Interface
from zope.interface import Attribute

class ILogoutAction(Interface):
    external_url = Attribute("""logout api url""")

    def logout(request):
        """logout action; return to ActionResult object"""

class IActionResult(Interface):
    return_to = Attribute("return_to")
    headers = Attribute("headers")

