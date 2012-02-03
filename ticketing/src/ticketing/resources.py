from zope.interface import Interface, Attribute, implements

class Root(object):
    def __init__(self, request):
        self.request = request

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
