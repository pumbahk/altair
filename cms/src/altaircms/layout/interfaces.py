from zope.interface import Interface

class ILayoutCreator(Interface):
    def create_file(params):
        pass

    def create_model(params):
        pass

