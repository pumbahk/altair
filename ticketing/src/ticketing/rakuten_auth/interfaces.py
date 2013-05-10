from zope.interface import Interface

class IRakutenOpenID(Interface):
    def get_session_id(request):
        pass

    def new_session(self):
        pass

    def get_session(self, request):
        pass

    def combine_session_id(self, url, session):
        pass

    def get_redirect_url(self, session):
        """ """

    def verify_authentication(request):
        """ """

    def get_return_url(sessoin):
        pass

    def set_return_url(session, url):
        pass

    def on_verify(request):
        pass

    def on_extra_verify(request):
        pass


class IRakutenOAuth(Interface):
    def get_access_token(oauth_consumer_key, oauth_token, secret):
        pass

class IRakutenIDAPI(Interface):
    def get_basic_info():
        pass

    def get_contact_info():
        pass

    def get_point_account():
        pass

class IRakutenIDAPIFactory(Interface):
    def __call__(access_token):
        pass

