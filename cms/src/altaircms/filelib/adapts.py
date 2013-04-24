class AfterCommit(object):
    def __init__(self, request, session, result):
        self.request = request
        self.session = session #session is filesession
        self.result = result

class AdaptsFileSession(object):
    def __init__(self, request, session):
        self.request = request
        self.session = session

    def commit(self):
        result = self.session.commit()
        self.request.registry.notify(AfterCommit(self.request, self.session, result))
        return result

    def add(self, *args, **kwargs):
        return self.session.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.session.delete(*args, **kwargs)

    def abspath(self, *args, **kwargs):
        return self.session.abspath(*args, **kwargs)
