from zope.interface import Interface, Attribute

class IFanclubOAuth(Interface):
    def get_access_token(request, token):
        pass
