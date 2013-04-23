from zope.interface import implementer
from .interfaces import IVirtualProxyFactory

@implementer(IVirtualProxyFactory)
class VirtualAssetFactory(object):
    def __init__(self, env):
        self.env = env

    def create(self, obj):
        return VirtualAssetModel(self, obj)

class VirtualAssetModel(object):
    def __init__(self, env, obj):
        self.env = env
        self.obj = obj

    @property
    def filepath(self):
        o = self.obj
        if o.file_url:
            return o.file_url
        return o.fileapth

    @property
    def image_path(self):
        o = self.obj
        if o.image_url:
            return o.image_url
        return o.image_path

    @property
    def thumbnail_path(self):
        o = self.obj
        if o.thumbnail_url:
            return o.thumbnail_url
        return o.thumbnail_path
