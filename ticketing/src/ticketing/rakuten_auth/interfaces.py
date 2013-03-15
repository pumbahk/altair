from zope.interface import Interface

class ITokenizer(Interface):
    def tokenize(nonce, short_clamed_id):
        pass

class IRakutenOpenID(Interface):

    def get_redirect_url(self):
        """ """

    def verify_authentication(request):
        """ """
