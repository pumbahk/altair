from zope.interface import Interface, Attribute

class IOrderDescriptorRegistry(Interface):
    def add_descriptor(descriptor):
        pass


class IOrderDescriptor(Interface):
    type = Attribute('''''')
    name = Attribute('''''')
    registry = Attribute('''''')

    def get_localized_name(request):
        pass

    def get_renderer(self, kind):
        pass


class IOrderDescriptorRenderer(Interface):
    def __call__(request, descr_registry, descr, value):
        pass
