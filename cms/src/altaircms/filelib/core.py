import logging
import os
import tempfile
logger = logging.getLogger(__name__)

from zope.interface import implementer, provider
from altaircms.filelib.interfaces import IUploadFile, IFileSession

import shutil
from shutil import copyfileobj


from collections import namedtuple
SignaturedFile = provider(IUploadFile)(namedtuple("File", "name signature handler"))
File = provider(IUploadFile)(namedtuple("File", "name handler"))

def rename_file(src, dst):
    try:
        shutil.move(src, dst) #for preventing invalid cross-device link.
    except (OSError, IOError), e:
        directory = os.path.dirname(dst)
        logger.exception(str(e))
        if not os.path.exists(directory):
            logger.info("%s is not found. create it." % directory)
            os.makedirs(directory)
            shutil.move(src, dst)

def on_file_exists_try_rename(target, realpath, retry):
    old_one_destination = tempfile.mktemp()
    logger.info("%s is exists. rename old one -> %s" % (realpath,  old_one_destination))
    shutil.move(realpath, old_one_destination)
    return retry(target, realpath)

def on_file_exists_overwrite(target, realpath, retry):
    return rename_file(target.signature, realpath)

class FileCreator(object):
    def __init__(self, root, on_file_exists=on_file_exists_overwrite):
        self.root = root
        self.pool = []
        self.on_file_exists = on_file_exists

    def add(self, uploadfile):
        if hasattr(uploadfile, "signature"):
            signatured_file = uploadfile
        elif hasattr(uploadfile, "file") and hasattr(uploadfile, "filename"): #for cgi.FieldStorage compability
            signatured_file = File(name=uploadfile.filename, handler=uploadfile.file)
        else:
            signatured_file = self._write_to_tmppath(uploadfile)
        self.pool.append(signatured_file)
        return signatured_file

    def _get_realpath(self, target):
        return os.path.join(self.root.make_path(), target.name)

    def _commit_one(self, target, realpath):
        try:
            if os.path.exists(realpath):
                return self.on_file_exists(target, realpath, self._commit_one)
            else:
                rename_file(target.signature, realpath)
                logger.debug("filesession. rename: %s -> %s" % (target.signature, realpath))
        except OSError, e:
            logger.warn("%s is not renamed" % target.signature)
            logger.exception(str(e))
        except Exception, e:
            logger.exception(str(e))
            raise
        
    def commit(self):
        while self.pool:
            signatured_file = self.pool.pop(0)
            realpath = self._get_realpath(signatured_file)
            self._commit_one(signatured_file, realpath)

    def _write_to_tmppath(self, uploadfile):
        path = tempfile.mktemp() #suffix?
        self.write_to_path(path, uploadfile.handler)
        return SignaturedFile(name=uploadfile.name, 
                                    handler=uploadfile.handler, 
                                    signature=path)

    def write_to_path(self, path, handler, option="wb"):
        name = getattr(handler, "name", "<stream>")
        with open(path, option) as wf:
            logger.debug("FileSession: write file. %s -> %s" % (name, path))
            copyfileobj(handler, wf)
    
class FileDeleter(object):
    def __init__(self, root):
        self.root = root
        self.pool = []

    def delete(self, uploadfile):
        if isinstance(uploadfile, (str, unicode)): # for passing filename directly.
            uploadfile = File(name=uploadfile, handler=None)
        filepath = self.root.abspath(uploadfile.name)
        if uploadfile.handler:
            raise Exception("Stream file can't delete %s" % uploadfile)
        if not os.path.exists(filepath):
            raise Exception("%s is not found" % filepath)
        self.pool.append(uploadfile)
        
    def commit(self):
        while self.pool:
            deleted_file = self.pool.pop(0)
            filepath = self.root.abspath(deleted_file.name)
            logger.debug("filesession. delete: %s" % (filepath))
            try:
                os.remove(filepath)
            except (OSError, IOError), e:
                logger.warn("%s is not deleted" % filepath)
                logger.exception(str(e))
            except Exception, e:
                logger.exception(str(e))
                raise

@implementer(IFileSession)
class FileSession(object):
    def __init__(self, prefix="", make_path=None, on_file_exists=on_file_exists_overwrite):
        if make_path is None:
            self.make_path = lambda : os.path.abspath(prefix)
        else:
            self.make_path = make_path
        self.deleter = FileDeleter(self)
        self.creator = FileCreator(self, on_file_exists=on_file_exists)
            

    def abspath(self, part):
        return os.path.join(self.make_path(), part)

    def is_overwrite(self, uploadfile):
        realpath = os.path.join(self.make_path(), uploadfile.name)
        return not os.path.exists(realpath)

    def add(self, uploadfile):
        return self.creator.add(uploadfile)

    def delete(self, uploadfile):
        return self.deleter.delete(uploadfile)

    def commit(self):
        self.deleter.commit()
        self.creator.commit()
