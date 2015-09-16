from zope.interface import Interface

class IOAuthAPIFactory(Interface):
    def create_oauth_negotiator():
        pass


    def create_oauth_api(access_token):
        pass

class IOAuthNegotiator(Interface):
    def get_access_token(request, authorization_code, redirect_uri):
        pass


class IOAuthAPI(Interface):
    def get_user_info(request):
        pass
