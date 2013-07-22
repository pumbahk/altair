from zope.interface import Interface, directlyProvides

class ISessionMaker(Interface):
    def __call__():
        """ create new session """
