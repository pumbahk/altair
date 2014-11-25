from zope.interface import Interface, Attribute

class IRendererHelper(Interface):
    renderer = Attribute('''renderer''')

    def get_renderer():
        pass

    def render_view(request, response, view, context):
        pass
   
    def render(value, system_values, request=None):
        pass 

    def render_to_response(value, system_values, request=None):
        pass

    def clone(name=None, package=None, registry=None):
        pass

class ILateBoundRendererHelper(IRendererHelper):
    def bind(registry, package):
        pass

class IDynamicRendererHelperFactory(Interface):
    def __call__(name, package, registry, **kwargs):
        pass

