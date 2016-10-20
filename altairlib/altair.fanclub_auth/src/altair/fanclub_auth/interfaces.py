from zope.interface import Interface, Attribute

class IFanclubOAuth(Interface):
    def get_access_token(request, token):
        pass

class IFanclubAuth(Interface):
    def verify_authentication(request):
        """ """

    def on_verify(request):
        pass

    def on_extra_verify(request):
        pass

    def set_return_url(session, url):
        pass

    def get_redirect_url(self, session):
        """ """

    def combine_session_id(self, url, session):
        pass

    def new_session(self):
        pass
