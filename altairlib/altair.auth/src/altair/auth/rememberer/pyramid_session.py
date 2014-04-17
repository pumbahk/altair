from zope.interface import implementer

from repoze.who.interfaces import IIdentifier

from altair.auth.api import get_current_request

@implementer(IIdentifier)
class PyramidSessionBasedRemembererPlugin(object):
    def __init__(self, key):
        self.key = key

    def identify(self, environ):
        request = get_current_request(environ) 
        return request.session.get(self.key)

    # IIdentifier
    def forget(self, environ, identity):
        request = get_current_request(environ)
        try:
            del request.session[self.key]
        except KeyError:
            pass
        return []

    # IIdentifier
    def remember(self, environ, identity):
        request = get_current_request(environ)
        request.session[self.key] = identity

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            id(self)) #pragma NO COVERAGE

def _bool(value):
    if isinstance(value, basestring):
        return value.lower() in ('yes', 'true', '1')
    return value

def make_plugin(key=__name__):
    plugin = PyramidSessionBasedRemembererPlugin(key)
    return plugin

