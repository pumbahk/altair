from zope.interface import implementer
from .interfaces import IFileSession

class AfterCommit(object):
    def __init__(self, request, session, result, options=None):
        self.request = request
        self.session = session #session is filesession
        self.result = result
        self.options = options or {}

@implementer(IFileSession)
class AdaptsFileSession(object):
    def __init__(self, request, session):
        self.request = request
        self.session = session

    def commit(self, extra_args=None):
        result = self.session.commit(extra_args=extra_args)
        self.request.registry.notify(AfterCommit(self.request, self.session, result, self.session.options))
        return result

    def add(self, *args, **kwargs):
        return self.session.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.session.delete(*args, **kwargs)

    def abspath(self, *args, **kwargs):
        return self.session.abspath(*args, **kwargs)

    def __getattr__(self, k):
        return getattr(self.session, k)

    
