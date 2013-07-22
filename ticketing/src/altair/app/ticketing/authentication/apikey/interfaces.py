from zope.interface import Interface, Attribute

class IAPIKeyEntryResolverFactory(Interface):
    def __call__(userid_prefix):
        """returns the IAPIKeyEntryResolver"""

class IAPIKeyEntryResolver(Interface):
    def __call__(apikey, request):
        """validate API key and returns group principals"""

class IAPIKeyEntry(Interface):
    userid = Attribute("""userid""")
    expiry = Attribute("""expiry""")
    principals = Attribute("""principals""")
