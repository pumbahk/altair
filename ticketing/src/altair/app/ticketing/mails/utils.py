from pyramid.events import BeforeRender

def build_value_with_render_event(request, value, system_values=None, context=None):
    if system_values is None:
        system_values = {
            'view':None,
            'renderer_name':"*dummy", # b/c
            'renderer_info':"*dummy",
            '_context': context,
            'request':request,
            'req':request,
            }
    system_values = BeforeRender(system_values, value)
    registry = request.registry
    registry.notify(system_values)
    system_values.update(value)
    return system_values

def unescape(s):
    from HTMLParser import HTMLParser
    return HTMLParser.unescape.__func__(HTMLParser, s)
