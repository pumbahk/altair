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
        content_length = None
        if hasattr(io, 'len'):
            content_length = io.len
        elif hasattr(io, 'seekable') and hasattr(io, 'seek') and hasattr(io, 'tell') and io.seekable():
            pos = io.tell()
            io.seek(0, 2)
            content_length = io.tell()
            io.seek(pos, 0)
        app_iter = None
        if request is not None:
            environ = request.environ
            if 'wsgi.file_wrapper' in environ:
                app_iter = environ['wsgi.file_wrapper'](io, _BLOCK_SIZE)
        if app_iter is None:
            app_iter = FileIter(io, _BLOCK_SIZE)
        self.app_iter = app_iter
        # assignment of content_length must come after assignment of app_iter
        if content_length is not None:
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

def get_absolute_path(name, curdir):
    if os.path.isabs(name):
        return name
    else:
        return os.path.join(curdir, name)

class ZipFileCreateFromList(object):
    def __init__(self, writename, files, curdir=None, flatten=False):
        self.writename = writename
        self.files = files
        self.curdir = curdir or os.getcwd()
        self.flatten = flatten

    def write_files_flatten(self, myzip, files):
        cwd = os.path.abspath(os.getcwd())
        try:
            for f in self.files:
                abspath = get_absolute_path(f, self.curdir)
                os.chdir(os.path.dirname(abspath))
                myzip.write(os.path.basename(abspath))
        finally:
            os.chdir(cwd)

    def write_files(self, myzip, files):
        for f in self.files:
            abspath = get_absolute_path(f, self.curdir)
            myzip.write(abspath)

    def __call__(self):
        path = get_absolute_path(self.writename, self.curdir)
        with zipfile.ZipFile(path, "w") as myzip:
            if self.flatten:
                self.write_files_flatten(myzip, self.files)
            else:
                self.write_files(myzip, self.files)
        return path

class ZipFileCreateRecursiveWalk(object):
    def __init__(self, writename, rootdir, curdir=None, flatten=False):
        self.writename = writename
        self.rootdir = rootdir
        self.curdir = curdir or rootdir
        self.flatten = flatten

    def write_files_flatten(self, myzip):
        cwd = os.path.abspath(os.getcwd())
        try:
            for root, d, files in os.walk(self.rootdir):
                for f in files:
                    os.chdir(root)
                    myzip.write(f)
        finally:
            os.chdir(cwd)

    def write_files(self, myzip):
        for root, d, files in os.walk(self.rootdir):
            for f in files:
                myzip.write(os.path.join(root, f))

    def __call__(self):
        path = get_absolute_path(self.writename, self.curdir)
        with zipfile.ZipFile(path, "w") as myzip:
            if self.flatten:
                self.write_files_flatten(myzip)
            else:
                self.write_files(myzip)
        return path
