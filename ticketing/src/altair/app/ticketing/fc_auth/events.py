class Authenticated(object):
    def __init__(self, request, membership, id, metadata):
        self.request = request
        self.membership = membership
        self.id = id
        self.metadata = metadata
