from . import IDENT_METADATA_KEY

class Authenticated(object):
    def __init__(self, request, userid, metadata):
        self.request = request
        self.userid = userid
        self.metadata = metadata
