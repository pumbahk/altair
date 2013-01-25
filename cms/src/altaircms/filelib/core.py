import logging
import os
import tempfile
logger = logging.getLogger(__name__)

from zope.interface import implementer, provider
from altaircms.filelib.interfaces import IUploadFile, IFileSession

from shutil import copyfileobj


from collections import namedtuple
SignaturedFile = provider(IUploadFile)(namedtuple("File", "name signature handler"))
File = provider(IUploadFile)(namedtuple("File", "name handler"))

def rename_file(src, dst):
    try:
        os.rename(src, dst)
    except OSError:
        directory = os.path.dirname(dst)
        logger.info("%s is not found. create it." % directory)
        os.makedirs(directory)
        os.rename(src, dst)

@implementer(IFileSession)
class FileSession(object):
    def __init__(self, prefix="", make_path=None):
        if make_path is None:
            self.make_path = lambda : os.path.abspath(prefix)
        else:
            self.make_path = make_path
        self.add_pool = []
        self.delete_pool = []

    def abspath(self, part):
        return os.path.join(self.make_path(), part)

    def is_overwrite(self, uploadfile):
        realpath = os.path.join(self.make_path(), uploadfile.name)
        return not os.path.exists(realpath)

    def add(self, uploadfile):
        if hasattr(uploadfile, "signature"):
            signatured_file = uploadfile
        elif hasattr(uploadfile, "file") and hasattr(uploadfile, "filename"): #for cgi.FieldStorage compability
            signatured_file = File(name=uploadfile.filename, handler=uploadfile.file)
        else:
            signatured_file = self._write_to_tmppath(uploadfile)
        self.add_pool.append(signatured_file)
        return signatured_file

    def delete(self, uploadfile):
        if isinstance(uploadfile, (str, unicode)): # for passing filename directly.
            uploadfile = File(name=uploadfile, handler=None)
        filepath = self.abspath(uploadfile.name)
        if uploadfile.handler:
            raise Exception("Stream file can't delete %s" % uploadfile)
        if not os.path.exists(filepath):
            raise Exception("%s is not found" % filepath)
        self.delete_pool.append(uploadfile)

    def commit(self):
        for deleted_file in self.delete_pool:
            filepath = self.abspath(deleted_file.name)
            logger.debug("filesession. delete: %s" % (filepath))
            try:
                os.remove(filepath)
            except OSError, e:
                logger.warn("%s is not deleted" % filepath)
                logger.exception(str(e))
            except Exception, e:
                logger.exception(str(e))

        for signatured_file in self.add_pool:
            try:
                realpath = os.path.join(self.make_path(), signatured_file.name)
                rename_file(signatured_file.signature, realpath)
                logger.debug("filesession. rename: %s -> %s" % (signatured_file.signature, realpath))
            except OSError, e:
                logger.warn("%s is not renamed" % signatured_file.signature)
                logger.exception(str(e))
            except Exception, e:
                logger.exception(str(e))

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
