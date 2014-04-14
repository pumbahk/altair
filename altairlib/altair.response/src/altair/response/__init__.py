# -*- coding:utf-8 -*-
from pyramid.response import(
    _BLOCK_SIZE,
    FileIter,
    Response
)
import os.path
import zipfile

## almost copy of pyramid.response.FileResponse
class FileLikeResponse(Response):
     def __init__(self, io, request=None, cache_max_age=None,
                 content_type=None, content_encoding=None,
                 filename=None):
        super(FileLikeResponse, self).__init__(conditional_response=True)
        if content_type is None:
            content_type = 'application/octet-stream'
        self.content_type = content_type
        self.content_encoding = content_encoding
        if filename is not None:
            self.headers=[
                ('Content-Disposition', 'attachment; filename=%s' % filename),
                ]
        content_length = io.len
        app_iter = None
        if request is not None:
            environ = request.environ
            if 'wsgi.file_wrapper' in environ:
                app_iter = environ['wsgi.file_wrapper'](io, _BLOCK_SIZE)
        if app_iter is None:
            app_iter = FileIter(io, _BLOCK_SIZE)
        self.app_iter = app_iter
        # assignment of content_length must come after assignment of app_iter
        self.content_length = content_length
        if cache_max_age is not None:
            self.cache_expires = cache_max_age


class ZipFileResponse(Response):
    def __init__(self, zip_create, request=None, cache_max_age=None,
                 content_type=None, content_encoding=None, filename=None):
        super(ZipFileResponse, self).__init__(conditional_response=True)
        self.content_type = content_type
        self.content_encoding = content_encoding
        if filename is not None:
            self.headers=[
                ('Content-Disposition', 'attachment; filename=%s' % filename),
                ]
        path = zip_create()
        content_length = os.path.getsize(path)
        f = open(path, 'rb')
        app_iter = None
        if request is not None:
            environ = request.environ
            if 'wsgi.file_wrapper' in environ:
                app_iter = environ['wsgi.file_wrapper'](f, _BLOCK_SIZE)
        if app_iter is None:
            app_iter = FileIter(f, _BLOCK_SIZE)
        self.app_iter = app_iter
        # assignment of content_length must come after assignment of app_iter
        self.content_length = content_length
        if cache_max_age is not None:
            self.cache_expires = cache_max_age

class ZipFileCreateFromList(object):
    def __init__(self, writename, files, curdir=None):
        self.writename = writename
        self.files = files
        self.curdir = curdir or os.path.curdir

    def __call__(self):
        if os.path.isabs(self.writename):
            path = self.writename
        else:
            path = os.path.join(self.curdir, self.writename)
        with zipfile.ZipFile(path, "w") as myzip:
            for f in self.files:
                myzip.write(os.path.join(self.curdir, f))
        return path

class ZipFileCreateRecursiveWalk(object):
    def __init__(self, writename, rootdir, curdir=None):
        self.writename = writename
        self.rootdir = rootdir
        self.curdir = curdir or rootdir

    def __call__(self):
        if os.path.isabs(self.writename):
            path = self.writename
        else:
            path = os.path.join(self.curdir, self.writename)
        with zipfile.ZipFile(path, "w") as myzip:
            for root, d, files in os.walk(self.rootdir):
                for f in files:
                    myzip.write(os.path.join(root, f))
        return path
