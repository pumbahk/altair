class Authenticated(object):
    def __init__(self, request, plugin, identity, metadata):
        self.request = request
        self.plugin = plugin
        self.identity = identity
        self.metadata = metadata
