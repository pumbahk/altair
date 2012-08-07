import os
import zipfile
import contextlib  
 
@contextlib.contextmanager  
def current_directory(dirname=None):  
  curdir = os.getcwd()  
  try:  
    if dirname is not None:  
      os.chdir(dirname)  
    yield  
  finally:  
    os.chdir(curdir) 

def create_zipfile_from_directory(path, writename):
    with zipfile.ZipFile(writename, "w") as myzip:
        for root, d, files in os.walk(path):
            for f in files:
                myzip.write(os.path.join(root, f))
