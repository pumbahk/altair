from . import IDENT_METADATA_KEY

class Authenticated(object):
    def __init__(self, request, id, metadata):
        self.request = request
        self.id = id
        self.metadata = metadata
