from zope.interface import Interface


class IRakutenOpenID(Interface):

    def get_redirect_url(self):
        """ """

    def verify_authentication(request):
        """ """
