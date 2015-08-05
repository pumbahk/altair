from zope.interface import Interface, Attribute

class ITabularDataColumn(Interface):
    name = Attribute('')
    spec = Attribute('')

class ITabularDataColumnSpecification(Interface):
    length = Attribute('')
    constraints = Attribute('')

    def marshal(context, python_value):
        pass

    def unmarshal(context, stringized_value):
        pass

class ITabularDataMarshaller(Interface):
    def __call__(row, out):
        pass

class ITabularDataUnmarshaller(Interface):
    def __call__(in_, exc_handler=None):
        pass

class IFileSender(Interface):
    def send_file(remote_path, f):
        pass

class IFileSenderFactory(Interface):
    def __call__(**kwargs):
        pass


class IFamiPortFileManagerFactory(Interface):
    def add_configuration_from_settings(type, settings):
        pass

    def get_configuration(type):
        pass

    def __call__(type, **overrides):
        pass
