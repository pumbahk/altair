import hashlib
from zope.interface import implementer
from .interfaces import IPreviewSecret

@implementer(IPreviewSecret)
class PreviewSecret(object):
    def __init__(self, salt):
        self.salt = salt

    @classmethod
    def from_settings(cls, settings, prefix="altair.preview."):
        return cls(settings[prefix+"salt"])

    def __call__(self, k):
       return hashlib.sha1(self.salt+str(k)).hexdigest() #digest()?
