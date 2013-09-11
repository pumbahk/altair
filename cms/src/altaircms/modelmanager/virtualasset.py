from zope.interface import implementer
from .interfaces import IRenderingObjectFactory
import urlparse

_NOT_FOUND_IMG = "/static/img/not_found.jpg"

def normalize_url(request, url):
    if url.startswith("s3://"):
        return "//{}".format(url[5:].replace("/", ".s3.amazonaws.com/", 1))
    return url

    # return url.replace("s3://", "{0}://s3.amazonaws.com/".format(scheme))

"""
The bucket you are attempting to access must be addressed using the specified endpoint. Please send all future requests to this endpoint.
http://tstar-dev.s3.amazonaws.com/asset/RT/2013-04-24/90329f574d6e48c5a8e5cd87dad8c7a5.png *ok
http://s3.amazonaws.com/tstar-dev/asset/RT/2013-04-24/90329f574d6e48c5a8e5cd87dad8c7a5.png *ng
"""

@implementer(IRenderingObjectFactory)
class VirtualAssetFactory(object):
    def __init__(self, static_route_name, notfound_image=_NOT_FOUND_IMG):
        self.static_route_name = static_route_name
        self.notfound_image = notfound_image

    def create(self, request, obj):
        return VirtualAssetModel(request, self, obj)

class VirtualAssetModel(object):
    def __init__(self, request, env, obj):
        self.request = request
        self.env = env
        self.obj = obj

    def route_path(self, subpath):
        subpath = subpath or (self.obj and self.obj.image_path) or self.env.notfound_image
        if subpath.startswith(("/", "http://", "https://")):
            return subpath
        else:
            return self.request.route_path(self.env.static_route_name, subpath=subpath)
        
    @property
    def filepath(self):
        o = self.obj
        if o is None:
            return self.env.notfound_image
        if o.file_url:
            return normalize_url(self.request, o.file_url)
        return self.route_path(o.filepath)

    @property
    def image_path(self):
        o = self.obj
        if o is None:
            return self.env.notfound_image
        if o.image_url:
            return normalize_url(self.request, o.image_url)
        return self.route_path(o.image_path)

    @property
    def thumbnail_path(self):
        o = self.obj
        if o is None:
            return self.env.notfound_image
        if o.thumbnail_url:
            return normalize_url(self.request, o.thumbnail_url)
        return self.route_path(o.thumbnail_path)

    def __getattr__(self, k):
        return getattr(self.obj, k)
