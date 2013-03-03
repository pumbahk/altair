import mimetypes
from .swfrect import swf_width_and_height

try:
    import Image #PIL?
except  ImportError:
    from PIL import Image


def detect_mimetype_from_filename(filename, params=None):
    params = params or {}
    mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    params.update(mimetype=mimetype)
    return params

def detect_size_from_io(io, params=None):
    pos = io.tell()
    params = params or {}
    try:
        while True:
            if io.read(4096) == "":
                break
        params.update(size=io.tell())
    finally:
        io.seek(pos)
    return params


def detect_width_height_from_imageio(imageio, params=None):
    params = params or {}
    pos = imageio.tell()
    try:
        width, height = Image.open(imageio).size
        params.update(width=width, height=height)
    finally:
        imageio.seek(pos)    
    return params

def detect_width_height_from_flashio(flashio, params=None):
    params = params or {}
    pos = flashio.tell()
    try:
        width, height = swf_width_and_height(flashio)
        params.update(width=width, height=height)
    finally:
        flashio.seek(pos)    
    return params

class ImageInfoDatector(object):
    def __init__(self, request):
        self.request = request

    def detect(self, io, filename):
        params = {}
        params = detect_mimetype_from_filename(filename, params=params)
        params = detect_size_from_io(io, params=params)
        params = detect_width_height_from_imageio(io, params=params)
        return params

class MovieInfoDatector(object):
    def __init__(self, request):
        self.request = request

    def detect(self, io, filename):
        params = {}
        params = detect_mimetype_from_filename(filename, params=params)
        params = detect_size_from_io(io, params=params)
        return params


class FlashInfoDatector(object):
    def __init__(self, request):
        self.request = request

    def detect(self, io, filename):
        params = {}
        params = detect_mimetype_from_filename(filename, params=params)
        params = detect_size_from_io(io, params=params)
        params = detect_width_height_from_flashio(io, params=params)
        return params
