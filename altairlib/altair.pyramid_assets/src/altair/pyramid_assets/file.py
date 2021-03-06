from pyramid.interfaces import IAssetDescriptor
from pyramid.path import Resolver, AssetResolver
from zope.interface import Interface, implementer, directlyProvides
from zope.interface.verify import verifyObject
from cStringIO import StringIO
from urlparse import urlparse
import re, os
from .interfaces import IAssetResolver, IWritableAssetDescriptor

def normalize_prefix(prefix, delimiter):
    return delimiter.join(c for c in prefix.split(delimiter) if c)

@implementer(IAssetDescriptor)
@implementer(IWritableAssetDescriptor)
class FileSchemeAssetDescriptor(object):
    def __init__(self, path):
        self.path = path

    def absspec(self):
        if os.path.isabs(self.path):
            return u'file://%s' % self.path
        else:
            return u'file:%s' % self.path

    def abspath(self):
        return os.path.abspath(self.path)

    def stream(self):
        return open(self.path, 'rb')

    def isdir(self):
        return os.path.isdir(self.path)

    def listdir(self):
        return os.listdir(self.path)

    def exists(self):
        return os.path.exist(self.path)

    def write(self, buf):
        open(self.path, 'wb').write(buf)
 
@implementer(IAssetResolver)
class FileSchemeAssetResolver(object):
    def __init__(self):
        pass

    def resolve(self, spec):
        url = urlparse(spec)
        if url.scheme != u'file':
            raise ValueError(spec)
        return FileSchemeAssetDescriptor(path=url.path)
