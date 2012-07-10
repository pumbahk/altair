from zope.interface import Interface
from zope.interface import Attribute

class ILogoutAction(Interface):
    external_url = Attribute("""logout api url""")

    def logout(request):
        """logout action; return to ActionResult object"""

class IActionResult(Interface):
    return_to = Attribute("return_to")
    headers = Attribute("headers")

class IOAuthComponent(Interface):
    client_id = Attribute("client id (organazation id)")
    secret_key = Attribute("secret_key")
    authorize_url = Attribute("authorize url")
    access_token_url = Attribute("access token url")
    
    def create_oauth_entry_url():
        pass

    def create_oauth_token_url(args):
        pass


class IAllowableQuery(Interface):
    def __call__(model):
        """ return allowable query(usually filtering by organization)"""
        pass
