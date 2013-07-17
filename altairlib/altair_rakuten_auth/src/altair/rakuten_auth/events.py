class Authenticated(object):
    def __init__(self, request, identity):
        self.request = request
        self.identity = identity
