import os
import zipfile
import contextlib  
import shutil
from datetime import datetime

## utility
def decompose_path(path):
    """
    >>> decompose_path("/foo/bar/boo.txt")
    ('/foo/bar', 'boo', '.txt')
    """
    d, b = os.path.split(path)
    b_, ext = os.path.splitext(b)
    return d, b_, ext
 
@contextlib.contextmanager  
def current_directory(dirname=None):  
  curdir = os.getcwd()  
  try:  
    if dirname is not None:  
      os.chdir(dirname)  
    yield  
  finally:  
    os.chdir(curdir) 

def create_zipfile_from_directory(path, writename, file_list = None):
    with zipfile.ZipFile(writename, "w") as myzip:
        if not file_list:
            for root, d, files in os.walk(path):
                for f in files:
                    myzip.write(os.path.join(root, f))
        else:
            for f in file_list:
                    myzip.write(f)

def is_zipfile(target):
    return zipfile.is_zipfile(target)

def extract_directory_from_zipfile(path, target):
    if not os.path.exists(path):
        os.makedirs(path)
    with zipfile.ZipFile(target, "r") as myzip:
        myzip.extractall(path)

def _default_change_name(path, _now=datetime.now):
    """
    >>> _default_change_name("/foo/bar.txt", lambda : datetime(2012, 1, 1))
    '/foo/.bar.20120101000000.txt'
    """
    dirname, basename, extname = decompose_path(path)
    sym = _now().strftime("%Y%m%d%H%M%S")
    return os.path.join(dirname, "."+basename+"."+sym+extname)

def create_directory_snapshot(path, change_name=_default_change_name):
    if not os.path.isdir(path):
        if os.path.exists(path):
            raise Exception("%s is not directory" % path)
        os.makedirs(path)
    src = os.path.abspath(path)
    dst = change_name(path)
    os.rename(src, dst)
    return dst

def snapshot_rollback(src, dst):
    shutil.rmtree(src)
    os.rename(dst, src)
    return src

if __name__ == "__main__":
    import doctest
    doctest.testmod()
