from zope.interface import Interface

class ICommunicator(Interface):
    def get_user_profile(openid_claimed_id):
        pass
