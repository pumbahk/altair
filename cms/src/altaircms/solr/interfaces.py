from zope.interface import Interface

class IFulltextSearch(Interface):

    def create_from_request(request):
        """create object from request(classmethod)"""

    def query(*args, **kwargs):
        """ fulltext search"""

    def register(*args, **kwargs):
        """ register args"""
