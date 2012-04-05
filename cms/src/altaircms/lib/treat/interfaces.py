from zope.interface import Interface

class ICreate(Interface):
    def create(self, *args, **kwargs):
        pass

class IUpdate(Interface):
    def update(self, *args, **kwargs):
        pass

