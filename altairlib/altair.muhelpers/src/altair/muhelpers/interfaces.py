from zope.interface import Interface


class IMuMailerFactory(Interface):
    def __call__(self):
        pass
