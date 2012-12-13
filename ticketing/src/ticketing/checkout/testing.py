from zope.interface import implementer
from .interfaces import ISigner
from pyramid import testing

@implementer(ISigner)
class DummySigner(object):
    def __init__(self, sign_result):
        self.sign_result = sign_result
        self.called = []

    def __call__(self, target):
        self.called.append(target)
        return self.sign_result
