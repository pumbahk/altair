from zope.interface import Interface

class ISejNotificationProcessor(Interface):
    def __call__(sej_order, order, notification):
        pass

class ISejNotificationProcessorFactory(Interface):
    def __call__(request, now):
        pass
