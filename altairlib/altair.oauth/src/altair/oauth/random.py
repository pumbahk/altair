from base64 import b64encode
from os import urandom
from zope.interface import implementer
from .interfaces import IRandomStringGenerator

@implementer(IRandomStringGenerator)
class RandomStringGenerator(object):
    def __init__(self, len):
        self.len = len

    def __call__(self):
        return b64encode(urandom((3 * self.len + 3) / 4))[:self.len]

