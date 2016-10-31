# -*- coding:utf-8 -*-

from zope.interface import Interface, Attribute

class IFanclubOAuth(Interface):
    """ polluxからoauthトークンを取得 """
    def get_request_token(request, callback_url):
        pass

    def get_access_token(request, request_token, request_token_secret, verifier):
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


class IFanclubAPI(Interface):
    """" トークンを使ってpolluxからリソースを取得する """
    def get_member_info(self):
        pass


class IFanclubAPIFactory(Interface):
    def __call__(request, access_token, access_secret):
        pass
