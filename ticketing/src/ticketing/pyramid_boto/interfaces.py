from zope.interface import Interface

class IS3ConnectionFactory(Interface):
    def __call__():
        pass
