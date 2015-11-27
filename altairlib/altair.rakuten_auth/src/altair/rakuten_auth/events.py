from . import IDENT_METADATA_KEY

class Authenticated(object):
    def __init__(self, request, plugin, id, metadata):
        self.request = request
        self.plugin = plugin
        self.id = id
        self.metadata = metadata
