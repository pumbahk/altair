class DummyMaker(object):
    def __init__(self, result):
        self.result = result

    def __call__(self):
        return self.result
